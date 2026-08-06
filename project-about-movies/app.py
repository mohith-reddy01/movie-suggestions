import os
from flask import Flask, render_template, request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)

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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_name = request.form.get('name', 'Guest').strip() or 'Guest'
        user_gender = request.form.get('gender', 'Prefer not to say').strip() or 'Prefer not to say'
        user_age_str = request.form.get('age', '0').strip()
        try:
            user_age = int(user_age_str)
        except ValueError:
            user_age = 0
        user_age = max(user_age, 0)
        user_category = request.form.get('category', 'Thriller').strip().capitalize()
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

    return render_template(
        'index.html',
        categories=movie_categories.keys(),
        movie_categories=movie_categories,
    )


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    user_name = request.form.get('name', 'Guest').strip() or 'Guest'
    user_gender = request.form.get('gender', 'Prefer not to say').strip() or 'Prefer not to say'
    user_age_str = request.form.get('age', '0').strip()
    try:
        user_age = int(user_age_str)
    except ValueError:
        user_age = 0
    user_age = max(user_age, 0)
    user_category = request.form.get('category', 'Thriller').strip().capitalize()
    continue_choice = request.form.get('continue', 'yes')
    user_feedback = request.form.get('feedback', '').strip()

    return render_template(
        'thanks.html',
        name=user_name,
        gender=user_gender,
        age=user_age,
        category=user_category,
        continue_choice=continue_choice,
        feedback=user_feedback,
    )


if __name__ == '__main__':
    app.run(debug=True)
