import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

def load_api_key():
    """
    Load the OpenAI API key from the .env file.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    return api_key

def get_sql_query(client, user_prompt, db_path):
    """
    Use OpenAI's GPT model to convert a natural language prompt into an SQL query.
    """
    # Get schema with sample data for better context
    schema_context = get_database_schema_with_samples(db_path)
    
    system_prompt = """You are an expert SQL query generator specialized in Primavera P6 XER databases.
    Your task is to convert natural language questions into accurate SQL queries.
    
    IMPORTANT RULES:
    1. Generate ONLY the SQL query without any explanations or markdown
    2. Use standard SQLite syntax
    3. Always use double quotes for table/column names
    4. Never use MySQL-specific or other database-specific functions
    5. Ensure all quotes are straight quotes, not smart quotes
    6. Do not include any natural language text in the response
    
    Common tables and their relationships:
    - TASK: Contains task/activity information
    - PROJWBS: Work breakdown structure
    - ACTVCODE: Activity codes
    - TASKPRED: Task predecessors/relationships
    """

    user_prompt_template = f"""Database Schema and Sample Data:
{schema_context}

Example valid queries:
1. SELECT "task_name", "start_date" FROM "TASK" WHERE "start_date" IS NOT NULL;
2. SELECT t."task_name", w."wbs_name" FROM "TASK" t JOIN "PROJWBS" w ON t."wbs_id" = w."wbs_id";

User Question: {user_prompt}

Return only the SQL query without any other text:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Fixed model name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_template}
            ],
            temperature=0.1,
            max_tokens=300,
            top_p=0.95
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Basic validation
        if not sql_query.upper().startswith('SELECT'):
            raise ValueError("Generated query must start with SELECT")
            
        return sql_query
        
    except Exception as e:
        raise RuntimeError(f"An error occurred while generating SQL: {e}")

def get_available_databases():
    """
    Get a list of all SQLite databases in the Database directory.
    
    Returns:
        list: List of database filenames
    """
    database_dir = os.path.join(os.getcwd(), "Database")
    if not os.path.exists(database_dir):
        return []
    
    return [f for f in os.listdir(database_dir) if f.endswith('.db')]

def select_database():
    """
    Show available databases and let user select one.
    
    Returns:
        str: Full path to the selected database
    """
    databases = get_available_databases()
    
    if not databases:
        raise ValueError("No databases found in the Database directory.")
    
    print("\nAvailable databases:")
    for idx, db in enumerate(databases, 1):
        print(f"{idx}. {db}")
    
    while True:
        try:
            choice = input("\nSelect a database (enter the number): ")
            idx = int(choice) - 1
            if 0 <= idx < len(databases):
                return os.path.join(os.getcwd(), "Database", databases[idx])
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_database_schema(db_path):
    """
    Retrieve the SQLite database schema to provide context to the LLM.
    
    Parameters:
        db_path (str): Path to the SQLite database
    
    Returns:
        str: The database schema as a string.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = ""
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = cursor.fetchall()
        schema += f"Table: {table_name}\n"
        schema += "Columns:\n"
        for col in columns:
            schema += f" - {col[1]} ({col[2]})\n"
        schema += "\n"
    
    cursor.close()
    conn.close()
    return schema

def execute_sql_query(sql_query, db_path):
    """
    Execute the given SQL query against the SQLite database and return the results.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Print the exact query for debugging
        print("Executing SQL Query:", sql_query)
        
        # Remove any smart quotes or special characters
        sql_query = sql_query.replace('"', '"').replace('"', '"').replace("'", "'")
        
        cursor.execute(sql_query)
        try:
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return columns, results
        except sqlite3.ProgrammingError:
            conn.commit()
            return [], []
    except sqlite3.Error as e:
        # More detailed error message
        print(f"Original query that caused error: {sql_query}")
        raise RuntimeError(f"SQLite error: {e}\nQuery: {sql_query}")
    finally:
        cursor.close()
        conn.close()

def format_results(columns, results):
    """
    Format the SQL query results into a readable string.
    
    Parameters:
        columns (list of str): The column names.
        results (list of tuples): The query results.
        
    Returns:
        str: Formatted results.
    """
    if not results:
        return "No results found or the query did not return any data."
    
    # Create a simple table format
    formatted = ""
    # Header
    formatted += " | ".join(columns) + "\n"
    formatted += "-+-".join(['---'] * len(columns)) + "\n"
    # Rows
    for row in results:
        formatted += " | ".join([str(item) for item in row]) + "\n"
    
    return formatted

def get_database_schema_with_samples(db_path):
    """
    Get database schema with sample data for better context.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = []
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        # Get column info
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = cursor.fetchall()
        
        # Get sample data (first 3 rows)
        try:
            cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 3;")
            samples = cursor.fetchall()
        except sqlite3.Error:
            samples = []
            
        # Format table information
        schema.append(f"Table: {table_name}")
        schema.append("Columns:")
        for col in columns:
            schema.append(f"  - {col[1]} ({col[2]})")
            
        if samples:
            schema.append("Sample Data:")
            for sample in samples:
                schema.append(f"  {dict(zip([c[1] for c in columns], sample))}")
        schema.append("\n")
    
    cursor.close()
    conn.close()
    
    return "\n".join(schema)

def main():
    api_key = load_api_key()
    client = OpenAI(api_key=api_key)
    
    print("Welcome to the XER Database Query Assistant!")
    
    try:
        # Let user select a database
        selected_db = select_database()
        print(f"\nUsing database: {os.path.basename(selected_db)}")
        
        print("\nType 'exit' to quit.")
        while True:
            user_input = input("\nEnter your question: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            try:
                # Get SQL query from OpenAI
                sql_query = get_sql_query(client, user_input, selected_db)
                print(f"\nGenerated SQL Query:\n{sql_query}\n")
                
                # Execute SQL query
                columns, results = execute_sql_query(sql_query, selected_db)
                
                # Format and display results
                formatted_results = format_results(columns, results)
                print(f"Query Results:\n{formatted_results}\n")
            except Exception as e:
                print(f"An error occurred: {e}\n")
    
    except ValueError as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()
