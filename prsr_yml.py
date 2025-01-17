# Exmple run scritp on Windows
#
# Find $ (dollar). Character escaping - \
# py .\main_yml.py multi_level.yml ".\$.*"
#
# Find sometext
# py .\main_yml.py multi_level.yml ".*sometext.*"
import re
import argparse
from collections import defaultdict

# Function to preprocess YAML content
def preprocess_yaml(file_path):
    cleaned_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            # Remove comments and separators
            stripped_line = line.split("#")[0].strip()  # Remove comments
            if stripped_line and stripped_line not in {"---", "..."}:
                cleaned_lines.append(stripped_line)
    return cleaned_lines

# Function to parse YAML content manually
def parse_yaml_manually(cleaned_lines):
    current_path = []
    data = defaultdict(list)

    for line in cleaned_lines:
        indent_level = len(line) - len(line.lstrip())
        key_value = line.strip().split(":", 1)

        # Handle key-value pairs
        if len(key_value) == 2:
            key, value = key_value[0].strip(), key_value[1].strip()
            value = value.strip('"').strip("'")  # Remove quotes if present

            # Adjust the current path based on indentation
            while len(current_path) > indent_level // 2:
                current_path.pop()
            current_path.append(key)

            # Record the full path and value
            full_path = ".".join(current_path)
            data[full_path].append(value)

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

    for path, values in parsed_data.items():
        for value in values:
            if regex.search(value):
                matches.append((path, value))
    return matches

# Function to save results to a file
def save_results_to_file(results, file_path):
    with open(file_path, 'w') as file:
        for path, value in results:
            file.write(f"Path: {path}, Value: {value}\n")

# Main logic
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Find and export YAML values matching a pattern, including exact duplicates.")
    parser.add_argument("input_file", help="Path to the input YAML file")
    parser.add_argument("pattern", help="Pattern to search for in YAML values")
    parser.add_argument("--output_file", help="Path to save the results (optional)")

    # Parse arguments
    args = parser.parse_args()

    # Preprocess YAML content
    try:
        cleaned_yaml = preprocess_yaml(args.input_file)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.")
        exit(1)

    # Parse YAML manually to handle duplicates
    parsed_data = parse_yaml_manually(cleaned_yaml)

    # Find matches
    results = find_matches(parsed_data, args.pattern)

    # Print results
    if results:
        for path, value in results:
            print(f"Path: {path}, Value: {value}")
        
        # Save to file if output_file is specified
        if args.output_file:
            save_results_to_file(results, args.output_file)
            print(f"Results saved to '{args.output_file}'")
    else:
        print("No matches found.")
