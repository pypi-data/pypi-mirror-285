# import pkg_resources
# import xmlrpc.client
# import socket
# import os


# Function to check internet connection
# def is_connected():
#     try:
#         # Connect to PyPI server to check internet connection
#         socket.create_connection(("pypi.org", 443), timeout=1)
#         return True
#     except OSError:
#         pass
#     return False



# Check for internet connection

# Import your functions here        
from .ascii import print_ascii, ascii_art, ascii_art_colored, print_ascii_colored
from .print_additions import (
    nice_print, print_warning, print_colored, print_debug, print_header,
    print_bold, print_danger, print_green, print_info, print_italic,
    print_red, print_strikethrough, print_success, print_system, print_underline
)
from .id import generateId, generateTextId, splitStringAt50Percent
from .jsonify import (
    addJson, backupJson, createJson, deleteJson, deleteJsonData,
    editJson, loadJsonData, overwriteJson, sortJsonFile,
    validateJson, renameJson,readJson
)
from .additional_functions import (
    camel_to_snake, deep_copy, factorial, flatten_list, is_prime,
    is_valid_date, is_valid_email, log_error, log_info, log_warning,
    merge_dicts, read_csv, remove_whitespace, retry_func, reverse_list,
    timer, write_to_file, unique_elements, truncate_string
)
from .files import (
    addFile,backupFile,createFile,deleteDataFromFile,deleteFile,editFile,
    loadDataFromFile,overwriteFile,readFile,renameFile,sortFile,validateFile
)
from .profanities import(has_profanity)
from .youtube import downloadYoutube
from .data_manipulation import (print_dir)

from .database import(add_data_to_table,check_if_database_exists,check_if_key_exists,
convert_to_db_format,create_sqlite_database,create_table,delete_database,unconvert,
table_exists,edit_data_in_table,edit_table,get_primary_columns,load_all_data,load_data_from_key,
purge_database,purge_table,remove_data_from_table,purge_database_data,remove_table,backup_database,check_if_table_exists)

from .api_request import request_api

from .colors import (get_all_colors,get_color_hex,verify_hex_color,hex_to_int)
# if is_connected():
#     def get_latest_version(package_name):
#         """Get the latest version of a package from PyPI."""
#         try:
#             client = xmlrpc.client.ServerProxy('https://pypi.org/pypi')
#             releases = client.package_releases(package_name)
#             if releases:
#                 return releases[0]  # Return the latest version
#             else:
#                 print("Package not found on PyPI.")
#                 return None
#         except Exception as e:
#             print(f"Failed to fetch latest version: {e}")
#             return None

#     # Check for updates when the package is imported
#     latest_version = get_latest_version("kurumii")
#     if latest_version:
#         installed_version = pkg_resources.get_distribution(__name__).version
#         if installed_version and latest_version > installed_version:
#             print_additions.print_info("A newer version is available. Please consider upgrading: `pip install --upgrade kurumii`")
#         else:
#             pass

#     try:
#         __version__ = pkg_resources.get_distribution(__name__).version
#     except pkg_resources.DistributionNotFound:
#         # Package is not installed
#         __version__ = None

#     def check_for_updates():
#         # Code to check for updates goes here
#         installed_version = __version__
#         # Assume get_latest_version() fetches the latest version from PyPI
#         latest_version = get_latest_version("kurumii")  # You need to implement this function
#         if latest_version and latest_version > installed_version:
#             print_additions.print_info("A newer version is available. Please consider upgrading.")

# else:
#     print_additions.print_red("No internet connection or too slow connection. Skipping version check.")
