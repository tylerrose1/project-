import mysql.connector
from flask import Flask, render_template, request, jsonify
from Recz import process_user_input, calculate_similarity, df_film_ohe  # Import necessary functions
import pandas as pd


# Create a Flask app instance
app = Flask(__name__, static_folder='assets')

#RDS Database Configuration
db_config = {
    "host": "filmquiz-1.cv0mcauishmo.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "password": "1528eloise08$092002",
    "database": "Hiike_Project"
}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Capture user input from the JSON request
        user_input = request.get_json()

        # Insert user input into RDS
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
        INSERT INTO user_inputs (genre, length, dcp, online_upload, qualifying, premiere_city, premiere_state,
                                 premiere_national, premiere_world, style, filmmaker_type, festival_focus, opening_date,
                                 early_deadline, regular_deadline, final_deadline)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_input['genre'], user_input['length'], user_input['dcp'], user_input['online_upload'],
            user_input['qualifying_'], user_input['premiere_city'], user_input['premiere_state'],
            user_input['premiere_national'], user_input['premiere_world'], user_input['style'],
            user_input['filmmaker_type'], user_input['festival_focus'], user_input['opening_date'],
            user_input['early_deadline'], user_input['regular_deadline'], user_input['final_deadline']
        ))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()

        # Trigger the recommendation function
        user_vector = process_user_input(user_input)
        similarity_scores = calculate_similarity(user_vector, df_film_ohe)
        df_film_ohe['similarity_score'] = similarity_scores
        top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

        # Insert recommendations into RDS
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        for _, row in top_recommendations.iterrows():
            query = """
            INSERT INTO recommendations (user_id, festival_name, location, similarity_score)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, row['name'], row['location'], row['similarity_score']))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 400



# # Create a Flask app instance
# app = Flask(__name__, static_folder='assets')

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

