import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="LaxScore Clean", layout="centered", page_icon="🥍")

st.title("🥍 LaxScore Hub")
st.caption("Real-time D1, D2, & D3 Data | Ad-Free")

# 2. Advanced Scraper with Error Handling
def get_data(div, mode="scores"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        if mode == "polls":
            # Target USILA Polls
            url = "https://usila.org/"
            response = requests.get(url, headers=headers, timeout=10)
            tables = pd.read_html(response.text)
            
            # Select table based on Division
            idx = {"D1": 0, "D2": 1, "D3": 2}
            df = tables[idx[div]].copy()
            
            # Clean up: USILA tables vary, so we force standard column names
            df.columns = [str(c) for c in df.columns] # Ensure strings
            return df.iloc[:, :3] # Just take first 3 columns (Rank, Team, Points/Record)

        else:
            # Target Live Scores
            # Note: Division 1 is '1', Division 2 is '2', etc.
            div_num = div[1] 
            url = f"https://www.insidelacrosse.com/ncaa/m/{div_num}/2026/scores"
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            games = []
            # Updated selector to be more broad to catch different site layouts
            for card in soup.select('div[class*="game-score"], div[class*="game-card"]'):
                try:
                    teams = [t.text.strip() for t in card.select('div[class*="team-name"]')]
                    scores = [s.text.strip() for s in card.select('div[class*="score"]')]
                    status = card.select_one('div[class*="status"]')
                    
                    if len(teams) >= 2:
                        games.append({
                            "Matchup": f"{teams[0]} vs {teams[1]}",
                            "Score": f"{scores[0]} - {scores[1]}" if len(scores) >= 2 else "TBD",
                            "Status": status.text.strip() if status else "Scheduled"
                        })
                except:
                    continue
            
            return pd.DataFrame(games)

    except Exception as e:
        # Return an empty dataframe with a note instead of crashing
        return pd.DataFrame(columns=["Matchup", "Score", "Status"])

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
