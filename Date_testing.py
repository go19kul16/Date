import streamlit as st
import pandas as pd

# Sample DataFrame
data = {'date': ['2025-02-05', '2025-02-11', '2025-02-04', '2025-02-09']}
df = pd.DataFrame(data)

# Convert the 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Format the 'date' column to dd-mm-yyyy
df['date'] = df['date'].dt.strftime('%d-%m-%Y')

# Function to highlight Sundays
def highlight_sundays(row):
    if pd.to_datetime(row['date'], format='%d-%m-%Y').dayofweek == 6:  # Sunday corresponds to 6
        if agree:
            return ['color: red'] * len(row)
    else:
        return [''] * len(row)

agree = st.checkbox("Highlight Sundays")
styled_df = df.style.apply(highlight_sundays, axis=1)

st.write("DataFrame with Sundays Highlighted:")
st.dataframe(styled_df)


e = RuntimeError("This is an exception of type RuntimeError")
st.exception(e)
