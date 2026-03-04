import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- 2026 D3 TOP 20 DIRECTORY (Week 4 Polls - March 2, 2026) ---
SCHOOL_DATA = {
    "Men's Lacrosse": {
        "Tufts (#1)": "https://gotuftsjumbos.com/sports/mens-lacrosse/schedule/2026",
        "Christopher Newport (#2)": "https://cnusports.com/sports/mens-lacrosse/schedule/2026",
        "Bowdoin (#3)": "https://athletics.bowdoin.edu/sports/mens-lacrosse/schedule/2026",
        "York (#4)": "https://ycpspartans.com/sports/mens-lacrosse/schedule/2026",
        "Lynchburg (#5)": "https://www.lynchburgsports.com/sports/mlax/schedule/2025-26",
        "Salisbury (#6)": "https://suseagulls.com/sports/mens-lacrosse/schedule/2026",
        "Stevens (#7)": "https://stevensducks.com/sports/mens-lacrosse/schedule/2026",
        "RIT (#8)": "https://ritathletics.com/sports/mens-lacrosse/schedule/2026",
        "Babson (#9)": "https://babsonathletics.com/sports/mens-lacrosse/schedule/2026",
        "Gettysburg (#10)": "https://gettysburgsports.com/sports/mens-lacrosse/schedule/2026",
        "Dickinson (#11)": "https://dickinsonathletics.com/sports/mens-lacrosse/schedule/2026",
        "St. John Fisher (#12)": "https://athletics.sjf.edu/sports/mens-lacrosse/schedule/2026",
        "Washington and Lee (#13)": "https://generalssports.com/sports/mens-lacrosse/schedule/2026",
        "SUNY Cortland (#14)": "https://www.cortlandreddragons.com/sports/mens-lacrosse/schedule/2026",
        "St. Lawrence (#15)": "https://saintsathletics.com/sports/mens-lacrosse/schedule/2026",
        "Amherst (#16)": "https://athletics.amherst.edu/sports/mens-lacrosse/schedule/2026",
        "Wesleyan (#17)": "https://athletics.wesleyan.edu/sports/mens-lacrosse/schedule/2026",
        "RPI (#18)": "https://rpiathletics.com/sports/mens-lacrosse/schedule/2026",
        "Swarthmore (#19)": "https://swarthmoreathletics.com/sports/mens-lacrosse/schedule/2026",
        "Bates (#20)": "https://gobatesbobcats.com/sports/mens-lacrosse/schedule/2026"
        "Nazareth":  https://nazathletics.com/sports/mens-lacrosse/schedule/2026
    },
    "Women's Lacrosse": {
        "Middlebury (#1)": "https://athletics.middlebury.edu/sports/womens-lacrosse/schedule/2026",
        "Tufts (#2)": "https://gotuftsjumbos.com/sports/womens-lacrosse/schedule/2026",
        "Salisbury (#3)": "https://suseagulls.com/sports/womens-lacrosse/schedule/2026",
        "Colby (#4)": "https://colbyathletics.com/sports/womens-lacrosse/schedule/2026",
        "Franklin & Marshall (#5)": "https://godiplomats.com/sports/womens-lacrosse/schedule/2026",
        "Denison (#6)": "https://denisonbigred.com/sports/womens-lacrosse/schedule/2026",
        "Gettysburg (#7)": "https://gettysburgsports.com/sports/womens-lacrosse/schedule/2026",
        "William Smith (#8)": "https://hwsathletics.com/sports/womens-lacrosse/schedule/2026",
        "Wesleyan (#9)": "https://athletics.wesleyan.edu/sports/womens-lacrosse/schedule/2026",
        "Stevens (#10)": "https://stevensducks.com/sports/womens-lacrosse/schedule/2026",
        "York (#11)": "https://ycpspartans.com/sports/womens-lacrosse/schedule/2026",
        "Washington and Lee (#12)": "https://generalssports.com/sports/womens-lacrosse/schedule/2026",
        "Amherst (#13)": "https://athletics.amherst.edu/sports/womens-lacrosse/schedule/2026",
        "Babson (#14)": "https://babsonathletics.com/sports/womens-lacrosse/schedule/2026",
        "St. John Fisher (#15)": "https://athletics.sjf.edu/sports/womens-lacrosse/schedule/2026",
        "MIT (#16)": "https://mitathletics.com/sports/womens-lacrosse/schedule/2026",
        "Pomona-Pitzer (#17)": "https://sagehens.com/sports/womens-lacrosse/schedule/2026",
        "TCNJ (#18)": "https://tcnjathletics.com/sports/womens-lacrosse/schedule/2026",
        "Christopher Newport (#19)": "https://cnusports.com/sports/womens-lacrosse/schedule/2026",
        "Ithaca (#20)": "https://athletics.ithaca.edu/sports/womens-lacrosse/schedule/2026"
    }
}

def get_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        record = "0-0"
        page_text = soup.get_text(" ", strip=True)
        rec_match = re.search(r'Overall\s*(\d+-\d+)', page_text, re.I)
        if rec_match: record = rec_match.group(1)
        else:
            rec_match = re.search(r'(\d+-\d+)\s*Overall', page_text, re.I)
            if rec_match: record = rec_match.group(1)

        games = []
        for row in soup.select('.sidearm-schedule-game'):
            row_text = row.get_text(" ", strip=True)
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d+', row_text, re.I)
            date_val = date_match.group(0) if date_match else "TBD"
            
            time_val = "TBD"
            time_regex = r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM|A\.M\.|P\.M\.))'
            time_matches = re.findall(time_regex, row_text, re.I)
            if time_matches:
                time_val = time_matches[0].upper().replace(".", "")
            elif "noon" in row_text.lower():
                time_val = "12:00 PM"
            
            opp_el = row.select_one('.sidearm-schedule-game-opponent-name')
            opp_val = opp_el.get_text(strip=True) if opp_el else "Unknown"
            opp_val = opp_val.replace("Opponent:", "").strip()
            
            venue = "Home"
            if "@" in opp_val or "at " in opp_val.lower() or row.select_one('.sidearm-schedule-game-location-is-away'):
                venue = "Away"
            opp_val = opp_val.replace("@", "").replace("at ", "").strip()

            status = "Scheduled"
            res_match = re.search(r'([WL],\s*\d+-\d+)', row_text, re.I)
            if res_match:
                status = res_match.group(1).upper()

            games.append({"Date": date_val, "Time": time_val, "Venue": venue, "Opponent": opp_val, "Status": status})

        return record, pd.DataFrame(games).drop_duplicates()
    except:
        return "N/A", pd.DataFrame()

# --- STREAMLIT UI ---
st.set_page_config(page_title="D3 Lax Tracker", layout="wide")

st.sidebar.title("🥍 Mode Selection")
mode = st.sidebar.radio("View Mode", ["Single Team Tracker", "Today's Top 20 Games"])

if mode == "Today's Top 20 Games":
    today_str = datetime.now().strftime("%b %-d") # "Mar 3"
    st.markdown(f"## 📅 Games Today: {today_str}")
    st.write("Scanning all 40 Top 20 schedules... this takes a moment.")
    
    todays_games = []
    progress_bar = st.progress(0)
    total_teams = 40
    current_count = 0

    for league in SCHOOL_DATA:
        for team_name, url in SCHOOL_DATA[league].items():
            _, df = get_data(url)
            if not df.empty:
                match = df[df['Date'].str.contains(today_str, case=False, na=False)]
                for _, row in match.iterrows():
                    todays_games.append({
                        "League": league,
                        "Ranked Team": team_name,
                        "Time": row['Time'],
                        "Opponent": row['Opponent'],
                        "Venue": row['Venue']
                    })
            current_count += 1
            progress_bar.progress(current_count / total_teams)

    if todays_games:
        st.dataframe(pd.DataFrame(todays_games), use_container_width=True, hide_index=True)
    else:
        st.info("No Top 20 games found for today.")

else:
    # Single Team View (Loads fast)
    st.sidebar.divider()
    league = st.sidebar.radio("Category", ["Men's Lacrosse", "Women's Lacrosse"])
    team = st.sidebar.selectbox("Select Team", list(SCHOOL_DATA[league].keys()))

    st.markdown(f"## {team}")
    with st.spinner("Fetching schedule..."):
        record, df = get_data(SCHOOL_DATA[league][team])

    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Record", record)
        c2.metric("Total Games", len(df))

        def style_table(val):
            if 'W,' in str(val): return 'background-color: #166534; color: white;'
            if 'L,' in str(val): return 'background-color: #991b1b; color: white;'
            return ''

        st.dataframe(df.style.applymap(style_table), use_container_width=True, hide_index=True)

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%m/%d %I:%M %p')}. Rankings: USILA/IWLCA Week 4.")

