"""Imports"""
import sqlite3

with open('quiz.sql', 'r', encoding="utf-8") as sql_file:
    sql_script = sql_file.read()

def create_db():
    """Create DataBase"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
    