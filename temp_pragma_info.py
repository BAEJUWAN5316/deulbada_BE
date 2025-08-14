
import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("""PRAGMA table_info(products_product);""")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    conn.close()
