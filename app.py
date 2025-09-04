# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secure_random_key')  # Use env var for security

# Database path for Render persistent storage
DB_PATH = '/data/students.db'  # Matches Render's persistent disk mount path

def init_db():
    # Ensure the directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        print(f"Database initialized at {DB_PATH}")
    except sqlite3.OperationalError as e:
        print(f"Error initializing database: {e}")
        raise

# Initialize database
if not os.path.exists(DB_PATH):
    init_db()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            if user and check_password_hash(user[2], password):  # user[2] is password
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'danger')
        except sqlite3.OperationalError as e:
            flash(f'Database error: {e}', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (username, password, name, email, age)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, name, email, age))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        except sqlite3.OperationalError as e:
            flash(f'Database error: {e}', 'danger')
    return render_template('register.html')

@app.route('/home')
def home():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT name, email, age FROM students WHERE username = ?', (session['username'],))
        student = cursor.fetchone()
        conn.close()
        if student:
            return render_template('home.html', student=student)
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('logout'))
    except sqlite3.OperationalError as e:
        flash(f'Database error: {e}', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
