# Schedule Database Query Assistant

## Description

The **Schedule Database Query Assistant** is a tool designed to facilitate the conversion of natural language queries into SQL queries for Primavera P6 schedule data. It processes both P6 XER files and PDF schedule exports, stores the data into separate SQLite databases, and allows users to interact with the databases using intuitive language prompts powered by OpenAI's API.

The tool specializes in handling:
- Primavera P6 XER files (native P6 export format)
- PDF exports of P6 schedules (typically activity lists or Gantt charts)

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
- `pdfplumber` (for PDF parsing)

You can install the required packages using `pip`:

```bash
pip install openai python-dotenv pandas xerparser pdfplumber
```

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/visheshvs/Chat_with_P6_Schedule.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd Chat_with_P6_Schedule
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
├── PDF_Data/           # Place your PDF files here
├── Database/           # Contains generated SQLite databases
├── PDF2CSV_Original/   # Contains original parsed PDF tables
│   ├── pdf1_name/
│   │   ├── page_1_table_1.csv
│   │   ├── page_1_table_2.csv
│   │   └── ...
│   └── pdf2_name/
└── CSV Exports/        # Contains processed CSV files
    ├── project1/       # XER exports
    ├── project2/       # XER exports
    ├── pdf1/          # PDF processed exports
    └── pdf2/          # PDF processed exports
```

## Usage

### 1. Processing XER Files

Place your XER files in the `XER_Data` directory and run:

```bash
python parse_xer_to_sql.py
```

### 2. Processing PDF Files

Place your PDF files containing tables in the `PDF_Data` directory and run:

```bash
python parse_pdf_to_sql.py
```

The PDF parser will:
- Extract tables from each page of the PDF
- Save original parsed tables in PDF2CSV_Original directory without transformations
- Process the tables to extract standardized columns:
  - Activity ID
  - Activity Name
  - Company (if exists)
  - Original Duration (if exists)
  - RD
  - Start Date
  - Finish Date
  - Total Float (if exists)
- Clean text data to remove formatting artifacts
- Store processed data in both SQLite database and CSV format
- Create separate folders for each PDF's exports

The parser creates two sets of outputs:
1. Original parsed tables (in PDF2CSV_Original directory)
   - Preserves original table structure
   - Minimal processing, just text cleaning
   - Separate CSV for each table on each page

2. Processed data (in CSV Exports and Database)
   - Standardized columns
   - Merged tables
   - Cleaned and formatted data
   - Single CSV and database table per PDF

### 3. Query the Databases

Run the query assistant:

```bash
python query_with_llm.py
```

The assistant will:
- Show a list of available databases (from both P6 XER and PDF sources)
- Let you select which database to query
- Accept natural language questions about the data

Example Interaction:
```
Welcome to the Schedule Database Query Assistant!

Available databases:
1. project1_database.db
2. project2_database.db
3. pdf1_database.db

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

- P6 XER sample files can be obtained from [Planning Engineer](https://planningengineer.net/tag/xer-file/)
- PDF files should contain tables that can be extracted by pdfplumber

## Credits

- **Vishesh Vikra Singh**
  - [Website](https://visheshvsingh.notion.site/)
  - [LinkedIn](https://www.linkedin.com/in/visheshvikram/)
