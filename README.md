# Quizolve 🧠

**[Live Website 🚀](https://quizolve.onrender.com)** | **[Report a Bug 🐛](https://github.com/deepajaysolanki/quizolve/issues)**

Quizolve is an interactive, full-stack learning platform designed to create adaptive, engaging, and personalized educational quizzes. Built with a robust Django architecture and powered by AI, it empowers users to generate, configure, and complete highly customizable quizzes while tracking their educational progress.

---

## ✨ Core Features

* **AI Quiz Generation:** Real-time generation of contextual multiple-choice questions from topic keywords using the Groq API and Llama 3 models.
* **Custom User Authentication:** Secure custom session-based login and registration system for personalized user profiles and dashboard access.
* **Dynamic Quiz Engine:** Take interactive quizzes with real-time answer mapping, score calculation, and progress tracking.
* **Responsive UI/UX:** A fully mobile-optimized, custom-styled frontend featuring modern CSS animations (3D tilts, Aurora sweeps) and an intuitive navigation system.
* **Relational Database Engineering:** Efficiently manages complex data structures, including quiz configurations, question-choice relationships, and historical test scores.

---

## 🛠️ Tech Stack

* **Backend:** Python, Django, SQL
* **Frontend:** HTML/CSS/JavaScript
* **AI Integration:** Groq(Llama)
* **Deployment & Version Control:** Render, Git

---

## 🚀 Local Installation & Setup

If you want to run this project locally on your machine, follow these steps:

### 1. Clone the repository
```bash
git clone [https://github.com/DeepSolanki09/quizolve.git](https://github.com/DeepSolanki09/quizolve.git)
cd quizolve

### 2. Create a virtual environment
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up Environment Variables
Create a .env file in the root directory (make sure this is in your .gitignore) and add the following:

    DB_NAME = 'your_db_name'
    DB_USER = 'your_username'
    DB_PASSWORD = 'your_db_password' 
    DB_HOST = 'localhost'
    DB_PORT = '3306'

    SECRET_KEY=your_django_secret_key_here
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost
    GROQ_API_KEY=your_groq_api_key_here

### 5. Create a superuser (Admin)
python manage.py createsuperuser

### 6. Start the development server
python manage.py runserver

📁 Project Structure
quizolve/
│
├── core/                   # Main Django project settings & configuration
├── app/                    # Primary application handling quizzes & users
│   ├── migrations/         # Database migration files
│   ├── templates/          # HTML templates (base.html, index.html, etc.)
│   ├── models.py           # Database schema (Quiz, Question, Choice, etc.)
│   ├── views.py            # Backend logic and request routing
│   └── urls.py             # App-level URL routing
│
├── static/                 # Static assets
│   ├── css/                # Custom stylesheets (main.css, about.css)
│   ├── js/                 # Vanilla JavaScript files
│   └── images/             # Image assets
│
├── manage.py               # Django execution script
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

👨‍💻 Creator

Deep Solanki

Full-Stack Developer
Portfolio: https://deepsolanki.onrender.com
