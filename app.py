import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- 2026 D3 TOP 20 DIRECTORY (Rankings as of March 2, 2026) ---
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
        "SUNY Cortland (#10)": "https://www.cortlandreddragons.com/sports/mens-lacrosse/schedule/2026",
        "St. Lawrence (#11)": "https://saintsathletics.com/sports/mens-lacrosse/schedule/2026",
        "Dickinson (#12)": "https://dickinsonathletics.com/sports/mens-lacrosse/schedule/2026",
        "Washington and Lee (#13)": "https://generalssports.com/sports/mens-lacrosse/schedule/2026",
        "Amherst (#14)": "https://athletics.amherst.edu/sports/mens-lacrosse/schedule/2026",
        "Lynchburg (#15)": "https://www.lynchburgsports.com/sports/mlax/schedule/2025-26",
        "RPI (#16)": "https://rpiathletics.com/sports/mens-lacrosse/schedule/2026",
        "Swarthmore (#17)": "https://swarthmoreathletics.com/sports/mens-lacrosse/schedule/2026",
        "St. John Fisher (#18)": "https://athletics.sjf.edu/sports/mens-lacrosse/schedule/2026",
        "Middlebury (#19)": "https://athletics.middlebury.edu/sports/mens-lacrosse/schedule/2026",
        "Babson (#20)": "https://babsonathletics.com/sports/mens-lacrosse/schedule/2026"
    },
    "Women's Lacrosse": {
        "Middlebury (#1)": "https://athletics.middlebury.edu/sports/womens-lacrosse/schedule/2026",
        "Tufts (#2)": "https://gotuftsjumbos.com/sports/womens-lacrosse/schedule/2026",
        "Colby (#3)": "https://colbyathletics.com/sports/womens-lacrosse/schedule/2026",
        "Wesleyan (#4)": "https://athletics.wesleyan.edu/sports/womens-lacrosse/schedule/2026",
        "Salisbury (#5)": "https://suseagulls.com/sports/womens-lacrosse/schedule/2026",
        "York (#6)": "https://ycpspartans.com/sports/womens-lacrosse/schedule/2026",
        "Gettysburg (#7)": "https://gettysburgsports.com/sports/womens-lacrosse/schedule/2026",
        "Denison (#8)": "https://denisonbigred.com/sports/womens-lacrosse/schedule/2026",
        "Franklin & Marshall (#9)": "https://godiplomats.com/sports/womens-lacrosse/schedule/2026",
        "William Smith (#10)": "https://hwsathletics.com/sports/womens-lacrosse/schedule/2026",
        "Washington and Lee (#11)": "https://generalssports.com/sports/womens-lacrosse/schedule/2026",
        "Pomona-Pitzer (#12)": "https://sagehens.com/sports/womens-lacrosse/schedule/2026",
        "Amherst (#13)": "https://athletics.amherst.edu/sports/womens-lacrosse/schedule/2026",
        "Stevens (#14)": "https://stevensducks.com/sports/womens-lacrosse/schedule/2026",
        "TCNJ (#15)": "https://tcnjathletics.com/sports/womens-lacrosse/schedule/2026",
        "St. John Fisher (#16)": "https://athletics.sjf.edu/sports/womens-lacrosse/schedule/2026",
        "Scranton (#17)": "https://athletics.scranton.edu/sports/womens-lacrosse/schedule/2026",
        "Babson (#18)": "https://babsonathletics.com/sports/womens-lacrosse/schedule/2026",
        "Messiah (#19)": "https://gomessiah.com/sports/womens-lacrosse/schedule/2026",
        "Haverford (#20)": "https://haverfordathletics.com/sports/womens-lacrosse/schedule/2026"
    }
}

def get_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 1. FIND RECORD
        record = "0-0"
        page_text = soup.get_text(" ", strip=True)
        rec_match = re.search(r'Overall\s*(\d+-\d+)', page_text, re.I)
        if rec_match: record = rec_match.group(1)

        games = []
        for row in soup.select('.sidearm-schedule-game'):
            # Grab all text including hidden links/aria-labels
            # This is key for Salisbury!
            row_text = row.get_text(" ", strip=True)
            
            # --- DATE ---
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d+', row_text, re.I)
            date_val = date_match.group(0) if date_match else "TBD"
            
            # --- TIME (Salisbury Fix) ---
            time_val = "TBD"
            # Look for ##:## AM/PM OR "## PM" (Salisbury uses "3 pm" style often)
            time_regex = r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM|A\.M\.|P\.M\.))'
            time_matches = re.findall(time_regex, row_text, re.I)
            
            if time_matches:
                # Take the first valid time found in the row
                time_val = time_matches[0].upper().replace(".", "")
            elif "noon" in row_text.lower():
                time_val = "12:00 PM"
            
            # --- OPPONENT ---
            opp_el = row.select_one('.sidearm-schedule-game-opponent-name')
            opp_val = opp_el.get_text(strip=True) if opp_el else "Unknown"
            opp_val = opp_val.replace("Opponent:", "").strip()
            
            # --- VENUE ---
            venue = "Home"
            if "@" in opp_val or "at " in opp_val.lower() or row.select_one('.sidearm-schedule-game-location-is-away'):
                venue = "Away"
            opp_val = opp_val.replace("@", "").replace("at ", "").strip()

            # --- STATUS ---
            status = "Scheduled"
            res_match = re.search(r'([WL],\s*\d+-\d+)', row_text, re.I)
            if res_match:
                status = res_match.group(1).upper()

            games.append({
                "Date": date_val,
                "Time": time_val,
                "Venue": venue,
                "Opponent": opp_val,
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
    c1.metric("Current Record", record)
    c2.metric("Total Games", len(df))

    def style_table(val):
        if 'W,' in str(val): return 'background-color: #166534; color: white; font-weight: bold; border-radius: 4px;'
        if 'L,' in str(val): return 'background-color: #991b1b; color: white; font-weight: bold; border-radius: 4px;'
        if val == "Away": return 'color: #b45309; font-weight: bold;'
        if val == "Home": return 'color: #64748b;'
        return ''

    st.dataframe(df.style.applymap(style_table), use_container_width=True, hide_index=True)
else:
    st.error("Updating from official site...")

st.divider()
st.caption(f"Last sync: {datetime.now().strftime('%m/%d %I:%M %p')}. Rankings: USILA/IWLCA Week 3.")

