import streamlit as st
import pandas as pd
from datetime import datetime
import io
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib
import json

# Set Seaborn style for better visuals
sns.set_theme(style="whitegrid")

# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load or initialize user credentials
def load_credentials():
    try:
        with open("user_credentials.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save user credentials
def save_credentials(credentials):
    with open("user_credentials.json", "w") as file:
        json.dump(credentials, file)

# Load existing credentials
USER_CREDENTIALS = load_credentials()

# Function to load existing data or create a new DataFrame for a specific user
def load_data(username):
    file_name = f'expenses_{username}.xlsx'
    try:
        data = pd.read_excel(file_name, engine='openpyxl')
    except FileNotFoundError:
        data = pd.DataFrame(columns=['Date', 'Title', 'Amount'])
    return data

# Function to save data to Excel for a specific user
def save_data(data, username):
    file_name = f'expenses_{username}.xlsx'
    data.to_excel(file_name, index=False, engine='openpyxl')

# Highlight Sundays in red
def highlight_sundays(df):
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is in datetime format
        def color_row(date):
            return ['background-color: red'] * len(df.columns) if date.dayofweek == 6 else [''] * len(df.columns)
        styled_df = df.style.apply(lambda row: color_row(row['Date']), axis=1)
        return styled_df
    return df  # Return the original if empty to avoid errors

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.show_login = False

# Add this function whenever you display DataFrame
def display_dataframe_with_sundays_highlight(df):
    styled_df = highlight_sundays(df)
    st.dataframe(styled_df)

# Signup Page
def signup_page():
    st.title('📝 Sign Up for Expense Tracker')
    new_username = st.text_input('Choose a Username')
    new_password = st.text_input('Choose a Password', type='password')
    confirm_password = st.text_input('Confirm Password', type='password')
    
    if st.button('🎉 Create Account', key='signup_button', help='Click to create an account'):
        if new_username and new_password and confirm_password:
            if new_password != confirm_password:
                st.error('❌ Passwords do not match. Please try again.')
            elif new_username in USER_CREDENTIALS:
                st.error('❌ Username already exists. Please choose a different one.')
            else:
                USER_CREDENTIALS[new_username] = hash_password(new_password)
                save_credentials(USER_CREDENTIALS)
                st.success('🎉 Signup successful! Redirecting to login page...')
                st.session_state.show_login = True
                st.rerun()
        else:
            st.error('❌ Please fill in all fields.')
    st.markdown(":red[**AFTER SIGNING UP PLEASE REFRESH THE PAGE**]")

# Include the rest of your existing functions here...
