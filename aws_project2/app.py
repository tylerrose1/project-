# import mysql.connector
# from flask import Flask, render_template, request, jsonify
# from Recz import process_user_input, calculate_similarity, df_film_ohe
# import pandas as pd
# from datetime import datetime
# import boto3
# import json

# # Initialize Lambda client
# lambda_client = boto3.client('lambda', region_name='us-east-2')  # Replace 'your-region' with your AWS region


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
#         # Capture and process user input
#         user_input = {
#             'genre': request.form['genre'],
#             'length': request.form['length'],
#             'filmmaker_type': request.form.get('filmmaker_type', ''),
#             'festival_focus': request.form.get('festival_focus', ''),
#             'style': request.form['style'],
#             'opening_date': request.form.get('opening_date', None),
#             'early_deadline': request.form.get('early_deadline', None),
#             'regular_date': request.form.get('regular_date', None),
#             'final_date': request.form.get('final_date', None),
#             'completion_date': request.form.get('completion_date', None),
#             'dcp': request.form.get('dcp') == 'yes',
#             'online_upload': request.form.get('online_upload') == 'yes',
#             'qualifying': request.form.get('qualifying') == 'yes',
#             'premiere_city': request.form.get('premiere_city') == 'yes',
#             'premiere_state': request.form.get('premiere_state') == 'yes',
#             'premiere_national': request.form.get('premiere_national') == 'yes',
#             'premiere_world': request.form.get('premiere_world') == 'yes',
#             'years_running': int(request.form.get('years_running', 0)),
#         }

#         # Insert user input into RDS
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         user_input_query = """
#         INSERT INTO user_inputs (
#             genre, length, online_upload, qualifying, style, filmmaker_type, festival_focus,
#             opening_date, early_deadline, regular_date, final_date, completion_date,
#             dcp, premiere_city, premiere_state, premiere_national, premiere_world, years_running
#         )
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         user_input_values = (
#             user_input['genre'], user_input['length'], user_input['online_upload'], user_input['qualifying'],
#             user_input['style'], user_input['filmmaker_type'], user_input['festival_focus'],
#             user_input['opening_date'], user_input.get('early_deadline', None), user_input['regular_date'],
#             user_input['final_date'], user_input['completion_date'], user_input['dcp'],
#             user_input['premiere_city'], user_input['premiere_state'], user_input['premiere_national'],
#             user_input['premiere_world'], user_input['years_running']
#         )
#         cursor.execute(user_input_query, user_input_values)
#         user_input_id = cursor.lastrowid

#         # Process user input
#         user_vector = process_user_input(user_input)
#         similarity_scores = calculate_similarity(user_vector, df_film_ohe)
#         df_film_ohe['similarity_score'] = similarity_scores
#         top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

#         # Fetch images from Lambda for recommendations
#         recommendations_with_images = []
#         for _, row in top_recommendations.iterrows():
#             lambda_payload = {"festival_name": row['name']}
#             try:
#                 response = lambda_client.invoke(
#                     FunctionName="predict_recommendations",  # Replace with your Lambda function name
#                     InvocationType="RequestResponse",
#                     Payload=json.dumps(lambda_payload)
#                 )
#                 response_payload = json.loads(response['Payload'].read())
#                 image_url = json.loads(response_payload.get('body', '{}')).get('image_url', '')
#             except Exception as e:
#                 image_url = None  # Handle Lambda errors

#             recommendations_with_images.append({
#                 "name": row['name'],
#                 "location": row['location'],
#                 "similarity_score": row['similarity_score'],
#                 "image_url": image_url
#             })

#         for _, row in top_recommendations.iterrows():
#                 lambda_payload = {"festival_name": row['name']}
#         try:
#             response = lambda_client.invoke(
#                 FunctionName="predict_recommendations",
#                 InvocationType="RequestResponse",
#                 Payload=json.dumps(lambda_payload)
#             )
#             response_payload = json.loads(response['Payload'].read())
#             print("Lambda Payload:", lambda_payload)  # Log the request payload
#             print("Lambda Response:", response_payload)  # Log the Lambda response
#             image_url = json.loads(response_payload.get('body', '{}')).get('image_url', '')
#         except Exception as e:
#             print("Lambda Error:", str(e))  # Log any errors
#             image_url = None

#             # Insert recommendations into RDS
#             recommendation_query = """
#             INSERT INTO recommendations (user_id, festival_name, location, similarity_score, image_url)
#             VALUES (%s, %s, %s, %s, %s)
#             """
#             cursor.execute(recommendation_query, (user_input_id, row['name'], row['location'], row['similarity_score'], image_url))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         # Render results page with recommendations and images
#         return render_template('result.html', prediction=recommendations_with_images)
    
    
#     except Exception as e:
#         print("Error:", str(e))
#         return jsonify({"error": str(e)}), 400

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)


import mysql.connector
from flask import Flask, render_template, request, jsonify
from Recz import process_user_input, calculate_similarity, df_film_ohe
import pandas as pd
from datetime import datetime
import boto3
import json

# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-2')  # Replace with your AWS region

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
        user_input_id = cursor.lastrowid

        # Process user input and calculate recommendations
        user_vector = process_user_input(user_input)
        similarity_scores = calculate_similarity(user_vector, df_film_ohe)
        df_film_ohe['similarity_score'] = similarity_scores
        top_recommendations = df_film_ohe.sort_values(by='similarity_score', ascending=False).head(5)

        # Fetch images from Lambda for recommendations
        recommendations_with_images = []
        for _, row in top_recommendations.iterrows():
            lambda_payload = {"festival_name": row['name']}
            try:
                response = lambda_client.invoke(
                    FunctionName="predict_recommendations",  # Lambda function name
                    InvocationType="RequestResponse",
                    Payload=json.dumps(lambda_payload)
                )
                response_payload = json.loads(response['Payload'].read())
                print("Lambda Payload:", lambda_payload)
                print("Lambda Response:", response_payload)
                image_url = json.loads(response_payload.get('body', '{}')).get('image_url', '')
            except Exception as e:
                print("Lambda Error:", str(e))
                image_url = None

            recommendations_with_images.append({
                "name": row['name'],
                "location": row['location'],
                "similarity_score": row['similarity_score'],
                "image_url": image_url
            })

            # Insert recommendations into RDS
            recommendation_query = """
            INSERT INTO recommendations (user_id, festival_name, location, similarity_score, image_url)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(recommendation_query, (user_input_id, row['name'], row['location'], row['similarity_score'], image_url))

        conn.commit()
        cursor.close()
        conn.close()

        # Render results page with recommendations and images
        return render_template('result.html', prediction=recommendations_with_images)
    
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)