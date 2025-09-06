from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure random key in production

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'school.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        # Add sample announcement
        cursor.execute('INSERT OR IGNORE INTO announcements (title, content) VALUES (?, ?)',
                      ('Welcome to Our School', 'Join us for the annual science fair next week!'))
        conn.commit()

# Initialize database
if not os.path.exists(DB_PATH):
    init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        flash('Please log in to access the homepage.', 'error')
        return redirect(url_for('login'))
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        cursor.execute('SELECT title, content FROM announcements')
        announcements = cursor.fetchall()
    
    return render_template('index.html', username=user[0], announcements=announcements)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')
        
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                              (username, generate_password_hash(password), email))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already taken.', 'error')
        
        return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
