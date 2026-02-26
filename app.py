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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    
    try:
        if mode == "polls":
            # USILA often changes their homepage structure
            url = "https://usila.org/"
            response = requests.get(url, headers=headers, timeout=15)
            
            # This is the "Magic" line: we tell pandas to use the 'lxml' engine explicitly
            tables = pd.read_html(response.text, flavor='lxml')
            
            # Map Table Index (D1 is usually the first table found)
            idx_map = {"D1": 0, "D2": 1, "D3": 2}
            target_idx = idx_map.get(div, 0)
            
            if len(tables) > target_idx:
                df = tables[target_idx].copy()
                # Clean up column names to avoid "Unnamed" errors
                df.columns = [f"Col_{i}" for i in range(len(df.columns))]
                # Rename the ones we want
                df = df.rename(columns={"Col_0": "Rank", "Col_1": "Team", "Col_2": "Record/Pts"})
                return df[["Rank", "Team", "Record/Pts"]].head(20)
            
            return pd.DataFrame()

        else:
            # Scoreboard Logic (Inside Lacrosse)
            # Use the division number from the selection (e.g., 'D1' -> '1')
            d_num = div[1]
            url = f"https://www.insidelacrosse.com/ncaa/m/{d_num}/2026/scores"
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            games = []
            # IL uses 'game-row' or 'score-card' depending on mobile/desktop view
            for card in soup.find_all('div', class_=lambda x: x and ('game' in x or 'score' in x)):
                names = [n.text.strip() for n in card.find_all(class_=lambda x: x and 'name' in x)]
                pts = [p.text.strip() for p in card.find_all(class_=lambda x: x and 'score' in x)]
                
                if len(names) >= 2:
                    games.append({
                        "Matchup": f"{names[0]} @ {names[1]}",
                        "Score": f"{pts[0]}-{pts[1]}" if len(pts) >= 2 else "TBD",
                        "Status": "Final" if "Final" in card.text else "Live/Scheduled"
                    })
            return pd.DataFrame(games)

    except Exception as e:
        # This will show you the ACTUAL error in the app UI for debugging
        st.error(f"Debug Info: {str(e)}")
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

