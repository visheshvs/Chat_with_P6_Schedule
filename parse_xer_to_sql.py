import os
import json
import pandas as pd
from xerparser import Xer
import sqlite3
from dotenv import load_dotenv

def convert_to_serializable(value):
    """
    Convert complex objects to serializable formats.
    
    Parameters:
        value: The value to convert.
        
    Returns:
        The serializable value.
    """
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    elif hasattr(value, '__dict__'):
        return json.dumps(vars(value))
    else:
        return value

def parse_xer_to_sqlite_and_csv(xer_file_path, sqlite_db_path, csv_export_dir):
    """
    Parse the XER file and store the data into a SQLite database and export as CSV files.
    
    Parameters:
        xer_file_path (str): Path to the .xer file.
        sqlite_db_path (str): Path to the SQLite database file.
        csv_export_dir (str): Directory path where CSV files will be saved.
    """
    # Ensure the CSV export directory exists
    os.makedirs(csv_export_dir, exist_ok=True)
    
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)

    # Parse the XER file
    try:
        xer = Xer.reader(xer_file_path)
        print(f"Successfully parsed XER file: {xer_file_path}")
    except Exception as e:
        print(f"Error parsing XER file: {e}")
        return
    
    # Connect to SQLite database (or create it if it doesn't exist)
    try:
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        print(f"Connected to SQLite database at: {sqlite_db_path}")
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite database: {e}")
        return
    
    # Iterate through each table in the XER file
    for table_name, table_data in xer.tables.items():
        if table_data:
            try:
                # Serialize data
                serialized_data = []
                for item in table_data:
                    if isinstance(item, dict):
                        # If item is a dictionary, use it directly
                        item_dict = {k: convert_to_serializable(v) for k, v in item.items()}
                    elif hasattr(item, '__dict__'):
                        # If item has a __dict__ attribute, convert it to a dictionary
                        item_dict = {k: convert_to_serializable(v) for k, v in vars(item).items()}
                    elif isinstance(item, str):
                        # If item is a string, assign it to a default key
                        item_dict = {'value': convert_to_serializable(item)}
                    else:
                        # For other data types, handle them as needed
                        item_dict = {'value': convert_to_serializable(str(item))}
                    
                    serialized_data.append(item_dict)
                
                # Create DataFrame
                df = pd.DataFrame(serialized_data)
                
                # Define table schema
                columns = df.columns.tolist()
                column_definitions = ', '.join([f'"{col}" TEXT' for col in columns])
                
                # Create table in SQLite
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS "{table_name}" (
                        {column_definitions}
                    )
                ''')
                print(f'Table "{table_name}" is ready in SQLite database.')
                
                # Prepare column names for the INSERT statement
                formatted_columns = ', '.join([f'"{col}"' for col in columns])
                
                # Insert data into SQLite table
                placeholders = ', '.join(['?'] * len(columns))
                insert_query = f'INSERT INTO "{table_name}" ({formatted_columns}) VALUES ({placeholders})'
                
                # Prepare data for insertion
                data_to_insert = df.values.tolist()
                
                # Insert data into table
                cursor.executemany(insert_query, data_to_insert)
                print(f'Inserted {len(data_to_insert)} records into table "{table_name}" in SQLite database.')
                
                # Export DataFrame to CSV
                csv_file_path = os.path.join(csv_export_dir, f"{table_name}.csv")
                df.to_csv(csv_file_path, index=False)
                print(f'Exported table "{table_name}" to CSV at: {csv_file_path}\n')
            
            except Exception as e:
                print(f"Error processing table '{table_name}': {e}\n")
                continue
    
    # Commit changes and close SQLite connection
    try:
        conn.commit()
        print(f"All data committed to SQLite database at: {sqlite_db_path}")
    except sqlite3.Error as e:
        print(f"Error committing changes to SQLite database: {e}")
    finally:
        conn.close()
        print("SQLite connection closed.")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Define the directory containing XER files
    xer_data_dir = os.path.join(os.getcwd(), "XER_Data")
    
    # Ensure XER_Data directory exists
    os.makedirs(xer_data_dir, exist_ok=True)
    
    # Get all XER files from the directory
    xer_files = [f for f in os.listdir(xer_data_dir) if f.lower().endswith('.xer')]
    
    if not xer_files:
        print("No XER files found in XER_Data directory.")
        return
    
    # Process each XER file
    for xer_file in xer_files:
        print(f"\nProcessing {xer_file}...")
        
        # Full path to the XER file
        xer_file_path = os.path.join(xer_data_dir, xer_file)
        
        # Create database name based on XER filename
        db_name = f"{os.path.splitext(xer_file)[0]}_database.db"
        sqlite_db = os.path.join(os.getcwd(), "Database", db_name)
        
        # Define the directory for CSV exports (separate folder for each XER file)
        csv_export_dir = os.path.join(os.getcwd(), "CSV Exports", os.path.splitext(xer_file)[0])
        
        # Parse XER and store data in SQLite and export as CSV
        parse_xer_to_sqlite_and_csv(xer_file_path, sqlite_db, csv_export_dir)

if __name__ == "__main__":
    main()
