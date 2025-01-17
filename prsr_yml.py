# Exmple run scritp on Windows
#
# Find $ (dollar). Character escaping - \
# py prsr_yml.py application.yml ".\$.*"
#
# Find sometext
# py prsr_yml.py application.yml ".*sometext.*"
import re
import argparse
from collections import defaultdict

# Function to preprocess YAML content and track line numbers
def preprocess_yaml(file_path):
    cleaned_lines = []
    line_mapping = []  # To track original line numbers
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            # Remove comments and separators
            stripped_line = line.split("#")[0].strip()  # Remove comments
            if stripped_line and stripped_line not in {"---", "..."}:
                cleaned_lines.append(stripped_line)
                line_mapping.append(line_number)
    return cleaned_lines, line_mapping

# Function to parse YAML manually and track line numbers
def parse_yaml_manually(cleaned_lines, line_mapping):
    current_path = []
    data = defaultdict(list)

    for index, line in enumerate(cleaned_lines):
        indent_level = len(line) - len(line.lstrip())
        key_value = line.strip().split(":", 1)
        line_number = line_mapping[index]  # Get the original line number

        # Handle key-value pairs
        if len(key_value) == 2:
            key, value = key_value[0].strip(), key_value[1].strip()
            value = value.strip('"').strip("'")  # Remove quotes if present

            # Adjust the current path based on indentation
            while len(current_path) > indent_level // 2:
                current_path.pop()
            current_path.append(key)

            # Record the full path, value, and line number
            full_path = ".".join(current_path)
            data[full_path].append((value, line_number))

        elif len(key_value) == 1:  # Keys without values
            key = key_value[0].strip()
            while len(current_path) > indent_level // 2:
                current_path.pop()
            current_path.append(key)

    return data

# Function to find matches in the parsed YAML data
def find_matches(parsed_data, pattern):
    matches = []
    regex = re.compile(pattern)

    for path, entries in parsed_data.items():
        for value, line_number in entries:
            if regex.search(value):
                matches.append((path, value, line_number))
    return matches

# Function to save results to a file
def save_results_to_file(results, file_path):
    with open(file_path, 'w') as file:
        for path, value, line_number in results:
            file.write(f"Path: {path}, Value: {value}, Line: {line_number}\n")

# Main logic
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Find and export YAML values matching a pattern, including exact duplicates and line numbers.")
    parser.add_argument("input_file", help="Path to the input YAML file")
    parser.add_argument("pattern", help="Pattern to search for in YAML values")
    parser.add_argument("--output_file", help="Path to save the results (optional)")

    # Parse arguments
    args = parser.parse_args()

    # Preprocess YAML content
    try:
        cleaned_yaml, line_mapping = preprocess_yaml(args.input_file)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.")
        exit(1)

    # Parse YAML manually to handle duplicates and track line numbers
    parsed_data = parse_yaml_manually(cleaned_yaml, line_mapping)

    # Find matches
    results = find_matches(parsed_data, args.pattern)

    # Print results
    if results:
        for path, value, line_number in results:
            print(f"Path: {path}, Value: {value}, Line: {line_number}")
        
        # Save to file if output_file is specified
        if args.output_file:
            save_results_to_file(results, args.output_file)
            print(f"Results saved to '{args.output_file}'")
    else:
        print("No matches found.")
