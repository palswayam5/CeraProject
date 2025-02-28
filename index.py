from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import time
from main import ask_gemini, generate_diagnosis  # Import consultation functions
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')  # Replace with the path to your service account key
firebase_admin.initialize_app(cred)
db = firestore.client()

# Firestore is schema-less, so no explicit database initialization is required.

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

        users_ref = db.collection('users')
        # Query for a user with the provided email
        query = users_ref.where('email', '==', email).limit(1).stream()
        user_doc = next(query, None)

        if user_doc:
            user = user_doc.to_dict()
            if check_password_hash(user['password'], password):
                # Store session info using Firestore's document id for the user
                session['user_id'] = user_doc.id
                session['user_name'] = user.get('name')
                session['user_email'] = user.get('email')
                if remember:
                    session.permanent = True
                return redirect(url_for('index'))

        flash("Please check your login details and try again.")
        return redirect(url_for('login'))

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

        users_ref = db.collection('users')
        # Verify that the email is not already registered
        query = users_ref.where('email', '==', email).limit(1).stream()
        if any(query):
            flash("Email address already exists!")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        # Create a new user document with a server timestamp
        users_ref.add({
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': firestore.SERVER_TIMESTAMP
        })

        flash("Account created successfully! Please log in.")
        return redirect(url_for('login'))

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
    # Start a new consultation
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
            # Save the consultation to Firestore
            consultations_ref = db.collection('consultations')
            consultations_ref.add({
                'user_id': session['user_id'],
                'patient_history': patient_history,
                'diagnosis': diagnosis,
                'created_at': firestore.SERVER_TIMESTAMP
            })
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
    consultations_ref = db.collection('consultations')
    query = consultations_ref.where('user_id', '==', session['user_id']) \
                             .order_by('created_at', direction=firestore.Query.DESCENDING) \
                             .stream()
    consultations = []
    for doc in query:
        data = doc.to_dict()
        data['id'] = doc.id
        consultations.append(data)
    return render_template("history.html", consultations=consultations)

@app.route("/view_consultation/<consultation_id>")
@login_required
def view_consultation(consultation_id):
    doc = db.collection('consultations').document(consultation_id).get()
    if not doc.exists or doc.to_dict().get('user_id') != session['user_id']:
        flash("Consultation not found or you don't have permission to view it.")
        return redirect(url_for('consultation_history'))

    consultation = doc.to_dict()
    consultation['id'] = doc.id
    return render_template("view_consultation.html", consultation=consultation)

if __name__ == "__main__":
    app.run(debug=True)
