movie_categories = {
    "Thriller": ["Inception", "Gone Girl", "Se7en"],
    "Comedy": ["Superbad", "Step Brothers", "The Grand Budapest Hotel"]
}

# Function to print movies from a selected category
def print_movies(category):
    movies = movie_categories.get(category, [])
    if movies:
        print(f"Movies in {category}:")
        for movie in movies:
            print(f"- {movie}")
    else:
        print(f"No movies found in category: {category}")


# Main program
user_name = input("What is your name? ")
print("Welcome " + user_name + " to the app!")
user_gender = input("What is your gender? ")
user_category = input("What category do you want in this app, dear " + user_name + "? ")
print("You are " + user_gender + " and you like to watch " + user_category + " movies.")

while True:
    user_response = input("Do you want to continue? (yes/no): ")
    
    if user_response.lower() == 'yes':
        print_movies(user_category.capitalize())
        break

    elif user_response.lower() == 'no':
        print("Closing the program. Goodbye!")
        break

    else:
        print("Please answer 'yes' or 'no'.")

# Last 4 lines should run here
print("We hope to see you again " + user_name)
print("So you enjoy this app " + user_name + "!")
input("Please share your feedback about this app " + user_name + ": ")
print("Thank you for sharing your thoughts about this app " + user_name)