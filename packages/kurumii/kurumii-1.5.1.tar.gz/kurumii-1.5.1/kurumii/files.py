import os
import shutil

def validateFile(filepath):
    """
    Check if a file exists.

    Args:
    - filepath (str): The path to the file to check.

    Returns:
    - True if the file exists, False otherwise.
    """
    return os.path.exists(filepath)

def readFile(filepath):
    """
    Read data from a file.

    Args:
    - filepath (str): The path of the file to read.

    Returns:
    - data: The data read from the file, or None if the file does not exist.
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return file.read()
    else:
        print(f"Warning: File '{filepath}' does not exist.")
        return None

def createFile(filename: str, path: str, data, allow_overwrite=False):
    """
    Write data to a file.

    Args:
    - filename (str): The name of the file to write.
    - path (str): The directory path where the file will be located.
    - data: The data to write to the file.
    - allow_overwrite (bool): Whether to allow overwriting an existing file (default False).

    Returns:
    - True if the file was successfully written, False otherwise.
    """
    filepath = os.path.join(path, filename)

    if os.path.exists(filepath) and not allow_overwrite:
        return False
    
    try:
        with open(filepath, 'w') as file:
            file.write(data)
        return True
    except Exception as e:
        print(f"Error writing data to file '{filepath}': {e}")
        return False
    
def addFile(filepath: str, data: str):
    """
    Add data to an existing file without overwriting.

    Args:
    - filepath (str): The path of the file to add data to.
    - data (str): The data to append to the file.

    Returns:
    - True if the data was successfully added, False otherwise.
    """
    try:
        with open(filepath, 'a') as file:  # Open the file in append mode ('a')
            file.write(data)  # Append data to the file
        return True
    except Exception as e:
        print(f"Error adding data to file '{filepath}': {e}")
        return False
def sortFile(filepath: str):
    """
    Sort the contents of a text file alphabetically.

    Args:
    - filepath (str): The path of the text file to be sorted.

    Returns:
    - True if the file was successfully sorted, False otherwise.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            lines.sort()  # Sort the lines alphabetically
        with open(filepath, 'w') as file:
            file.writelines(lines)  # Write the sorted lines back to the file
        return True
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return False
    except Exception as e:
        print(f"Error sorting file '{filepath}': {e}")
        return False

def overwriteFile(filepath: str, data: str):
    """
    Overwrite an existing text file with new data.

    Args:
    - filepath (str): The path of the file to overwrite.
    - data (str): The data to write to the file.

    Returns:
    - True if the file was successfully overwritten, False otherwise.
    """
    try:
        with open(filepath, 'w') as file:
            file.write(data)  # Overwrite the file with new data
        return True
    except Exception as e:
        print(f"Error overwriting file '{filepath}': {e}")
        return False

def editFile(filepath: str, search_value: str, new_value: str):
    """
    Edit existing data in a text file.

    Args:
    - filepath (str): The path of the file to edit.
    - search_value (str): The value to search for in the file.
    - new_value (str): The new value to replace the search value with.

    Returns:
    - True if the data was successfully edited, False otherwise.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()

        found_value = False
        for i, line in enumerate(lines):
            if search_value in line:
                lines[i] = line.replace(search_value, new_value)
                found_value = True

        if not found_value:
            print(f"Error: Value '{search_value}' not found in the file '{filepath}'.")
            return False

        with open(filepath, 'w') as file:
            file.writelines(lines)
        return True
    except Exception as e:
        print(f"Error editing data in file '{filepath}': {e}")
        return False

def loadDataFromFile(filepath: str, search_value: str):
    """
    Load specific data from a text file based on the provided search value.

    Args:
    - filepath (str): The path of the file to load data from.
    - search_value (str): The value to search for in the file.

    Returns:
    - The data corresponding to the specified search value if found, None otherwise.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()

        found_data = None
        for line in lines:
            if search_value in line:
                found_data = line.strip()  # Strip any leading or trailing whitespace
                break

        if found_data is None:
            print(f"Error: Value '{search_value}' not found in the file '{filepath}'.")
        return found_data
    except Exception as e:
        print(f"Error loading data from file '{filepath}': {e}")
        return None

def deleteDataFromFile(filepath: str, search_value: str):
    """
    Delete specific data from a text file based on the provided search value.

    Args:
    - filepath (str): The path of the file to delete data from.
    - search_value (str): The value to search for in the file to identify the item to delete.

    Returns:
    - True if the data was successfully deleted, False otherwise.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()

        found_value = False
        new_lines = []
        for line in lines:
            if search_value not in line:
                new_lines.append(line)
            else:
                found_value = True

        if not found_value:
            print(f"Error: Value '{search_value}' not found in the file '{filepath}'.")
            return False

        with open(filepath, 'w') as file:
            file.writelines(new_lines)
        return True
    except Exception as e:
        print(f"Error deleting data from file '{filepath}': {e}")
        return False


def deleteFile(filepath, confirm=True):
    """
    Delete a file.

    Args:
    - filepath (str): The file path of the file to delete.
    - confirm (bool): Whether to confirm the deletion (default is True).

    Returns:
    - True if the file was successfully deleted, False otherwise.
    """
    if confirm:
        user_input = input(f"Are you sure you want to delete the file '{filepath}'? (y/n): ")
        if user_input.lower() != 'y':
            print("Deletion canceled.")
            return False
    
    try:
        os.remove(filepath)
        print(f"File '{filepath}' deleted successfully.")
        return True
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return False
    except Exception as e:
        print(f"Error deleting file '{filepath}': {e}")
        return False

def backupFile(filepath, backup_filename=None):
    """
    Create a backup of a file.

    Args:
    - filepath (str): The file path of the file to create a backup of.
    - backup_filename (str, optional): The name of the backup file. If not provided, a default name will be used.

    Returns:
    - True if the backup was successfully created, False otherwise.
    """
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        return False
    
    if backup_filename is None:
        backup_filename = os.path.splitext(os.path.basename(filepath))[0] + "_backup" + os.path.splitext(filepath)[1]
    
    backup_filepath = os.path.join(os.path.dirname(filepath), backup_filename)
    
    try:
        shutil.copy(filepath, backup_filepath)
        print(f"Backup created: '{backup_filepath}'")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
def renameFile(old_filepath, new_filename):
    """
    Rename a file.

    Args:
    - old_filepath (str): The current file path of the file.
    - new_filename (str): The new filename for the file.

    Returns:
    - True if the file was successfully renamed, False otherwise.
    """
    try:
        # Get the directory of the old file path
        directory = os.path.dirname(old_filepath)
        
        # Construct the new file path using the directory and new filename
        new_filepath = os.path.join(directory, new_filename)
        
        # Rename the file
        os.rename(old_filepath, new_filepath)
        
        print(f"File '{old_filepath}' renamed to '{new_filepath}'")
        return True
    except FileNotFoundError:
        print(f"Error: File '{old_filepath}' not found.")
        return False
    except Exception as e:
        print(f"Error renaming file '{old_filepath}': {e}")
        return False
