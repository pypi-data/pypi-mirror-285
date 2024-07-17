import re
import datetime
import copy
import csv
import math
import logging
import time


def remove_whitespace(text:str):
    """
    Removes every whitespace from a string.

    Args:
        - text (str): The text to convert.

    Returns:
        - string: The converted string.
"""
    text = text.replace(" ","")
    return(text)

def camel_to_snake(text: str):
    """
    Converts camel case to snake case. eg: FromThisCase  to  this_case

    Args:
        - text (str): The text to convert.

    Returns:
        - string: The converted string.
"""
    text_combined = ""
    for index, char in enumerate(text):
        if index == 0:
            text_combined += char.lower()  # Convert the first character to lowercase
        elif char.isupper():
            text_combined += "_" + char.lower()
        else:
            text_combined += char
    return(text_combined)

def truncate_string(text:str,num:int):
    """
    Truncates a string after a certain amount.

    Args:
        - text (str): The text to truncate.

    Returns:
        - string: The truncated string.
"""
    combined_text = ""
    for index, char in enumerate(text):
        if index > num-1:
            char = char.replace(f"{char}","...")
            combined_text = combined_text + char
            break
        combined_text = combined_text + char
    return(combined_text)


def is_valid_email(email):
    """
    Checks if a given string is a valid email address.

    Args:
        - email (str): The email address to validate.

    Returns:
        - bool: True if the email address is valid, False otherwise.
    """
    # Regular expression pattern for validating email addresses
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_date(date_string, date_format):
    """
    Validates a date string against a specified format.

    Args:
        - date_string (str): The date string to validate.
        - date_format (str): The expected format of the date string.

    Returns:
        - bool: True if the date string is valid, False otherwise.
    """
    try:
        datetime.datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def flatten_list(nested_list):
    """
    Flattens a nested list into a single list.

    Args:
        - nested_list (list): The nested list to flatten.

    Returns:
        - list: The flattened list.
    """
    return [item for sublist in nested_list for item in sublist]

def merge_dicts(*dicts):
    """
    Merges multiple dictionaries into one.

    Args:
        - *dicts: Variable number of dictionaries to merge.

    Returns:
        - dict: The merged dictionary.
    """
    merged_dict = {}
    for d in dicts:
        for key, value in d.items():
            if key in merged_dict:
                raise ValueError(f"Duplicate key found: {key}")
            merged_dict[key] = value
    return merged_dict



def deep_copy(data_structure):
    """
    Creates a deep copy of a nested data structure.

    Args:
        - data_structure: The nested data structure to copy.

    Returns:
        - object: The deep copy of the nested data structure.
    """
    return copy.deepcopy(data_structure)


def read_csv(file_path):
    """
    Reads data from a CSV file into a list of dictionaries.

    Args:
        - file_path (str): The path to the CSV file.

    Returns:
        - list: A list of dictionaries representing the CSV data.
        - False: If the function failed.
    """
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]
    except Exception as e:
        print(e)
        return(False)

def write_to_file(data, file_path):
    """
    Writes data to a file.

    Args:
        - data: The data to write to the file.
        - file_path (str): The path to the file.

    Returns:
        - bool: If the the function succeeded or not.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(data)
            return(True)
    except Exception as e:
        print(e)
        return(False)
    
def factorial(n):
    """
    Calculates the factorial of a number.

    Args:
        - n (int): The number.

    Returns:
        - int: The factorial of the number.
    """
    return math.factorial(n)

def is_prime(n):
    """
    Checks if a number is prime.

    Args:
        - n (int): The number.

    Returns:
        - bool: True if the number is prime, False otherwise.
    """
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def timer(func, confirm:bool=True):
    """
    Measures the execution time of a given function.

    Args:
        - func: The function to measure execution time for.
        - confirm (bool): Whether to confirm the execution of the function (default is True).


    Returns:
        - float: The execution time in seconds.
        - None: If the execution fails.
    """
    # Display a warning message

    
    if confirm == True:
        inp = input("Warning: The provided function will be executed to measure execution time. Continue? (y/n): ")
        if inp.lower() == "y":
            start_time = time.time()
            func()
            end_time = time.time()
            return end_time - start_time
        else:
            print("Execution canceled.")
            return(None)
    else:
        start_time = time.time()
        func()
        end_time = time.time()
        return end_time - start_time


def retry_func(func, attempts=3, confirm:bool=True):
    """
    Retries a function call a specified number of times if it fails.

    Args:
        - func: The function to retry.
        - attempts (int): The maximum number of attempts (default is 3).
        - confirm (bool): Whether to confirm the execution of the function (default is True).

    Returns:
        - True: If the function has been executed successfully.
        - None: If the execution fails.
    """
    if confirm == True:
        inp = input("Warning: The provided function will be executed. Continue? (y/n): ")
        if inp.lower() == "y":
            for _ in range(attempts):
                try:
                    func()
                    return(True)
                except Exception as e:
                    print ("\033[1;33;4m" + f"Attempt failed: {e}" + "\033[0m")
            raise Exception ("\033[91m" + "Maximum number of attempts reached" + "\033[0m")
        else:
            print("Execution canceled.")
            return(None)
    for _ in range(attempts):
                try:
                    func()
                    return(True)
                except Exception as e:
                    print ("\033[1;33;4m" + f"Attempt failed: {e}" + "\033[0m")
    raise Exception ("\033[91m" + "Maximum number of attempts reached" + "\033[0m")

def log_info(message):
    """
    Logs an informational message.

    Args:
        - message (str): The message to log.
    """
    logging.info(message)

def log_warning(message):
    """
    Logs a warning message.

    Args:
        - message (str): The message to log.
    """
    logging.warning(message)

def log_error(message):
    """
    Logs an error message.

    Args:
        - message (str): The message to log.
    """
    logging.error(message)

def reverse_list(lst):
    """
    Reverses the elements of a list.

    Args:
        - lst (list): The input list.

    Returns:
        - list: The reversed list.
    """
    return lst[::-1]

def unique_elements(lst):
    """
    Returns unique elements from a list.

    Args:
        - lst (list): The input list.

    Returns:
        - list: A list containing unique elements.
    """
    return list(set(lst))
def validateHex(hex_color):
    """
    Validates a hexadecimal color code and returns its RGB representation if valid.
    
    Args:
        hex_color (str): The hexadecimal color code to validate.
        
    Returns:
        tuple or None: A tuple containing the RGB representation (as integers between 0 and 255) 
                       if the hex color is valid. Returns None if the hex color is invalid.
    """
    hex_color = hex_color.lstrip('#')
    
    # Check if the length of the string is valid for hex color (either 3 or 6 characters)
    if len(hex_color) != 3 and len(hex_color) != 6:
        return None
    
    # Check if all characters are valid hexadecimal digits
    if not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
        return None
    
    # If the length is 3, expand the shorthand notation to 6 characters
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    
    # Convert hexadecimal to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)