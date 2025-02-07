import streamlit as st
import pandas as pd

# Sample DataFrame
data = {'date': ['2025-02-05', '2025-02-11', '2025-02-04', '2025-02-09']}
df = pd.DataFrame(data)

# Convert the 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Function to highlight Sundays
def highlight_sundays(row):
    if row['date'].dayofweek == 6:  # Sunday corresponds to 6
        return ['background-color: red'] * len(row)
    else:
        return [''] * len(row)

# Apply the highlight function
styled_df = df.style.apply(highlight_sundays, axis=1)

st.write("DataFrame with Sundays Highlighted:")
st.dataframe(styled_df)

st.balloons()
st.snow()
