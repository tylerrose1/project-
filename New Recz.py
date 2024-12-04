import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime
from sklearn.model_selection import train_test_split

# Loading the datasets 
film_festival_df  = pd.read_excel('/Users/tylerknohl/Desktop/DS4300/Hiike-Website-main/Film_Festival.xlsx', sheet_name='Sheet1')
films_accepted_df = pd.read_excel('/Users/tylerknohl/Desktop/DS4300/Hiike-Website-main/Films_Accepted.xlsx', sheet_name='Sheet1')

# Normalizes the type of text and makes everything lowercase 
film_festival_df['Name'] = film_festival_df['Name'].str.strip().str.lower()
films_accepted_df['Film Festival Name'] = films_accepted_df['Film Festival Name'].str.strip().str.lower()

# Merges the two datasets 
merged_df = films_accepted_df.merge(
    film_festival_df,
    left_on='Film Festival Name',
    right_on='Name',
    how='inner'
)


# Makes sure accepted is 1 and 0 for yes and no
merged_df['Accepted'] = merged_df['Accepted'].apply(lambda x: 1 if x == 'Yes' else 0)

print(merged_df.columns)

# One Hot Encode 

def oneHotEncode(df, columns):
    df = df.copy()  # Avoid modifying the original DataFrame
    
    for col in columns: 
        # Ensure all data in the column is treated as strings
        df[col] = df[col].fillna('').astype(str)

        # Check if the column contains multiple labels (comma-separated)
        if df[col].str.contains(",").any():
            # Split multi-labeled entries into lists
            df[col] = df[col].apply(lambda x: [label.strip() for label in x.split(",")])

            # Apply MultiLabelBinarizer for multi-labeled columns
            mlb = MultiLabelBinarizer()
            encoded_d = mlb.fit_transform(df[col])

            # Create a DataFrame with encoded variables
            encoded_df = pd.DataFrame(encoded_d, columns=[f"{col}_{label.strip()}" for label in mlb.classes_], index=df.index)
        else:
            # Use pd.get_dummies for single-labeled columns
            encoded_df = pd.get_dummies(df[col], prefix=col, drop_first=True)
        
        # Concatenate the encoded columns to the original DataFrame
        df = pd.concat([df, encoded_df], axis=1)

        # Drop the original column after encoding
        df = df.drop(columns=[col])
    
    return df


# Specify columns to encode
columns_to_encode = ['Premiere Status',
                     'Short or Feature_y', 'Short or Feature_x', 'Style_x', 'Genre_x', 'Qualifying', 'Style_y', 'Genre_y',
                     'Filmmaker Type', 'File Type: DCP', 'File Type: Online Screener',
                     'City Premiere Necessary', 'State Premiere Necessary',
                     'National Premiere Necessary', 'World Premiere Necessary', 'Festival Focus']


df_film_ohe = oneHotEncode(merged_df, columns_to_encode)


# Normalize columns 
numerical_columns = ['Years Running', 'Length', 'Max Short Runtime', 'Min Feature Runtime','Budget']  # Add relevant numerical columns
scaler = MinMaxScaler()
df_film_ohe[numerical_columns] = scaler.fit_transform(df_film_ohe[numerical_columns])


# Training and
# Define features and target
X = df_film_ohe.drop(columns=['Accepted'])  # Drop target column from features
y = df_film_ohe['Accepted']  # Target variable

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)



# features that are relevant to model, would be genre, length, filmmaker type, 
# festival focus, style,  if it is was a short or feature, premiere. the other information 
# is not relevant to the model but i stil want the user to know this information
# (for example, if the film festival requires a dcp or a premiere)
# because if you had a dcp thats not a way to show that you would not get into the festival 
# but we should also reccomend film festivals that are similiar but do not require a dcp
# we want to also show the ones that require a dcp and then if the users says they do not have one 
# provide them with a place to get one (charges extra)