import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- TOP 20 DIRECTORY ---
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

# --- TOOLS ---
def get_team_record_robust(soup):
    targets = ['.sidearm-schedule-record', '.overall-record', '.record', '.c-schedule-header__record']
    raw_text = ""
    for selector in targets:
        found = soup.select_one(selector)
        if found:
            raw_text = found.get_text(strip=True)
            break
    if not raw_text:
        rec_search = soup.find(string=re.compile(r'Overall:?\s*\d+-\d+'))
        if rec_search: raw_text = rec_search
    clean_match = re.search(r'(\d+-\d+)', raw_text)
    return clean_match.group(1) if clean_match else "N/A"

def get_school_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200: return "N/A", pd.DataFrame()
        soup = BeautifulSoup(resp.text, 'html.parser')
        record = get_team_record_robust(soup)
        games = []

        if "goheels.com" in url:
            table = soup.find('table')
            if table:
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        games.append({"Date": cols[0].get_text(strip=True), "Opponent": cols[3].get_text(strip=True), "Status": cols[6].get_text(strip=True) or "Scheduled"})
        elif "fightingirish.com" in url:
            for item in soup.select('.c-event-card'):
                opp_tag = item.select_one('.c-event-card__opponent')
                res_tag = item.select_one('.c-event-card__score')
                date_tag = item.select_one('.c-event-card__date')
                if opp_tag:
                    games.append({
                        "Date": date_tag.get_text(strip=True) if date_tag else "TBD",
                        "Opponent": opp_tag.get_text(strip=True),
                        "Status": res_tag.get_text(strip=True) if res_tag else "Upcoming"
                    })
        else:
            for item in soup.select('.sidearm-schedule-game'):
                opp = item.select_one('.sidearm-schedule-game-opponent-name')
                res = item.select_one('.sidearm-schedule-game-result')
                date_container = item.select_one('.sidearm-schedule-game-date, .sidearm-schedule-game-upcoming-date')
                date_val = "TBD"
                if date_container:
                    parts = [s.get_text(strip=True) for s in date_container.find_all(True) if s.get_text(strip=True) != "2026"]
                    date_val = " ".join(parts) if parts else date_container.get_text(" ", strip=True).replace("2026", "").strip()
                if opp:
                    games.append({"Date": date_val, "Opponent": opp.get_text(strip=True).replace("Opponent:", "").strip(), "Status": res.get_text(strip=True) if res else "Scheduled"})
        
        final_df = pd.DataFrame(games).drop_duplicates()
        if not final_df.empty:
            final_df.insert(0, "Game #", range(1, len(final_df) + 1))
            final_df["Game #"] = final_df["Game #"].apply(lambda x: f"Game {x}")
        return record, final_df
    except:
        return "N/A", pd.DataFrame()

def style_df(styler):
    # Style for Game # column
    styler.applymap(lambda x: 'background-color: rgba(70, 130, 180, 0.2); color: #ADD8E6; font-weight: bold;', subset=['Game #'])
    
    # Style for Status column
    def color_status(val):
        if 'W' in val: return 'background-color: rgba(40, 167, 69, 0.3); color: #90EE90; font-weight: bold;'
        if 'L' in val: return 'background-color: rgba(220, 53, 69, 0.3); color: #FFB6C1;'
        if any(x in val.upper() for x in ['AM', 'PM', 'LIVE']): return 'background-color: rgba(255, 193, 7, 0.3); color: #FFFACD;'
        return ''
    
    styler.applymap(color_status, subset=['Status'])
    return styler

# --- UI ---
st.set_page_config(page_title="LaxTracker Pro", page_icon="🥍", layout="wide")

div = st.sidebar.radio("Division", ["D1", "D3"])
team = st.sidebar.selectbox("Select Team", list(SCHOOL_DATA[div].keys()))

st.markdown(f"""
    <div style="line-height: 1.1; margin-bottom: 10px;">
        <span style="font-size: 52px; font-weight: 900; color: #FFFFFF; letter-spacing: -1px;">{team}</span><br>
        <span style="font-size: 16px; font-weight: 400; color: #888888; letter-spacing: 3px; text-transform: uppercase;">Team Dashboard</span>
    </div>
    """, unsafe_allow_html=True)

with st.spinner(f"Updating..."):
    record, df = get_school_data(SCHOOL_DATA[div][team])

if not df.empty:
    c1, c2 = st.columns([1, 1])
    c1.metric(f"Record", record)
    c2.caption(f"Synced at {datetime.now().strftime('%I:%M %p')}")
    
    dynamic_height = (len(df) * 35) + 50
    
    st.dataframe(
        style_df(df.style),
        use_container_width=True,
        hide_index=True,
        height=dynamic_height
    )
else:
    st.error("Data unavailable.")

st.divider()
st.link_button("📺 ESPN Lacrosse Scoreboard", "https://www.espn.com/mens-college-lacrosse/scoreboard", use_container_width=True)
