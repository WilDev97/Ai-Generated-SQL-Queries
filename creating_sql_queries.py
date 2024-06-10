from anthropic import Anthropic
import sqlite3

# set up Anthopic API client
client = Anthropic(api_key="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")
MODEL_NAME = "claude-3-opus-20240229"

# Create or connect to sandbox database
connection = sqlite3.connect("test_db.db")
cursor = connection.cursor()

# sample data
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

# insert sample data
sample_data = [
     (1, "John Doe", "Sales", 50000),
    (2, "Jane Smith", "Engineering", 75000),
    (3, "Mike Johnson", "Sales", 60000),
    (4, "Emily Brown", "Engineering", 80000),
    (5, "David Lee", "Marketing", 55000)
]

cursor.executemany("INSERT INTO employees VALUES (?,?,?,?)", sample_data)
connection.commit()


# Define a function that can send natural language to Claude and retrieve generated SQL query
def ask_claude(query, schema):
    prompt = f"""Here is the schema for the database:

    {schema}

Return only an a SQL query and nothing else. Given this schema, can you output a SQL query to answer the following question?
Question: {query} """
    
    response = client.messages.create(
        model = MODEL_NAME,
        max_tokens=2048,
        messages=[
            {"role":"user","content": prompt}
        ]
    )
    return response.content[0].text

# Retrieve database schema and format as a string
schema = cursor.execute("PRAGMA table_info(employees)").fetchall()
schema_str = "CREATE TABLE EMPLOYEES (\n" + "\n".join([f"{col[1]} {col[2]}" for col in schema]) + "\n)"
print(schema_str)

# Example of question in natural language
question = "What are the names and salaries of employees in the Sales and Marketing departments?" # Capitalization Matters!
# Give question to claude and retrieve SQL query
sql_query =  ask_claude(question, schema_str)
print(sql_query)

# Lastly, execute the AI generated sql query using test database
results = cursor.execute(sql_query).fetchall()

for row in results:
    print(row)

connection.close()