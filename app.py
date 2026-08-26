"""Movie suggestions Flask application with user authentication and feedback system."""
import os
import sqlite3
import smtplib
import ssl
from email.message import EmailMessage
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret')

DB_PATH = os.path.join(app.root_path, 'users.db')

movie_categories = {
    "Thriller": [
        "Inception",
        "Gone Girl",
        "Se7en",
        "Fight Club",
        "Shutter Island",
        "Prisoners",
        "Zodiac",
        "The Girl with the Dragon Tattoo",
        "Memento",
        "Sicario",
    ],
    "Comedy": [
        "Superbad",
        "Step Brothers",
        "The Grand Budapest Hotel",
        "Anchorman",
        "Bridesmaids",
        "The Hangover",
        "Mean Girls",
        "Airplane!",
        "Groundhog Day",
        "Hot Fuzz",
    ],
    "Action": [
        "Mad Max: Fury Road",
        "John Wick",
        "The Dark Knight",
        "Gladiator",
        "Die Hard",
        "The Bourne Identity",
        "Casino Royale",
        "Mission: Impossible - Fallout",
        "The Matrix",
        "Terminator 2: Judgment Day",
    ],
    "Romance": [
        "The Notebook",
        "Pride & Prejudice",
        "La La Land",
        "Before Sunrise",
        "Eternal Sunshine of the Spotless Mind",
        "Romeo + Juliet",
        "A Walk to Remember",
        "(500) Days of Summer",
        "Silver Linings Playbook",
        "Titanic",
    ],
    "Sci-Fi": [
        "Interstellar",
        "The Matrix",
        "Blade Runner 2049",
        "Arrival",
        "Ex Machina",
        "Alien",
        "The Martian",
        "Minority Report",
        "Her",
        "Looper",
    ],
    "Drama": [
        "The Shawshank Redemption",
        "Forrest Gump",
        "The Social Network",
        "Schindler's List",
        "The Godfather",
        "American Beauty",
        "The Pursuit of Happyness",
        "A Beautiful Mind",
        "Spotlight",
        "Fight Club",
    ],
    "Animation": [
        "Toy Story",
        "Spider-Man: Into the Spider-Verse",
        "Coco",
        "Spirited Away",
        "Up",
        "WALL-E",
        "Finding Nemo",
        "The Lion King",
        "Zootopia",
        "How to Train Your Dragon",
    ],
}

movie_ratings = {
    "Gone Girl": 18,
    "Se7en": 18,
    "John Wick": 18,
    "Mad Max: Fury Road": 18,
}

movie_posters = {
    "(500) Days of Summer": "https://upload.wikimedia.org/wikipedia/en/d/d1/Five_hundred_days_of_summer.jpg",
    "A Beautiful Mind": "https://upload.wikimedia.org/wikipedia/en/b/b8/A_Beautiful_Mind_Poster.jpg",
    "A Walk to Remember": "https://upload.wikimedia.org/wikipedia/en/d/dc/A_Walk_to_Remember_Poster.jpg",
    "Airplane": "https://upload.wikimedia.org/wikipedia/en/2/21/Airplane%21_%281980_film%29.jpg",
    "Airplane!": "https://upload.wikimedia.org/wikipedia/en/2/21/Airplane%21_%281980_film%29.jpg",
    "Alien": "https://upload.wikimedia.org/wikipedia/en/c/c3/Alien_movie_poster.jpg",
    "American Beauty": "https://upload.wikimedia.org/wikipedia/en/9/9a/American_Beauty_1999_film_poster.jpg",
    "Anchorman": "https://upload.wikimedia.org/wikipedia/en/6/64/Movie_poster_Anchorman_The_Legend_of_Ron_Burgundy.jpg",
    "Arrival": "https://upload.wikimedia.org/wikipedia/en/d/df/Arrival%2C_Movie_Poster.jpg",
    "Before Sunrise": "https://upload.wikimedia.org/wikipedia/en/d/da/Before_Sunrise_poster.jpg",
    "Blade Runner 2049": "https://upload.wikimedia.org/wikipedia/en/9/9b/Blade_Runner_2049_poster.png",
    "Bridesmaids": "https://upload.wikimedia.org/wikipedia/en/d/df/BridesmaidsPoster.jpg",
    "Casino Royale": "https://upload.wikimedia.org/wikipedia/en/8/82/Casino_Royale_%282006_film_poster%29.jpg",
    "Coco": "https://upload.wikimedia.org/wikipedia/en/9/98/Coco_%282017_film%29_poster.jpg",
    "Die Hard": "https://upload.wikimedia.org/wikipedia/en/c/ca/Die_Hard_%281988_film%29_poster.jpg",
    "Eternal Sunshine of the Spotless Mind": "https://upload.wikimedia.org/wikipedia/en/a/a4/Eternal_Sunshine_of_the_Spotless_Mind.png",
    "Ex Machina": "https://upload.wikimedia.org/wikipedia/en/b/ba/Ex-machina-uk-poster.jpg",
    "Fight Club": "https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_poster.jpg",
    "Finding Nemo": "https://upload.wikimedia.org/wikipedia/en/2/29/Finding_Nemo.jpg",
    "Forrest Gump": "https://upload.wikimedia.org/wikipedia/en/6/67/Forrest_Gump_poster.jpg",
    "Gladiator": "https://upload.wikimedia.org/wikipedia/en/f/fb/Gladiator_%282000_film_poster%29.png",
    "Gone Girl": "https://upload.wikimedia.org/wikipedia/en/0/05/Gone_Girl_Poster.jpg",
    "Groundhog Day": "https://upload.wikimedia.org/wikipedia/en/b/b1/Groundhog_Day_%28movie_poster%29.jpg",
    "Her": "https://upload.wikimedia.org/wikipedia/en/4/44/Her2013Poster.jpg",
    "Hot Fuzz": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c9/HotFuzzUKposter.jpg/330px-HotFuzzUKposter.jpg",
    "How to Train Your Dragon": "https://upload.wikimedia.org/wikipedia/en/9/99/How_to_Train_Your_Dragon_Poster.jpg",
    "Inception": "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg",
    "Interstellar": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
    "John Wick": "https://upload.wikimedia.org/wikipedia/en/9/98/John_Wick_TeaserPoster.jpg",
    "La La Land": "https://upload.wikimedia.org/wikipedia/en/a/ab/La_La_Land_%28film%29.png",
    "Looper": "https://upload.wikimedia.org/wikipedia/en/0/0a/Looper_poster.jpg",
    "Mad Max: Fury Road": "https://upload.wikimedia.org/wikipedia/en/6/6e/Mad_Max_Fury_Road.jpg",
    "Mean Girls": "https://upload.wikimedia.org/wikipedia/en/a/ac/Mean_Girls_film_poster.png",
    "Memento": "https://upload.wikimedia.org/wikipedia/en/c/c7/Memento_poster.jpg",
    "Minority Report": "https://upload.wikimedia.org/wikipedia/en/4/44/Minority_Report_Poster.jpg",
    "Mission: Impossible - Fallout": "https://upload.wikimedia.org/wikipedia/en/f/ff/MI_%E2%80%93_Fallout.jpg",
    "Pride & Prejudice": "https://upload.wikimedia.org/wikipedia/en/0/03/Prideandprejudiceposter.jpg",
    "Prisoners": "https://upload.wikimedia.org/wikipedia/en/6/63/Prisoners2013Poster.jpg",
    "Romeo + Juliet": "https://upload.wikimedia.org/wikipedia/en/b/b4/William_shakespeares_romeo_and_juliet_movie_poster.jpg",
    "Schindler's List": "https://upload.wikimedia.org/wikipedia/en/3/38/Schindler%27s_List_movie.jpg",
    "Se7en": "https://upload.wikimedia.org/wikipedia/en/6/68/Seven_%28movie%29_poster.jpg",
    "Shutter Island": "https://upload.wikimedia.org/wikipedia/en/7/76/Shutterislandposter.jpg",
    "Sicario": "https://upload.wikimedia.org/wikipedia/en/4/4b/Sicario_poster.jpg",
    "Silver Linings Playbook": "https://upload.wikimedia.org/wikipedia/en/9/9a/Silver_Linings_Playbook_Poster.jpg",
    "Spider-Man: Into the Spider-Verse": "https://upload.wikimedia.org/wikipedia/en/f/fa/Spider-Man_Into_the_Spider-Verse_poster.png",
    "Spirited Away": "https://upload.wikimedia.org/wikipedia/en/d/db/Spirited_Away_Japanese_poster.png",
    "Spotlight": "https://upload.wikimedia.org/wikipedia/en/f/f3/Spotlight_%28film%29_poster.jpg",
    "Step Brothers": "https://upload.wikimedia.org/wikipedia/en/d/d9/StepbrothersMP08.jpg",
    "Superbad": "https://upload.wikimedia.org/wikipedia/en/8/8b/Superbad_Poster.png",
    "Terminator 2: Judgment Day": "https://upload.wikimedia.org/wikipedia/en/5/5e/Terminator_2-Judgment_Day.png",
    "The Bourne Identity": "https://upload.wikimedia.org/wikipedia/en/4/49/The_Bourne_Identity_%282002%29_US_poster.jpg",
    "The Dark Knight": "https://upload.wikimedia.org/wikipedia/en/1/1c/The_Dark_Knight_%282008_film%29.jpg",
    "The Girl with the Dragon Tattoo": "https://upload.wikimedia.org/wikipedia/en/8/80/The_Girl_with_the_Dragon_Tattoo_Poster.jpg",
    "The Godfather": "https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_ver1.jpg",
    "The Grand Budapest Hotel": "https://upload.wikimedia.org/wikipedia/en/1/1c/The_Grand_Budapest_Hotel.png",
    "The Hangover": "https://upload.wikimedia.org/wikipedia/en/b/b9/Hangoverposter09.jpg",
    "The Lion King": "https://upload.wikimedia.org/wikipedia/en/3/3d/The_Lion_King_poster.jpg",
    "The Martian": "https://upload.wikimedia.org/wikipedia/en/c/cd/The_Martian_film_poster.jpg",
    "The Matrix": "https://upload.wikimedia.org/wikipedia/en/d/db/The_Matrix.png",
    "The Notebook": "https://upload.wikimedia.org/wikipedia/en/8/86/Posternotebook.jpg",
    "The Pursuit of Happyness": "https://upload.wikimedia.org/wikipedia/en/8/81/Poster-pursuithappyness.jpg",
    "The Shawshank Redemption": "https://upload.wikimedia.org/wikipedia/en/8/81/ShawshankRedemptionMoviePoster.jpg",
    "The Social Network": "https://upload.wikimedia.org/wikipedia/en/8/8c/The_Social_Network_film_poster.png",
    "Titanic": "https://upload.wikimedia.org/wikipedia/en/1/18/Titanic_%281997_film%29_poster.png",
    "Toy Story": "https://upload.wikimedia.org/wikipedia/en/1/13/Toy_Story.jpg",
    "Up": "https://upload.wikimedia.org/wikipedia/en/0/05/Up_%282009_film%29.jpg",
    "WALL-E": "https://upload.wikimedia.org/wikipedia/en/4/4c/WALL-E_poster.jpg",
    "Zodiac": "https://upload.wikimedia.org/wikipedia/en/3/3a/Zodiac2007Poster.jpg",
    "Zootopia": "https://upload.wikimedia.org/wikipedia/en/9/96/Zootopia_%28movie_poster%29.jpg",
}

# Detailed metadata for movies
movie_details = {
    "(500) Days of Summer": {"imdb": 7.7, "cost": "$1.99", "ott": "Hulu", "category": "Romance", "description": "A nonlinear story of a failed relationship and the expectations of love."},
    "A Beautiful Mind": {"imdb": 8.2, "cost": "$2.99", "ott": "Prime Video", "category": "Drama", "description": "The story of John Nash and his struggles with schizophrenia and genius."},
    "A Walk to Remember": {"imdb": 7.4, "cost": "$1.99", "ott": "Netflix", "category": "Romance", "description": "A popular teenager falls for a quiet, bookish girl with a secret."},
    "Airplane": {"imdb": 7.7, "cost": "$1.99", "ott": "Prime Video", "category": "Comedy", "description": "A spoof of disaster films centered on a troubled airplane flight."},
    "Airplane!": {"imdb": 7.7, "cost": "$1.99", "ott": "Prime Video", "category": "Comedy", "description": "A spoof of disaster films centered on a troubled airplane flight."},
    "Alien": {"imdb": 8.4, "cost": "$2.99", "ott": "Hulu", "category": "Sci-Fi", "description": "The crew of a commercial space tug encounter a deadly lifeform."},
    "American Beauty": {"imdb": 8.3, "cost": "$2.99", "ott": "Hulu", "category": "Drama", "description": "A man experiences a midlife crisis and seeks meaning in suburban life."},
    "Anchorman": {"imdb": 7.2, "cost": "$1.99", "ott": "Paramount+", "category": "Comedy", "description": "The exploits of a 1970s news anchorman and his news team."},
    "Arrival": {"imdb": 7.9, "cost": "$2.99", "ott": "HBO Max", "category": "Sci-Fi", "description": "A linguist tries to communicate with alien visitors to learn their purpose."},
    "Before Sunrise": {"imdb": 8.1, "cost": "$2.99", "ott": "Criterion", "category": "Romance", "description": "Two strangers meet on a train and spend a night in Vienna."},
    "Blade Runner 2049": {"imdb": 8.0, "cost": "$3.99", "ott": "HBO Max", "category": "Sci-Fi", "description": "A young blade runner's discovery of a long-buried secret leads him to track down former blade runner Rick Deckard."},
    "Bridesmaids": {"imdb": 6.8, "cost": "$1.99", "ott": "Hulu", "category": "Comedy", "description": "Competition between the maid of honor and a bridesmaid over who is the bride's best friend."},
    "Casino Royale": {"imdb": 8.0, "cost": "$2.99", "ott": "Prime Video", "category": "Action", "description": "James Bond's first mission as 007 pits him against a private banker funding terrorists."},
    "Coco": {"imdb": 8.4, "cost": "$2.99", "ott": "Disney+", "category": "Animation", "description": "Aspiring musician Miguel enters the Land of the Dead to find his great-great-grandfather, a legendary singer."},
    "Die Hard": {"imdb": 8.2, "cost": "$2.99", "ott": "Hulu", "category": "Action", "description": "An NYPD officer tries to save hostages during a Christmas party takeover."},
    "Eternal Sunshine of the Spotless Mind": {"imdb": 8.3, "cost": "$2.99", "ott": "Netflix", "category": "Romance", "description": "A couple undergoes a procedure to erase memories of each other."},
    "Ex Machina": {"imdb": 7.7, "cost": "$2.99", "ott": "Netflix", "category": "Sci-Fi", "description": "A programmer is invited to administer the Turing test to an intelligent robot."},
    "Fight Club": {"imdb": 8.8, "cost": "$2.99", "ott": "Hulu", "category": "Thriller", "description": "An insomniac office worker crosses paths with a devil-may-care soapmaker."},
    "Finding Nemo": {"imdb": 8.1, "cost": "$2.99", "ott": "Disney+", "category": "Animation", "description": "A father's journey to find his missing son across the ocean."},
    "Forrest Gump": {"imdb": 8.8, "cost": "$3.99", "ott": "Paramount+", "category": "Drama", "description": "The history of the United States from the 1950s to the '70s unfolds through the perspective of an Alabama man with an IQ of 75."},
    "Gladiator": {"imdb": 8.5, "cost": "$3.99", "ott": "HBO Max", "category": "Action", "description": "A former Roman general seeks revenge for the murder of his family."},
    "Gone Girl": {"imdb": 8.1, "cost": "$2.99", "ott": "Prime Video", "category": "Thriller", "description": "A man becomes the prime suspect in the disappearance of his wife."},
    "Groundhog Day": {"imdb": 8.0, "cost": "$2.99", "ott": "Hulu", "category": "Comedy", "description": "A weatherman finds himself living the same day repeatedly."},
    "Her": {"imdb": 8.0, "cost": "$2.99", "ott": "Netflix", "category": "Sci-Fi", "description": "A man develops a relationship with an intelligent operating system."},
    "Hot Fuzz": {"imdb": 7.8, "cost": "$1.99", "ott": "Netflix", "category": "Comedy", "description": "A top London cop is transferred to a seemingly idyllic village with a dark secret."},
    "How to Train Your Dragon": {"imdb": 8.1, "cost": "$2.99", "ott": "Hulu", "category": "Animation", "description": "A young Viking befriends a dragon and learns they are not the enemy."},
    "Inception": {"imdb": 8.8, "cost": "$3.99", "ott": "Netflix", "category": "Thriller", "description": "A thief who steals corporate secrets through dream-sharing technology."},
    "Interstellar": {"imdb": 8.6, "cost": "$3.99", "ott": "Paramount+", "category": "Sci-Fi", "description": "A team travels through a wormhole in search of a new home for humanity."},
    "John Wick": {"imdb": 7.4, "cost": "$2.99", "ott": "Peacock", "category": "Action", "description": "An ex-hitman comes out of retirement to track down the gangsters who wronged him."},
    "La La Land": {"imdb": 8.0, "cost": "$2.99", "ott": "Prime Video", "category": "Romance", "description": "A jazz musician and an aspiring actress fall in love in Los Angeles."},
    "Looper": {"imdb": 7.4, "cost": "$2.99", "ott": "Hulu", "category": "Sci-Fi", "description": "A hitman faced with a future version of himself must make a choice."},
    "Mad Max: Fury Road": {"imdb": 8.1, "cost": "$3.99", "ott": "HBO Max", "category": "Action", "description": "Post-apocalyptic action on a high-speed chase across the desert."},
    "Mean Girls": {"imdb": 7.0, "cost": "$1.99", "ott": "Netflix", "category": "Comedy", "description": "A naive teenager navigates the social jungle of a modern high school."},
    "Memento": {"imdb": 8.4, "cost": "$2.99", "ott": "HBO Max", "category": "Thriller", "description": "A man with short-term memory loss attempts to track down his wife's killer."},
    "Minority Report": {"imdb": 7.6, "cost": "$2.99", "ott": "HBO Max", "category": "Sci-Fi", "description": "A cop in a future where crimes are stopped before they happen goes on the run."},
    "Mission: Impossible - Fallout": {"imdb": 7.7, "cost": "$3.99", "ott": "Paramount+", "category": "Action", "description": "Ethan Hunt and his team race against time after a mission goes wrong."},
    "Pride & Prejudice": {"imdb": 7.8, "cost": "$2.99", "ott": "Netflix", "category": "Romance", "description": "Sparks fly when spirited Elizabeth Bennet meets single, rich, and proud Mr. Darcy."},
    "Prisoners": {"imdb": 8.1, "cost": "$2.99", "ott": "Prime Video", "category": "Thriller", "description": "A father takes matters into his own hands after his daughter disappears."},
    "Romeo + Juliet": {"imdb": 6.7, "cost": "$1.99", "ott": "Hulu", "category": "Romance", "description": "A modern take on Shakespeare's tragic romance."},
    "Schindler's List": {"imdb": 8.9, "cost": "$3.99", "ott": "HBO Max", "category": "Drama", "description": "The true story of Oskar Schindler who saved many Jews during WWII."},
    "Se7en": {"imdb": 8.6, "cost": "$2.99", "ott": "HBO Max", "category": "Thriller", "description": "Two detectives hunt a serial killer who bases his crimes on the seven deadly sins."},
    "Shutter Island": {"imdb": 8.1, "cost": "$2.99", "ott": "Netflix", "category": "Thriller", "description": "U.S. Marshals investigate a psychiatric facility on an isolated island."},
    "Sicario": {"imdb": 7.6, "cost": "$2.99", "ott": "Netflix", "category": "Thriller", "description": "An FBI agent is enlisted in a government task force to aid in the escalating war against drugs."},
    "Silver Linings Playbook": {"imdb": 7.7, "cost": "$2.99", "ott": "Netflix", "category": "Romance", "description": "Two troubled people form an unlikely bond while trying to rebuild their lives."},
    "Spider-Man: Into the Spider-Verse": {"imdb": 8.4, "cost": "$3.99", "ott": "Netflix", "category": "Animation", "description": "Teen Miles Morales becomes the new Spider-Man and joins other Spider-Heroes from alternate universes."},
    "Spirited Away": {"imdb": 8.6, "cost": "$2.99", "ott": "HBO Max", "category": "Animation", "description": "A young girl enters a world of spirits and must find a way to save her parents."},
    "Spotlight": {"imdb": 8.1, "cost": "$2.99", "ott": "HBO Max", "category": "Drama", "description": "The true story of the Boston Globe's investigation into child abuse in the Catholic Church."},
    "Step Brothers": {"imdb": 6.9, "cost": "$1.99", "ott": "Hulu", "category": "Comedy", "description": "Two immature adults are forced to live together as step brothers."},
    "Superbad": {"imdb": 7.6, "cost": "$1.99", "ott": "Paramount+", "category": "Comedy", "description": "Two co-dependent high school seniors try to enjoy their remaining time together."},
    "Terminator 2: Judgment Day": {"imdb": 8.5, "cost": "$3.99", "ott": "HBO Max", "category": "Action", "description": "A cyborg protects a young boy who will lead humanity's fight against machines."},
    "The Bourne Identity": {"imdb": 7.9, "cost": "$2.99", "ott": "Netflix", "category": "Action", "description": "A man with amnesia tries to discover his true identity while being pursued."},
    "The Dark Knight": {"imdb": 9.0, "cost": "$3.99", "ott": "Max", "category": "Action", "description": "Batman faces the Joker, a criminal mastermind who plunges Gotham into chaos."},
    "The Girl with the Dragon Tattoo": {"imdb": 7.8, "cost": "$2.99", "ott": "Netflix", "category": "Thriller", "description": "Journalist Mikael Blomkvist is aided in his search for a woman who has been missing for forty years by young hacker Lisbeth Salander."},
    "The Godfather": {"imdb": 9.2, "cost": "$3.99", "ott": "Paramount+", "category": "Drama", "description": "The aging patriarch of an organized crime dynasty transfers control to his son."},
    "The Grand Budapest Hotel": {"imdb": 8.1, "cost": "$3.99", "ott": "Hulu", "category": "Comedy", "description": "A whimsical story of a legendary concierge and his protégé."},
    "The Hangover": {"imdb": 7.7, "cost": "$1.99", "ott": "HBO Max", "category": "Comedy", "description": "Three buddies wake up from a bachelor party in Las Vegas with no memory."},
    "The Lion King": {"imdb": 8.5, "cost": "$2.99", "ott": "Disney+", "category": "Animation", "description": "A young lion prince flees his kingdom only to learn the true meaning of responsibility and bravery."},
    "The Martian": {"imdb": 8.0, "cost": "$2.99", "ott": "Prime Video", "category": "Sci-Fi", "description": "An astronaut struggles to survive alone on Mars after being left behind."},
    "The Matrix": {"imdb": 8.7, "cost": "$3.99", "ott": "HBO Max", "category": "Action", "description": "A computer hacker learns about the true nature of reality and his role in the war against its controllers."},
    "The Notebook": {"imdb": 7.8, "cost": "$2.99", "ott": "Netflix", "category": "Romance", "description": "A touching love story told from memory."},
    "The Pursuit of Happyness": {"imdb": 8.0, "cost": "$2.99", "ott": "Netflix", "category": "Drama", "description": "A struggling salesman takes custody of his son as he begins a life-changing professional career."},
    "The Shawshank Redemption": {"imdb": 9.3, "cost": "$3.99", "ott": "HBO Max", "category": "Drama", "description": "A banker convicted of uxoricide forms a friendship over a quarter of a century with a hardened convict."},
    "The Social Network": {"imdb": 8.1, "cost": "$2.99", "ott": "Netflix", "category": "Drama", "description": "The story of the creation of the social networking website Facebook and the resulting lawsuits."},
    "Titanic": {"imdb": 7.8, "cost": "$3.99", "ott": "Paramount+", "category": "Romance", "description": "A love story unfolds aboard the ill-fated RMS Titanic."},
    "Toy Story": {"imdb": 8.3, "cost": "$2.99", "ott": "Disney+", "category": "Animation", "description": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room."},
    "Up": {"imdb": 8.2, "cost": "$2.99", "ott": "Disney+", "category": "Animation", "description": "An elderly man ties thousands of balloons to his house to see the wilds of South America."},
    "WALL-E": {"imdb": 8.4, "cost": "$2.99", "ott": "Disney+", "category": "Animation", "description": "A waste-collecting robot inadvertently embarks on a space journey that will decide the fate of mankind."},
    "Zodiac": {"imdb": 7.7, "cost": "$2.99", "ott": "Hulu", "category": "Thriller", "description": "A cartoonist becomes obsessed with tracking down the Zodiac killer."},
    "Zootopia": {"imdb": 8.0, "cost": "$2.99", "ott": "Disney+", "category": "Animation", "description": "A rookie bunny cop and a cynical con artist fox must work together to uncover a conspiracy."},
}


def slugify(title: str) -> str:
    """Convert movie title to URL-friendly slug format."""
    return (
        title.lower().replace("&", "and").replace(" ", "-").replace(":", "").replace("'", "")
    )


def title_from_slug(slug: str) -> str | None:
    """Convert URL slug back to original movie title."""
    for t in movie_posters:
        if slugify(t) == slug:
            return t
    return None


def get_db_connection():
    """Create and return a database connection."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Initialize database tables for users and feedback."""
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
    """Fetch a user from the database by username."""
    with get_db_connection() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,),
        ).fetchone()


def create_user(username, display_name, password):
    """Create a new user with hashed password in the database."""
    password_hash = generate_password_hash(password)
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)',
            (username, display_name, password_hash),
        )
        conn.commit()


def send_email(subject: str, body: str, to_address: str | None = None) -> bool:
    """Send a simple email using SMTP. Uses environment variables for configuration.

    Required env vars:
    - SMTP_SERVER
    - SMTP_PORT
    - SMTP_USERNAME
    - SMTP_PASSWORD
    - ADMIN_EMAIL (fallback recipient if to_address not provided)
    - EMAIL_FROM (optional, defaults to SMTP_USERNAME)
    """
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USERNAME')
    smtp_pass = os.environ.get('SMTP_PASSWORD')
    admin_email = os.environ.get('ADMIN_EMAIL')
    email_from = os.environ.get('EMAIL_FROM') or smtp_user

    if to_address is None:
        to_address = admin_email

    if not smtp_server or not smtp_user or not smtp_pass or not to_address:
        # missing config
        print('Email not sent: SMTP configuration or recipient missing')
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = to_address
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as e:
        print('Failed to send email:', e)
        return False


def login_required(view):
    """Decorator to require user login for protected routes."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped_view


# Ensure DB tables exist (CREATE TABLE IF NOT EXISTS is idempotent)
init_db()


def save_feedback(feedback_data):
    """Save user feedback to the database.

    Args:
        feedback_data: Dictionary containing the feedback fields.
    """
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO feedback (user_name, user_gender, user_age, category, continue_choice, feedback) VALUES (?, ?, ?, ?, ?, ?)',
            (
                feedback_data['user_name'],
                feedback_data['user_gender'],
                feedback_data['user_age'],
                feedback_data['category'],
                feedback_data['continue_choice'],
                feedback_data['feedback_text'],
            ),
        )
        conn.commit()


@app.context_processor
def inject_user():
    """Inject current user and movie posters into all template contexts."""
    return {
        'current_user': session.get('display_name') or session.get('username'),
        'movie_posters': movie_posters,
    }


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with validation."""
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
            # notify admin about new registration
            try:
                subject = f'New user registered: {username}'
                body = f'Username: {username}\nDisplay name: {display_name}\n'
                send_email(subject, body)
            except (smtplib.SMTPException, OSError):
                pass
            user = get_user_by_username(username)
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['display_name'] = user['display_name']
            return redirect(url_for('index'))

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with credential validation."""
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
    """Clear user session and redirect to login page."""
    session.clear()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Display movie suggestions based on user preferences."""
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
                f"Movies in {user_category} suitable for under 18:"
                if filtered_movies
                else f"No movies available in {user_category} for your age."
            )
        else:
            category_message = (
                f"Movies in {user_category}:"
                if filtered_movies
                else f"No movies found in category: {user_category}"
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
    """Process and save user feedback submission."""
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
            save_feedback({
                'user_name': user_name,
                'user_gender': user_gender,
                'user_age': user_age,
                'category': user_category,
                'continue_choice': continue_choice,
                'feedback_text': user_feedback,
            })
            # email feedback details to admin
            try:
                subject = f'Feedback from {user_name} ({user_category})'
                body = (
                    f'Name: {user_name}\nGender: {user_gender}\nAge: {user_age}\n'
                    f'Category: {user_category}\nContinue: {continue_choice}\n'
                    f'Feedback:\n{user_feedback}'
                )
                send_email(subject, body)
            except (smtplib.SMTPException, OSError):
                pass
        except sqlite3.DatabaseError:
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
    """Display detailed information about a specific movie."""
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
