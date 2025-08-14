
import sqlite3
import os

db_path = 'db.sqlite3'
# Ensure the database file exists before trying to connect
if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("DELETE FROM django_migrations WHERE app = 'products';")
    conn.commit()
    print('Products app migration history cleared from database.')
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    conn.close()
