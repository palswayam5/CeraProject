from flask import Flask, render_template, request, jsonify, session
import time
from main import ask_gemini, generate_diagnosis  # Import consultation functions

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

@app.route("/")
def index():
    # Initialize session variables for a new consultation
    session["patient_history"] = ""
    session["consultation_active"] = True
    return render_template("index.html")

@app.route("/send_response", methods=["POST"])
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
            return jsonify({
                "response": "Thank you for providing all the necessary information.",
                "diagnosis": diagnosis
            })
        else:
            # Append the AI question to the conversation history for context
            session["patient_history"] += f"\n\nQuestion: {ai_response}"
            return jsonify({"response": ai_response})

# @app.route("/send_audio", methods=["GET"])
# def send_audio():
#     # Use live audio input from the server's microphone
#     user_message = get_live_audio_input("Please speak your response:")
    
#     # Process input the same way as text input
#     if session.get("patient_history", "") == "":
#         session["patient_history"] = f"Initial symptoms: {user_message}"
#         ai_response = ask_gemini(session["patient_history"])
#         return jsonify({"response": ai_response, "audio_text": user_message})
#     else:
#         patient_history = session["patient_history"] + f"\n\nAnswer: {user_message}"
#         session["patient_history"] = patient_history

#         ai_response = ask_gemini(patient_history)
        
#         if "DIAGNOSIS_READY" in ai_response:
#             diagnosis = generate_diagnosis(patient_history)
#             return jsonify({
#                 "response": "Thank you for providing all the necessary information.",
#                 "diagnosis": diagnosis,
#                 "audio_text": user_message
#             })
#         else:
#             session["patient_history"] += f"\n\nQuestion: {ai_response}"
#             return jsonify({"response": ai_response, "audio_text": user_message})

#Note: Remove the following run block as Vercel will handle invocation.
if __name__ == "__main__":
    app.run(debug=True)
