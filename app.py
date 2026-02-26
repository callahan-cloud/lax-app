import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="LaxScore",
    page_icon="icon.png.png"  # This tells the app to use your image!
)

# Add this near the top of your code
st.empty() # Clears old data
st.cache_data.clear() # Forces a fresh scrape

# 1. Page Configuration for Mobile
st.set_page_config(page_title="LaxScore Clean", layout="centered")

# Custom CSS to make it look like a dark-mode sports app
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥍 LaxScore Hub")
st.caption("Real-time D1, D2, & D3 Data | Ad-Free")

# 2. Data Fetching Logic
def get_data(div, mode="polls"):
    # This header is more detailed to look exactly like a Chrome browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    if mode == "polls":
        url = "https://usila.org/" 
        try:
            # We fetch the page first, then hand it to Pandas
            response = requests.get(url, headers=headers, timeout=10)
            tables = pd.read_html(response.text)
            
            # Division Map: D1 is usually table 0, D2 is 1, D3 is 2
            idx = {"D1": 0, "D2": 1, "D3": 2}
            df = tables[idx[div]]
            
            # Clean up columns (Standardizing common USILA headers)
            df.columns = ['Rank', 'Team', 'Record', 'Points', 'First Place']
            return df[['Rank', 'Team', 'Points']]
        except Exception as e:
            # This helps us see the error in the app
            return pd.DataFrame({"Error": [f"Could not reach polls: {str(e)}"]})

# 3. App Tabs
tab1, tab2 = st.tabs(["📊 Top 20 Polls", "⏱️ Live Scoreboard"])

with tab1:
    div_poll = st.segmented_control("Division", ["D1", "D2", "D3"], default="D1", key="poll_div")
    poll_df = get_data(div_poll, mode="polls")
    st.table(poll_df)

with tab2:
    div_score = st.segmented_control("Division", ["D1", "D2", "D3"], default="D1", key="score_div")
    if st.button("🔄 Refresh Scores"):
        st.cache_data.clear()
    
    score_df = get_data(div_score, mode="scores")
    
    # Display as clean cards
    for _, row in score_df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            col1.write(f"**{row['Matchup']}**")
            col2.write(f"`{row['Score']}`")
            st.caption(f"Status: {row['Status']}")

st.divider()

st.info("Tip: Add this page to your iPhone/Android Home Screen for one-tap access.")

