import mysql.connector
from flask import Flask, render_template, request, jsonify
from Recz import process_user_input, calculate_similarity, df_film_ohe
import pandas as pd
from datetime import datetime
import boto3


# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name='your-region')  # Replace 'your-region' with your AWS region


# RDS Database Configuration
db_config = {
    "host": "filmquiz-1.cv0mcauishmo.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "password": "1528eloise08$092002",
    "database": "Hiike"
}

# Function to connect to the RDS database
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Create a Flask app instance
app = Flask(__name__, static_folder='assets')

@app.route('/')
def home():
    return render_template('index_projectpurposes.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Debugging: Print form data
        print("Form Data:", request.form)

        # Capture and process user input
        user_input = {
            'genre': request.form['genre'],
            'length': request.form['length'],
            'filmmaker_type': request.form.get('filmmaker_type', ''),
            'festival_focus': request.form.get('festival_focus', ''),
            'style': request.form['style'],
            'opening_date': request.form.get('opening_date', None),
            'early_deadline': request.form.get('early_deadline', None),
            'regular_date': request.form.get('regular_date', None),
            'final_date': request.form.get('final_date', None),
            'completion_date': request.form.get('completion_date', None),
            'dcp': request.form.get('dcp') == 'yes',
            'online_upload': request.form.get('online_upload') == 'yes',
            'qualifying': request.form.get('qualifying') == 'yes',
            'premiere_city': request.form.get('premiere_city') == 'yes',
            'premiere_state': request.form.get('premiere_state') == 'yes',
            'premiere_national': request.form.get('premiere_national') == 'yes',
            'premiere_world': request.form.get('premiere_world') == 'yes',
            'years_running': int(request.form.get('years_running', 0)),
        }

        # Insert user input into RDS
        conn = get_db_connection()
        cursor = conn.cursor()

        user_input_query = """
        INSERT INTO user_inputs (
            genre, length, online_upload, qualifying, style, filmmaker_type, festival_focus,
            opening_date, early_deadline, regular_date, final_date, completion_date,
            dcp, premiere_city, premiere_state, premiere_national, premiere_world, years_running
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        user_input_values = (
            user_input['genre'], user_input['length'], user_input['online_upload'], user_input['qualifying'],
            user_input['style'], user_input['filmmaker_type'], user_input['festival_focus'],
            user_input['opening_date'], user_input.get('early_deadline', None), user_input['regular_date'],
            user_input['final_date'], user_input['completion_date'], user_input['dcp'],
            user_input['premiere_city'], user_input['premiere_state'], user_input['premiere_national'],
            user_input['premiere_world'], user_input['years_running']
        )
        cursor.execute(user_input_query, user_input_values)
        user_input_id = cursor.lastrowid  # Get the inserted row's ID

        # Process user input
        user_vector = process_user_input(user_input)

        # Calculate similarity with festivals in the dataset
        similarity_scores = calculate_similarity(user_vector, df_film_ohe)

        # Add similarity scores to the dataframe
        df_film_ohe['similarity_score'] = similarity_scores

        # Sort festivals by similarity score and return top 5
        top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

        # Insert recommendations into RDS
        recommendation_query = """
        INSERT INTO recommendations (user_id, festival_name, location, similarity_score)
        VALUES (%s, %s, %s, %s)
        """
        for _, row in top_recommendations.iterrows():
            recommendation_values = (user_input_id, row['name'], row['location'], row['similarity_score'])
            cursor.execute(recommendation_query, recommendation_values)

        conn.commit()  # Commit all transactions
        cursor.close()
        conn.close()

        # Render results page with top recommendations
        return render_template('result.html', prediction=top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records'))
    
    except Exception as e:
        # Debugging: Log the error
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)


# import mysql.connector
# from flask import Flask, render_template, request, jsonify
# from Recz import process_user_input, calculate_similarity, df_film_ohe
# import pandas as pd

# # RDS Database Configuration
# db_config = {
#     "host": "filmquiz-1.cv0mcauishmo.us-east-2.rds.amazonaws.com",
#     "user": "admin",
#     "password": "1528eloise08$092002",
#     "database": "Hiike"
# }

# # Function to connect to the RDS database
# def get_db_connection():
#     return mysql.connector.connect(**db_config)

# # Create a Flask app instance
# app = Flask(__name__, static_folder='assets')

# @app.route('/')
# def home():
#     return render_template('index_projectpurposes.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         # Debugging: Print form data
#         print("Form Data:", request.form)

#         # Capture and process user input
#         user_input = {
#         'genre': request.form['genre'],
#         'length': request.form['length'],
#         'filmmaker_type': request.form.get('filmmaker_type', ''),
#         'festival_focus': request.form.get('festival_focus', ''),
#         'style': request.form['style'],
#         'opening_date': request.form.get('opening_date', None),
#         'regular_date': request.form.get('regular_date', None),
#         'final_date': request.form.get('final_date', None),
#         'previously_distributed_premiere': request.form.get('previously_distributed_premiere') == 'yes',
#         'completion_date': request.form.get('completion_date', None),
#         'dcp': request.form.get('dcp') == 'yes',
#         'online_upload': request.form.get('online_upload') == 'yes',
#         'qualifying': request.form.get('qualifying') == 'yes',
#         'premiere_city': request.form.get('premiere_city') == 'yes',
#         'premiere_state': request.form.get('premiere_state') == 'yes',
#         'premiere_national': request.form.get('premiere_national') == 'yes',
#         'premiere_world': request.form.get('premiere_world') == 'yes',
#         'years_running': int(request.form.get('years_running', 0))
# }

#         # user_input = {
#         #     'genre': request.form['genre'],
#         #     'length': request.form['length'],
#         #     'filmmaker_type': request.form.get('filmmaker_type', ''),
#         #     'festival_focus': request.form.get('festival_focus', ''),
#         #     'style': request.form['style'],
#         #     'opening_date': request.form.get('opening_date', None),
#         #     'regular_date': request.form.get('regular_date', None),
#         #     'final_date': request.form.get('final_date', None),
#         #     'previously_distributed_premiere': request.form.get('previously_distributed_premiere') == 'yes',
#         #     'completion_date': request.form.get('completion_date', None),
#         #     'dcp': request.form.get('dcp') == 'yes',
#         #     'qualifying': request.form.get('qualifying') == 'yes',
#         #     'years_running': int(request.form.get('years_running', 0))
#         # }

        

#         # Insert user input into RDS
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         user_input_query = """
#         INSERT INTO user_inputs (genre, length, filmmaker_type, festival_focus, style, opening_date, regular_date, final_date,
#                                  previously_distributed_premiere, completion_date, dcp, qualifying, years_running)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         user_input_values = (
#             user_input['genre'], user_input['length'], user_input['filmmaker_type'], user_input['festival_focus'],
#             user_input['style'], user_input['opening_date'], user_input['regular_date'], user_input['final_date'],
#             user_input['previously_distributed_premiere'], user_input['completion_date'], user_input['dcp'],
#             user_input['qualifying'], user_input['years_running']
#         )
#         cursor.execute(user_input_query, user_input_values)
#         user_input_id = cursor.lastrowid  # Get the inserted row's ID

#         # Process user input
#         user_vector = process_user_input(user_input)

#         # Calculate similarity with festivals in the dataset
#         similarity_scores = calculate_similarity(user_vector, df_film_ohe)

#         # Add similarity scores to the dataframe
#         df_film_ohe['similarity_score'] = similarity_scores

#         # Sort festivals by similarity score and return top 5
#         top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

#         # Insert recommendations into RDS
#         recommendation_query = """
#         INSERT INTO recommendations (user_input_id, festival_name, location, similarity_score)
#         VALUES (%s, %s, %s, %s)
#         """
#         for _, row in top_recommendations.iterrows():
#             recommendation_values = (user_input_id, row['name'], row['location'], row['similarity_score'])
#             cursor.execute(recommendation_query, recommendation_values)

#         conn.commit()  # Commit all transactions
#         cursor.close()
#         conn.close()

#         # Render results page with top recommendations
#         return render_template('result.html', prediction=top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records'))
    
#     except Exception as e:
#         # Debugging: Log the error
#         print("Error:", str(e))
#         return jsonify({"error": str(e)}), 400

# if __name__ == '__main__':
#     # Run the Flask app
#     app.run(debug=True)



# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         # Capture user input from the form
#         user_input = {
#             #'location': request.form['location'],
#             'genre': request.form['genre'],
#             'length': request.form['length'],
#             'filmmaker_type': request.form['filmmaker_type'],
#             'festival_focus': request.form['filmmaker_type'],
#             'style': request.form['style'],
#             'opening_date': request.form['opening_date'],
#             'regular_date': request.form['regular_date'],
#             'final_date': request.form['final_date'],
#             'previously_distributed_premiere': request.form['previously_distributed_premiere'],
#             'completion_date': request.form['completion_date'],
#             'file_rule': request.form['file_rule'],
#             'qualifying': request.form['qualifying'],
#             'years running': request.form['years running']  # Fixed the field name here
#         }

#         # Process the user input (calling the process_user_input function)
#         user_vector = process_user_input({
#             "genre": user_input.get('genre', ''),
#             "length": user_input.get('length', ''),
#             "dcp": 'yes' if user_input.get('file_rule', '').lower() == 'yes' else 'no',
#             "online_upload": 'yes' if user_input.get('file_rule', '').lower() == 'yes' else 'no',
#             "qualifying_": 'yes' if user_input.get('qualifying', '').lower() == 'yes' else 'no',
#             "premiere_city": 'yes' if user_input.get('previously_distributed_premiere', '').lower() == 'yes' else 'no',
#             "premiere_state": 'yes' if user_input.get('focus', '').lower() == 'state' else 'no',
#             "premiere_national": 'yes' if user_input.get('focus', '').lower() == 'national' else 'no',
#             "premiere_world": 'yes' if user_input.get('focus', '').lower() == 'world' else 'no',
#             "style": user_input.get('style', ''),
#             "filmmaker_type": user_input.get('filmmaker_type', ''),
#             "festival_focus": user_input.get('festival_focus', ''),
#             "opening_date": user_input.get('opening_date', ''),
#             "early_deadline": user_input.get('regular_date', ''),  # Regular date as early deadline
#             "regular_deadline": user_input.get('regular_date', ''),
#             "final_deadline": user_input.get('final_date', ''),
#             "years running": user_input.get('years running', '0')  # Ensure years_running is processed correctly
#         })

#         # Calculate similarity with festivals in the dataset
#         similarity_scores = calculate_similarity(user_vector, df_film_ohe)

#         # Add the similarity scores to the dataframe
#         df_film_ohe['similarity_score'] = similarity_scores

#         # Sort festivals by similarity score and return top 5
#         top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

#         # Pass the top recommendations to the results page
#         return render_template('result.html', prediction=top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records'))
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400



# @app.route('/')
# def home():
#     return render_template('index_test.html')


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


# # Create a Flask app instance
# app = Flask(__name__)




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













# # Create a Flask app instance
# app = Flask(__name__, static_folder='assets')

# #RDS Database Configuration
# db_config = {
#     "host": "filmquiz-1.cv0mcauishmo.us-east-2.rds.amazonaws.com",
#     "user": "admin",
#     "password": "1528eloise08$092002",
#     "database": "Hiike_Project"
# }

# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         # Capture user input from the JSON request
#         user_input = request.get_json()

#         # Insert user input into RDS
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
#         query = """
#         INSERT INTO user_inputs (genre, length, dcp, online_upload, qualifying, premiere_city, premiere_state,
#                                  premiere_national, premiere_world, style, filmmaker_type, festival_focus, opening_date,
#                                  early_deadline, regular_deadline, final_deadline)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(query, (
#             user_input['genre'], user_input['length'], user_input['dcp'], user_input['online_upload'],
#             user_input['qualifying_'], user_input['premiere_city'], user_input['premiere_state'],
#             user_input['premiere_national'], user_input['premiere_world'], user_input['style'],
#             user_input['filmmaker_type'], user_input['festival_focus'], user_input['opening_date'],
#             user_input['early_deadline'], user_input['regular_deadline'], user_input['final_deadline']
#         ))
#         conn.commit()
#         user_id = cursor.lastrowid
#         cursor.close()
#         conn.close()

#         # Trigger the recommendation function
#         user_vector = process_user_input(user_input)
#         similarity_scores = calculate_similarity(user_vector, df_film_ohe)
#         df_film_ohe['similarity_score'] = similarity_scores
#         top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

#         # Insert recommendations into RDS
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
#         for _, row in top_recommendations.iterrows():
#             query = """
#             INSERT INTO recommendations (user_id, festival_name, location, similarity_score)
#             VALUES (%s, %s, %s, %s)
#             """
#             cursor.execute(query, (user_id, row['name'], row['location'], row['similarity_score']))
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify(top_recommendations[['name', 'location', 'similarity_score']].to_dict(orient='records'))

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
