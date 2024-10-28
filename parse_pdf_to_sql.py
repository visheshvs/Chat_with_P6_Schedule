import os
import json
import pandas as pd
import sqlite3
import pdfplumber
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

def extract_tables_from_pdf(pdf_file_path):
    """
    Extract and merge tables from PDF file.
    """
    all_rows = []
    project_name = None
    standard_columns = [
        'Activity ID', 'Activity Name', 'Company', 'Original Duration',
        'RD', 'Start Date', 'Finish Date', 'Total Float'
    ]
    #TODO: Add standard columns for each PDF file https://docs.oracle.com/cd/F37125_01/p6help/en/helpmain.htm?toc.htm?47261.htm
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            print(f"Successfully opened PDF: {pdf_file_path}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                
                for table_data in page_tables:
                    if not table_data or len(table_data) < 2:  # Need at least 2 rows
                        continue
                    
                    # Get project name from first row, first column if not already set
                    if not project_name and table_data[0][0]:
                        project_name = str(table_data[0][0]).strip()
                        print(f"Found project name: {project_name}")
                    
                    # Get all unique column names from second row (row 1)
                    original_headers = [str(col).strip() for col in table_data[1] if col and str(col).strip() != 'None']
                    print("\nOriginal headers found:", original_headers)
                    
                    # Map original headers to standard headers
                    header_mapping = {}
                    for idx, header in enumerate(table_data[1]):
                        if header and str(header).strip() != 'None':
                            header_lower = str(header).lower().strip().replace(' ', '')
                            for std_col in standard_columns:
                                std_col_lower = std_col.lower().replace(' ', '')
                                if std_col_lower in header_lower or header_lower in std_col_lower:
                                    header_mapping[idx] = std_col
                                    break
                    
                    print("Header mapping:", header_mapping)
                    
                    # Process data rows (starting from row 2)
                    for row in table_data[2:]:
                        if any(row):  # Skip empty rows
                            row_dict = {}
                            for idx, value in enumerate(row):
                                if idx in header_mapping:  # Only include mapped columns
                                    clean_value = str(value).strip() if value else None
                                    if clean_value and clean_value.lower() != 'none':
                                        row_dict[header_mapping[idx]] = clean_value
                            
                            if row_dict:  # Only add if we have valid data
                                all_rows.append(row_dict)
        
        print(f"\nProject Name: {project_name}")
        print(f"Total rows extracted: {len(all_rows)}")
        
        if len(all_rows) == 0:
            print("WARNING: No rows were extracted!")
            print("This might be because:")
            print("1. No matching columns were found")
            print("2. The table structure doesn't match expectations")
        else:
            print("Columns found in data:", list(all_rows[0].keys()))
        
        return project_name, all_rows
    
    except Exception as e:
        print(f"\nError extracting tables from PDF file: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        return None, []

def clean_text(text):
    """
    Clean text by removing duplicate consecutive characters.
    
    Parameters:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text or not isinstance(text, str):
        return text
        
    # Convert multiple consecutive same characters into single character
    cleaned = ''
    prev_char = ''
    count = 0
    max_repeats = 2  # Maximum number of allowed repeats
    
    for char in text:
        if char == prev_char:
            count += 1
            if count < max_repeats:
                cleaned += char
        else:
            count = 1
            cleaned += char
        prev_char = char
    
    return cleaned.strip()

def save_original_tables(pdf_file_path, original_export_dir):
    """
    Save the original parsed tables from PDF without any transformations.
    
    Parameters:
        pdf_file_path (str): Path to the PDF file
        original_export_dir (str): Directory to save original CSV files
    """
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            print(f"\nSaving original tables from: {pdf_file_path}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                
                for table_num, table_data in enumerate(page_tables, 1):
                    if table_data:
                        # Clean the table data
                        cleaned_data = []
                        for row in table_data:
                            cleaned_row = [clean_text(cell) if cell else cell for cell in row]
                            cleaned_data.append(cleaned_row)
                        
                        # Convert table data to DataFrame
                        df = pd.DataFrame(cleaned_data)
                        
                        # Create filename for this table
                        csv_filename = f"page_{page_num}_table_{table_num}.csv"
                        csv_path = os.path.join(original_export_dir, csv_filename)
                        
                        # Save to CSV
                        df.to_csv(csv_path, index=False, header=False)
                        print(f"Saved original table to: {csv_path}")

    except Exception as e:
        print(f"Error saving original tables: {e}")

def parse_pdf_to_sqlite_and_csv(pdf_file_path, sqlite_db_path, csv_export_dir):
    """
    Parse the PDF file and store the data into a SQLite database and export as CSV files.
    """
    # Ensure directories exist
    os.makedirs(csv_export_dir, exist_ok=True)
    os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)
    
    # Create directory for original CSV exports
    original_export_dir = os.path.join(os.getcwd(), "PDF2CSV_Original", 
                                     os.path.splitext(os.path.basename(pdf_file_path))[0])
    os.makedirs(original_export_dir, exist_ok=True)
    
    # Save original tables first
    save_original_tables(pdf_file_path, original_export_dir)

    # Extract tables from PDF
    project_name, merged_data = extract_tables_from_pdf(pdf_file_path)
    if not merged_data:
        print("No valid data found in the PDF file.")
        return
    
    try:
        # Create DataFrame with only the standard columns that exist in the data
        df = pd.DataFrame(merged_data)
        
        # Connect to SQLite database
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        
        # Create table name from project name or use default
        table_name = "PROJECT_DATA"
        
        # Define table schema
        columns = df.columns.tolist()
        column_definitions = ', '.join([f'"{col}" TEXT' for col in columns])
        
        # Create table in SQLite
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                {column_definitions}
            )
        ''')
        
        # Insert data into SQLite table
        formatted_columns = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f'INSERT INTO "{table_name}" ({formatted_columns}) VALUES ({placeholders})'
        
        # Insert data
        cursor.executemany(insert_query, df.values.tolist())
        print(f'Inserted {len(df)} records into table "{table_name}" in SQLite database.')
        
        # Export DataFrame to CSV
        csv_file_path = os.path.join(csv_export_dir, f"{table_name}.csv")
        df.to_csv(csv_file_path, index=False)
        print(f'Exported merged data to CSV at: {csv_file_path}')
        
        # Commit and close connection
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error processing data: {e}")
        if 'conn' in locals():
            conn.close()

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Define the directory containing PDF files
    pdf_data_dir = os.path.join(os.getcwd(), "PDF_Data")
    
    # Ensure PDF_Data directory exists
    os.makedirs(pdf_data_dir, exist_ok=True)
    
    # Get all PDF files from the directory
    pdf_files = [f for f in os.listdir(pdf_data_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in PDF_Data directory.")
        return
    
    # Process each PDF file
    for pdf_file in pdf_files:
        print(f"\nProcessing {pdf_file}...")
        
        # Full path to the PDF file
        pdf_file_path = os.path.join(pdf_data_dir, pdf_file)
        
        # Create database name based on PDF filename
        db_name = f"{os.path.splitext(pdf_file)[0]}_database.db"
        sqlite_db = os.path.join(os.getcwd(), "Database", db_name)
        
        # Define the directory for CSV exports (separate folder for each PDF file)
        csv_export_dir = os.path.join(os.getcwd(), "CSV Exports", os.path.splitext(pdf_file)[0])
        
        # Parse PDF and store data in SQLite and export as CSV
        parse_pdf_to_sqlite_and_csv(pdf_file_path, sqlite_db, csv_export_dir)

if __name__ == "__main__":
    main()
