import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- FULL TOP 20 DIRECTORY (FEB 2026) ---
SCHOOL_DATA = {
    "D1": {
        "Notre Dame": "https://fightingirish.com/sports/mlax/schedule/",
        "North Carolina": "https://goheels.com/sports/mens-lacrosse/schedule/text",
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
        "Wesleyan": "https://athletics.wesleyan.edu/sports/mens-lacrosse/schedule/2026",
        "York": "https://ycpspartans.com/sports/mens-lacrosse/schedule/2026",
        "Stevens": "https://stevensducks.com/sports/mens-lacrosse/schedule/2026",
        "Gettysburg": "https://gettysburgsports.com/sports/mens-lacrosse/schedule/2026",
        "SUNY Cortland": "https://www.cortlandreddragons.com/sports/mens-lacrosse/schedule/2026",
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

def get_school_scores(url, school_name):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        games = []

        # 1. UNC TEXT-ONLY LOGIC (Targeted for the tabular /text layout)
        if "goheels.com" in url and "/text" in url:
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:] # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        date = cols[0].text.strip()
                        opponent = cols[3].text.strip() # The "Opponent" column
                        result = cols[6].text.strip() if cols[6].text.strip() else "Scheduled"
                        games.append({"Date": date, "Opponent": opponent, "Result": result})

        # 2. NOTRE DAME LOGIC (WMT)
        elif "fightingirish.com" in url:
            for item in soup.select('.c-event-card'):
                opp = item.select_one('.c-event-card__opponent')
                res = item.select_one('.c-event-card__score')
                date = item.select_one('.c-event-card__date')
                if opp:
                    games.append({
                        "Date": date.text.strip() if date else "TBD",
                        "Opponent": opp.text.strip(), 
                        "Result": res.text.strip() if res else "Upcoming"
                    })

        # 3. STANDARD SIDEARM LOGIC
        else:
            for item in soup.select('.sidearm-schedule-game'):
                opp = item.select_one('.sidearm-schedule-game-opponent-name')
                res = item.select_one('.sidearm-schedule-game-result')
                date = item.select_one('.sidearm-schedule-game-upcoming-date')
                if opp:
                    games.append({
                        "Date": date.text.strip() if date else "2026",
                        "Opponent": opp.text.strip(), 
                        "Result": res.text.strip() if res else "Upcoming"
                    })
        
        return pd.DataFrame(games).drop_duplicates()
    except Exception as e:
        return pd.DataFrame()

# --- UI ---
st.set_page_config(page_title="LaxTracker Pro", layout="centered", page_icon="🥍")
st.title("🥍 Official Top 20 Tracker")

div_choice = st.sidebar.radio("Select Division", ["D1", "D3"])
target_team = st.sidebar.selectbox("Choose Team", list(SCHOOL_DATA[div_choice].keys()))

tab1, tab2 = st.tabs(["📅 Live Schedule", "📺 ESPN Scoreboard"])

with tab1:
    url = SCHOOL_DATA[div_choice][target_team]
    st.subheader(f"{target_team} Results")
    with st.spinner("Syncing with school athletics..."):
        df = get_school_scores(url, target_team)
        if not df.empty:
            st.table(df)
        else:
            st.error("Live sync unavailable for this school.")
            st.link_button(f"🔗 View {target_team} Schedule", url)

with tab2:
    st.info("Direct link to today's NCAA Men's Lacrosse scoreboard.")
    st.link_button("📺 Open ESPN Lacrosse Scoreboard", 
                   "https://www.espn.com/mens-college-lacrosse/scoreboard", 
                   use_container_width=True, type="primary")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Direct from school athletic departments.")
