import streamlit as st
import pandas as pd
from datetime import datetime
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
        data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)  # ensure Date is datetime
    except FileNotFoundError:
        data = pd.DataFrame(columns=['Date', 'Title', 'Amount'])
    return data
# Function to save data to Excel for a specific user
def save_data(data, username):
    file_name = f'expenses_{username}.xlsx'
    # Ensure 'Date' is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(data['Date']):
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce', dayfirst=True)  # Coerce errors to NaT if necessary
    
    # Now we can format the 'Date' column safely
    data['Date'] = data['Date'].dt.strftime('%d-%m-%Y')  # ensure date format before saving
    data.to_excel(file_name, index=False, engine='openpyxl')

# Signup Page
def signup_page():
    st.title('📝 Sign Up for Expense Tracker')
    new_username = st.text_input('Choose a Username')
    new_password = st.text_input('Choose a Password', type='password')
    confirm_password = st.text_input('Confirm Password', type='password')
    
    if st.button('🎉 Create Account'):
        if new_username and new_password and confirm_password:
            if new_password != confirm_password:
                st.error('❌ Passwords do not match. Please try again.')
            elif new_username in USER_CREDENTIALS:
                st.error('❌ Username already exists. Please choose a different one.')
            else:
                USER_CREDENTIALS[new_username] = hash_password(new_password)
                save_credentials(USER_CREDENTIALS)
                st.success('🎉 Signup successful! Redirecting to login page...')
                st.session_state.show_login = False
                st.experimental_rerun()  # Redirect to login after signup
        else:
            st.error('❌ Please fill in all fields.')

# Login Page
def login_page():
    st.title('🔑 Login to Expense Tracker')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    if st.button('✅ Login'):
        if username and password:
            hashed_password = hash_password(password)
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == hashed_password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f'🎉 Login successful! Welcome {username}.')
                st.experimental_rerun()
            else:
                st.error('❌ Invalid username or password. Please try again.')
        else:
            st.error('❌ Please enter both username and password.')
    
    if st.button('📝 Sign Up'):
        st.session_state.show_login = True
        st.experimental_rerun()

# Logout Function
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.show_login = True
    st.experimental_rerun()

# Add Expense Page
def add_expense_page():
    st.title('💰 Add Daily Expense')
    expense_date = st.date_input('📅 Date', value=datetime.today())
    expense_title = st.text_input('📝 Title of Expense')
    expense_amount = st.number_input('💸 Amount', min_value=0, step=10)

    if st.button('✅ Submit'):
        if expense_title.strip() == '':
            st.error('❌ Expense title cannot be empty.')
            return

        data = load_data(st.session_state.username)
        new_row = pd.DataFrame({'Date': [expense_date], 'Title': [expense_title], 'Amount': [expense_amount]})
        data = pd.concat([data, new_row], ignore_index=True)
        save_data(data, st.session_state.username)
        st.success('✅ Expense has been added successfully!')

# Search Expense Page
def search_expense_page():
    st.title('🔍 Search Expenses')
    search_type = st.selectbox('Select Search Type', ['Select an Option', 'Specific Date', 'Date Range'], index=0)
    
    data = load_data(st.session_state.username)

    if search_type == 'Specific Date':
        search_date = st.date_input('📅 Select Date to Search', value=datetime.today())
        if st.button('🔍 Search'):
            filtered_data = data[data['Date'] == pd.to_datetime(search_date)]
            if not filtered_data.empty:
                st.write('### 📊 Expenses for the Selected Date:')
                st.dataframe(filtered_data)
                total_amount = filtered_data['Amount'].sum()
                st.write(f'### 💰 Total Expense: ₹{total_amount:.2f}')
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(data=filtered_data, x='Title', y='Amount', palette='viridis', ax=ax)
                ax.set_title('Expenses Breakdown')
                st.pyplot(fig)
            else:
                st.info('No expenses found for the selected date.')
    elif search_type == 'Date Range':
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input('📅 Start Date', value=datetime.today())
        with col2:
            end_date = st.date_input('📅 End Date', value=datetime.today())
        
        if st.button('🔍 Search Date Range'):
            filtered_data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
            if not filtered_data.empty:
                st.write('### 📊 Expenses for the Selected Period:')
                st.dataframe(filtered_data)
                total_amount = filtered_data['Amount'].sum()
                st.write(f'### 💰 Total Expense: ₹{total_amount:.2f}')
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(data=filtered_data, x='Title', y='Amount', palette='viridis', ax=ax)
                ax.set_title('Expenses Breakdown')
                st.pyplot(fig)
            else:
                st.info('No expenses found for the selected date range.')
    else:
        st.info('Please select a search type to proceed.')

# Monthly Expense Report
def monthly_expense_page():
    st.title('📅 Monthly Expense Report')

    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox('Select a Month', months)

    data = load_data(st.session_state.username)

    if not data.empty:
        data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
        data['Month'] = data['Date'].dt.month
        month_index = months.index(selected_month) + 1
        monthly_data = data[data['Month'] == month_index]

        if not monthly_data.empty:
            st.write(f'### 📊 Expenses for {selected_month}')
            total_expense = monthly_data['Amount'].sum()
            st.write(f'### 💰 Total Expense for {selected_month}: {total_expense}')

            # Bar Chart Visualization
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(data=monthly_data, x="Title", y="Amount", ax=ax, palette="coolwarm")
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            st.pyplot(fig)

            # Pie Chart Visualization
            st.subheader("📊 Monthly Expense Distribution (Pie Chart)")
            pie_data = monthly_data.groupby("Title")["Amount"].sum()
            fig2, ax2 = plt.subplots(figsize=(7, 7))
            ax2.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', colors=sns.color_palette("coolwarm"))
            st.pyplot(fig2)
        else:
            st.write(f"No expenses recorded for {selected_month}.")

# Edit Expense Page
def edit_expense_page():
    st.title('✏️ Edit Expenses')
    
    data = load_data(st.session_state.username)
    
    if data.empty:
        st.info("No expenses found.")
        return
    
    edit_date = st.date_input('📅 Select Date', value=datetime.today())
    filtered_data = data[data['Date'] == pd.to_datetime(edit_date)]

    if filtered_data.empty:
        st.info("No expenses found for the selected date.")
        return
    
    expense_options = filtered_data.apply(lambda row: f"{row['Title']} - {row['Amount']}", axis=1).tolist()
    selected_expense_index = st.selectbox("Select Expense to Edit:", expense_options)

    if selected_expense_index:
        selected_row_index = filtered_data.index[expense_options.index(selected_expense_index)]
        new_title = st.text_input("📝 Edit Title", value=data.at[selected_row_index, 'Title'])
        new_amount = st.number_input("💸 Edit Amount", min_value=1, step=1, value=int(data.at[selected_row_index, 'Amount']))

        if st.button("💾 Save Changes"):
            data.at[selected_row_index, 'Title'] = new_title
            data.at[selected_row_index, 'Amount'] = new_amount
            save_data(data, st.session_state.username)
            st.success("✅ Expense updated successfully!")
            st.experimental_rerun()

# Delete Expense Page
def delete_expense_page():
    st.title('🗑️ Delete Expenses')

    data = load_data(st.session_state.username)

    if data.empty:
        st.info("No expenses found.")
        return

    delete_date = st.date_input('📅 Select Date', value=datetime.today())
    filtered_data = data[data['Date'] == pd.to_datetime(delete_date)]

    if filtered_data.empty:
        st.info("No expenses found for the selected date.")
        return

    expense_options = filtered_data.apply(lambda row: f"{row['Title']} - {row['Amount']}", axis=1).tolist()
    selected_expense_index = st.selectbox("Select Expense to Delete:", expense_options)

    if selected_expense_index:
        selected_row_index = filtered_data.index[expense_options.index(selected_expense_index)]

        if st.button("🗑️ Delete Expense"):
            data = data.drop(selected_row_index)
            save_data(data, st.session_state.username)
            st.success("✅ Expense deleted successfully!")
            st.experimental_rerun()

# Navigation Logic
if 'show_login' not in st.session_state:
    st.session_state.show_login = True

if st.session_state.show_login:
    signup_page()  # Show the signup page initially
elif not st.session_state.authenticated:
    login_page()  # Show the login page if not authenticated
else:
    st.sidebar.title("🧭 Navigation")
    menu = ['💰 Add Expense', '🔍 Search Expenses', '📅 Monthly Expenses', '✏️ Edit Expenses', '🗑️ Delete Expenses', '🚪 Logout']
    choice = st.sidebar.selectbox('Select an Option', menu)

    if choice == '💰 Add Expense':
        add_expense_page()
    elif choice == '🔍 Search Expenses':
        search_expense_page()
    elif choice == '📅 Monthly Expenses':
        monthly_expense_page()
    elif choice == '✏️ Edit Expenses':
        edit_expense_page()
    elif choice == '🗑️ Delete Expenses':
        delete_expense_page()
    elif choice == '🚪 Logout':
        logout()
