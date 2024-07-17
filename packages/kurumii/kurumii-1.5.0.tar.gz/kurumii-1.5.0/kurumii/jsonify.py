import json
import os
import shutil

def validateJson(filepath):
    """
    Check if a file exists and is a valid JSON file.

    Args:
    - filepath (str): The path to the file to check.

    Returns:
    - True if the file exists and is a valid JSON file, False otherwise.
    """
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'r') as file:
            json.load(file)
        return True
    except (json.JSONDecodeError, IOError):
        return False



def readJson(filepath):
    """
    Read JSON data from a file.

    Args:
    - filepath (str): The path of the file to read.

    Returns:
    - data: The JSON data read from the file, or an empty dictionary if the file does not exist or is empty.
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            try:
                data = json.load(file)
                return data
            except json.JSONDecodeError:
                print("Error: Failed to decode JSON data from the file.")
                return {}
    else:
        print(f"Warning: File '{filepath}' does not exist. Returning empty dictionary.")
        return {}
    

def createJson(path, filename, data=None, allow_overwrite=False):
    """
    Write JSON data to a file.

    Args:
    - path (str): The directory path where the file will be located.
    - filename (str): The name of the file to write.
    - data: The JSON-compatible data to write to the file.
    - allow_overwrite (bool): Whether to allow overwriting an existing file (default False).

    Returns:
    - True if the file was successfully created, False otherwise.
    """
    filepath = os.path.join(path, filename)
    if os.path.exists(filepath) and not allow_overwrite:
        return False
    
    try:
        with open(filepath, 'w') as file:
            json.dump(data, file)
        return True
    except Exception as e:
        print(f"Error writing JSON data to file '{filename}' at path '{path}': {e}")
        return False
    



def addJson(filepath, data):
    """
    Add data to an existing JSON file without overwriting.

    Args:
    - filepath (str): The file path where the file is located.
    - data: The JSON-compatible data to add to the file.

    Returns:
    - True if the data was successfully added, False otherwise.
    """
    if not validateJson(filepath):
        print(f"Error: File '{filepath}' is not a valid JSON file or does not exist.")
        return False
    
    try:
        with open(filepath, 'r') as file:
            existing_data = json.load(file)
        
        if not isinstance(existing_data, list):
            existing_data = [existing_data]  # Convert to list if it's not already
        
        existing_data.append(data)
        
        with open(filepath, 'w') as file:
            json.dump(existing_data, file)
        return True
    except Exception as e:
        print(f"Error adding data to JSON file '{filepath}': {e}")
        return False





def sortJsonFile(filepath, default_key=None):
    """
    Sort a JSON file.

    Args:
    - filepath (str): The path of the JSON file to be sorted.
    - default_key (str, optional): The key to use for sorting. If not provided, the function will attempt 
                                   to use the first key found in the first JSON object. Default is None.
    
    Returns:
    - None
    """
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            if default_key is None and data:
                default_key = list(data[0].keys())[0]  # Use the first key found in the first dictionary
            sorted_data = sorted(data, key=lambda x: x.get(default_key, ''))
        with open(filepath, 'w') as file:
            json.dump(sorted_data, file, indent=4)  # Add indentation for readability
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"Error sorting JSON file '{filepath}': {e}")


def overwriteJson(filepath, data):
    """
    Overwrite an existing JSON file with new data.

    Args:
    - filepath (str): The full path to the file to overwrite.
    - data: The JSON-compatible data to write to the file.

    Returns:
    - True if the file was successfully overwritten, False otherwise.
    """
    try:
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)  # Overwrite the file with new data
        return True
    except Exception as e:
        print(f"Error overwriting JSON file '{filepath}': {e}")
        return False
    
def editJson(filepath, search_key, search_value, new_value):
    """
    Edit existing JSON data in a file.

    Args:
    - filepath (str): The file path where the file is located.
    - search_key: The key to search for in the JSON data.
    - search_value: The value corresponding to the search_key to identify the item to edit.
    - new_values (dict): A dictionary containing the new key-value pairs to update.

    Returns:
    - True if the data was successfully edited, False otherwise.
    """
    if not validateJson(filepath):
        print(f"Error: File '{filepath}' is not a valid JSON file or does not exist.")
        return False
    
    try:
        with open(filepath, 'r') as file:
            existing_data = json.load(file)
        
        found_key = False
        for item in existing_data:
            if search_key in item and item[search_key] == search_value:
                for key, value in new_value.items():
                    item[key] = value
                found_key = True
                print("Key found")
                break
        
        if not found_key:
            print(f"Error: Key '{search_key}' with value '{search_value}' not found in the JSON data.")
            return False
        
        with open(filepath, 'w') as file:
            json.dump(existing_data, file, indent=4)  # Add indentation for readability
        return True
    except Exception as e:
        print(f"Error editing data in JSON file '{filepath}': {e}")
        return False


def loadJsonData(filepath, search_key, search_value):
    """
    Load specific data from a JSON file based on the provided search key and value.

    Args:
    - filepath (str): The file path where the JSON file is located.
    - search_key: The key to search for in the JSON data.
    - search_value: The value corresponding to the search_key to identify the item to load.

    Returns:
    - The data corresponding to the specified search key and value if found, None otherwise.
    """
    if not validateJson(filepath):
        print(f"Error: File '{filepath}' is not a valid JSON file or does not exist.")
        return None
    
    try:
        with open(filepath, 'r') as file:
            existing_data = json.load(file)
        
        for item in existing_data:
            if search_key in item and item[search_key] == search_value:
                return item
        
        print(f"Error: Key '{search_key}' with value '{search_value}' not found in the JSON data.")
        return None
    except Exception as e:
        print(f"Error loading data from JSON file '{filepath}': {e}")
        return None


def deleteJsonData(filepath, search_key, search_value):
    """
    Delete specific data from a JSON file based on the provided search key and value.

    Args:
    - filepath (str): The file path where the JSON file is located.
    - search_key: The key to search for in the JSON data.
    - search_value: The value corresponding to the search_key to identify the item to delete.

    Returns:
    - True if the data was successfully deleted, False otherwise.
    """
    if not validateJson(filepath):
        print(f"Error: File '{filepath}' is not a valid JSON file or does not exist.")
        return False
    
    try:
        with open(filepath, 'r') as file:
            existing_data = json.load(file)
        
        found_item = None
        for item in existing_data:
            if search_key in item and item[search_key] == search_value:
                found_item = item
                break
        
        if found_item:
            existing_data.remove(found_item)
            with open(filepath, 'w') as file:
                json.dump(existing_data, file, indent=4)  # Rewrite the JSON file
            return True
        else:
            print(f"Error: Key '{search_key}' with value '{search_value}' not found in the JSON data.")
            return False
    except Exception as e:
        print(f"Error deleting data from JSON file '{filepath}': {e}")
        return False

def deleteJson(filepath, confirm=True):
    """
    Delete a JSON file.

    Args:
    - filepath (str): The file path of the JSON file to delete.
    - confirm (bool): Whether to confirm the deletion (default is True).

    Returns:
    - True if the file was successfully deleted, False otherwise.
    """
    if confirm:
        user_input = input(f"Are you sure you want to delete the JSON file '{filepath}'? (y/n): ")
        if user_input.lower() != 'y':
            print("Deletion canceled.")
            return False
    
    try:
        os.remove(filepath)
        print(f"JSON file '{filepath}' deleted successfully.")
        return True
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return False
    except Exception as e:
        print(f"Error deleting JSON file '{filepath}': {e}")
        return False

def backupJson(filepath, backup_filename=None):
    """
    Create a backup of a JSON file.

    Args:
    - filepath (str): The file path of the JSON file to create a backup of.
    - backup_filename (str, optional): The name of the backup file. If not provided, a default name will be used.

    Returns:
    - True if the backup was successfully created, False otherwise.
    """
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        return False
    
    if backup_filename is None:
        backup_filename = os.path.splitext(os.path.basename(filepath))[0] + "_backup.json"
    
    backup_filepath = os.path.join(os.path.dirname(filepath), backup_filename)
    
    try:
        shutil.copy(filepath, backup_filepath)
        print(f"Backup created: '{backup_filepath}'")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
def renameJson(old_filepath, new_filename):
    """
    Rename a JSON file.

    Args:
    - old_filepath (str): The current file path of the JSON file.
    - new_filename (str): The new filename for the JSON file.

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
        
        print(f"JSON file '{old_filepath}' renamed to '{new_filepath}'")
        return True
    except FileNotFoundError:
        print(f"Error: File '{old_filepath}' not found.")
        return False
    except Exception as e:
        print(f"Error renaming JSON file '{old_filepath}': {e}")
        return False


"""
To DOS
Merge JSON Files: A function to merge the contents of multiple JSON files into one.

Deep Copy JSON Data: A function to create a deep copy of the JSON data, useful for preserving the original data before modifications.

Filter JSON Data: A function to filter the JSON data based on specific criteria, returning only the items that match the filter.

Convert JSON to CSV: A function to convert JSON data into CSV format for compatibility with spreadsheet software.

Convert CSV to JSON: A function to convert CSV data into JSON format.
"""