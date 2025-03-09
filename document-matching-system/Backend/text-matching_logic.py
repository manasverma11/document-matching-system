from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime
import difflib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_FILE = 'database.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT,
                        credits INTEGER DEFAULT 20,
                        last_reset TEXT
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        filename TEXT,
                        content TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS credit_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        status TEXT DEFAULT 'pending',
                        FOREIGN KEY(user_id) REFERENCES users(id)
                     )''')
        conn.commit()
init_db()

# Reset credits at midnight
def reset_credits():
    now = datetime.datetime.utcnow().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET credits = 20, last_reset = ? WHERE last_reset < ?", (now, now))
        conn.commit()

# Register user
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    hashed_pw = generate_password_hash(password)
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role, last_reset) VALUES (?, ?, ?, ?)", 
                      (username, hashed_pw, role, datetime.datetime.utcnow().isoformat()))
            conn.commit()
            return jsonify({'message': 'User registered successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'message': 'Username already exists'}), 400

# Login user
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, password, role, credits, last_reset FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            reset_credits()  # Ensure daily reset
            return jsonify({'message': 'Login successful', 'role': user[3], 'credits': user[4]}), 200
        return jsonify({'message': 'Invalid credentials'}), 401

# Request additional credits
@app.route('/credits/request', methods=['POST'])
def request_credits():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    user_id = session['user_id']
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO credit_requests (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return jsonify({'message': 'Credit request submitted'}), 200

# Admin approves or denies credit requests
@app.route('/admin/credits/approve', methods=['POST'])
def approve_credits():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.json
    request_id = data.get('request_id')
    approve = data.get('approve', False)
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if approve:
            c.execute("SELECT user_id FROM credit_requests WHERE id=? AND status='pending'", (request_id,))
            user = c.fetchone()
            if user:
                c.execute("UPDATE users SET credits = credits + 10 WHERE id=?", (user[0],))
        c.execute("UPDATE credit_requests SET status=? WHERE id=?", ('approved' if approve else 'denied', request_id))
        conn.commit()
        return jsonify({'message': 'Credit request updated'}), 200

# Upload and scan document
@app.route('/scan', methods=['POST'])
def upload_document():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    user_id = session['user_id']
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    content = file.read().decode('utf-8')
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT credits FROM users WHERE id=?", (user_id,))
        credits = c.fetchone()[0]
        if credits <= 0:
            return jsonify({'message': 'Not enough credits'}), 403
        c.execute("INSERT INTO documents (user_id, filename, content) VALUES (?, ?, ?)", (user_id, filename, content))
        c.execute("UPDATE users SET credits = credits - 1 WHERE id=?", (user_id,))
        conn.commit()
        return jsonify({'message': 'File uploaded and scanned successfully'}), 201

# Find similar documents
@app.route('/matches/<int:doc_id>', methods=['GET'])
def find_matches(doc_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT content FROM documents WHERE id=?", (doc_id,))
        doc = c.fetchone()
        if not doc:
            return jsonify({'message': 'Document not found'}), 404
        query_content = doc[0]
        
        c.execute("SELECT id, content FROM documents WHERE id != ?", (doc_id,))
        documents = c.fetchall()
        matches = []
        
        for doc in documents:
            similarity = difflib.SequenceMatcher(None, query_content, doc[1]).ratio()
            if similarity > 0.5:  # Threshold for similarity
                matches.append({'doc_id': doc[0], 'similarity': round(similarity, 2)})
        
        return jsonify({'matches': matches}), 200

if __name__ == '__main__':
    app.run(debug=True)
