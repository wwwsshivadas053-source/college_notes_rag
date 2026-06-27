# 🎓 College Notes RAG Chatbot

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge\&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge\&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge\&logo=sqlite)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange?style=for-the-badge\&logo=google)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</p>

<p align="center">

### 📚 AI-Powered Study Assistant using Retrieval-Augmented Generation (RAG)

Upload lecture notes, textbooks, and study materials in PDF format, then ask natural language questions to receive context-aware answers powered by Google's Gemini AI and Retrieval-Augmented Generation.

</p>

---

# 📖 Overview

The **College Notes RAG Chatbot** is an AI-powered educational platform designed to help students interact intelligently with their study materials.

Instead of manually searching through hundreds of pages of lecture notes, students simply upload PDFs and ask questions in natural language. The application retrieves the most relevant sections using semantic search before generating accurate responses using **Google Gemini**.

If Gemini is unavailable, the system automatically falls back to local TF-IDF retrieval, ensuring uninterrupted functionality.

---

# ✨ Key Features

### 📄 PDF Knowledge Base

* Upload lecture notes
* Upload textbooks
* Upload assignments
* Automatic PDF text extraction
* Smart document chunking

---

### 🤖 AI Question Answering

* Retrieval-Augmented Generation (RAG)
* Gemini AI integration
* Context-aware answers
* Semantic search
* Citation from uploaded notes

---

### 🔍 Intelligent Retrieval

* Gemini Embeddings
* FAISS Vector Database
* TF-IDF fallback retrieval
* Per-user document indexing

---

### 👤 User Management

* User Registration
* Secure Login
* Flask-Login Authentication
* Role-Based Access Control

---

### 👨‍💼 Admin Dashboard

* Manage Users
* Manage Uploaded Notes
* View Feedback
* View Chat Logs
* Delete Documents
* Dashboard Analytics

---

### 💬 Chat Features

* Ask unlimited questions
* Contextual conversations
* Store chat history
* Feedback collection

---

# 🛠 Tech Stack

| Category        | Technology              |
| --------------- | ----------------------- |
| Backend         | Flask                   |
| Language        | Python                  |
| Database        | SQLite / PostgreSQL     |
| AI Model        | Google Gemini           |
| Embeddings      | Gemini Embeddings       |
| Vector Search   | FAISS                   |
| Local Retrieval | TF-IDF                  |
| Authentication  | Flask-Login             |
| PDF Processing  | PyMuPDF                 |
| Frontend        | HTML5, CSS3, JavaScript |
| Styling         | Tailwind CSS            |
| Deployment      | Render                  |

---

# 🧠 System Architecture

```
                User
                  │
                  ▼
         Upload PDF Notes
                  │
                  ▼
          PDF Text Extraction
             (PyMuPDF)
                  │
                  ▼
           Smart Chunking
                  │
                  ▼
       Generate Embeddings
      (Gemini Embeddings)
                  │
                  ▼
          Store in FAISS
          (or TF-IDF)
                  │
                  ▼
         User asks Question
                  │
                  ▼
      Retrieve Relevant Chunks
                  │
                  ▼
       Gemini AI Generation
                  │
                  ▼
          Intelligent Answer
```

---

# 📂 Project Structure

```
College-Notes-RAG/

│
├── app/
│   ├── admin.py
│   ├── auth.py
│   ├── chat.py
│   ├── main.py
│   ├── models.py
│   ├── pdf_service.py
│   ├── rag_service.py
│   │
│   ├── templates/
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
│
├── instance/
│
├── config.py
├── run.py
├── requirements.txt
├── requirements-faiss.txt
├── .env.example
├── README.md
└── PMD.md
```

---

# 📸 User Interface

## 🏠 Home Page

![Home](https://github.com/user-attachments/assets/181ba6b6-eae2-44cc-9041-2af3575bcdc9)

---

## 🔐 Login

![Login](https://github.com/user-attachments/assets/2ee1620c-307c-43a1-9e1a-0da9640dc516)

---

## 📄 Upload Notes

![Upload](https://github.com/user-attachments/assets/7dfd8795-6984-47ac-9710-bbded9df7b3e)

---

## 💬 AI Chat

![Chat](https://github.com/user-attachments/assets/2695940e-bf1f-4b72-93cf-0b80c2258950)

---

## 👨‍💼 Admin Dashboard

![Admin](https://github.com/user-attachments/assets/ed9f451c-31d4-4041-af4a-dfb8a04e3603)

---

## 👥 User Management

![Users](https://github.com/user-attachments/assets/eff282c0-3ca9-4d68-9778-72fd49c20127)

---

## ⭐ Feedback

![Feedback](https://github.com/user-attachments/assets/2ced98a9-0ece-459f-8045-234c5f306d7d)

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/college_notes_rag.git

cd college_notes_rag
```

---

## Create Virtual Environment

Windows

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

Linux/macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

Optional

```bash
pip install -r requirements-faiss.txt
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
SECRET_KEY=your_secret_key

GEMINI_API_KEY=your_api_key

GEMINI_MODEL=gemini-2.0-flash

GEMINI_EMBEDDING_MODEL=gemini-embedding-001

DATABASE_URL=
```

---

# ▶ Run Application

```bash
python run.py
```

Open

```
http://127.0.0.1:5000
```

---

# 🚀 Deployment (Render)

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn run:app
```

Environment Variables

```
SECRET_KEY

GEMINI_API_KEY

GEMINI_MODEL

GEMINI_EMBEDDING_MODEL

DATABASE_URL
```

---

# 🔒 Security

* API keys stored using environment variables
* Role-based authentication
* Password hashing
* Session management
* Secure file uploads
* SQLAlchemy ORM protection
* Production-ready configuration

---

# 📈 Future Enhancements

* Multi-PDF conversations
* OCR support
* Voice-based questioning
* Mobile responsive improvements
* Dark mode
* PDF summarization
* Citation highlighting
* Export chat history
* Multi-language support
* Docker deployment

---

# 👤 Author

## **Prajwal T.S**

### AI & Machine Learning Developer

**GitHub**

https://github.com/wwwsshivadas053-source

**LinkedIn**

https://www.linkedin.com/in/prajwal-t-s-354a57359

---

# ⭐ Support

If you found this project helpful:

🌟 Star this repository

🍴 Fork the repository 

💡 Share your feedback

---

# 📄 License

This project is licensed under the **MIT License**.

---

<p align="center">

Made with ❤️ by **Prajwal T.S**

</p>
