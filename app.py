import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import random

# --- HARDENED SCRAPER ---

def get_stealth_data(url):
    # Rotating User-Agents to confuse the 'Bot Blockers'
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1" # 'Do Not Track' header
    }

    try:
        # Using a timeout so the app doesn't hang forever
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

def get_rankings(div_id):
    # LaxNumbers Ratings Page
    url = f"https://www.laxnumbers.com/ratings.php?v={div_id}"
    html = get_stealth_data(url)
    if not html: return pd.DataFrame()
    
    try:
        # We use 'lxml' or 'html.parser' specifically
        df = pd.read_html(html)[0]
        # Clean up columns to ensure they match our app
        df.columns = [str(c).strip() for c in df.columns]
        return df[['Rank', 'Team', 'Record', 'Rating']].head(25)
    except:
        return pd.DataFrame()

def get_scores(div_id):
    # LaxNumbers Scoreboard Page
    url = f"https://www.laxnumbers.com/scoreboard/{div_id}"
    html = get_stealth_data(url)
    if not html: return pd.DataFrame()
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        games = []
        # Target the specific scoreboard container
        for row in soup.find_all('div', class_='row mb-2'):
            divs = row.find_all('div')
            if len(divs) >= 2:
                matchup = divs[0].get_text(strip=True).replace("@", " @ ")
                score = divs[1].get_text(strip=True)
                games.append({"Matchup": matchup, "Status": score})
        return pd.DataFrame(games)
    except:
        return pd.DataFrame()

# --- APP UI ---

st.set_page_config(page_title="LaxScore Pro", layout="centered", page_icon="🥍")

st.title("🥍 LaxScore Pro Hub")

div_choice = st.sidebar.selectbox("Select Division", ["D1", "D2", "D3"])
div_map = {"D1": "401", "D2": "402", "D3": "403"}
curr_id = div_map[div_choice]

tab1, tab2, tab3 = st.tabs(["📊 Top 25", "⏱️ Scores", "🔥 Ranked"])

# Fetch Data
with st.spinner("Connecting to live feed..."):
    rank_df = get_rankings(curr_id)
    score_df = get_scores(curr_id)

with tab1:
    if not rank_df.empty:
        st.table(rank_df)
    else:
        st.warning("🔄 Source site is busy. Tap 'Refresh' in the sidebar.")

with tab2:
    st.link_button("📺 Open ESPN+ Lax Stream", "https://www.espn.com/mens-college-lacrosse/scoreboard", use_container_width=True)
    if not score_df.empty:
        for _, row in score_df.iterrows():
            with st.container(border=True):
                st.write(f"**{row['Matchup']}**")
                st.caption(f"Score: {row['Status']}")
    else:
        st.info("No games currently live.")

with tab3:
    if not rank_df.empty and not score_df.empty:
        top_20 = rank_df['Team'].head(20).tolist()
        found = False
        for _, row in score_df.iterrows():
            if any(team.lower() in row['Matchup'].lower() for team in top_20):
                found = True
                with st.container(border=True):
                    st.write(f"🏆 **{row['Matchup']}**")
                    st.write(f"Score: `{row['Status']}`")
        if not found: st.write("No Top 20 games today.")
    else:
        st.write("Data sync pending...")

if st.sidebar.button("🔄 Force Refresh Data"):
    st.cache_data.clear()
