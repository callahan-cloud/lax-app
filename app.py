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
    # Hardened headers to bypass NCAA bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.ncaa.com/",
        "Origin": "https://www.ncaa.com"
    }
    
    div_map = {"D1": "1", "D2": "2", "D3": "3"}
    d_num = div_map.get(div, "1")

    try:
        if mode == "polls":
            # Using the specific USILA coaches poll path
            url = f"https://data.ncaa.com/casablanca/rankings/lacrosse-men/d{d_num}/usila-coaches-poll/data.json"
            resp = requests.get(url, headers=headers, timeout=10)
            
            # Safety check: if it's not JSON, it will raise an error here
            data = resp.json()
            
            poll_list = []
            for item in data.get('rankings', []):
                poll_list.append({
                    "Rank": item.get('current_rank', '-'),
                    "Team": item.get('name', 'Unknown'),
                    "Record": item.get('record', '-')
                })
            return pd.DataFrame(poll_list)

        else:
            # Scoreboard Logic
            # Note: We use today's date based on the system (Feb 26, 2026)
            url = f"https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d{d_num}/2026/02/26/scoreboard.json"
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                return pd.DataFrame(columns=["Matchup", "Score", "Status"])
                
            data = resp.json()
            games_list = []
            for g in data.get('games', []):
                # Digging into the NCAA's complex JSON structure
                home = g['game']['home']['names']['short']
                away = g['game']['away']['names']['short']
                h_score = g['game']['home']['score']
                a_score = g['game']['away']['score']
                status = g['game']['gameState']
                
                games_list.append({
                    "Matchup": f"{away} @ {home}",
                    "Score": f"{a_score} - {h_score}",
                    "Status": status
                })
            return pd.DataFrame(games_list)

    except Exception as e:
        # Instead of crashing, we show the error and return an empty table
        st.error(f"Waiting for Data: {div} {mode} might not be updated yet.")
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





