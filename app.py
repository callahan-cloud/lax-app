import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- TOP 20 SCHOOLS MAPPING (SIDEARM SPORTS SITES) ---
SCHOOL_DATA = {
    "D1": {
        "Notre Dame": "https://fightingirish.com/sports/mlax/schedule/season/2026/",
        "North Carolina": "https://goheels.com/sports/mens-lacrosse/schedule/2026",
        "Cornell": "https://cornellbigred.com/sports/mens-lacrosse/schedule/2026",
        "Richmond": "https://richmondspiders.com/sports/mens-lacrosse/schedule/2026",
        "Duke": "https://goduke.com/sports/mens-lacrosse/schedule/2026",
        "Harvard": "https://gocrimson.com/sports/mens-lacrosse/schedule/2026",
        "Syracuse": "https://cuse.com/sports/mens-lacrosse/schedule/2026",
        "Army": "https://goarmywestpoint.com/sports/mens-lacrosse/schedule/2026",
        "Ohio State": "https://ohiostatebuckeyes.com/sports/mens-lacrosse/schedule/2026",
        "Princeton": "https://goprincetontigers.com/sports/mens-lacrosse/schedule/2026",
        "Georgetown": "https://guhoyas.com/sports/mens-lacrosse/schedule/2026",
        "Maryland": "https://umterps.com/sports/mens-lacrosse/schedule/2026",
        "Virginia": "https://virginiasports.com/sports/mens-lacrosse/schedule/2026",
        "Rutgers": "https://scarletknights.com/sports/mens-lacrosse/schedule/2026",
        "Penn State": "https://gopsusports.com/sports/mens-lacrosse/schedule/2026",
        "Johns Hopkins": "https://hopkinssports.com/sports/mens-lacrosse/schedule/2026",
        "Denver": "https://denverpioneers.com/sports/mens-lacrosse/schedule/2026",
        "Saint Joseph's": "https://sjuhawks.com/sports/mens-lacrosse/schedule/2026",
        "Penn": "https://pennathletics.com/sports/mens-lacrosse/schedule/2026",
        "Albany": "https://ualbanysports.com/sports/mens-lacrosse/schedule/2026"
    },
    "D3": {
        "Tufts": "https://gotuftsjumbos.com/sports/mens-lacrosse/schedule/2026",
        "Salisbury": "https://suseagulls.com/sports/mens-lacrosse/schedule/2026",
        "Christopher Newport": "https://cnusports.com/sports/mens-lacrosse/schedule/2026",
        "RIT": "https://ritathletics.com/sports/mens-lacrosse/schedule/2026",
        "Bowdoin": "https://athletics.bowdoin.edu/sports/mens-lacrosse/schedule/2026",
        "York": "https://ycpspartans.com/sports/mens-lacrosse/schedule/2026",
        "Stevens": "https://stevensducks.com/sports/mens-lacrosse/schedule/2026",
        "Gettysburg": "https://gettysburgsports.com/sports/mens-lacrosse/schedule/2026",
        "Cortland": "https://www.cortlandreddragons.com/sports/mens-lacrosse/schedule/2026",
        "St. Lawrence": "https://saintsathletics.com/sports/mens-lacrosse/schedule/2026",
        "Dickinson": "https://dickinsonathletics.com/sports/mens-lacrosse/schedule/2026",
        "Washington and Lee": "https://generalssports.com/sports/mens-lacrosse/schedule/2026",
        "Amherst": "https://athletics.amherst.edu/sports/mens-lacrosse/schedule/2026",
        "Lynchburg": "https://www.lynchburgsports.com/sports/mlax/schedule/2025-26",
        "RPI": "https://rpiathletics.com/sports/mens-lacrosse/schedule/2026",
        "Swarthmore": "https://swarthmoreathletics.com/sports/mens-lacrosse/schedule/2026",
        "St. John Fisher": "https://athletics.sjf.edu/sports/mens-lacrosse/schedule/2026",
        "Middlebury": "https://athletics.middlebury.edu/sports/mens-lacrosse/schedule/2026",
        "Babson": "https://babsonathletics.com/sports/mens-lacrosse/schedule/2026"
    }
}

def get_school_scores(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        games = []
        for item in soup.select('.sidearm-schedule-game'):
            opponent = item.select_one('.sidearm-schedule-game-opponent-name')
            date = item.select_one('.sidearm-schedule-game-upcoming-date')
            result = item.select_one('.sidearm-schedule-game-result')
            
            if opponent:
                opp_name = opponent.get_text(strip=True)
                game_date = date.get_text(strip=True) if date else "TBD"
                # Clean up the score/result text
                game_res = result.get_text(strip=True).replace('\n', ' ') if result else "Upcoming"
                games.append({"Date": game_date, "Opponent": opp_name, "Result": game_res})
        return pd.DataFrame(games)
    except:
        return pd.DataFrame()

# --- STREAMLIT UI ---
st.set_page_config(page_title="LaxTracker Top 20", page_icon="🥍")
st.title("🥍 Official Top 20 Tracker")

# 1. Sidebar Selections
div_choice = st.sidebar.radio("Select Division", ["D1", "D3"])
team_list = list(SCHOOL_DATA[div_choice].keys())
target_team = st.sidebar.selectbox("Choose Team", team_list)

# 2. Tabs
tab1, tab2 = st.tabs(["📊 Schedule & Results", "📺 ESPN+ Hub"])

with tab1:
    st.subheader(f"{target_team} 2026 Tracker")
    url = SCHOOL_DATA[div_choice][target_team]
    
    with st.spinner(f"Scraping {target_team} Athletics..."):
        df = get_school_scores(url)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error("This school's site format is unique or blocked. Check 'Watch Live' for scores.")

with tab2:
    st.link_button("📺 Open ESPN+ Lacrosse Hub", 
                   "https://www.espn.com/watch/catalog/7783307b-8c43-34e4-96d5-a8c62c99c758/lacrosse",
                   use_container_width=True, type="primary")

st.sidebar.markdown("---")
st.sidebar.caption("Data pulled directly from school athletic departments.")
