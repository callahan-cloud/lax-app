import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- 2026 D3 TOP 20 DIRECTORY ---
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
        "Gettysburg (#4)": "https://gettysburgsports.com/sports/womens-lacrosse/schedule/2026",
        "Wesleyan (#5)": "https://athletics.wesleyan.edu/sports/womens-lacrosse/schedule/2026",
        "Franklin & Marshall (#6)": "https://godiplomats.com/sports/womens-lacrosse/schedule/2026",
        "York (#7)": "https://ycpspartans.com/sports/womens-lacrosse/schedule/2026",
        "Salisbury (#8)": "https://suseagulls.com/sports/womens-lacrosse/schedule/2026",
        "Washington and Lee (#9)": "https://generalssports.com/sports/womens-lacrosse/schedule/2026",
        "Denison (#10)": "https://denisonbigred.com/sports/womens-lacrosse/schedule/2026",
        "St. John Fisher (#11)": "https://athletics.sjf.edu/sports/womens-lacrosse/schedule/2026",
        "William Smith (#12)": "https://hwsathletics.com/sports/womens-lacrosse/schedule/2026",
        "Pomona-Pitzer (#13)": "https://sagehens.com/sports/womens-lacrosse/schedule/2026",
        "Amherst (#14)": "https://athletics.amherst.edu/sports/womens-lacrosse/schedule/2026",
        "Stevens (#15)": "https://stevensducks.com/sports/womens-lacrosse/schedule/2026",
        "TCNJ (#16)": "https://tcnjathletics.com/sports/womens-lacrosse/schedule/2026",
        "Rowan (#17)": "https://www.rowanathletics.com/sports/womens-lacrosse/schedule/2026",
        "Haverford (#18)": "https://haverfordathletics.com/sports/womens-lacrosse/schedule/2026",
        "Babson (#19)": "https://babsonathletics.com/sports/womens-lacrosse/schedule/2026",
        "Trinity (#20)": "https://bantamsports.com/sports/womens-lacrosse/schedule/2026"
    }
}

# --- TOOLKIT ---
def extract_date(element):
    month_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    day_pattern = r"(\d{1,2})"
    text = element.get_text(" ", strip=True)
    match = re.search(f"{month_pattern}\s*{day_pattern}", text, re.IGNORECASE)
    return f"{match.group(1)} {match.group(2)}" if match else "TBD"

def get_record(soup):
    for selector in ['.sidearm-schedule-record', '.overall-record', '.record', '.c-schedule-header__record']:
        found = soup.select_one(selector)
        if found:
            match = re.search(r'(\d+-\d+)', found.get_text(strip=True))
            if match: return match.group(1)
    return "0-0"

def get_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        record = get_record(soup)
        games = []
        for item in soup.select('.sidearm-schedule-game'):
            opp_el = item.select_one('.sidearm-schedule-game-opponent-name, .sidearm-schedule-game-opponent-name-short')
            res_el = item.select_one('.sidearm-schedule-game-result')
            time_el = item.select_one('.sidearm-schedule-game-time') # New selector for time
            away_flag = item.select_one('.sidearm-schedule-game-location-is-away, .sidearm-schedule-game-away')
            
            if opp_el:
                raw_opp = opp_el.get_text(strip=True).replace("Opponent:", "").strip()
                is_away = "@" in raw_opp or "at " in raw_opp.lower() or away_flag is not None
                venue = "Away" if is_away else "Home"
                clean_opp = raw_opp.replace("@", "").replace("at ", "").strip()
                
                # Clean up time string (removes extra spaces/tags)
                raw_time = time_el.get_text(strip=True) if time_el else "TBD"
                
                games.append({
                    "Date": extract_date(item),
                    "Time": raw_time, 
                    "Venue": venue, 
                    "Opponent": clean_opp, 
                    "Status": res_el.get_text(strip=True) if res_el else "Scheduled"
                })
        
        df = pd.DataFrame(games).drop_duplicates()
        return record, df
    except:
        return "N/A", pd.DataFrame()

def apply_styles(styler):
    # Venue: Amber Away / Slate Home
    styler.applymap(lambda x: 'color: #b45309; font-weight: bold;' if x == "Away" else 'color: #64748b;', subset=['Venue'])
    # Time column: subtle styling
    styler.applymap(lambda x: 'color: #1e293b; font-weight: 500;', subset=['Time'])
    
    def color_status(val):
        if 'W' in val: return 'background-color: #166534; color: #ffffff; font-weight: bold; border-radius: 4px;'
        if 'L' in val: return 'background-color: #991b1b; color: #ffffff; font-weight: bold; border-radius: 4px;'
        return 'color: #334155;'
        
    styler.applymap(color_status, subset=['Status'])
    return styler

# --- UI SETUP ---
st.set_page_config(page_title="simple D3 score tracker", page_icon="🥍", layout="wide")

st.sidebar.title("🥍 simple D3 score tracker")
league = st.sidebar.radio("Category", ["Men's Lacrosse", "Women's Lacrosse"])

team_options = list(SCHOOL_DATA[league].keys())
team = st.sidebar.selectbox("Select Team (Ranked)", team_options)
team_url = SCHOOL_DATA[league][team]

st.markdown(f"""
    <div style="line-height: 1.1; margin-bottom: 20px;">
        <span style="font-size: 38px; font-weight: 900; color: #0f172a; letter-spacing: -1px;">{team}</span><br>
        <span style="font-size: 14px; font-weight: 700; color: #64748b; letter-spacing: 2px; text-transform: uppercase;">D3 Score Tracker • 2026 Season</span>
    </div>
    """, unsafe_allow_html=True)

with st.spinner(f"Updating {team}..."):
    record, df = get_data(team_url)

if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Season Record", record)
    with col2:
        st.metric("Scheduled Games", len(df))
    
    st.dataframe(
        apply_styles(df.style), 
        use_container_width=True, 
        hide_index=True, 
        height=(len(df) * 38) + 100
    )
else:
    st.warning(f"Data for {team} is currently unavailable.")
    st.link_button(f"🔗 View {team} Official Schedule", team_url, use_container_width=True)

st.divider()
st.caption(f"Sync attempt at {datetime.now().strftime('%m/%d/%Y %I:%M %p')}. Rankings: USILA/IWLCA Week 3.")
