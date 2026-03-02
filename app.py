import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- 2026 D3 DIRECTORY ---
SCHOOL_DATA = {
    "Men's Lacrosse": {
        "Tufts (#1)": "https://gotuftsjumbos.com/sports/mens-lacrosse/schedule/2026",
        "Salisbury (#2)": "https://suseagulls.com/sports/mens-lacrosse/schedule/2026",
        "Christopher Newport (#3)": "https://cnusports.com/sports/mens-lacrosse/schedule/2026",
        "RIT (#4)": "https://ritathletics.com/sports/mens-lacrosse/schedule/2026",
        "Bowdoin (#5)": "https://athletics.bowdoin.edu/sports/mens-lacrosse/schedule/2026",
        "Wesleyan (#6)": "https://athletics.wesleyan.edu/sports/mens-lacrosse/schedule/2026",
        "York (#7)": "https://ycpspartans.com/sports/mens-lacrosse/schedule/2026",
        "Stevens (#8)": "https://stevensducks.com/sports/mens-lacrosse/schedule/2026",
        "Gettysburg (#9)": "https://gettysburgsports.com/sports/mens-lacrosse/schedule/2026",
        "SUNY Cortland (#10)": "https://www.cortlandreddragons.com/sports/mens-lacrosse/schedule/2026"
    },
    "Women's Lacrosse": {
        "Middlebury (#1)": "https://athletics.middlebury.edu/sports/womens-lacrosse/schedule/2026",
        "Tufts (#2)": "https://gotuftsjumbos.com/sports/womens-lacrosse/schedule/2026",
        "Colby (#3)": "https://colbyathletics.com/sports/womens-lacrosse/schedule/2026",
        "Gettysburg (#4)": "https://gettysburgsports.com/sports/womens-lacrosse/schedule/2026",
        "Wesleyan (#5)": "https://athletics.wesleyan.edu/sports/womens-lacrosse/schedule/2026"
    }
}

def get_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Get Record
        record = "0-0"
        rec_el = soup.select_one('.sidearm-schedule-record, .c-schedule-header__record')
        if rec_el:
            match = re.search(r'(\d+-\d+)', rec_el.get_text())
            if match: record = match.group(1)

        games = []
        for item in soup.select('.sidearm-schedule-game'):
            # 1. DATE
            date_el = item.select_one('.sidearm-schedule-game-date')
            date_txt = date_el.get_text(strip=True) if date_el else "TBD"

            # 2. TIME (The Deep Scrape)
            time_txt = "TBD"
            time_container = item.select_one('.sidearm-schedule-game-time')
            if time_container:
                # Priority 1: Check aria-label (Best for Sidearm)
                time_span = time_container.find('span')
                if time_span and time_span.has_attr('aria-label'):
                    time_txt = time_span['aria-label']
                else:
                    time_txt = time_container.get_text(strip=True)
            
            # Clean "P.M." or "p.m." to "PM"
            time_txt = re.sub(r'\s+', ' ', time_txt)
            time_txt = time_txt.replace('.', '').upper().strip()
            
            # 3. OPPONENT
            opp_el = item.select_one('.sidearm-schedule-game-opponent-name a, .sidearm-schedule-game-opponent-name span')
            opp_txt = opp_el.get_text(strip=True) if opp_el else "Unknown"

            # 4. VENUE
            away_flag = item.select_one('.sidearm-schedule-game-location-is-away')
            venue = "Away" if away_flag or "@" in opp_txt else "Home"
            opp_txt = opp_txt.replace("@", "").strip()

            # 5. STATUS / RESULT
            res_el = item.select_one('.sidearm-schedule-game-result')
            status = res_el.get_text(strip=True) if res_el else "Scheduled"
            if "TBD" in status: status = "Scheduled"

            games.append({
                "Date": date_txt,
                "Time": time_txt,
                "Venue": venue,
                "Opponent": opp_txt,
                "Status": status
            })

        df = pd.DataFrame(games).drop_duplicates()
        return record, df
    except Exception as e:
        return f"Error: {e}", pd.DataFrame()

# --- STREAMLIT UI ---
st.set_page_config(page_title="simple D3 score tracker", layout="wide")

st.sidebar.title("🥍 simple D3 score tracker")
league = st.sidebar.radio("Category", ["Men's Lacrosse", "Women's Lacrosse"])
team = st.sidebar.selectbox("Select Team", list(SCHOOL_DATA[league].keys()))

st.markdown(f"## {team}")
st.markdown("### D3 Score Tracker • 2026 Season")

record, df = get_data(SCHOOL_DATA[league][team])

if not df.empty:
    c1, c2 = st.columns(2)
    c1.metric("Record", record)
    c2.metric("Games", len(df))

    # Apply table styling
    def style_df(s):
        return s.applymap(lambda x: 'color: #b45309; font-weight: bold;' if x == "Away" else '', subset=['Venue'])\
                .applymap(lambda x: 'background-color: #166534; color: white; font-weight: bold;' if 'W' in str(x) else '', subset=['Status'])\
                .applymap(lambda x: 'background-color: #991b1b; color: white; font-weight: bold;' if 'L' in str(x) else '', subset=['Status'])

    st.dataframe(style_df(df.style), use_container_width=True, hide_index=True)
else:
    st.error("Could not fetch data. The website structure may have changed.")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%I:%M %p')}")
