from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import time
from main import ask_gemini, generate_diagnosis  # Import consultation functions
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

# Database initialization
def init_db():
    conn = sqlite3.connect('medichat.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_history TEXT NOT NULL,
        diagnosis TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes for authentication
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False
        
        conn = sqlite3.connect('medichat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user[3], password):
            # Store user session
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            
            # If remember me is checked, make the session permanent
            if remember:
                session.permanent = True
                
            return redirect(url_for('index'))
        
        flash("Please check your login details and try again.")
        return redirect(url_for('login'))
    
    # If user is already logged in, redirect to home page
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('register'))
        
        # Check if email already exists
        conn = sqlite3.connect('medichat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            conn.close()
            flash("Email address already exists!")
            return redirect(url_for('register'))
        
        # Create a new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                      (name, email, hashed_password))
        conn.commit()
        conn.close()
        
        flash("Account created successfully! Please log in.")
        return redirect(url_for('login'))
    
    # If user is already logged in, redirect to home page
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# Main application routes
@app.route("/")
@login_required
def index():
    # Initialize session variables for a new consultation
    session["patient_history"] = ""
    session["consultation_active"] = True
    return render_template("index.html", user_name=session.get('user_name'))

@app.route("/send_response", methods=["POST"])
@login_required
def send_response():
    user_message = request.json.get("message")
    
    # First message: treat as initial symptoms
    if session.get("patient_history", "") == "":
        session["patient_history"] = f"Initial symptoms: {user_message}"
        ai_response = ask_gemini(session["patient_history"])
        return jsonify({"response": ai_response})
    else:
        # Append user's answer to the history
        patient_history = session["patient_history"] + f"\n\nAnswer: {user_message}"
        session["patient_history"] = patient_history

        # Get next AI question (or diagnosis signal)
        ai_response = ask_gemini(patient_history)
        
        if "DIAGNOSIS_READY" in ai_response:
            # Generate final diagnosis when ready
            diagnosis = generate_diagnosis(patient_history)
            
            # Save the consultation to the database
            if 'user_id' in session:
                conn = sqlite3.connect('medichat.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO consultations (user_id, patient_history, diagnosis) VALUES (?, ?, ?)",
                              (session['user_id'], patient_history, diagnosis))
                conn.commit()
                conn.close()
                
            return jsonify({
                "response": "Thank you for providing all the necessary information.",
                "diagnosis": diagnosis
            })
        else:
            # Append the AI question to the conversation history for context
            session["patient_history"] += f"\n\nQuestion: {ai_response}"
            return jsonify({"response": ai_response})

@app.route("/history")
@login_required
def consultation_history():
    conn = sqlite3.connect('medichat.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, diagnosis, created_at FROM consultations WHERE user_id = ? ORDER BY created_at DESC", 
                  (session['user_id'],))
    consultations = cursor.fetchall()
    conn.close()
    
    return render_template("history.html", consultations=consultations)

@app.route("/view_consultation/<int:consultation_id>")
@login_required
def view_consultation(consultation_id):
    conn = sqlite3.connect('medichat.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consultations WHERE id = ? AND user_id = ?", 
                  (consultation_id, session['user_id']))
    consultation = cursor.fetchone()
    conn.close()
    
    if not consultation:
        flash("Consultation not found or you don't have permission to view it.")
        return redirect(url_for('consultation_history'))
    
    return render_template("view_consultation.html", consultation=consultation)

# For local development only - remove in production
if __name__ == "__main__":
    app.run(debug=True)