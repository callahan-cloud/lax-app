import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- DATA SCRAPERS ---

def get_rankings(div_id):
    url = f"https://www.laxnumbers.com/ratings.php?v={div_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        df_list = pd.read_html(url)
        df = df_list[0]
        return df[['Rank', 'Team', 'Record', 'Rating']]
    except:
        return pd.DataFrame()

def get_scores(div_id):
    url = f"https://www.laxnumbers.com/scoreboard/{div_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        games = []
        for game in soup.find_all('div', class_='row mb-2'):
            teams = game.find_all('div', class_='col-8')
            scores = game.find_all('div', class_='col-4')
            if teams:
                matchup = teams[0].get_text(strip=True)
                res = scores[0].get_text(strip=True) if scores else "Scheduled"
                games.append({"Matchup": matchup, "Status": res})
        return pd.DataFrame(games)
    except:
        return pd.DataFrame()

# --- APP LAYOUT ---

st.set_page_config(page_title="LaxScore Elite", layout="centered", page_icon="🥍")
st.title("🥍 LaxScore Elite Hub")

div_choice = st.sidebar.selectbox("Division", ["D1", "D2", "D3"])
div_map = {"D1": "401", "D2": "402", "D3": "403"}
current_id = div_map[div_choice]

tab1, tab2, tab3 = st.tabs(["📊 Top 25", "⏱️ All Scores", "🔥 Top Matchups"])

# PRE-FETCH DATA (To avoid multiple requests)
rank_df = get_rankings(current_id)
score_df = get_scores(current_id)

with tab1:
    st.subheader(f"{div_choice} Power Rankings")
    if not rank_df.empty:
        st.table(rank_df.head(25))

with tab2:
    st.subheader(f"Full {div_choice} Scoreboard")
    st.link_button("📺 Watch Live on ESPN+", "https://www.espn.com/watch/catalog/7783307b-8c43-34e4-96d5-a8c62c99c758/lacrosse", use_container_width=True)
    if not score_df.empty:
        for _, row in score_df.iterrows():
            with st.container(border=True):
                st.write(f"**{row['Matchup']}**")
                st.caption(f"Result: {row['Status']}")

with tab3:
    st.subheader("🔥 Top 20 Matchups")
    st.info("Showing games where at least one team is in the Top 20.")
    
    if not rank_df.empty and not score_df.empty:
        # Get list of top 20 team names
        top_20_teams = rank_df['Team'].head(20).tolist()
        
        found_matchup = False
        for _, row in score_df.iterrows():
            # Check if any top 20 team name is mentioned in the matchup string
            if any(team.lower() in row['Matchup'].lower() for team in top_20_teams):
                found_matchup = True
                with st.container(border=True):
                    st.write(f"🏆 **{row['Matchup']}**")
                    st.write(f"Score/Time: `{row['Status']}`")
        
        if not found_matchup:
            st.write("No ranked teams playing today.")
    else:
        st.write("Data currently unavailable for Top 20 filtering.")

st.sidebar.markdown("---")
st.sidebar.caption("Data: LaxNumbers.com")
