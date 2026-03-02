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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 1. FIND RECORD (REGEX SEARCH ACROSS WHOLE PAGE)
        record = "0-0"
        page_text = soup.get_text(" ", strip=True)
        rec_match = re.search(r'Overall\s*(\d+-\d+)', page_text, re.I)
        if rec_match:
            record = rec_match.group(1)
        else:
            # Fallback for different wording
            rec_match = re.search(r'(\d+-\d+)\s*Overall', page_text, re.I)
            if rec_match: record = rec_match.group(1)

        games = []
        # 2. FIND GAME ROWS
        for row in soup.select('.sidearm-schedule-game'):
            row_text = row.get_text(" ", strip=True)
            
            # --- EXTRACT DATE ---
            # Looks for "Mar 2" or "March 2"
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d+', row_text, re.I)
            date_val = date_match.group(0) if date_match else "TBD"
            
            # --- EXTRACT TIME ---
            # Looks for 1:00 PM, 1:00 p.m., or Noon
            time_val = "TBD"
            time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|A\.M\.|P\.M\.))', row_text, re.I)
            if time_match:
                time_val = time_match.group(1).upper().replace(".", "")
            elif "noon" in row_text.lower():
                time_val = "12:00 PM"
            
            # --- EXTRACT OPPONENT ---
            opp_el = row.select_one('.sidearm-schedule-game-opponent-name')
            opp_val = opp_el.get_text(strip=True) if opp_el else "Unknown"
            opp_val = opp_val.replace("Opponent:", "").strip()
            
            # --- EXTRACT VENUE ---
            venue = "Home"
            if "@" in opp_val or "at " in opp_val.lower() or row.select_one('.sidearm-schedule-game-location-is-away'):
                venue = "Away"
            opp_val = opp_val.replace("@", "").replace("at ", "").strip()

            # --- EXTRACT STATUS ---
            status = "Scheduled"
            # If there is a W or L followed by a score like W, 15-10
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

# Header Styles
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #0f172a; }
    </style>
    """, unsafe_allow_html=True)

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
    st.error("Site structure blocked the update. Please try another team.")

st.divider()
st.caption(f"Sync: {datetime.now().strftime('%m/%d %I:%M %p')}. Data pulled via pattern-recognition.")
