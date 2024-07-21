def read(input_file):
    try:
        with open(input_file, 'r') as file:
            content = file.read().splitlines()
            return content
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return None
