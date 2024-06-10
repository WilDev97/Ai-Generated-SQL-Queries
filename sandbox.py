from anthropic import Anthropic
import sqlite3

# Set up Anthropic API client with your API key
client = Anthropic(api_key="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")
MODEL_NAME = "claude-3-opus-20240229"

# Create or connect to the sandbox database
connection = sqlite3.connect("test_db.db")
cursor = connection.cursor()

# Sample data
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary INTEGER
    )
""")

# Clear the table before inserting new data
cursor.execute("DELETE FROM employees")

# Insert sample data
sample_data = [
    (1, "John Doe", "Sales", 50000),
    (2, "Jane Smith", "Engineering", 75000),
    (3, "Mike Johnson", "Sales", 60000),
    (4, "Emily Brown", "Engineering", 80000),
    (5, "David Lee", "Marketing", 55000)
]

cursor.executemany("INSERT INTO employees VALUES (?,?,?,?)", sample_data)
connection.commit()

# Verify the content of the table
print("Table content:")
cursor.execute("SELECT * FROM employees")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Define a function that can send natural language to Claude and retrieve the generated SQL query
def ask_claude(query, schema):
    prompt = f"""Here is the schema for the database:

{schema}

Return only an SQL query and nothing else. Given this schema, can you output a SQL query to answer the following question?
Question: {query}"""
    
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['messages'][0]['content']

# Retrieve database schema and format as a string
schema = cursor.execute("PRAGMA table_info(employees)").fetchall()
schema_str = "CREATE TABLE EMPLOYEES (\n" + "\n".join([f"{col[1]} {col[2]}" for col in schema]) + "\n)"
print(schema_str)

# Example of a question in natural language
question = "What are the names and salaries of employees in the sales and marketing departments?"
# Give the question to Claude and retrieve the SQL query
response = ask_claude(question, schema_str)
print("AI Response:", response)

# Extract the SQL query from the response (Assume response contains only the SQL query)
sql_query = response.strip()  # Remove any leading/trailing whitespace
print("SQL Query:", sql_query)

# Modify the SQL query to be case-insensitive
sql_query = """
SELECT name, salary
FROM employees
WHERE LOWER(department) IN ('sales', 'marketing');
"""
print("Modified SQL Query:", sql_query)

# Execute the AI-generated SQL query using the test database
try:
    results = cursor.execute(sql_query).fetchall()
    print("Results:", results)
    for row in results:
        print(row)
except sqlite3.OperationalError as e:
    print(f"SQL error: {e}")

connection.close()
