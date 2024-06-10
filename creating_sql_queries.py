from anthropic import Anthropic
import sqlite3

# set up Anthopic API client
client = Anthropic()
MODEL_NAME = "claude-3-opus-20240229"

# Create or connect to sandbox database
connection = sqlite3.connect("test_db.db")
cursor =  connection.cursor()

# sample data
cursor.execute("""
    CREATE TABLE IF NOT EXIST employees (
               id INTEGER PRIMARY KEY,
               name TEXT,
               department TEXT,
               salary INTEGER
               )
""")

# insert sample data
sample_data = [
     (1, "John Doe", "Sales", 50000),
    (2, "Jane Smith", "Engineering", 75000),
    (3, "Mike Johnson", "Sales", 60000),
    (4, "Emily Brown", "Engineering", 80000),
    (5, "David Lee", "Marketing", 55000)
]

cursor.executemany("INSERT INTO employees VALEUS (?,?,?,?)", sample_data)
connection.commit