from flask import Flask, render_template, request, redirect, url_for, session, flash  # Import necessary modules from Flask
from werkzeug.security import generate_password_hash, check_password_hash  # Import password hashing functions
import sqlite3  # Import SQLite3 for database operations
import logging  # Import logging for debugging

app = Flask(__name__)  # Create an instance of the Flask app
app.secret_key = 'supersecretkey'  # Set a secret key for security

logging.basicConfig(level=logging.DEBUG)  # Set up logging to show debug messages

def get_db_connection():
    try:
        conn = sqlite3.connect('database.db')  # Connect to the database
        conn.row_factory = sqlite3.Row  # Allow accessing columns by name
        return conn  # Return the connection object
    except sqlite3.Error as e:
        app.logger.error(f"Database connection error: {e}")  # Log any database connection error
        return None  # Return None if connection fails

@app.route('/')
def index():
    return redirect(url_for('register'))  # Redirect to the registration page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']  # Get the entered username
        password = request.form['password']  # Get the entered password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)  # Hash the password for security

        conn = get_db_connection()  # Connect to the database
        if conn is None:
            flash('Database connection failed')  # Show an error message if connection fails
            return redirect(url_for('register'))  # Redirect to the registration page

        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()  # Check if the username exists
            if user:
                flash('Username already exists')  # Show an error message if username exists
            else:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))  # Add new user to the database
                conn.commit()  # Save the changes
                flash('Registered successfully! Please login.')  # Show a success message
                return redirect(url_for('login'))  # Redirect to the login page
        except sqlite3.DatabaseError as e:
            app.logger.error(f"Database error: {e}")  # Log any database error
            flash('Database error occurred. Please try again later.')  # Show a database error message
        finally:
            conn.close()  # Close the database connection
        
        return redirect(url_for('register'))  # Redirect to the registration page if registration fails
    return render_template('register.html')  # Show the registration page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Get the entered username
        password = request.form['password']  # Get the entered password

        conn = get_db_connection()  # Connect to the database
        if conn is None:
            flash('Database connection failed')  # Show an error message if connection fails
            return redirect(url_for('login'))  # Redirect to the login page

        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()  # Find the user in the database
            if user and check_password_hash(user['password'], password):  # Check if the password is correct
                session['user_id'] = user['id']  # Save the user's ID in the session
                return redirect(url_for('dashboard'))  # Redirect to the dashboard
            else:
                flash('Invalid username or password')  # Show an error message if login fails
        except sqlite3.DatabaseError as e:
            app.logger.error(f"Database error: {e}")  # Log any database error
            flash('Database error occurred. Please try again later.')  # Show a database error message
        finally:
            conn.close()  # Close the database connection
        
        return redirect(url_for('login'))  # Redirect to the login page if login fails
    return render_template('login.html')  # Show the login page

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    user_id = session['user_id']  # Get the user's ID from the session
    conn = get_db_connection()  # Connect to the database
    if conn is None:
        flash('Database connection failed')  # Show an error message if connection fails
        return redirect(url_for('login'))  # Redirect to the login page

    try:
        passwords = conn.execute('SELECT * FROM passwords WHERE user_id = ?', (user_id,)).fetchall()  # Get all passwords for the user
    except sqlite3.DatabaseError as e:
        app.logger.error(f"Database error: {e}")  # Log any database error
        flash('Database error occurred. Please try again later.')  # Show a database error message
        return redirect(url_for('login'))  # Redirect to the login page
    finally:
        conn.close()  # Close the database connection

    return render_template('dashboard.html', passwords=passwords)  # Show the dashboard page with passwords

@app.route('/add_password', methods=['POST'])
def add_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    site_name = request.form['site_name']  # Get the entered site name
    site_url = request.form['site_url']  # Get the entered site URL
    site_password = request.form['site_password']  # Get the entered site password

    conn = get_db_connection()  # Connect to the database
    if conn is None:
        flash('Database connection failed')  # Show an error message if connection fails
        return redirect(url_for('dashboard'))  # Redirect to the dashboard

    try:
        conn.execute('INSERT INTO passwords (user_id, site_name, site_url, site_password) VALUES (?, ?, ?, ?)',
                     (session['user_id'], site_name, site_url, site_password))  # Add the new password to the database
        conn.commit()  # Save the changes
    except sqlite3.DatabaseError as e:
        app.logger.error(f"Database error: {e}")  # Log any database error
        flash('Database error occurred. Please try again later.')  # Show a database error message
    finally:
        conn.close()  # Close the database connection

    return redirect(url_for('dashboard'))  # Redirect to the dashboard

@app.route('/update_password/<int:id>', methods=['POST'])
def update_password(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    site_name = request.form['site_name']  # Get the entered site name
    site_url = request.form['site_url']  # Get the entered site URL
    site_password = request.form['site_password']  # Get the entered site password

    conn = get_db_connection()  # Connect to the database
    if conn is None:
        flash('Database connection failed')  # Show an error message if connection fails
        return redirect(url_for('dashboard'))  # Redirect to the dashboard

    try:
        conn.execute('UPDATE passwords SET site_name = ?, site_url = ?, site_password = ? WHERE id = ? AND user_id = ?',
                     (site_name, site_url, site_password, id, session['user_id']))  # Update the password in the database
        conn.commit()  # Save the changes
    except sqlite3.DatabaseError as e:
        app.logger.error(f"Database error: {e}")  # Log any database error
        flash('Database error occurred. Please try again later.')  # Show a database error message
    finally:
        conn.close()  # Close the database connection

    return redirect(url_for('dashboard'))  # Redirect to the dashboard

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user ID from the session
    return redirect(url_for('index'))  # Redirect to the home page

if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode
