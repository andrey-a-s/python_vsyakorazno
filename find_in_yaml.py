# Exmple run scritp
#
# Find $ (dollar). Character escaping - \
# docker run --rm yaml-finder --yaml_string "$(cat multi_level.yml)" ".\$.*"
#
# Find sometext
# docker run --rm yaml-finder --yaml_string "$(cat multi_level.yml)" ".*sometext.*"

import re
import argparse
from collections import defaultdict


# Function to preprocess YAML content
def preprocess_yaml(yaml_content):
    cleaned_lines = []
    line_numbers = {}
    for i, line in enumerate(yaml_content.splitlines(), start=1):
        stripped_line = line.split("#")[0].strip()  # Remove comments
        if stripped_line and stripped_line not in {"---", "..."}:
            cleaned_lines.append((stripped_line, i))
            line_numbers[stripped_line] = i
    return cleaned_lines, line_numbers


# Function to parse YAML manually
def parse_yaml_manually(cleaned_lines):
    current_path = []
    data = defaultdict(list)

    for line, line_number in cleaned_lines:
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

    for path, values in parsed_data.items():
        for value, line_number in values:
            if regex.search(value):
                matches.append((path, value, line_number))
    return matches


# Function to save results to a file
def save_results_to_file(results, file_path):
    with open(file_path, 'w') as file:
        for path, value, line_number in results:
            file.write(f"Line: {line_number}, Path: {path}, Value: {value}\n")


# Main logic
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and export YAML values matching a pattern, including duplicates and line numbers.")
    parser.add_argument("--yaml_string", help="YAML content as a string", required=True)
    parser.add_argument("pattern", help="Pattern to search for in YAML values")
    parser.add_argument("--output_file", help="Path to save the results (optional)")

    # Parse arguments
    args = parser.parse_args()

    # Preprocess YAML content
    yaml_content = args.yaml_string
    cleaned_yaml, line_numbers = preprocess_yaml(yaml_content)

    # Parse YAML manually to handle duplicates
    parsed_data = parse_yaml_manually(cleaned_yaml)

    # Find matches
    results = find_matches(parsed_data, args.pattern)

    # Print results
    if results:
        for path, value, line_number in results:
            print(f"Line: {line_number}, Path: {path}, Value: {value}")
        
        # Save to file if output_file is specified
        if args.output_file:
            save_results_to_file(results, args.output_file)
            print(f"Results saved to '{args.output_file}'")
    else:
        print("No matches found.")
