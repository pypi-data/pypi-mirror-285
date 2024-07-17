import os

def print_dir(directory: str):
    """
    Print every folder and file in a directory structure.

    Parameters:
        - directory (str): The directory path to start the search from.
    """
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    # Print the current directory
    print(directory)

    # Iterate over all items in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Check if it's a directory
        if os.path.isdir(item_path):
            # Recursively call the function for subdirectories
            print_dir(item_path)
        else:
            # Print the file
            print(item_path)