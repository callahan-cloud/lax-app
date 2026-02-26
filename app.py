import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# 1. Page Configuration for Mobile
st.set_page_config(page_title="LaxScore Clean", layout="centered", page_icon="🥍")

# Custom CSS for a clean, dark sports interface
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1e2129; 
        border-radius: 5px; 
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Hardened Data Fetching Logic
def get_data(div_choice, mode="polls"):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.ncaa.com/",
        "Accept": "application/json"
    }
    
    # Map selection to NCAA URL segments
    div_path = {"D1": "d1", "D2": "d2", "D3": "d3"}[div_choice]
    
    try:
        if mode == "polls":
            # Target the USILA Coaches Poll JSON
            url = f"https://data.ncaa.com/casablanca/rankings/lacrosse-men/{div_path}/usila-coaches-poll/data.json"
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            # The "Full List" is usually in the 'rankings' key
            # If that's missing, we check 'ranks' or the general data object
            raw_list = data.get('rankings', data.get('ranks', []))
            
            poll_results = []
            for item in raw_list:
                poll_results.append({
                    "Rank": item.get('current_rank', item.get('rank', '-')),
                    "Team": item.get('name', item.get('school', 'Unknown')),
                    "Points": item.get('points', '-'),
                    "Record": item.get('record', '-')
                })
            return pd.DataFrame(poll_results)

        else:
            # Scoreboard Logic (Set for today: Feb 26, 2026)
            url = f"https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/{div_path}/2026/02/26/scoreboard.json"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200: return pd.DataFrame()
            
            data = resp.json()
            games = []
            for g in data.get('games', []):
                game_data = g.get('game', {})
                games.append({
                    "Matchup": f"{game_data['away']['names']['short']} @ {game_data['home']['names']['short']}",
                    "Score": f"{game_data['away']['score']} - {game_data['home']['score']}",
                    "Status": game_data.get('gameState', 'Scheduled')
                })
            return pd.DataFrame(games)

    except Exception:
        return pd.DataFrame()

# 3. Main UI App Layout
st.title("🥍 LaxScore Clean")

tab1, tab2 = st.tabs(["📊 Top 20 Polls", "⏱️ Live Scores"])

with tab1:
    poll_div = st.segmented_control("Select Division", ["D1", "D2", "D3"], default="D1", key="p_div")
    df_poll = get_data(poll_div, mode="polls")
    
    if not df_poll.empty:
        st.dataframe(df_poll, use_container_width=True, hide_index=True)
    else:
        st.info(f"The {poll_div} Poll is currently updating. Check back shortly.")

with tab2:
    score_div = st.segmented_control("Select Division", ["D1", "D2", "D3"], default="D1", key="s_div")
    if st.button("🔄 Refresh Scores"):
        st.cache_data.clear()
        
    df_scores = get_data(score_div, mode="scores")
    
    if not df_scores.empty:
        for _, row in df_scores.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{row['Matchup']}**")
                c2.write(f"`{row['Score']}`")
                st.caption(f"Status: {row['Status']}")
    else:
        st.info(f"No live {score_div} games found for today.")

# 4. Footer with Time Stamp
st.divider()
# Use Eastern Time for US Lacrosse standard
now = datetime.now(pytz.timezone('US/Eastern'))
st.caption(f"Last Sync: {now.strftime('%b %d, %I:%M %p')} ET")
st.caption("Data: NCAA/USILA Coaches Poll. No Ads.")
