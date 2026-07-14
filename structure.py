import json
import os
import sys
from tkinter import Tk, filedialog

# Increase the recursion limit for deeply nested or complex JSON objects
sys.setrecursionlimit(10000)


def extract_schema(data):
    """Recursively extracts the hierarchical structure of JSON, replacing values with type names."""
    if isinstance(data, dict):
        return {key: extract_schema(value) for key, value in data.items()}
    elif isinstance(data, list):
        if not data:
            return []
        # Return structure of the first element to avoid repetitive deep processing
        return [extract_schema(data[0])]
    else:
        return type(data).__name__


def generate_text_tree_iterative(data):
    """Generates a scannable text tree structure iteratively using a stack to prevent recursion depth crashes."""
    if not isinstance(data, (dict, list)):
        return []

    lines = []
    # Stack stores tuples of (current_node, current_indentation_level)
    # We process in reverse to maintain top-to-bottom layout order
    stack = [(data, 0)]

    while stack:
        curr, indent = stack.pop()

        if isinstance(curr, dict):
            # Reverse items so they are popped and printed in correct forward order
            for key, value in reversed(curr.items()):
                if isinstance(value, (dict, list)):
                    stack.append((value, indent + 1))
                lines.append("  " * indent + f"├── {key}")

        elif isinstance(curr, list):
            if curr:
                stack.append((curr[0], indent + 1))
            lines.append("  " * indent + "└── [Array Items]")

    # Because we built it dynamically via stack, we reverse the print lines to layout correctly
    return lines[::-1]


if __name__ == "__main__":
    # Define folder configurations
    INPUT_FOLDER = "JSON files"
    OUTPUT_FOLDER = "structure results"

    # Ensure folders exist
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Initialize Tkinter and hide the main blank window
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)  # Bring window to front

    print("Opening file selection window...")
    input_file_path = filedialog.askopenfilename(
        initialdir=INPUT_FOLDER,
        title="Select a JSON file to explore",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )

    if not input_file_path:
        print("Operation cancelled. No file was selected.")
        sys.exit(0)

    filename = os.path.basename(input_file_path)
    base_name, _ = os.path.splitext(filename)

    try:
        print(f"Loading {filename} into memory...")
        with open(input_file_path, 'r', encoding='utf-8') as f:
            source_json = json.load(f)

        print("Extracting structural data hierarchy...")
        # 1. Generate structural data structure
        schema_structure = extract_schema(source_json)

        print("Generating layout map tree...")
        # 2. Generate text tree via safety loop
        text_tree_lines = generate_text_tree_iterative(schema_structure)

        # Construct destinations inside structure results folder
        json_out_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_structure.json")
        txt_out_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_structure.txt")

        # Save outputs
        with open(json_out_path, 'w', encoding='utf-8') as fj:
            json.dump(schema_structure, fj, indent=2)

        with open(txt_out_path, 'w', encoding='utf-8') as ft:
            ft.write(f"Structure Map for {filename}\n")
            ft.write("=" * 40 + "\n")
            ft.write("\n".join(text_tree_lines))

        print(f"\nSuccess! Extracted structure from: {filename}")
        print(f" -> Saved: {json_out_path}")
        print(f" -> Saved: {txt_out_path}")

    except Exception as e:
        print(f"\nError processing file: {e}")
