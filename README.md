# 🧠 Notewise AI - Intelligent Study Assistant

Notewise AI is a full-stack intelligent study application that transforms PDF learning materials into interactive study aids. Using **Google Gemini AI**, it generates Flashcards, Quizzes, and "Arena Mode" application scenarios to help users master complex topics.

![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20|%20React%20|%20PostgreSQL-blue)

## 🚀 Features

-   **📄 PDF Ingestion:** Upload any study PDF; the AI extracts structure, topics, and concepts.
-   **🃏 Flashcards with SRS:** Uses the **Sm-2 Spaced Repetition Algorithm** to schedule reviews efficiently.
-   **📝 Dynamic Quizzes:** AI generates fresh multiple-choice questions on demand from your study material.
-   **⚔️ Application Arena:** A unique mode where the AI creates real-world scenarios and **grades your written solutions** (0-100) with specific feedback.
-   **📊 Dashboard:** Tracks mastery scores, due reviews, and study progress.

## 🛠️ Tech Stack

### Backend
-   **Framework:** Python FastAPI
-   **Database:** PostgreSQL (SQLAlchemy ORM)
-   **AI Engine:** Google Gemini Pro 2.0 (via `google.generativeai`)
-   **PDF Processing:** PyMuPDF (fitz)
-   **Auth:** OAuth2 with JWT Tokens

### Frontend
-   **Framework:** React (Vite)
-   **Styling:** CSS Modules (Dark Mode UI)
-   **State:** React Hooks

## 📦 Installation & Setup

### Prerequisites
-   Python 3.9+
-   Node.js & npm
-   PostgreSQL installed and running locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt