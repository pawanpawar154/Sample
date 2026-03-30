from flask import Flask, render_template, request, redirect, session, url_for
from analyzer import analyze_report
import sqlite3
import os
import re
import requests
import json

# 🔹 Firebase import
# app.py
from firebase_config import firebase_admin  # ensures Firebase is initialized
from firebase_admin import auth as firebase_auth

app = Flask(__name__)
app.secret_key = "secret123"

# 📂 Upload folder
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🗄️ Create DB
def init_db():
    conn = sqlite3.connect("medireport.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        filename TEXT,
        result TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# Landing Page
@app.route('/')
def landing():
    return render_template('landingpage.html')


# 🔐 LOGIN (Firebase)
# 🔐 LOGIN (Firebase)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Firebase REST API to verify password
        import requests, json
        API_KEY =  "AIzaSyD3uBOlPg7Lp8wcUD3AFahRIBcjvyRyToQ"  # from Firebase Web App config
        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        response = requests.post(url, data=payload)
        result = response.json()

        if 'idToken' in result:
            user = firebase_auth.get_user_by_email(email)
            session['user'] = user.display_name
            session['email'] = user.email
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')


# 📝 SIGNUP (Firebase)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            # 🔹 Create user in Firebase
            user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=username
            )

            # Optional: store username/email in SQLite for reports
            conn = sqlite3.connect("medireport.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (username,email,password) VALUES (?, ?, ?)",
                (username, email, "")  # password not stored locally
            )
            conn.commit()
            conn.close()

            return redirect('/login')

        except firebase_admin._auth_utils.EmailAlreadyExistsError:
            return render_template('signup.html', error="Email already exists")

    return render_template('signup.html')


# 🏠 HOME
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    return render_template('home.html')


# 📄 PDF TEXT EXTRACTION
def extract_text_from_pdf(filepath):
    import PyPDF2

    text = ""
    with open(filepath, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text


# 🖼️ IMAGE OCR
def extract_text_from_image(filepath):
    import pytesseract
    from PIL import Image

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    img = Image.open(filepath)
    text = pytesseract.image_to_string(img)

    return text


# 📤 UPLOAD + ANALYZE
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    if 'file' not in request.files or request.files['file'].filename == "":
        return "No file selected"

    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    if file.filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
    elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(filepath)
    else:
        return "Unsupported file type"

    result, explanation = analyze_report(text)

    conn = sqlite3.connect("medireport.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (email, filename, result) VALUES (?, ?, ?)",
        (session['email'], file.filename, ", ".join(result))
    )
    conn.commit()
    conn.close()

    return render_template('result.html', result=result, explanation=explanation)


# 📜 HISTORY
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("medireport.db")
    cursor = conn.cursor()
    cursor.execute("SELECT filename, result, date FROM reports WHERE email=?", (session['email'],))
    data = cursor.fetchall()
    conn.close()
    return render_template('history.html', data=data)


# 👤 PROFILE
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("medireport.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reports WHERE email=?", (session['email'],))
    count = cursor.fetchone()[0]
    conn.close()

    return render_template('profile.html', username=session['user'], count=count)


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('email', None)
    return redirect('/')


# ▶ RUN
if __name__ == '__main__':
    app.run(debug=True)