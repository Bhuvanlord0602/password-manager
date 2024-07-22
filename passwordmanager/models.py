import sqlite3  # Import tool to work with the database

def init_db():
    conn = sqlite3.connect('database.db')  # Connect to the database
    c = conn.cursor()  # Create a cursor to execute SQL commands
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Unique ID for each user, automatically increases
            username TEXT UNIQUE NOT NULL,  # Username must be unique and not empty
            password TEXT NOT NULL  # Password cannot be empty
        )
    ''')  # Create the 'users' table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Unique ID for each password, automatically increases
            user_id INTEGER,  # ID of the user who owns this password
            site_name TEXT NOT NULL,  # Name of the website, cannot be empty
            site_url TEXT NOT NULL,  # URL of the website, cannot be empty
            site_password TEXT NOT NULL,  # Password for the website, cannot be empty
            FOREIGN KEY (user_id) REFERENCES users(id)  # Link to the 'users' table
        )
    ''')  # Create the 'passwords' table if it doesn't exist
    conn.commit()  # Save the changes to the database
    conn.close()  # Close the connection to the database

if __name__ == "__main__":
    init_db()  # Run the function to initialize the database
