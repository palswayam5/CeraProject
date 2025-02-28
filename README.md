# Final-Project-Cera  

# 🏥 MediChat - AI-Powered Medical Assistant  

MediChat is an **AI-powered medical consultation system** that helps users receive **intelligent health insights** by describing symptoms.  
It uses **Google's Gemini AI** to provide interactive medical consultations, follow-up questions, and potential diagnoses.  

🚀 **Built with Flask, SQLite, and Gemini AI**  

---

## 📌 Table of Contents  
- [🌟 Features](#-features)  
- [🛠️ Prerequisites](#-prerequisites)  
- [💾 Installation](#-installation)  
- [🔧 Configuration](#-configuration)  
- [🚀 Usage](#-usage)  
- [📡 API Endpoints](#-api-endpoints)  
- [🧪 Testing](#-testing)  
- [🤝 Contributing](#-contributing)  
- [📜 License](#-license)  
- [📩 Contact](#-contact)  

---

## 🌟 Features  
✅ **AI-Powered Medical Consultations** - Users describe symptoms, and AI asks follow-up questions or provides a diagnosis.  
✅ **Secure Authentication** - User login and registration with encrypted passwords.  
✅ **Huggign Face API Integration**  
✅ **User-Friendly Interface** - Clean and responsive UI built with Bootstrap.  

---

## 🛠️ Prerequisites  
Before running this project, make sure you have:  
- **Python 3.8+**  
- **pip (Python package manager)**  
- **Flask framework**  
- **Google Generative AI SDK**  
- **SQLite** (for local database storage)  

---

## 💾 Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/palswayam5/CeraProject.git
cd CeraProject
```

### 2️⃣ Install Dependencies  
```bash
pip install -r requirements.txt
```

### 3️⃣ Set up the Google API Key  
This project requires a **Google API Key** for the Gemini AI model.  

- **Add it to a `.env` file** inside the project directory:  
  ```
   HF_API_TOKEN = your_api_key_here
  ```

---

## 🔧 Running the Application  

### 1️⃣ Start the Flask Application  
Run the Flask app using:  
```bash
python index.py
```
By default, the application will be available at:  
```
http://127.0.0.1:5000/
```

### 2️⃣ Login & Register  
- Open **http://127.0.0.1:5000/login** in your browser.  
- Register a new account or log in with existing credentials.  

### 3️⃣ Start a Medical Consultation  
- Enter your symptoms.  
- The AI will ask follow-up questions.  
- Once enough information is gathered, AI provides a possible diagnosis.  

---

## 📡 API Endpoints  

### 1️⃣ Authentication  
| Method | Endpoint  | Description |
|--------|----------|-------------|
| `POST` | `/login` | Log in a user |
| `POST` | `/register` | Register a new user |
| `GET` | `/logout` | Logout the user |

### 2️⃣ Consultation  
| Method | Endpoint  | Description |
|--------|----------|-------------|
| `GET` | `/` | Start a consultation session |
| `POST` | `/send_response` | Send user input and get AI response |

---

## 🤝 Contributing  
Contributions are **welcome**! Follow these steps to contribute:  

1️⃣ **Fork the repository**  
2️⃣ **Create a new branch**  
   ```bash
   git checkout -b feature-new-feature
   ```
3️⃣ **Commit and push your changes**  
   ```bash
   git commit -m "Added new feature"
   git push origin feature-new-feature
   ```
4️⃣ **Create a Pull Request**  

---

## 📩 Contact  
For questions or support, contact:  
- **GitHub:** [palswayam5](https://github.com/palswayam5)  
- **Email:** [your.email@example.com](mailto:palswayam5@gmail.com)  

---

🎉 **Enjoy using MediChat!** 🚀  
