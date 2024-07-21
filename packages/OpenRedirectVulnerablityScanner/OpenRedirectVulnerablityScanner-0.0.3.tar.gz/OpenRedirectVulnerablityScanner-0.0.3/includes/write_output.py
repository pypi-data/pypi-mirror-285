def write(output, data):
    try:
        with open(output, 'a') as file:
            file.write(data + '\n')
    except FileNotFoundError:
        print(f"Error: The file '{output}' was not found.")
    except IsADirectoryError:
        print(f"Error: The path '{output}' is a directory, not a file.")
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
