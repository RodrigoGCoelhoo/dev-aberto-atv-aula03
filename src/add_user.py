"""Imports"""
from sqlite3 import connect
from hashlib import md5

def add_user(user, pwd, user_type):
    """
    Function used to add a new user
    """
    conn = connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('Insert into USER(?,?,?);', (user, pwd, user_type))
    conn.commit()
    conn.close()

def main():
    """
    Main function
    """
    with open('users.csv','r', encoding="utf-8") as file:
        lines = file.read().splitlines()

    for users in lines:
        (user, user_type) = users.split(',')
        print(user)
        print(user_type)
        add_user(user, md5(user.encode()).hexdigest(), user_type)

if __name__ == '__main__':
    main()
