# Movie Suggestions & Recommendation Platform

A dynamic full-stack web application built with Python and Flask that delivers personalized movie recommendations based on user preferences and age ratings. The app features secure user authentication, persistent SQLite database storage, dynamic movie detail pages, feedback submission, and automated SMTP email notifications.

---

## 🔗 Project Links

- **Live Application:** [https://movie-suggestion2-production.up.railway.app/](https://movie-suggestion2-production.up.railway.app/)
- **GitHub Repository:** [https://github.com/mohith-reddy01/movie-suggestions.git](https://github.com/mohith-reddy01/movie-suggestions.git)

---

## ✨ Features

- 🔐 **User Authentication**: Secure user registration, password hashing (Werkzeug), session management, and login protection for member areas.
- 🎬 **Dynamic Movie Suggestions**: Explore curated recommendations across genres (Thriller, Comedy, Action, Romance, Sci-Fi, Drama, Animation).
- 🔞 **Age Rating Filtering**: Automatic content filtering ensuring age-appropriate recommendations based on user age input.
- 📄 **Movie Detail Pages**: Dedicated detail views with IMDb ratings, OTT streaming provider details, rental pricing, and synopsis.
- 💬 **User Feedback System**: Store user feedback submissions directly into the SQLite database.
- 📧 **SMTP Email Notifications**: Automated emails dispatched to admin on new user registrations and feedback submissions.
- 🚀 **Cloud Deployment**: Production-ready deployment configuration on Railway with Gunicorn.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, Werkzeug Security
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3 (Modern Dark Cinematic UI), Jinja2 Templates
- **Production Server**: Gunicorn
- **Deployment**: Railway

---

## 🚀 Getting Started Locally

### 1. Clone the Repository

```bash
git clone https://github.com/mohith-reddy01/movie-suggestions.git
cd movie-suggestions
```

### 2. Set Up a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)

Configure SMTP credentials if you wish to receive registration and feedback email notifications:

#### PowerShell:
```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "your-email@gmail.com"
$env:SMTP_PASSWORD = "your-16-char-app-password"
$env:ADMIN_EMAIL = "your-email@gmail.com"
$env:SECRET_KEY = "your-secret-key"
```

#### Bash (Linux/macOS):
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-16-char-app-password"
export ADMIN_EMAIL="your-email@gmail.com"
export SECRET_KEY="your-secret-key"
```

### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 📁 Project Structure

```text
movie-suggestions/
├── .github/
│   └── workflows/
│       └── pylint.yml          # GitHub Actions CI linting workflow
├── static/
│   ├── images/                 # SVG posters and visual assets
│   └── style.css               # Dark theme styles and responsive layout
├── templates/
│   ├── base.html               # Base Jinja2 layout with navigation
│   ├── index.html              # Main dashboard with movie recommendations
│   ├── login.html              # User login form
│   ├── register.html           # User registration form
│   ├── movie.html              # Individual movie detail view
│   ├── result.html             # Filtered recommendation results
│   └── thanks.html             # Feedback confirmation page
├── .gitignore                  # Git ignore rules
├── .pylintrc                   # Pylint configuration
├── app.py                      # Core Flask application and database logic
├── index.html                  # GitHub Pages redirect entry point
├── requirements.txt            # Python dependencies
├── run_ngrok.py                # Optional ngrok tunneling utility
└── README.md                   # Documentation
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
