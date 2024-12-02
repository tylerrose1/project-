from flask import Flask, render_template, request, jsonify
from Recz import process_user_input, calculate_similarity, df_film_ohe  # Import necessary functions
import pandas as pd

# Create a Flask app instance
app = Flask(__name__, static_folder='assets')

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Capture user input from the JSON request
        user_input = request.get_json()

        # Process the user input (calling the process_user_input function)
        user_vector = process_user_input(user_input)

        # Calculate similarity with festivals in the dataset
        similarity_scores = calculate_similarity(user_vector, df_film_ohe)

        # Add the similarity scores to the dataframe
        df_film_ohe['similarity_score'] = similarity_scores

        # Sort festivals by similarity score and return top 5
        top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

        # Return the top recommendations as JSON to the frontend
        return jsonify(top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records'))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
