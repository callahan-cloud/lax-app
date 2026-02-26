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
def get_data(div, mode="scores"):
    # We use a mobile headers to ensure the site serves us the clean version
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    }
    
    if mode == "polls":
        # Pulling Rankings (Example: USILA/NCAA structure)
        url = "https://usila.org/" 
        try:
            tables = pd.read_html(requests.get(url, headers=headers).text)
            idx = {"D1": 0, "D2": 1, "D3": 2}
            return tables[idx[div]].head(20)[['Rank', 'Team', 'Points']]
        except:
            return pd.DataFrame({"Rank": ["N/A"], "Team": ["Polls updating..."], "Points": ["-"]})

    else:
        # Pulling Live Scores from Inside Lacrosse
        url = f"https://www.insidelacrosse.com/ncaa/m/{div[1]}/2026/scores"
        try:
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            games = []
            
            # This targets the specific score containers on the page
            for card in soup.find_all('div', class_='game-score-card'):
                teams = card.find_all('div', class_='team-name')
                scores = card.find_all('div', class_='team-score')
                status = card.find('div', class_='game-status')
                
                if len(teams) >= 2:
                    games.append({
                        "Matchup": f"{teams[0].text.strip()} @ {teams[1].text.strip()}",
                        "Score": f"{scores[0].text.strip()} - {scores[1].text.strip()}",
                        "Status": status.text.strip() if status else "Scheduled"
                    })
            return pd.DataFrame(games)
        except:
            return pd.DataFrame({"Matchup": ["No live games found"], "Score": ["-"], "Status": ["Check back soon"]})

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
