from flask import Flask, render_template, request, jsonify
from Recz import process_user_input, calculate_similarity, df_film_ohe  # Import necessary functions
import pandas as pd

app = Flask(__name__, static_folder='assets')

# Route to serve the HTML file
@app.route('/')
def home():
    return render_template('index_test.html')

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/predict', methods=['POST'])
def predict():
    # Get user input from the request
    user_input = request.get_json()

    # Process user input to match festival data
    user_vector = process_user_input(user_input)

    # Calculate similarity
    similarity_scores = calculate_similarity(user_vector, df_film_ohe)

    # Add similarity scores to the festival data
    df_film_ohe['similarity_score'] = similarity_scores

    # Sort by similarity score and get top recommendations
    top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

    # Prepare the response to include name, location, and similarity score
    response = top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records')

    return jsonify(response)




# from flask import Flask, render_template, request, jsonify
# from Recz import process_user_input, calculate_similarity, df_film_ohe  # Import necessary functions and preprocessed data
# import pandas as pd

# app = Flask(__name__, static_folder='assets')  # Specify the static folder for CSS/JS files

# # Route to serve the HTML file
# @app.route('/')
# def home():
#     return render_template('index_test.html')  # Make sure 'index_test.html' is in the templates folder

# # Route to handle prediction requests
# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         # Get user input from the request
#         user_input = request.get_json()

#         # Validate user input
#         if not user_input:
#             return jsonify({"error": "Invalid input"}), 400

#         # Process user input to match festival data
#         user_vector = process_user_input(user_input)

#         # Calculate similarity
#         similarity_scores = calculate_similarity(user_vector, df_film_ohe)

#         # Add similarity scores to the festival data
#         df_film_ohe['similarity_score'] = similarity_scores

#         # Sort by similarity score and get top recommendations
#         top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

#         # Prepare the response to include name, location, and similarity score
#         response = top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records')

#         return jsonify(response)

#     except Exception as e:
#         # Handle errors and return meaningful messages
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)



# # Create a Flask app instance
# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         # Capture user input from the JSON request
#         user_input = request.get_json()

#         # Process the user input (calling the process_user_input function)
#         user_vector = process_user_input(user_input)

#         # Calculate similarity with festivals in the dataset
#         similarity_scores = calculate_similarity(user_vector, df_film_ohe)

#         # Add the similarity scores to the dataframe
#         df_film_ohe['similarity_score'] = similarity_scores

#         # Sort festivals by similarity score and return top 5
#         top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

#         # Return the top recommendations as JSON to the frontend
#         return jsonify(top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records'))
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# if __name__ == '__main__':
#     app.run(debug=True)