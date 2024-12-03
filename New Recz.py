import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime
from sklearn.model_selection import train_test_split

# Loading the datasets 
film_festival_df  = pd.read_excel('/Users/tylerknohl/Desktop/DS4300/Hiike-Website-main/Film_Festival.xlsx', sheet_name='Sheet1')
films_accepted_df = pd.read_excel('/Users/tylerknohl/Desktop/DS4300/Hiike-Website-main/Films_Accepted.xlsx', sheet_name='Sheet1')

# Normalizes the type of text and makes everything lowercase 
film_festival_df['Name'] = film_festival_df['Name'].str.strip().str.lower()
films_accepted_df['Film Festival'] = films_accepted_df['Film Festival'].str.strip().str.lower()

# Merges the two datasets 
merged_df = films_accepted_df.merge(
    film_festival_df,
    left_on='Film Festival',
    right_on='Name',
    how='inner'
)

print(merged_df.columns)

file_path = '/Users/tylerknohl/Desktop/DS4300/Hiike-Website-main/merged_film.xlsx'
merged_df.to_excel(file_path, index=False)

merged = pd.read_excel('/Users/tylerknohl/Desktop/DS4300/Hiike-Website-main/merged_film.xlsx', sheet_name='Sheet1')
