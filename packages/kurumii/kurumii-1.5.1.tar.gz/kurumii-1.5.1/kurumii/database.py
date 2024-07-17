import os
import json
import sqlite3
import shutil
from datetime import datetime


class DatabaseCreationError(Exception):
    pass
class FileExistsError(Exception):
    pass
class FileDeletionError(Exception):
    pass
class PrimaryKeyError(Exception):
    pass
class TableCreationError(Exception):
    pass
class DatabaseConnectionError(Exception):
    pass
class TableDeletionError(Exception):
    pass
class DataAdditionError(Exception):
    pass
class DataRemovalError(Exception):
    pass
class DataRemovalError(Exception):
    pass
class DataPurgeError(Exception):
    pass
class DatabasePurgeError(Exception):
    pass
class DatabaseDataPurgeError(Exception):
    pass
class TableEditError(Exception):
    pass
class KeyExistenceError(Exception):
    pass
class LoadDataError(Exception):
    pass

def convert_to_db_format(value):
    """
    Convert dictionaries and lists to a format suitable for insertion into a database.

    Args:
        - value (dict or list): The value to be converted.

    Returns:
        - str: The converted value as a JSON string.

    """
    if isinstance(value, dict) or isinstance(value, list):
        return json.dumps(value)
    else:
        return value
 
def unconvert(value):
    """
    Convert JSON strings back to Python lists or dictionaries.

    Args:
        - value (str): The JSON string to be converted.

    Returns:
        - dict or list: The converted Python object.

    """
    return json.loads(value)

def get_primary_columns(filepath, table_name = "data"):
    try:
        # Connect to the database
        conn = sqlite3.connect(filepath)
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        table_exists = c.fetchone()
        if not table_exists:
            conn.close()
            return False
        
        # Execute query to get columns information
        c.execute(f"PRAGMA table_info('{table_name}')")
        columns_info = c.fetchall()

        # Get primary key columns
        primary_columns = [col[1] for col in columns_info if col[5] == 1]
        
        conn.close()
        return primary_columns
    except Exception as e:
        print(f"Error getting the primary columns of {filepath}/{table_name}: {e}")
        return None

def create_sqlite_database(filename:str,path:str=".\\db",overwrite=False, logging=False):
    """
    Create an empty SQLite database file.

    Args:
        - path (str, optional): The path where the database file should be created. Defaults to current directory.
        - filename (str): The name of the database file.
        - overwrite (bool, optional): Whether to overwrite the existing file if it already exists. 
                                    Defaults to False.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.
    
    Returns:
        - tuple: 
            - A tuple containing a boolean indicating whether the database file was created successfully
              and the path of the created database file.
    
    Raises:
        - DatabaseCreationError: If an error occurs while creating the database file.
        - FileExistsError: If the file already exists and overwrite is False.
        - FileDeletionError: If an error occurs while deleting the existing file.
    Raises do not work
    
    Example:
        >>> create_sqlite_database(path="path/to/your/folder", filename="example.db", overwrite=True, logging=True)
    """
    # Ensure that the directory exists
    os.makedirs(path, exist_ok=True)

    # Check if the file already exists
    file_path = os.path.join(path, filename)
    if os.path.exists(file_path):
        if not overwrite:
            if logging:
                print("File already exists. Set 'overwrite' to True to overwrite existing file.")
            return False, file_path
        else:
            try:
                os.remove(file_path)
            except Exception as e:
                if logging:
                    print(f"Error occurred while deleting existing file: {e}")
                return False, file_path
    
    # Create a new SQLite database file
    try:
        conn = sqlite3.connect(file_path)
        conn.close()
        if logging:
            print(f"Empty database file '{filename}' created successfully in '{file_path}'.")
        return True, file_path
    except Exception as e:
        if logging:
            print(f"Error occurred while creating database file: {e}")
        return False, file_path




def create_table(columns, filepath, primary_key, table_name="data", overwrite=False, logging=False):
    """
    Add a table to an SQLite database.

    Args:
        - columns (str): A string representing the columns of the table in SQLite syntax.
        - filepath (str): The path to the SQLite database file.
        - primary_key (str): The primary key of the table.
        - table_name (str, optional): The name of the table to be added. Defaults to 'data'
        - overwrite (bool, optional): Whether to overwrite the existing table if it already exists. 
                                    Defaults to False.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.

    Returns:
        - bool: A boolean indicating whether the table was added successfully (True) or not (False).

    Raises:
        - FileExistsError: If the table already exists and overwrite is False.
        - PrimaryKeyError: If the specified primary key is not found in the columns.
        - DatabaseCreationError: If an error occurs while adding the table to the database.

    Example:
        >>>  create_table(columns="id INTEGER, name TEXT, age INTEGER", filepath="path/to/your/database.db", primary_key="id", table_name="users", overwrite=True, logging=True)

    """

    if os.path.exists(filepath):
        try:
            # Connect to the database
            conn = sqlite3.connect(filepath)
            c = conn.cursor()

            # Check if table exists and if overwriting is allowed
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            existing_table = c.fetchone()
            if existing_table and not overwrite:
                if logging:
                    print(f"Table '{table_name}' already exists in the database. Use 'overwrite=True' to replace it.")
                conn.close()
                if logging:
                    print(f"Table '{table_name}' already exists in the database.")
                return(False)
                

            if existing_table and overwrite:
                c.execute(f"DROP TABLE IF EXISTS {table_name}")

            # Check if primary key exists in columns
            if primary_key not in columns:
                if logging:
                    print(f"Primary key '{primary_key}' not found in columns.")
                return(False)

            # Create table
            create_table_query = f"CREATE TABLE {table_name} ({columns}, PRIMARY KEY ({primary_key}))"
            c.execute(create_table_query)

            # Commit changes
            conn.commit()

            # Close connection
            conn.close()

            if logging:
                print(f"Table '{table_name}' created successfully in '{filepath}'.")
            return(True)
        except sqlite3.Error as e:
            if logging:
                print(f"Error creating table '{table_name}': {str(e)}")
            return(False)
    else:
        if logging:
            print(f"The file '{filepath}' does not exist")
        return(False)

def remove_table(filepath, table_name="data", confirm=False, logging=False):
    """
    Remove a table from an SQLite database.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str, optional): The name of the table to be deleted. Defaults to 'data'
        - confirm (bool, optional): Whether to prompt the user for confirmation before deletion. Defaults to False.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.
    
    Returns:
        - bool: A boolean indicating whether the table was deleted successfully (True) or not (False).
    
    Raises:
        - TableDeletionError: If an error occurs while deleting the table from the database.
    Raises do not work
    Example:
        >>> delete_table_from_database(table_name="my_table", filepath="my_database.db", confirm=True, logging=True)
    """
    if os.path.exists(filepath):
        try:
            # Confirm deletion if requested
            if confirm:
                confirmation = input(f"Are you sure you want to delete table '{table_name}' from '{filepath}'? (y/n): ")
                if confirmation.lower() != "y":
                    if logging:
                        print("Deletion canceled.")
                    return False

            # Connect to the database
            conn = sqlite3.connect(filepath)
            c = conn.cursor()

            # Check if table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            existing_table = c.fetchone()
            if not existing_table:
                if logging:
                    print(f"Table '{table_name}' does not exist in the database.")
                conn.close()
                return False

            # Delete the table
            c.execute(f"DROP TABLE {table_name}")

            # Commit changes
            conn.commit()

            # Close connection
            conn.close()

            if logging:
                print(f"Table '{table_name}' deleted successfully from '{filepath}'.")
            return True
        except sqlite3.Error as e:
            if logging:
                print(f"Error deleting table '{table_name}': {str(e)}")
            return False
    else:
        if logging:
            print(f"The file '{filepath}' does not exist")
        return(False)

def add_data_to_table(data, filepath, table_name="data", logging=False):
    """
    Add data to a specified table in an SQLite database without overwriting existing data.

    Args:
        - data (dict or list of dicts): The data to be added to the table. If a single dictionary is provided,
          it represents a single row of data. If a list of dictionaries is provided, each dictionary represents
          a row of data.
        - filepath (str): The path to the SQLite database file.
        - table_name (str, optional): The name of the table to which data will be added. Defaults to "data".
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.
    
    Returns:
        - bool: Whether the operation succeeded (True) or not (False).

    Example:
        >>> add_data_to_table(data=[{"test1":54,"test2":2,"test3":2},{"test1":55,"test2":2,"test3":2}], filepath=".\\db\\test.db", table_name="data2",logging=True)
        
    Raises:
        - AddDataError: If an error occurs while adding data to the table.
    Raises do not work
    """
    try:
        primary_columns = get_primary_columns(filepath=filepath, table_name=table_name)
        primary_column = primary_columns[0]  # Assuming there's only one primary column
        conn = sqlite3.connect(filepath)
        c = conn.cursor()
        
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            if logging:
                print("Data must be provided as a dictionary or a list of dictionaries.")
            return False

        for row in data:
            if isinstance(row, dict):
                # Check if the primary key value already exists
                if primary_column in row:
                    c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {primary_column} = ?", (row[primary_column],))
                    count = c.fetchone()[0]
                    if count > 0:
                        if logging:
                            print(f"Data with {primary_column}={row[primary_column]} already exists, skipping.")
                        continue

                # Convert dictionaries and lists to a format suitable for insertion into the database
                row = {key: convert_to_db_format(value) for key, value in row.items()}

                columns = ', '.join(row.keys())
                placeholders = ', '.join('?' * len(row))
                values = tuple(row.values())
                c.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
                if logging:
                    print("Data added successfully.")
            else:
                if logging:
                    print("Data must be provided as a dictionary or a list of dictionaries.")
                return False

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error while trying to add data to the database ({filepath}): {e}")
    
def table_exists(filepath:str, table_name:str = "data",logging = False):
    """
    Check if a table exists in the SQLite database.

    Args:
        - database_file (str): The path to the SQLite database file.
        - table_name (str): The name of the table to check.
        - logging (bool): Weither to log if a table exists.
    Returns:
        - bool: True if the table exists, False otherwise.

    Example:
        >>> table_exists(filepath=".\\db\\test.db",table_name="data2")
    """
    try:
        conn = sqlite3.connect(filepath)
        c = conn.cursor()
        # Query to check if the table exists in the database schema
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = c.fetchone()[0]
        conn.close()
        if logging == True:
            print(f"{table_name} exists.")
        return result == 1
    except sqlite3.OperationalError:
        # Catch OperationalError when table doesn't exist
        return False

    except Exception as e:
        if logging == True:
            print(f"Error checking table existence: {str(e)}")
        return False

def edit_data_in_table(filepath, data, table_name="data", logging=False):
    """
    Edit data in a specified table in an SQLite database.

    Args:
        - filepath (str): The path to the SQLite database file.
        - data (dict or list of dicts): The data to be edited in the table. If a single dictionary is provided,
          it represents a single row of data. If a list of dictionaries is provided, each dictionary represents
          a row of data. If the key value is not foundd or does not exists, it will be added in a new row.
        - table_name (str, optional): The name of the table to edit. Defaults to "data".
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.

    Returns:
        - bool: Whether the operation succeeded (True) or not (False).

    Example:
        >>> edit_data_in_table(table_name="data2",logging=True,data={"test1":533,"test2":3,"test3":4},filepath=".\\db\\test.db")
    """
    try:
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        # Check if the table exists
        if not table_exists(filepath, table_name):
            if logging:
                print(f"Table '{table_name}' does not exist in the database.")
            conn.close()
            return False

        # Get the primary key column of the table
        primary_column = get_primary_columns(filepath=filepath,table_name=table_name)
        primary_column = primary_column[0]

        if isinstance(data, dict):
            data = [data]  # Convert single dictionary to list of dictionaries

        for row_data in data:
            if primary_column in row_data:
                # Check if a row with the same primary key value exists
                c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {primary_column} = ?", (row_data[primary_column],))
                count = c.fetchone()[0]
                if count > 0:
                    # Update the row with the new data
                    set_clause = ', '.join([f"{column} = ?" for column in row_data.keys() if column != primary_column])
                    values = tuple(row_data[column] for column in row_data.keys() if column != primary_column)
                    c.execute(f"UPDATE {table_name} SET {set_clause} WHERE {primary_column} = ?", (*values, row_data[primary_column]))
                    if logging:
                        print("Data updated successfully.")
                    continue  # Move to the next row

            # Insert a new row with the data
            columns = ', '.join(row_data.keys())
            placeholders = ', '.join('?' * len(row_data))
            values = tuple(row_data.values())
            c.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            if logging:
                print("New data added successfully.")

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if logging:
            print(f"Error editing data in the table: {str(e)}")
        return False

def remove_data_from_table(filepath, key_values, table_name = "data",  logging=False):
    """
    Remove data from a specified table in an SQLite database based on specific key-value pairs.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str): The name of the table to remove data from.
        - key_values (int, str, list): The value(s) used to identify the row(s) to be removed.
          If a single value is provided, it represents a single key value. If a list of values
          is provided, each value represents a key value.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.

    Returns:
        - bool: Whether the operation succeeded (True) or not (False).

    """
    try:
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        # Get the primary column dynamically
        primary_column = get_primary_columns(filepath=filepath, table_name=table_name)
        if not primary_column:
            if logging:
                print("Error: Primary column not found for the table.")
            return False

        primary_column = primary_column[0]

        # Ensure key_values is a list
        if not isinstance(key_values, list):
            key_values = [key_values]

        for value in key_values:
            # Constructing WHERE clause to identify the row(s) based on the key value(s)
            where_clause = f"{primary_column} = ?"
            where_values = (value,)

            # Executing DELETE query
            c.execute(f"DELETE FROM {table_name} WHERE {where_clause}", where_values)

            # Check if any row(s) were deleted
            if c.rowcount > 0:
                if logging:
                    print(f"{c.rowcount} row(s) deleted successfully for {primary_column}: {value}")
            else:
                if logging:
                    print(f"No matching rows found for deletion for {primary_column}: {value}")

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if logging:
            print(f"Error removing data from the table: {str(e)}")
        return False

def purge_table(filepath, table_name = "data", confirm=False, logging=False):
    """
    Purge (clear) all data from a specified table in an SQLite database.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str): The name of the table to purge.
        - confirm (bool, optional): Whether to prompt for manual confirmation before purging. Defaults to False.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.

    Returns:
        - bool: Whether the operation succeeded (True) or not (False).

    Example:
        >>> purge_table(confirm=True,filepath=".\\db\\test.db",logging=True,table_name="data2")
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        # Prompt for manual confirmation if confirm is True
        if confirm:
            user_input = input(f"Are you sure you want to purge all data from the table '{table_name}'? (y/n): ").strip().lower()
            if user_input != 'y':
                print("Operation aborted.")
                return False

        # Execute DELETE query to remove all data from the table
        c.execute(f"DELETE FROM {table_name}")

        # Commit the transaction
        conn.commit()

        if logging:
            print(f"All data purged successfully from the table '{table_name}'.")

        return True
    except Exception as e:
        if logging:
            print(f"Error purging data from the table: {str(e)}")
        return False
    finally:
        # Close the connection
        conn.close()

def purge_database(filepath, confirm=False, logging=False):
    """
    Purge (remove) all tables from an SQLite database file.

    Args:
        - filepath (str): The path to the SQLite database file.
        - confirm (bool, optional): Whether to prompt for manual confirmation before purging. Defaults to False.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.

    Returns:
        - bool: Whether the operation succeeded (True) or not (False).

    Example:
        >>> purge_database(confirm=False,filepath=".\\db\\test.db",logging=True)
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        # Fetch a list of all tables in the database
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()

        # Prompt for manual confirmation if confirm is True
        if confirm:
            user_input = input("Are you sure you want to purge the entire database? This action will remove all tables. (y/n): ").strip().lower()
            if user_input != 'y':
                print("Operation aborted.")
                return False

        # Remove each table from the database
        for table in tables:
            table_name = table[0]
            c.execute(f"DROP TABLE IF EXISTS {table_name}")

            if logging:
                print(f"Table '{table_name}' purged successfully.")

        # Commit the transaction
        conn.commit()

        if logging:
            print("All tables purged successfully from the database.")

        return True
    except Exception as e:
        if logging:
            print(f"Error purging database: {str(e)}")
        return False
    finally:
        # Close the connection
        conn.close()

def purge_database_data(filepath, confirm=False, logging=False):
    """
    Purge (remove) all data from tables in an SQLite database file.

    Args:
        - filepath (str): The path to the SQLite database file.
        - confirm (bool, optional): Whether to prompt for manual confirmation before purging. Defaults to False.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.

    Returns:
        - bool: Whether the operation succeeded (True) or not (False).

    Example:
        >>> purge_database_data(confirm=True,filepath=".\\db\\test.db",logging=True)
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        # Fetch a list of all tables in the database
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()

        # Prompt for manual confirmation if confirm is True
        if confirm:
            user_input = input("Are you sure you want to purge all data from all tables in the database? This action cannot be undone. (y/n): ").strip().lower()
            if user_input != 'y':
                print("Operation aborted.")
                return False

        # Remove data from each table
        for table in tables:
            table_name = table[0]
            c.execute(f"DELETE FROM {table_name}")

            if logging:
                print(f"Data purged successfully from table '{table_name}'.")

        # Commit the transaction
        conn.commit()

        if logging:
            print("All data purged successfully from the database.")

        return True
    except Exception as e:
        if logging:
            print(f"Error purging database data: {str(e)}")
        return False
    finally:
        # Close the connection
        conn.close()

def edit_table(filepath, new_structure, primary_key_column, table_name = "data",logging=False):
    """
    Edit the structure of a table in an SQLite database.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str): The name of the table to edit.
        - new_structure (str): The new structure of the table in the format "column1 DATATYPE, column2 DATATYPE, ..."
        - primary_key_column (str): The name of the primary key column.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.

    Returns:
        - bool: Whether the operation succeeded (True) or not (False).
    
    Example:
        >>> edit_table(filepath=".\\db\\test.db",logging=True,new_structure="test1 INTEGER, test2 TEXT, test3 INTEGER",primary_key_column="test1",table_name="data")
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        # Construct the SQL query to edit the table structure
        query = f"BEGIN TRANSACTION; \
                  ALTER TABLE {table_name} RENAME TO temp_{table_name}; \
                  CREATE TABLE {table_name} ({new_structure}, PRIMARY KEY ({primary_key_column})); \
                  INSERT INTO {table_name} SELECT * FROM temp_{table_name}; \
                  DROP TABLE temp_{table_name}; \
                  COMMIT;"

        # Execute the SQL query to edit the table
        c.executescript(query)

        # Commit the transaction
        conn.commit()

        if logging:
            print("Table structure edited successfully.")

        return True
    except Exception as e:
        if logging:
            print(f"Error editing table structure: {str(e)}")
        return False
    finally:
        # Close the connection
        conn.close()

def check_if_key_exists(filepath, value, table_name="data",  logging = False):
    """
    Check if a specific key-value pair exists in a table in an SQLite database.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str): The name of the table to check.
        - value (any): The value to check for existence.
        - logging (bool, optional): Whether to log success or failure messages. Defaults to False.
       
    Returns:
        - bool: Whether the key-value pair exists (True) or not (False).
        
    Example:
        >>> print(check_if_key_exists(filepath=".\\db\\test.db",table_name = "data2",value=54))
    """
    try:
        # Connect to the SQLite database
        key_column = get_primary_columns(filepath=filepath,table_name=table_name)
        if key_column:
            key_column = key_column[0]
            conn = sqlite3.connect(filepath)
            c = conn.cursor()

            # Execute the SQL query to check if the key-value pair exists
            c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {key_column} = ?", (value,))
            count = c.fetchone()[0]

            # Close the connection
            conn.close()

            # Return True if count is greater than 0, indicating existence, otherwise return False
            return count > 0
        else:
            if logging == True:
                print("Table or DB Not found")
    except Exception as e:
        if logging == True:
            print(f"Error checking key-value existence: {str(e)}")
    
def delete_database(filepath, logging=False, confirm=False):
    """
    Delete an SQLite database file.

    Args:
        - filepath (str): The path to the SQLite database file.
        - logging (bool, optional): Whether to log messages. Defaults to False.
        - confirm (bool, optional): Whether to ask for confirmation before deletion. Defaults to False.

    Returns:
        - bool: Whether the operation succeeded (True) or not (False).

    Example:
        >>> delete_database(confirm=True,filepath=".\\db\\test.db",logging=True)
    """
    try:
        if not os.path.exists(filepath):
            if logging:
                print(f"Database file '{filepath}' does not exist.")
            return False

        if confirm:
            confirmation = input(f"Are you sure you want to delete the database file '{filepath}'? (y/n): ").strip().lower()
            if confirmation != 'y':
                if logging:
                    print("Operation aborted")
                return False

        os.remove(filepath)
        if logging:
            print(f"Database file '{filepath}' deleted successfully.")
        return True
    except Exception as e:
        if logging:
            print(f"Error deleting database file: {str(e)}")
        return False

def check_if_database_exists(filepath):
    """
    Check if an SQLite database file exists.

    Args:
        - filepath (str): The path to the SQLite database file.

    Returns:
        - bool: Whether the database file exists (True) or not (False).

    Example:
        >>> print(check_if_database_exists(filepath=".\\db\\test.db"))
    """
    return os.path.exists(filepath)

def load_data_from_key(filepath, value, table_name = "data", logging = False):
    """
    Load data from an SQLite database based on a specific primary key value.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str): The name of the table from which to load data.
        - value (any): The value of the primary key to search for.

    Returns:
        - dict or None: The data corresponding to the primary key value, or None if no matching data is found.
        
    Raises:
        - LoadDataError: If an error occurs while loading data.

    Raises do not work

    Example:
        >>> data = load_data_from_key(filepath=".\\db\\test.db",table_name="data3",logging=True,value=54)
    """
    try:
        if check_if_database_exists(filepath=filepath) == True:
            if table_exists(filepath=filepath,table_name=table_name) == True:
                primary_column = get_primary_columns(filepath=filepath, table_name=table_name)
                primary_column = primary_column[0]  # Assuming there's only one primary column

                conn = sqlite3.connect(filepath)
                c = conn.cursor()

                # Execute the SQL query to select data based on the primary key value
                c.execute(f"SELECT * FROM {table_name} WHERE {primary_column} = ?", (value,))
                row = c.fetchone()

                if row:
                    # Convert JSON strings back to Python objects if necessary
                    data = {}
                    for i, column in enumerate(c.description):
                        column_name = column[0]
                        column_value = row[i]
                        # Check if the column value is a serialized JSON string
                        if isinstance(column_value, str) and column_value.startswith('{') and column_value.endswith('}'):
                            data[column_name] = unconvert(column_value)
                        else:
                            data[column_name] = column_value
                    return data
                else:
                    return None
            else:
                if logging == True:
                    print(f"The table is not found: {table_name}")     
                return(False)   
        else:
            if logging == True:
                print(f"The Database is not found: {filepath}")
            return(False)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
    finally:
        conn.close()

def load_all_data(filepath, table_name = "data", logging=False):
    """
    Load all data from an SQLite database table.

    Args:
        filepath (str): The path to the SQLite database file.
        table_name (str): The name of the table from which to load data.
        logging (bool, optional): Whether to log error messages. Defaults to False.

    Returns:
        list or None: A list containing dictionaries representing the rows of data from the table, 
                      or None if an error occurs.

    Example:
        >>> data = load_all_data(filepath=".\\db\\test.db", table_name="data", logging=True)
        """
    try:
        if not check_if_database_exists(filepath):
            if logging:
                print(f"The Database is not found: {filepath}")
            return None

        if not table_exists(filepath=filepath, table_name=table_name):
            if logging:
                print(f"The table is not found: {table_name}")
            return None

        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        c.execute(f"SELECT * FROM {table_name}")
        rows = c.fetchall()

        data = []
        for row in rows:
            row_data = {}
            for i, column in enumerate(c.description):
                column_name = column[0]
                column_value = row[i]
                if isinstance(column_value, str) and column_value.startswith('{') and column_value.endswith('}'):
                    row_data[column_name] = unconvert(column_value)
                else:
                    row_data[column_name] = column_value
            data.append(row_data)

        return data
    except Exception as e:
        if logging:
            print(f"Error loading data: {str(e)}")
        return None
    finally:
        conn.close()

def backup_database(source_filepath, backup_dir=".\\backup"):
    """
    Create a backup of an SQLite database file with a specified naming convention.

    Args:
        - source_filepath (str): The path to the source SQLite database file.
        - backup_dir (str, optional): The directory where the backup will be saved. Defaults to ".\\backup".

    Returns:
        - str: The filepath of the created backup.
        - bool: True if the backup was successful, False otherwise.

    Example: 
        >>> backup_database(backup_dir="./db-bu",source_filepath="./db/test.db")
    """
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Extract filename and extension from source filepath
        filename, ext = os.path.splitext(os.path.basename(source_filepath))
        
        # Generate backup filename with date
        backup_filename = f"backup-{filename}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{ext}"
        
        # Create backup filepath
        backup_filepath = os.path.join(backup_dir, backup_filename)
        
        # Perform backup
        shutil.copyfile(source_filepath, backup_filepath)
        
        return backup_filepath, True
    except Exception as e:
        print(f"Error backing up database: {e}")
        return None, False

def check_if_table_exists(filepath, table_name = "data"):
    """
    Check if a table exists in an SQLite database.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str): The name of the table to check.

    Returns:
        - bool: Whether the table exists (True) or not (False).
    
    Example:
        >>> ex = check_if_table_exists(filepath="./db/test.db",table_name="data3")
    """
    try:
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

        # Check if the table exists
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = c.fetchone()

        conn.close()

        return result is not None
    except Exception as e:
        print(f"Error checking if table exists: {e}")
        return False

def load_data_from_value(filepath, value, table_name="data", column=None, ignore_primary=False, logging=False):
    """
    Load data from an SQLite database based on a specific value present in any column, or a specified column.

    Args:
        - filepath (str): The path to the SQLite database file.
        - table_name (str): The name of the table from which to load data.
        - value (any): The value to search for in the table.
        - column (str, optional): The specific column to search in. If None, searches all columns.
        - ignore_primary (bool, optional): If True, includes primary key columns in the search. Defaults to False.
        - logging (bool): If True, enables logging of error messages.

    Returns:
        - list: A list of dictionaries, where each dictionary contains the data of a row that has the value in any column.
        
    Raises:
        - LoadDataError: If an error occurs while loading data.

    Example:
        >>> data_list = load_data_from_value(filepath=".\\db\\test.db", table_name="data3", value=54, logging=True)
    """
    try:
        if check_if_database_exists(filepath=filepath):
            if table_exists(filepath=filepath, table_name=table_name):
                primary_columns = get_primary_columns(filepath=filepath, table_name=table_name)
                conn = sqlite3.connect(filepath)
                c = conn.cursor()

                # Fetch all column names
                c.execute(f"PRAGMA table_info({table_name})")
                columns_info = c.fetchall()
                all_columns = [col[1] for col in columns_info]

                if column:
                    if column not in all_columns:
                        if logging:
                            print(f"The column '{column}' is not found in the table: {table_name}")
                        return []
                    search_columns = [column]
                else:
                    if ignore_primary:
                        search_columns = all_columns
                    else:
                        search_columns = [col for col in all_columns if col not in primary_columns]

                # Prepare the query to search for the value in the specified columns
                conditions = [f"{col} = ?" for col in search_columns]
                params = [value] * len(search_columns)

                query = f"SELECT rowid, * FROM {table_name} WHERE {' OR '.join(conditions)}"
                c.execute(query, params)

                rows = c.fetchall()

                result = []
                for row in rows:
                    row_data = {}
                    for i, column in enumerate(c.description):
                        column_name = column[0]
                        if column_name == 'rowid':
                            continue
                        column_value = row[i]
                        # Check if the column value is a serialized JSON string
                        if isinstance(column_value, str) and column_value.startswith('{') and column_value.endswith('}'):
                            row_data[column_name] = unconvert(column_value)
                        else:
                            row_data[column_name] = column_value
                    result.append(row_data)
                
                return result
            else:
                if logging:
                    print(f"The table is not found: {table_name}")
                return []
        else:
            if logging:
                print(f"The Database is not found: {filepath}")
            return []
    except Exception as e:
        raise LoadDataError(f"Error loading data: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()





# Example usage:
# exists = check_if_database_exists("example.db")
# print(exists)
# # remove_data_from_table(table_name="data2",filepath=".\\db\\test.db",key_values=5333,logging=True)
# data2 = [{"test1":56,"test2":2,"test3":[1,"test",2]},{"test1":55,"test2":2,"test3":2}] 
# create_sqlite_database(filename="test.db",logging=False,overwrite=False,path=".\\db")
# create_table(columns="test1 INTEGER, test2 TEXT, test3 TEXT",filepath=".\\db\\test.db",logging=False,overwrite=False,primary_key="test1",table_name="data3")
# # add_data_to_table(data=data1, filepath=".\\db\\test.db", table_name="data2",logging=True)
# add_data_to_table(data=data2, filepath=".\\db\\test.db", table_name="data3",logging=True)
# data = load_data_from_value(filepath="./db/test.db", value = "2", logging = False, table_name = "data3")
# print(data)