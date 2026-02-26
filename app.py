import streamlit as st
import pandas as pd
import requests

# 1. PAGE SETUP
st.set_page_config(page_title="LaxScore 2026", layout="centered", page_icon="🥍")

# 2. DATA SOURCE: NCAA DATA FEED (MORE STABLE THAN SCRAPING)
def get_ncaa_data(div_path, mode="rankings"):
    """
    Fetches official NCAA JSON data. 
    This is much harder for them to block than web scraping.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    if mode == "rankings":
        # The official USILA Coaches Poll path on NCAA servers
        url = f"https://data.ncaa.com/casablanca/rankings/lacrosse-men/{div_path}/usila-coaches-poll/data.json"
    else:
        # Today's Scoreboard
        url = f"https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/{div_path}/2026/02/26/scoreboard.json"

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return pd.DataFrame()
        
        data = r.json()
        
        if mode == "rankings":
            ranks = data.get('rankings', [])
            return pd.DataFrame([{
                "Rank": i.get('current_rank'),
                "Team": i.get('name'),
                "Record": i.get('record'),
                "Points": i.get('points')
            } for i in ranks])
        else:
            games = data.get('games', [])
            return pd.DataFrame([{
                "Matchup": f"{g['game']['away']['names']['short']} @ {g['game']['home']['names']['short']}",
                "Score": f"{g['game']['away']['score']} - {g['game']['home']['score']}",
                "Status": g['game']['gameState']
            } for g in games])
    except:
        return pd.DataFrame()

# 3. UI DESIGN
st.title("🥍 LaxScore 2026")
div = st.sidebar.selectbox("Division", ["D1", "D2", "D3"])
div_path = div.lower()

tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "⏱️ Scores", "🔥 Top 20 Games"])

# FETCH DATA
rank_df = get_ncaa_data(div_path, "rankings")
score_df = get_ncaa_data(div_path, "scoreboard")

with tab1:
    if not rank_df.empty:
        st.dataframe(rank_df, hide_index=True, use_container_width=True)
    else:
        st.warning("Official Poll is updating. Please check back in a few minutes.")

with tab2:
    st.link_button("📺 Watch Live on ESPN+", "https://plus.espn.com/", use_container_width=True)
    if not score_df.empty:
        for _, row in score_df.iterrows():
            with st.container(border=True):
                st.write(f"**{row['Matchup']}**")
                st.caption(f"Score: {row['Score']} ({row['Status']})")
    else:
        st.info("No games scheduled for today.")

with tab3:
    if not rank_df.empty and not score_df.empty:
        top_20 = rank_df['Team'].head(20).tolist()
        found = False
        for _, row in score_df.iterrows():
            if any(t in row['Matchup'] for t in top_20):
                found = True
                with st.container(border=True):
                    st.write(f"🏆 **{row['Matchup']}**")
                    st.write(f"Score: {row['Score']}")
        if not found: st.write("No Top 20 matchups today.")
