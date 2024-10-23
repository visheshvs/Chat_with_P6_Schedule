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

def get_sql_query(client, user_prompt):
    """
    Use OpenAI's GPT model to convert a natural language prompt into an SQL query.
    
    Parameters:
        client (OpenAI): The OpenAI client object.
        user_prompt (str): The natural language question from the user.
        
    Returns:
        str: The generated SQL query.
    """
    prompt = f"""You are a helpful assistant that converts user questions into SQL queries based on the following SQLite database schema:
{get_database_schema()}

User Query: {user_prompt}

SQL Query:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that converts natural language questions into SQL queries based on the provided database schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=150,
            temperature=0,
            top_p=1,
            n=1,
            stop=["#"]
        )
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

    # Extract the SQL query from the response
    try:
        sql_query = response.choices[0].message.content.strip()
    except (IndexError, AttributeError) as e:
        raise RuntimeError(f"Unexpected response format from OpenAI: {e}")

    return sql_query

def get_database_schema():
    """
    Retrieve the SQLite database schema to provide context to the LLM.
    
    Returns:
        str: The database schema as a string.
    """
    sqlite_db = os.path.join(os.getcwd(), "project_database.db")
    conn = sqlite3.connect(sqlite_db)
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

def execute_sql_query(sql_query):
    """
    Execute the given SQL query against the SQLite database and return the results.
    
    Parameters:
        sql_query (str): The SQL query to execute.
        
    Returns:
        tuple: A tuple containing a list of column names and a list of result tuples.
    """
    sqlite_db = os.path.join(os.getcwd(), "project_database.db")
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        # Attempt to fetch results
        try:
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return columns, results
        except sqlite3.ProgrammingError:
            # Query did not return results (e.g., UPDATE, INSERT)
            conn.commit()
            return [], []
    except sqlite3.Error as e:
        raise RuntimeError(f"SQLite error: {e}")
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

def main():
    api_key = load_api_key()
    client = OpenAI(api_key=api_key)
    
    print("Welcome to the XER Database Query Assistant!")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("Enter your question: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        
        try:
            # Get SQL query from OpenAI
            sql_query = get_sql_query(client, user_input)
            print(f"\nGenerated SQL Query:\n{sql_query}\n")
            
            # Execute SQL query
            columns, results = execute_sql_query(sql_query)
            
            # Format and display results
            formatted_results = format_results(columns, results)
            print(f"Query Results:\n{formatted_results}\n")
        except Exception as e:
            print(f"An error occurred: {e}\n")

if __name__ == "__main__":
    main()
