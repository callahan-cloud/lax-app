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
    # Using a Session makes the "handshake" with the website more reliable
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    try:
        if mode == "polls":
            # USILA direct links for 2026
            div_map = {
                "D1": "https://usila.org/sports/2022/2/10/div-i-mens-poll.aspx",
                "D2": "https://usila.org/sports/2022/2/10/div-ii-mens-poll.aspx",
                "D3": "https://usila.org/sports/2022/2/10/div-iii-mens-poll.aspx"
            }
            url = div_map[div]
            
            response = session.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Target the specific table rows in the USILA 'sidearm' stats layout
            rows = soup.find_all('tr')
            poll_data = []
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    rank = cols[0].get_text(strip=True)
                    # Only grab rows where the first column is a number (the Rank)
                    if rank.isdigit():
                        poll_data.append({
                            "Rank": rank,
                            "Team": cols[1].get_text(strip=True),
                            "Record/Pts": cols[2].get_text(strip=True) if len(cols) > 2 else "-"
                        })
            
            return pd.DataFrame(poll_data).head(20)

        else:
            # Inside Lacrosse Scoreboard
            d_num = div[1]
            url = f"https://www.insidelacrosse.com/ncaa/m/{d_num}/2026/scores"
            resp = session.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            games = []
            # Updated selectors for the 2026 IL Layout
            for card in soup.select('.game-score-card, .score-strip, .event-card'):
                names = [n.get_text(strip=True) for n in card.select('.team-name, .name')]
                scores = [s.get_text(strip=True) for s in card.select('.team-score, .score')]
                status = card.select_one('.game-status, .status, .time')
                
                if len(names) >= 2:
                    games.append({
                        "Matchup": f"{names[0]} @ {names[1]}",
                        "Score": f"{scores[0]}-{scores[1]}" if len(scores) >= 2 else "TBD",
                        "Status": status.get_text(strip=True) if status else "Scheduled"
                    })
            return pd.DataFrame(games)

    except Exception as e:
        # This will print the actual error to your app screen so we can see it
        st.error(f"⚠️ Connection Issue: {str(e)}")
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



