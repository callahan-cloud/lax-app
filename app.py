import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- ADVANCED STEALTH SCRAPER ---

def get_html(url):
    # This header is the 'Secret Sauce'—it looks exactly like a real iPhone
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    try:
        session = requests.Session()
        resp = session.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.text
        return None
    except:
        return None

def get_rankings(div_id):
    url = f"https://www.laxnumbers.com/ratings.php?y=2026&v={div_id}"
    html = get_html(url)
    if not html: return pd.DataFrame()
    
    try:
        # We manually find the table to ensure it exists
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        if not table: return pd.DataFrame()
        
        df = pd.read_html(str(table))[0]
        # Standardizing column names for LaxNumbers 2026
        df.columns = [str(c).strip() for c in df.columns]
        return df[['Rank', 'Team', 'Record', 'Rating']]
    except:
        return pd.DataFrame()

def get_scores(div_id):
    url = f"https://www.laxnumbers.com/scoreboard/{div_id}"
    html = get_html(url)
    if not html: return pd.DataFrame()
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        games = []
        # LaxNumbers 2026 uses 'row mb-2' for their scoreboard rows
        for row in soup.find_all('div', class_='row mb-2'):
            cols = row.find_all('div')
            if len(cols) >= 2:
                matchup = cols[0].get_text(strip=True).replace("@", " @ ")
                status = cols[1].get_text(strip=True)
                games.append({"Matchup": matchup, "Status/Score": status})
        return pd.DataFrame(games)
    except:
        return pd.DataFrame()

# --- MOBILE UI ---

st.set_page_config(page_title="LaxTracker", layout="centered", page_icon="🥍")

st.title("🥍 LaxScore Hub")
div_choice = st.sidebar.selectbox("Division", ["D1", "D2", "D3"])
div_map = {"D1": "401", "D2": "402", "D3": "403"}
current_id = div_map[div_choice]

tab1, tab2, tab3 = st.tabs(["📊 Top 25", "⏱️ Scores", "🔥 Ranked"])

# Fetching Data
with st.spinner('Syncing with LaxNumbers...'):
    rank_df = get_rankings(current_id)
    score_df = get_scores(current_id)

with tab1:
    if not rank_df.empty:
        st.table(rank_df.head(25))
    else:
        st.error("Connection blocked by source site. Please try refreshing.")

with tab2:
    st.link_button("📺 ESPN+ Live Streams", "https://www.espn.com/watch/catalog/7783307b-8c43-34e4-96d5-a8c62c99c758/lacrosse", use_container_width=True)
    if not score_df.empty:
        for _, row in score_df.iterrows():
            with st.container(border=True):
                st.write(f"**{row['Matchup']}**")
                st.caption(f"Score: {row['Status/Score']}")
    else:
        st.info("No games detected for today.")

with tab3:
    if not rank_df.empty and not score_df.empty:
        top_20 = rank_df['Team'].head(20).tolist()
        found = False
        for _, row in score_df.iterrows():
            if any(t.lower() in row['Matchup'].lower() for t in top_20):
                found = True
                with st.container(border=True):
                    st.write(f"🏆 **{row['Matchup']}**")
                    st.write(f"Status: `{row['Status/Score']}`")
        if not found: st.write("No Top 20 matchups today.")
    else:
        st.write("Rankings data unavailable for filtering.")
