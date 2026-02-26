import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# 1. Page Configuration
st.set_page_config(page_title="LaxScore Hub", layout="centered", page_icon="🥍")

# 2. Dynamic Data Fetching
def get_data(div_choice, mode="polls"):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.ncaa.com/",
    }
    
    div_path = {"D1": "d1", "D2": "d2", "D3": "d3"}[div_choice]
    
    # Get Today's Date for the Scoreboard
    tz = pytz.timezone('US/Eastern')
    today = datetime.now(tz)
    date_str = today.strftime("%Y/%m/%d") # Format: 2026/02/26

    try:
        if mode == "polls":
            # Direct USILA Coaches Poll Path
            url = f"https://data.ncaa.com/casablanca/rankings/lacrosse-men/{div_path}/usila-coaches-poll/data.json"
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            # NCAA JSONs often nest data under 'rankings'
            raw_data = data.get('rankings', [])
            if not raw_data:
                return pd.DataFrame()
                
            poll_list = []
            for item in raw_data:
                poll_list.append({
                    "Rank": item.get('current_rank', '-'),
                    "Team": item.get('name', 'Unknown'),
                    "Record": item.get('record', '-')
                })
            return pd.DataFrame(poll_list)

        else:
            # Scoreboard Logic - Using the dynamic date
            url = f"https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/{div_path}/{date_str}/scoreboard.json"
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                return pd.DataFrame() # No games today
            
            data = resp.json()
            games = []
            for g in data.get('games', []):
                game_info = g.get('game', {})
                games.append({
                    "Matchup": f"{game_info['away']['names']['short']} @ {game_info['home']['names']['short']}",
                    "Score": f"{game_info['away']['score']} - {game_info['home']['score']}",
                    "Status": game_info.get('gameState', 'Scheduled')
                })
            return pd.DataFrame(games)

    except Exception as e:
        # This will show you exactly what is failing in the background
        st.sidebar.error(f"Debug: {str(e)}")
        return pd.DataFrame()

# 3. UI Construction
st.title("🥍 LaxScore Hub")

tab1, tab2 = st.tabs(["📊 Polls", "⏱️ Scores"])

with tab1:
    p_div = st.segmented_control("Division", ["D1", "D2", "D3"], default="D1", key="p")
    p_df = get_data(p_div, mode="polls")
    if not p_df.empty:
        st.table(p_df)
    else:
        st.warning(f"No {p_div} Poll data found. The NCAA may be updating their server.")

with tab2:
    s_div = st.segmented_control("Division", ["D1", "D2", "D3"], default="D1", key="s")
    s_df = get_data(s_div, mode="scores")
    if not s_df.empty:
        for _, row in s_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{row['Matchup']}**")
                col2.write(f"`{row['Score']}`")
                st.caption(f"Status: {row['Status']}")
    else:
        st.info(f"No {s_div} games scheduled for today ({datetime.now(pytz.timezone('US/Eastern')).strftime('%b %d')}).")

# 4. Refresh & Timestamp
st.divider()
now = datetime.now(pytz.timezone('US/Eastern'))
st.caption(f"Last Sync: {now.strftime('%I:%M %p')} ET")
if st.button("🔄 Force Refresh"):
    st.cache_data.clear()
