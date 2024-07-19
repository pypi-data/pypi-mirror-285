import duckdb
from datetime import datetime


def generate_catalog_table_name(station, location, platform):
    """
    Generates a table name based on station, location, and platform abbreviations.

    Parameters:
    station (str): The abbreviation for the station.
    location (str): The abbreviation for the location.
    platform (str): The abbreviation for the platform.

    Returns:
    str: The generated table name.
    """
    return f"{station}_{location}_{platform}_data"



def save_date_grouped_filepaths_to_duckdb(db_path, table_name, data_dict):
    """
    Saves grouped image data to a DuckDB database.

    This function connects to a DuckDB database specified by db_path, creates a table if it does
    not already exist, and inserts data from a dictionary where the keys are formatted creation 
    dates and the values are lists of file paths.

    Parameters:
    db_path (str): The path to the DuckDB database file.
    table_name (str): The name of the table to insert data into.
    data_dict (dict): A dictionary where keys are formatted creation dates (as strings) and values 
                      are lists of file paths that correspond to those dates.

    Raises:
    ValueError: If any error occurs during the process.

    Example:
    >>> data_dict = {
    >>>     '2023-01-01 12:00:00': ['/path/to/image1.jpg'],
    >>>     '2023-01-02 13:00:00': ['/path/to/image2.jpg']
    >>> }
    >>> save_date_grouped_filepaths_to_duckdb('/path/to/database.duckdb', 'STA_LOC_PLT_data', data_dict)
    """
    try:
        # Connect to DuckDB
        conn = duckdb.connect(database=db_path, read_only=False)
        
        # Create table if it doesn't exist
        conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            creation_date TEXT,
            filepath TEXT,
            year INTEGER
        );
        """)
        
        # Insert data into the table
        insert_query = f"INSERT INTO {table_name} (creation_date, filepath, year) VALUES (?, ?, ?)"
        for date, paths in data_dict.items():
            year = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').year
            for path in paths:
                conn.execute(insert_query, [date, path, year])
    except Exception as e:
        raise ValueError(f"An error occurred while saving to DuckDB: {e}")
    finally:
        # Close the connection
        conn.close()

        
def filter_by_year_from_grouped_filepaths_duckdb(db_path, table_name, year):
    """
    Filters and retrieves entries from a DuckDB database for a specified year.

    This function connects to a DuckDB database, executes a query to retrieve entries
    from the specified table that match the given year, and transforms the result into
    a dictionary where the keys are creation dates and the values are lists of file paths.

    Parameters:
    db_path (str): The path to the DuckDB database file.
    table_name (str): The name of the table to query.
    year (int): The year to filter entries by.

    Returns:
    dict: A dictionary where keys are creation dates (as strings) and values are lists
          of file paths that correspond to those dates.

    Example:
    >>> db_path = '/path/to/database.duckdb'
    >>> table_name = 'image_table'
    >>> year = 2023
    >>> filter_by_year_from_duckdb(db_path, table_name, year)
    {
        '2023-01-01 12:00:00': ['/path/to/image1.jpg'],
        '2023-02-01 13:00:00': ['/path/to/image2.jpg']
    }
    """
    # Connect to DuckDB
    conn = duckdb.connect(database=db_path, read_only=True)
    
    # Execute the query to retrieve entries for the specified year
    query = f"""
    SELECT creation_date, filepath 
    FROM {table_name}
    WHERE year = ?
    """
    result = conn.execute(query, [year]).fetchall()
    
    # Close the connection
    conn.close()
    
    # Transform the result into a dictionary
    filtered_dict = {}
    for row in result:
        date, path = row
        if date not in filtered_dict:
            filtered_dict[date] = []
        filtered_dict[date].append(path)
    
    return filtered_dict 


def get_all_filepaths_in_duckdb(db_path, table_name):
    """
    Retrieves all stored file paths from a specified table in a DuckDB database.

    This function connects to a DuckDB database, retrieves all file paths stored in the specified
    table, and returns them as a list.

    Parameters:
    db_path (str): The path to the DuckDB database file.
    table_name (str): The name of the table to retrieve file paths from.

    Returns:
    list: A list of file paths stored in the specified table.

    Example:
    >>> db_path = '/path/to/database.duckdb'
    >>> table_name = 'backup_files'
    >>> get_all_backup_filepaths_in_duckdb(db_path, table_name)
    ['/path/to/backup/file1.jpg', '/path/to/backup/file2.jpg']
    """
    # Connect to the DuckDB database and retrieve stored file paths
    conn = duckdb.connect(db_path)
    query = f'SELECT filepath FROM {table_name}'
    result = conn.execute(query).fetchall()
    conn.close()

    # Extract file paths from the result
    stored_filepaths = [row[0] for row in result]
    return stored_filepaths
