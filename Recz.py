import pandas as pd 
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score
import numpy as np
import seaborn as sns
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# #df_film = pd.read_excel('/Users/tylerknohl/Desktop/Hiike_Projects/data/Fixed Sheet Test.xlsx')
df_film = pd.read_csv('/Users/tylerknohl/Desktop/Hiike_Projects/data/Festival Data - Sheet1.csv')

# Function to onehotencode the categorical variables 
def oneHotEncode(df, columns):
    for i in columns: 
        df[i] = df[i].fillna('').apply(lambda x: x.split(",") if isinstance(x, str) else [])

        # Use multi-label binarizer to one hot encode the variables
        mlb = MultiLabelBinarizer()
        encoded_d = mlb.fit_transform(df[i])

        # Create a new data frame with the encoded variables
        encoded_df = pd.DataFrame(encoded_d, columns=[f"{i}_{label.strip()}" for label in mlb.classes_])

        # Concatenate the encoded columns to the original DataFrame
        df = pd.concat([df, encoded_df], axis=1)

        # Drop the original column after encoding
        df = df.drop(columns=[i])
    
    return df

# Specify columns to encode
columns_to_encode = ['Qualifying', 'Style', 'Genre', 'Filmmaker Type', 'Festival Focus', 'Length']

df_film_ohe = oneHotEncode(df_film, columns_to_encode)


# Define the columns to clean and convert to date format
date_columns = ['Opening Date', 'Early Deadline', 'Regular Deadline', 'Final Deadline', 'Completed After Date', 'Completed By Date']

def clean_dates(df, columns):
    for col in columns:
        # Handle non-standard text, trim whitespaces, and convert to datetime format
        df[col] = pd.to_datetime(df[col].str.strip(), errors='coerce', format='%d-%b-%y')  # Customize the date format if needed

    return df

# Clean the date columns
df_film_ohe = clean_dates(df_film_ohe, date_columns)

# Function to clean the runtime columns 
def clean_runtime_value(value):
    if pd.isna(value):
        return np.nan

    # Remove text like "min", "mins", and strip spaces
    value = value.replace('min', '').replace('mins', '').strip()

    # Handle range values like "40, 41"
    if ',' in value:
        value_range = [int(x.strip()) for x in value.split(',')]
        return np.mean(value_range)  # Take the average of the range for simplicity
    
    # Handle values like "<40" (convert to lower bound) and ">60" (upper bound)
    if value.startswith('<'):
        return int(value[1:].strip()) - 1  # e.g., "<40" becomes 39
    if value.startswith('>'):
        return int(value[1:].strip()) + 1  # e.g., ">60" becomes 61
    
    # Try to convert the value to an integer
    try:
        return int(value)
    except ValueError:
        return np.nan

# Apply the cleaning function to the runtime columns
runtime_columns = ['Max Short Runtime', 'Min Feature Runtime', 'Budget']
for col in runtime_columns:
    df_film_ohe[col] = df_film_ohe[col].apply(clean_runtime_value)


# Apply the cleaning function to the yes and no columns 
def yes_no_to_binary(df, columns):
    for col in columns:
        df[col] = df[col].apply(lambda x: 1 if x == 'Yes' else 0)
    return df
columns_to_convert = ['File Type: DCP', 'File Type: Online Screener', 'City Premiere Necessary', 'State Premiere Necessary', 'National Premiere Necessary', 'World Premiere Necessary']

# Apply the function to the specified columns
df_film_ohe = yes_no_to_binary(df_film_ohe, columns_to_convert)

df_film_ohe.columns = df_film_ohe.columns.str.lower()

# Clean column names in the DataFrame
df_film_ohe.columns = df_film_ohe.columns.str.lower().str.strip().str.replace(' ', '_')

# Check for duplicate column names and drop if necessary
df_film_ohe = df_film_ohe.loc[:, ~df_film_ohe.columns.duplicated()]

#function to convert dates to numeric values (days from today)
def convert_date_to_numeric(date_str):
    if pd.isnull(date_str):
        return 0  # Default value for missing dates
    try:
        date_obj = pd.to_datetime(date_str)
        return (date_obj - datetime.now()).days
    except Exception:
        return 0
    

# Normalize 'years_running' to a range between 0 and 1, then scale down its impact to avoid it dominating the cosine similarity
df_film_ohe['years_running'] = pd.to_numeric(df_film_ohe['years_running'], errors='coerce').fillna(0)
df_film_ohe['years_running'] = (df_film_ohe['years_running'] - df_film_ohe['years_running'].min()) / (df_film_ohe['years_running'].max() - df_film_ohe['years_running'].min())

# Apply a weight to 'years_running' to reduce its impact
years_running_weight = 0.1
df_film_ohe['years_running'] *= years_running_weight



# Updated process_user_input to handle missing 'years_running' without weighing heavily
def process_user_input(user_input):
    # Parse genres
    genres = user_input['genre'].split(', ')
    genres_one_hot = {f'genre_{g.strip().lower()}': 1 for g in genres}

    # Parse length
    length_one_hot = {'length_short': 1 if user_input['length'] == 'short' else 0, 'length_feature': 1 if user_input['length'] == 'feature' else 0}

    # Parse yes/no fields (for DCP, online upload, qualifying, premiere requirements)
    dcp = 1 if user_input['dcp'] == 'yes' else 0
    online_upload = 1 if user_input['online_upload'] == 'yes' else 0
    qualifying = 1 if user_input['qualifying_'] == 'yes' else 0
    premiere_city = 1 if user_input['premiere_city'] == 'yes' else 0
    premiere_state = 1 if user_input['premiere_state'] == 'yes' else 0
    premiere_national = 1 if user_input['premiere_national'] == 'yes' else 0
    premiere_world = 1 if user_input['premiere_world'] == 'yes' else 0

    # Parse style
    style = user_input['style'].split(', ')
    style_one_hot = {f'style_{s.strip().lower()}': 1 for s in style}

    # Parse filmmaker type
    filmmaker_type = user_input['filmmaker_type'].split(', ')
    filmmaker_type_one_hot = {f'filmmaker_type_{ft.strip().lower()}': 1 for ft in filmmaker_type}

    # Parse festival focus
    festival_focus = user_input['festival_focus'].split(', ')
    festival_focus_one_hot = {f'festival_focus_{ff.strip().lower()}': 1 for ff in festival_focus}

    # Convert dates to numeric (days from today)
    opening_date_numeric = convert_date_to_numeric(user_input.get('opening_date'))
    early_deadline_numeric = convert_date_to_numeric(user_input.get('early_deadline'))
    regular_deadline_numeric = convert_date_to_numeric(user_input.get('regular_deadline'))
    final_deadline_numeric = convert_date_to_numeric(user_input.get('final_deadline'))

    # Handle 'years_running' if provided, or exclude it
    years_running = user_input.get('years_running', None)
    if years_running is not None:
        years_running = float(years_running)
        years_running = (years_running - df_film['years_running'].min()) / (df_film['years_running'].max() - df_film['years_running'].min())
        years_running *= years_running_weight
    else:
        years_running = None

    # Create the user vector with all values
    user_vector = {
        **genres_one_hot,
        **length_one_hot,
        'file_type:_dcp': dcp,
        'file_type:_online_screener': online_upload,
        'qualifying_': qualifying,
        'city_premiere_necessary': premiere_city,
        'state_premiere_necessary': premiere_state,
        'national_premiere_necessary': premiere_national,
        'world_premiere_necessary': premiere_world,
        **style_one_hot,
        **filmmaker_type_one_hot,
        **festival_focus_one_hot,
        'opening_date': opening_date_numeric,
        'early_deadline': early_deadline_numeric,
        'regular_deadline': regular_deadline_numeric,
        'final_deadline': final_deadline_numeric,
    }

    # Add 'years_running' to the user vector only if it's provided
    if years_running is not None:
        user_vector['years_running'] = years_running

    # Dynamically add missing columns from the DataFrame
    for col in df_film_ohe.columns:
        if col not in user_vector:
            user_vector[col] = 0  # Set missing features to 0
    
    return user_vector

# Function to calculate cosine similarity, excluding non-numeric columns like 'name', 'location'
def calculate_similarity(user_vector, dataframe):
    # Convert the user vector to a DataFrame to match the format of df_film
    user_vector_df = pd.DataFrame([user_vector])

    # Select only numeric columns for cosine similarity (excluding 'name', 'location', etc.)
    relevant_columns = [col for col in dataframe.columns if dataframe[col].dtype in [np.float64, np.int64]]
    df_film_relevant = dataframe[relevant_columns].select_dtypes(include=[np.number])

    # Ensure only numeric columns are used from the user vector
    user_vector_df_relevant = user_vector_df[relevant_columns].select_dtypes(include=[np.number])

    # Fill NaN values with 0 to handle missing values
    df_film_relevant = df_film_relevant.fillna(0)
    user_vector_df_relevant = user_vector_df_relevant.fillna(0)

    # Calculate cosine similarity between the user vector and all the festivals
    similarity_scores = cosine_similarity(user_vector_df_relevant, df_film_relevant)

    return similarity_scores[0]

# Example user input (without 'years_running' to see how it behaves)
user_vector = process_user_input({
    "genre": "Comedy, Horror, Thriller, Fantasy",
    "length": "short",
    "dcp": "yes",
    "online_upload": "yes",
    "qualifying_": "yes",
    "premiere_city": "yes",
    "premiere_state": "no",
    "premiere_national": "no",
    "premiere_world": "yes",
    "style": "Documentary, Animation",
    "filmmaker_type": "BIPOC, Female",
    "festival_focus": "international",
    "opening_date": "2024-01-01",
    "early_deadline": "2024-02-01",
    "regular_deadline": "2024-03-01",
    "final_deadline": "2024-04-01"
})

# Calculate similarity between user input and festivals
similarity_scores = calculate_similarity(user_vector, df_film_ohe)

# Add similarity scores to the dataframe
df_film_ohe['similarity_score'] = similarity_scores

# Sort by similarity score
df_film_sorted = df_film_ohe.sort_values(by='similarity_score', ascending=False)

# Display the top recommendations (including 'name' and 'location')
top_recommendations = df_film_sorted[['name', 'location', 'years_running', 'similarity_score']].head(5)
print(top_recommendations)


# Add infromation to the similarity scores where the user 
# is a first time filmmaker or f they have submitted to festivals before 
# make sure sundacne is not in ther top five festovals if they havent submitted before 


