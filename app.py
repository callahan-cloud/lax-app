import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="LaxScore Clean", layout="centered", page_icon="🥍")

st.title("🥍 LaxScore Hub")
st.caption("Real-time D1, D2, & D3 Data | Ad-Free")

# 2. Advanced Scraper with Error Handling
def get_data(div, mode="polls"):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }
    
    # Map 'D1' to the NCAA's internal numbering
    div_map = {"D1": "1", "D2": "2", "D3": "3"}
    d_num = div_map.get(div, "1")

    try:
        if mode == "polls":
            # Direct link to the official NCAA Rankings JSON (Fast & Reliable)
            url = f"https://data.ncaa.com/casablanca/rankings/lacrosse-men/d{d_num}/usila-coaches-poll/data.json"
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            poll_list = []
            for item in data['rankings']:
                poll_list.append({
                    "Rank": item['current_rank'],
                    "Team": item['name'],
                    "Record": item.get('record', '-')
                })
            return pd.DataFrame(poll_list)

        else:
            # Direct link to the NCAA Scoreboard JSON
            # This is the "Gold Standard" for live scores
            url = f"https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d{d_num}/2026/02/26/scoreboard.json"
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            games = []
            for game in data.get('games', []):
                game_info = game.get('game', {})
                games.append({
                    "Matchup": f"{game_info['away']['names']['short']} @ {game_info['home']['names']['short']}",
                    "Score": f"{game_info['away']['score']} - {game_info['home']['score']}",
                    "Status": game_info.get('gameState', 'Scheduled')
                })
            return pd.DataFrame(games)

    except Exception as e:
        st.error(f"⚠️ Data Feed Issue: {str(e)}")
        return pd.DataFrame()
# 3. The UI
tab1, tab2 = st.tabs(["📊 Top 20 Polls", "⏱️ Live Scoreboard"])

with tab1:
    div_poll = st.pills("Division", ["D1", "D2", "D3"], default="D1", key="p_div")
    poll_df = get_data(div_poll, mode="polls")
    
    if not poll_df.empty:
        st.dataframe(poll_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Could not load polls. The source site might be down.")

with tab2:
    div_score = st.pills("Division", ["D1", "D2", "D3"], default="D1", key="s_div")
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
    
    score_df = get_data(div_score, mode="scores")
    
    # THE FIX: Check if the dataframe is empty before looping
    if isinstance(score_df, pd.DataFrame) and not score_df.empty:
        for _, row in score_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{row['Matchup']}**")
                col2.write(f"`{row['Score']}`")
                st.caption(f"Status: {row['Status']}")
    else:
        st.info(f"No live {div_score} scores found for today. Check back during game time!")

st.divider()
st.caption("Built for Lax Fans. No Ads. No BS.")




