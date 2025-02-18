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

def edit_expense_page():
    st.title('✏️ Edit Expenses')

    # Load user's expense data
    data = load_data(st.session_state.username)

    if data.empty:
        st.info("No expenses found.")
        return

    # Ensure 'Date' column is in datetime format and drop invalid rows
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data.dropna(subset=['Date'])

    # Step 1: Select Date to Edit
    edit_date = st.date_input('📅 Select Date', value=datetime.today())

    # Step 2: Filter data by the selected date
    filtered_data = data[data['Date'].dt.date == edit_date]

    if filtered_data.empty:
        st.info(f"No expenses found for {edit_date}.")
        return

    # Step 3: Select Expense to Edit
    expense_options = filtered_data.apply(lambda row: f"{row['Title']} - {row['Amount']}", axis=1).tolist()
    selected_expense = st.selectbox("Select Expense to Edit:", expense_options)

    if not selected_expense:
        return

    # Find the corresponding row index
    selected_row_index = filtered_data.index[expense_options.index(selected_expense)]

    # Step 4: Edit Fields (populate with existing data)
    new_title = st.text_input("📝 Edit Title", value=filtered_data.at[selected_row_index, 'Title'])
    new_amount = st.number_input("💸 Edit Amount", min_value=1, step=1, value=int(filtered_data.at[selected_row_index, 'Amount']))

    # Step 5: Save Changes after confirmation
    edit_agreement = st.checkbox("I Agree to Edit This Expense", key="agree_edit")
    if edit_agreement:
        if st.button("💾 Save Changes"):
            # Update data with the new values
            data.at[selected_row_index, 'Title'] = new_title
            data.at[selected_row_index, 'Amount'] = new_amount
            
            # Save the updated data
            save_data(data, st.session_state.username)
            
            # Display success message and rerun
            st.success("✅ Expense updated successfully!")
            st.experimental_rerun()  # Refresh page to reflect changes

def delete_expense_page():
    st.title('🗑️ Delete Expenses')

    data = load_data(st.session_state.username)

    if data.empty:
        st.info("No expenses found.")
        return

    # Step 1: Select Date
    delete_date = st.date_input('📅 Select Date', value=datetime.today())
    filtered_data = data[data['Date'] == pd.to_datetime(delete_date)]

    if filtered_data.empty:
        st.info("No expenses found for the selected date.")
        return

    # Step 2: Select Expense to Delete
    expense_options = filtered_data.apply(lambda row: f"{row['Title']} - {row['Amount']}", axis=1).tolist()
    selected_expense = st.selectbox("Select Expense to Delete:", expense_options)

    if not selected_expense:
        return

    # Find the corresponding row
    selected_row_index = filtered_data.index[expense_options.index(selected_expense)]

    # Step 3: Confirmation and Delete Button
    delete_agreement = st.checkbox("I Agree to Delete This Expense", key="delete_agree")
    if delete_agreement:
        if st.button("🗑️ Delete Expense"):
            # Remove the selected expense from the data
            data = data.drop(selected_row_index)
            save_data(data, st.session_state.username)
            st.success("✅ Expense deleted successfully!")
            st.rerun()

def search_expense_page():
    st.title('🔍 Search Expenses')
    search_type = st.selectbox(
        'Select Search Type', 
        ['Select an Option', 'Specific Date', 'Date Range'], 
        index=0,
        help="Choose whether to search by a specific date or a date range"
    )
    
    # Load user-specific data
    data = load_data(st.session_state.username)

    # Convert 'Date' column back to datetime for filtering purposes
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)

    if search_type == 'Specific Date':
        search_date = st.date_input('📅 Select Date to Search', value=datetime.today())
        if st.button('🔍 Search'):
            filtered_data = data[data['Date'] == pd.to_datetime(search_date)]
            if not filtered_data.empty:
                st.write('### 📊 Expenses for the Selected Date:')
                st.dataframe(filtered_data)
                total_amount = filtered_data['Amount'].sum()
                st.write(f'### 💰 Total Expense: ₹{total_amount:.2f}')
                # Plotting
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
            filtered_data = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]
            if not filtered_data.empty:
                st.write('### 📊 Expenses for the Selected Period:')
                st.dataframe(filtered_data)
                total_amount = filtered_data['Amount'].sum()
                st.write(f'### 💰 Total Expense: ₹{total_amount:.2f}')
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(data=filtered_data, x='Title', y='Amount', palette='viridis', ax=ax)
                ax.set_title('Expenses Breakdown')
                st.pyplot(fig)
            else:
                st.info('No expenses found for the selected date range.')
    else:
        st.info('Please select a search type to proceed.')

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
                
                # Set session state to show login page
                st.session_state.show_login = True
                # Rerun the app to show the login page after successful signup
                st.experimental_rerun()  # This will re-run the whole app
                
        else:
            st.error('❌ Please fill in all fields.')
    
    st.markdown(":red[**AFTER SIGNING UP PLEASE REFRESH THE PAGE**]")


if 'show_login' in st.session_state and st.session_state.show_login:
    login_page()
elif not st.session_state.authenticated:
    login_page()
else:
    # If logged in, show the main menu
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
        lo

