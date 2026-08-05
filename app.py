import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret')

DB_PATH = os.path.join(app.root_path, 'users.db')

movie_categories = {
    "Thriller": ["Inception", "Gone Girl", "Se7en"],
    "Comedy": ["Superbad", "Step Brothers", "The Grand Budapest Hotel"],
    "Action": ["Mad Max: Fury Road", "John Wick", "The Dark Knight"],
    "Romance": ["The Notebook", "Pride & Prejudice", "La La Land"],
    "Sci-Fi": ["Interstellar", "The Matrix", "Blade Runner 2049"],
    "Drama": ["The Shawshank Redemption", "Forrest Gump", "The Social Network"],
    "Animation": ["Toy Story", "Spider-Man: Into the Spider-Verse", "Coco"]}

movie_ratings = {
    "Gone Girl": 18,
    "Se7en": 18,
    "John Wick": 18,
    "Mad Max: Fury Road": 18,
}

movie_posters = {
    "Inception": "https://via.placeholder.com/220x330/283593/ffffff?text=Inception",
    "Gone Girl": "https://via.placeholder.com/220x330/6a1b9a/ffffff?text=Gone+Girl",
    "Se7en": "https://via.placeholder.com/220x330/37474f/ffffff?text=Se7en",
    "Superbad": "https://via.placeholder.com/220x330/ff7043/ffffff?text=Superbad",
    "Step Brothers": "https://via.placeholder.com/220x330/00897b/ffffff?text=Step+Brothers",
    "The Grand Budapest Hotel": "https://via.placeholder.com/220x330/d81b60/ffffff?text=Grand+Budapest",
    "Mad Max: Fury Road": "https://via.placeholder.com/220x330/f4511e/ffffff?text=Mad+Max",
    "John Wick": "https://via.placeholder.com/220x330/1e88e5/ffffff?text=John+Wick",
    "The Dark Knight": "https://via.placeholder.com/220x330/212121/ffffff?text=Dark+Knight",
    "The Notebook": "https://via.placeholder.com/220x330/ab47bc/ffffff?text=The+Notebook",
    "Pride & Prejudice": "https://via.placeholder.com/220x330/546e7a/ffffff?text=Pride+%26+Prejudice",
    "La La Land": "https://via.placeholder.com/220x330/4caf50/ffffff?text=La+La+Land",
    "Interstellar": "https://via.placeholder.com/220x330/3949ab/ffffff?text=Interstellar",
    "The Matrix": "https://via.placeholder.com/220x330/2e7d32/ffffff?text=The+Matrix",
    "Blade Runner 2049": "https://via.placeholder.com/220x330/ef6c00/ffffff?text=Blade+Runner+2049",
    "The Shawshank Redemption": "https://via.placeholder.com/220x330/6d4c41/ffffff?text=Shawshank",
    "Forrest Gump": "https://via.placeholder.com/220x330/8e24aa/ffffff?text=Forrest+Gump",
    "The Social Network": "https://via.placeholder.com/220x330/039be5/ffffff?text=Social+Network",
    "Toy Story": "https://via.placeholder.com/220x330/ffca28/333333?text=Toy+Story",
    "Spider-Man: Into the Spider-Verse": "https://via.placeholder.com/220x330/ec407a/ffffff?text=Spider-Verse",
    "Coco": "https://via.placeholder.com/220x330/f06292/ffffff?text=Coco",
}

# Detailed metadata for movies
movie_details = {
    "Inception": {"imdb": 8.8, "cost": "$3.99", "ott": "Netflix", "category": "Thriller", "description": "A thief who steals corporate secrets through dream-sharing technology."},
    "Gone Girl": {"imdb": 8.1, "cost": "$2.99", "ott": "Prime Video", "category": "Thriller", "description": "A man becomes the prime suspect in the disappearance of his wife."},
    "Se7en": {"imdb": 8.6, "cost": "$2.99", "ott": "HBO Max", "category": "Thriller", "description": "Two detectives hunt a serial killer who bases his crimes on the seven deadly sins."},
    "Superbad": {"imdb": 7.6, "cost": "$1.99", "ott": "Paramount+", "category": "Comedy", "description": "Two co-dependent high school seniors try to enjoy their remaining time together."},
    "Step Brothers": {"imdb": 6.9, "cost": "$1.99", "ott": "Hulu", "category": "Comedy", "description": "Two immature adults are forced to live together as step brothers."},
    "The Grand Budapest Hotel": {"imdb": 8.1, "cost": "$3.99", "ott": "Hulu", "category": "Comedy", "description": "A whimsical story of a legendary concierge and his protégé."},
    "Mad Max: Fury Road": {"imdb": 8.1, "cost": "$3.99", "ott": "HBO Max", "category": "Action", "description": "Post-apocalyptic action on a high-speed chase across the desert."},
    "John Wick": {"imdb": 7.4, "cost": "$2.99", "ott": "Peacock", "category": "Action", "description": "An ex-hitman comes out of retirement to track down the gangsters who wronged him."},
    "The Dark Knight": {"imdb": 9.0, "cost": "$3.99", "ott": "Max", "category": "Action", "description": "Batman faces the Joker, a criminal mastermind who plunges Gotham into chaos."},
    "The Notebook": {"imdb": 7.8, "cost": "$2.99", "ott": "Netflix", "category": "Romance", "description": "A touching love story told from memory."},
    "La La Land": {"imdb": 8.0, "cost": "$2.99", "ott": "Prime Video", "category": "Romance", "description": "A jazz musician and an aspiring actress fall in love in Los Angeles."},
    "Interstellar": {"imdb": 8.6, "cost": "$3.99", "ott": "Paramount+", "category": "Sci-Fi", "description": "A team travels through a wormhole in search of a new home for humanity."},
}


def slugify(title: str) -> str:
    return (
        title.lower().replace("&", "and").replace(" ", "-").replace(":", "").replace("'", "")
    )


def title_from_slug(slug: str) -> str | None:
    for t in movie_posters.keys():
        if slugify(t) == slug:
            return t
    return None


def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )
        # feedback table to store user feedback submissions
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                user_gender TEXT,
                user_age INTEGER,
                category TEXT,
                continue_choice TEXT,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_user_by_username(username):
    with get_db_connection() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,),
        ).fetchone()


def create_user(username, display_name, password):
    password_hash = generate_password_hash(password)
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)',
            (username, display_name, password_hash),
        )
        conn.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped_view


# Ensure DB tables exist (CREATE TABLE IF NOT EXISTS is idempotent)
init_db()


def save_feedback(user_name, user_gender, user_age, category, continue_choice, feedback_text):
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO feedback (user_name, user_gender, user_age, category, continue_choice, feedback) VALUES (?, ?, ?, ?, ?, ?)',
            (user_name, user_gender, user_age, category, continue_choice, feedback_text),
        )
        conn.commit()


@app.context_processor
def inject_user():
    return {
        'current_user': session.get('display_name') or session.get('username'),
        'movie_posters': movie_posters,
    }


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        display_name = request.form.get('display_name', '').strip() or username
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            error = 'Please choose a username and a password.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif get_user_by_username(username) is not None:
            error = 'That username is already taken.'
        else:
            create_user(username, display_name, password)
            user = get_user_by_username(username)
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['display_name'] = user['display_name']
            return redirect(url_for('index'))

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = get_user_by_username(username)

        if user is None:
            error = 'Invalid username or password.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Invalid username or password.'
        else:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['display_name'] = user['display_name']
            return redirect(url_for('index'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        user_name = request.form.get('name', session.get('display_name', 'Guest')).strip() or 'Guest'
        user_gender = request.form.get('gender', 'Prefer not to say').strip() or 'Prefer not to say'
        user_age_str = request.form.get('age', '0').strip()
        try:
            user_age = int(user_age_str)
        except ValueError:
            user_age = 0
        user_age = max(user_age, 0)
        category_input = request.form.get('category', 'Thriller') or 'Thriller'
        category_input = category_input.strip()
        user_category = category_input if category_input in movie_categories else 'Thriller'
        continue_choice = request.form.get('continue', 'yes')

        movies = movie_categories.get(user_category, [])
        filtered_movies = [movie for movie in movies if user_age >= movie_ratings.get(movie, 0)]
        restriction_warning = None
        if user_age < 18 and len(filtered_movies) < len(movies):
            restriction_warning = 'Some 18+ movies were removed because you are under 18.'

        if user_age < 18:
            category_message = (
                f"Movies in {user_category} suitable for under 18:" if filtered_movies else f"No movies available in {user_category} for your age."
            )
        else:
            category_message = (
                f"Movies in {user_category}:" if filtered_movies else f"No movies found in category: {user_category}"
            )

        return render_template(
            'result.html',
            name=user_name,
            gender=user_gender,
            age=user_age,
            category=user_category,
            continue_choice=continue_choice,
            movies=filtered_movies,
            category_message=category_message,
            restriction_warning=restriction_warning,
        )

    featured_posters = dict(list(movie_posters.items())[:9])
    return render_template(
        'index.html',
        categories=movie_categories.keys(),
        featured_posters=featured_posters,
    )


@app.route('/submit-feedback', methods=['POST'])
@login_required
def submit_feedback():
    user_name = request.form.get('name', session.get('display_name', 'Guest')).strip() or 'Guest'
    user_gender = request.form.get('gender', 'Prefer not to say').strip() or 'Prefer not to say'
    user_age_str = request.form.get('age', '0').strip()
    try:
        user_age = int(user_age_str)
    except ValueError:
        user_age = 0
    user_age = max(user_age, 0)
    category_input = request.form.get('category', 'Thriller') or 'Thriller'
    category_input = category_input.strip()
    user_category = category_input if category_input in movie_categories else 'Thriller'
    continue_choice = request.form.get('continue', 'yes')
    user_feedback = request.form.get('feedback', '').strip()

    # persist feedback to the database
    if user_feedback:
        try:
            save_feedback(user_name, user_gender, user_age, user_category, continue_choice, user_feedback)
        except Exception:
            # ignore DB errors for now but continue to thanks page
            pass

    return render_template(
        'thanks.html',
        name=user_name,
        gender=user_gender,
        age=user_age,
        category=user_category,
        continue_choice=continue_choice,
        feedback=user_feedback,
    )



@app.route('/movie/<slug>')
@login_required
def movie_detail(slug):
    title = title_from_slug(slug)
    if title is None:
        return redirect(url_for('index'))
    details = movie_details.get(title, {})
    poster = movie_posters.get(title)
    return render_template('movie.html', title=title, details=details, poster=poster)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
