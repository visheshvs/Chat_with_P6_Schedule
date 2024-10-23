# XER Database Query Assistant

## Description

The **XER Database Query Assistant** is a tool designed to facilitate the conversion of natural language queries into SQL queries based on a given SQLite database schema. It parses XER files, stores the data into a SQLite database, and allows users to interact with the database using intuitive language prompts powered by OpenAI's GPT-4 model.

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

   Otherwise, install the required packages individually as shown in the Prerequisites section.

## Usage

1. **Parse XER File and Populate SQLite Database**

   Ensure you have a sample XER file. A sample file is provided from [Planning Engineer](https://planningengineer.net/tag/xer-file/).

   ```bash
   python parse_xer_to_sql.py
   ```

   This script will parse the XER file, store the data in `project_database.db`, and export the tables as CSV files in the `CSV Exports` directory.

2. **Run the Query Assistant**

   ```bash
   python query_with_llm.py
   ```

   - **Example Interaction:**

     ```
     Welcome to the XER Database Query Assistant!
     Type 'exit' to quit.

     Enter your question: List all projects with their start dates.
     
     Generated SQL Query:
     SELECT project_name, start_date FROM projects;

     Query Results:
     project_name | start_date
     ------------+------------
     Project A    | 2023-01-15
     Project B    | 2023-02-20
     ```

## Sample File

The sample XER file used in this project is sourced from [Planning Engineer](https://planningengineer.net/tag/xer-file/).

## Credits

- **Vishesh Vikra Singh**
  - [Website](https://visheshvsingh.notion.site/)
  - [LinkedIn](https://www.linkedin.com/in/visheshvikram/)

