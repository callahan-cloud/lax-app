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
    # Standard desktop header to get the full table
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Pull overall record
        record = "0-0"
        rec_area = soup.find('div', class_='sidearm-schedule-record')
        if rec_area:
            record = rec_area.get_text(strip=True).split(' ')[0]

        games = []
        # Target the main game rows
        for row in soup.find_all('li', class_='sidearm-schedule-game'):
            
            # 1. DATE - Look for the dedicated date span
            date_el = row.find('div', class_='sidearm-schedule-game-date')
            date_txt = date_el.get_text(" ", strip=True) if date_el else "TBD"
            
            # 2. TIME - Look in the time span OR the result span if game hasn't happened
            time_el = row.find('div', class_='sidearm-schedule-game-time')
            res_el = row.find('div', class_='sidearm-schedule-game-result')
            
            raw_time = ""
            if time_el: raw_time += time_el.get_text(" ", strip=True)
            if res_el: raw_time += " " + res_el.get_text(" ", strip=True)
            
            # Regex to find #:## PM or AM
            time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)', raw_time.upper())
            final_time = time_match.group(1) if time_match else "TBD"
            if "NOON" in raw_time.upper(): final_time = "12:00 PM"

            # 3. OPPONENT
            opp_el = row.find('div', class_='sidearm-schedule-game-opponent-name')
            opp_txt = opp_el.get_text(strip=True) if opp_el else "Unknown"
            
            # 4. VENUE & CLEANUP
            away = row.find('span', class_='sidearm-schedule-game-location-is-away')
            venue = "Away" if away or "@" in opp_txt else "Home"
            opp_txt = opp_txt.replace("@", "").replace("Opponent:", "").strip()

            # 5. STATUS (W/L or Scheduled)
            status = "Scheduled"
            if res_el:
                res_text = res_el.get_text(strip=True)
                if any(x in res_text for x in ['W,', 'L,']):
                    status = res_text
            
            games.append({
                "Date": date_txt,
                "Time": final_time,
                "Venue": venue,
                "Opponent": opp_txt,
                "Status": status
            })

        df = pd.DataFrame(games).drop_duplicates()
        return record, df
    except Exception as e:
        return f"Err: {e}", pd.DataFrame()

# --- UI ---
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
    c2.metric("Total Games", len(df))

    # Bold, clean styling for iPhone
    def highlight(val):
        if 'W' in str(val): return 'background-color: #166534; color: white; font-weight: bold;'
        if 'L' in str(val): return 'background-color: #991b1b; color: white; font-weight: bold;'
        if val == "Away": return 'color: #b45309; font-weight: bold;'
        return ''

    st.dataframe(df.style.applymap(highlight), use_container_width=True, hide_index=True)
else:
    st.error("Data refresh failed. Checking connection...")

st.divider()
st.caption(f"Last sync: {datetime.now().strftime('%m/%d/%Y %I:%M %p')}")
