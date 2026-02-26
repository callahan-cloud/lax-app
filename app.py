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
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    }
    
    try:
        if mode == "polls":
            # USILA uses different sub-pages for divisions now
            div_path = {"D1": "div-i-mens-poll", "D2": "div-ii-mens-poll", "D3": "div-iii-mens-poll"}
            url = f"https://usila.org/sports/2022/2/10/{div_path[div]}.aspx"
            
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the ranking table rows
            rows = soup.find_all('tr')
            data = []
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Clean the text (remove extra spaces/newlines)
                    rank = cols[0].text.strip()
                    team = cols[1].text.strip()
                    pts = cols[2].text.strip()
                    
                    # Only add if the first column is actually a number (the Rank)
                    if rank.isdigit():
                        data.append({"Rank": rank, "Team": team, "Pts": pts})
            
            return pd.DataFrame(data).head(20)

        else:
            # Scores Logic (Inside Lacrosse)
            d_num = div[1] # Extracts '1' from 'D1'
            url = f"https://www.insidelacrosse.com/ncaa/m/{d_num}/2026/scores"
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            games = []
            # Updated to look for the specific "Score Strip" container
            for card in soup.select('.game-score-card, .score-strip'):
                teams = [t.text.strip() for t in card.select('.team-name, .name')]
                scores = [s.text.strip() for s in card.select('.team-score, .score')]
                status = card.select_one('.game-status, .time')
                
                if len(teams) >= 2:
                    games.append({
                        "Matchup": f"{teams[0]} @ {teams[1]}",
                        "Score": f"{scores[0]}-{scores[1]}" if len(scores) >= 2 else "TBD",
                        "Status": status.text.strip() if status else "Scheduled"
                    })
            return pd.DataFrame(games)

    except Exception as e:
        st.error(f"Scraper Error: {str(e)}")
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


