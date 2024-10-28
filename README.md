# XER Database Query Assistant

## Description

The **XER Database Query Assistant** is a tool designed to facilitate the conversion of natural language queries into SQL queries based on a given SQLite database schema. It processes multiple XER files, stores the data into separate SQLite databases, and allows users to interact with the databases using intuitive language prompts powered by OpenAI's GPT-4 model.

## Prerequisites

Ensure you have the following installed on your system:

- **Python**: Version 3.8 or higher
- **SQLite**: For managing the database

### Python Packages

The project relies on the following Python packages:

- `openai`
- `python-dotenv`
- `sqlite3` (Standard library)
- `pandas`
- `xerparser`

You can install the required packages using `pip`:

```bash
pip install openai python-dotenv pandas xerparser
```

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd your-repo
   ```

3. **Set Up Environment Variables**

   Create a `.env` file in the root directory and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Install Dependencies**

   If you have a `requirements.txt` file, you can install all dependencies at once:

   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

The project will create the following directory structure:

```
project_root/
├── XER_Data/           # Place your .xer files here
├── Database/           # Contains generated SQLite databases
└── CSV Exports/        # Contains exported CSV files
    ├── project1/
    └── project2/
```

## Usage

1. **Place XER Files**

   Place your XER files in the `XER_Data` directory. The script will process all files with the `.xer` extension.

2. **Parse XER Files and Populate SQLite Databases**

   ```bash
   python parse_xer_to_sql.py
   ```

   This script will:
   - Process all XER files in the `XER_Data` directory
   - Create separate databases for each XER file in the `Database` directory
   - Export tables as CSV files in separate folders under `CSV Exports`

3. **Run the Query Assistant**

   ```bash
   python query_with_llm.py
   ```

   The assistant will:
   - Show a list of available databases
   - Let you select which database to query
   - Accept natural language questions about the data

   **Example Interaction:**
   ```
   Welcome to the XER Database Query Assistant!

   Available databases:
   1. project1_database.db
   2. project2_database.db

   Select a database (enter the number): 1

   Using database: project1_database.db
   Type 'exit' to quit.

   Enter your question: List all tasks with their start dates.
   
   Generated SQL Query:
   SELECT task_name, start_date FROM TASK;

   Query Results:
   task_name | start_date
   ----------+------------
   Task A    | 2023-01-15
   Task B    | 2023-02-20
   ```

## Sample Files

Sample XER files can be obtained from [Planning Engineer](https://planningengineer.net/tag/xer-file/).

## Credits

- **Vishesh Vikra Singh**
  - [Website](https://visheshvsingh.notion.site/)
  - [LinkedIn](https://www.linkedin.com/in/visheshvikram/)
