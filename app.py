import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- 2026 TOP 20 DIRECTORY (ORDERED BY RANKING) ---
SCHOOL_DATA = {
    "Men's Lacrosse": {
        "D3": {
            "Tufts (#1)": "https://gotuftsjumbos.com/sports/mens-lacrosse/schedule/2026",
            "Salisbury (#2)": "https://suseagulls.com/sports/mens-lacrosse/schedule/2026",
            "RIT (#3)": "https://ritathletics.com/sports/mens-lacrosse/schedule/2026",
            "Christopher Newport (#4)": "https://cnusports.com/sports/mens-lacrosse/schedule/2026",
            "Bowdoin (#5)": "https://athletics.bowdoin.edu/sports/mens-lacrosse/schedule/2026",
            "Dickinson (#6)": "https://dickinsonathletics.com/sports/mens-lacrosse/schedule/2026",
            "St. Lawrence (#7)": "https://saintsathletics.com/sports/mens-lacrosse/schedule/2026",
            "York (#8)": "https://ycpspartans.com/sports/mens-lacrosse/schedule/2026",
            "Gettysburg (#9)": "https://gettysburgsports.com/sports/mens-lacrosse/schedule/2026",
            "Stevens (#10)": "https://stevensducks.com/sports/mens-lacrosse/schedule/2026",
            "Washington and Lee (#11)": "https://generalssports.com/sports/mens-lacrosse/schedule/2026",
            "Union (#12)": "https://unionathletics.com/sports/mens-lacrosse/schedule/2026",
            "Wesleyan (#13)": "https://athletics.wesleyan.edu/sports/mens-lacrosse/schedule/2026",
            "Lynchburg (#14)": "https://www.lynchburgsports.com/sports/mlax/schedule/2025-26",
            "Amherst (#15)": "https://athletics.amherst.edu/sports/mens-lacrosse/schedule/2026",
            "Swarthmore (#16)": "https://swarthmoreathletics.com/sports/mens-lacrosse/schedule/2026",
            "Williams (#17)": "https://ephsports.williams.edu/sports/mens-lacrosse/schedule/2026",
            "Babson (#18)": "https://babsonathletics.com/sports/mens-lacrosse/schedule/2026",
            "Middlebury (#19)": "https://athletics.middlebury.edu/sports/mens-lacrosse/schedule/2026",
            "RPI (#20)": "https://rpiathletics.com/sports/mens-lacrosse/schedule/2026"
        },
        "D1": {
            "Notre Dame (#1)": "https://fightingirish.com/sports/mlax/schedule/",
            "Duke (#2)": "https://goduke.com/sports/mens-lacrosse/schedule/2026",
            "Virginia (#3)": "https://virginiasports.com/sports/mens-lacrosse/schedule/2026",
            "Maryland (#4)": "https://umterps.com/sports/mens-lacrosse/schedule/2026",
            "Johns Hopkins (#5)": "https://hopkinssports.com/sports/mens-lacrosse/schedule/2026",
            "Cornell (#6)": "https://cornellbigred.com/sports/mens-lacrosse/schedule/2026",
            "Denver (#7)": "https://denverpioneers.com/sports/mens-lacrosse/schedule/2026",
            "Yale (#8)": "https://yalebulldogs.com/sports/mens-lacrosse/schedule/2026",
            "Syracuse (#9)": "https://cuse.com/sports/mens-lacrosse/schedule/2026",
            "Penn State (#10)": "https://gopsusports.com/sports/mens-lacrosse/schedule/2026",
            "Georgetown (#11)": "https://guhoyas.com/sports/mens-lacrosse/schedule/2026",
            "Army (#12)": "https://goarmywestpoint.com/sports/mens-lacrosse/schedule/2026",
            "Princeton (#13)": "https://goprincetontigers.com/sports/mens-lacrosse/schedule/2026",
            "Michigan (#14)": "https://mgoblue.com/sports/mens-lacrosse/schedule/2026",
            "Richmond (#15)": "https://richmondspiders.com/sports/mens-lacrosse/schedule/2026",
            "Harvard (#16)": "https://gocrimson.com/sports/mens-lacrosse/schedule/2026",
            "Penn (#17)": "https://pennathletics.com/sports/mens-lacrosse/schedule/2026",
            "Rutgers (#18)": "https://scarletknights.com/sports/mens-lacrosse/schedule/2026",
            "Ohio State (#19)": "https://ohiostatebuckeyes.com/sports/mens-lacrosse/schedule/2026",
            "Towson (#20)": "https://towsontigers.com/sports/mens-lacrosse/schedule/2026"
        }
    },
    "Women's Lacrosse": {
        "D3": {
            "Middlebury (#1)": "https://athletics.middlebury.edu/sports/womens-lacrosse/schedule/2026",
            "Northwestern (#2)": "https://nusports.com/sports/womens-lacrosse/schedule/2026",
            "William Smith (#3)": "https://hwsathletics.com/sports/womens-lacrosse/schedule/2026",
            "Salisbury (#4)": "https://suseagulls.com/sports/womens-lacrosse/schedule/2026",
            "Tufts (#5)": "https://gotuftsjumbos.com/sports/womens-lacrosse/schedule/2026",
            "Franklin & Marshall (#6)": "https://godiplomats.com/sports/womens-lacrosse/schedule/2026",
            "Gettysburg (#7)": "https://gettysburgsports.com/sports/womens-lacrosse/schedule/2026",
            "York (#8)": "https://ycpspartans.com/sports/womens-lacrosse/schedule/2026",
            "TCNJ (#9)": "https://tcnjathletics.com/sports/womens-lacrosse/schedule/2026",
            "Colby (#10)": "https://colbyathletics.com/sports/womens-lacrosse/schedule/2026",
            "Wesleyan (#11)": "https://athletics.wesleyan.edu/sports/womens-lacrosse/schedule/2026",
            "Pomona-Pitzer (#12)": "https://sagehens.com/sports/womens-lacrosse/schedule/2026",
            "Trinity (CT) (#13)": "https://bantamsports.com/sports/womens-lacrosse/schedule/2026",
            "Roanoke (#14)": "https://roanokecatamounts.com/sports/womens-lacrosse/schedule/2026",
            "Christopher Newport (#15)": "https://cnusports.com/sports/womens-lacrosse/schedule/2026",
            "Cortland (#16)": "https://www.cortlandreddragons.com/sports/womens-lacrosse/schedule/2026",
            "Ithaca (#17)": "https://athletics.ithaca.edu/sports/womens-lacrosse/schedule/2026",
            "Williams (#18)": "https://ephsports.williams.edu/sports/womens-lacrosse/schedule/2026",
            "St. John Fisher (#19)": "https://athletics.sjf.edu/sports/womens-lacrosse/schedule/2026",
            "Stevens (#20)": "https://stevensducks.com/sports/womens-lacrosse/schedule/2026"
        },
        "D1": {
            "Northwestern (#1)": "https://nusports.com/sports/womens-lacrosse/schedule/2026",
            "Boston College (#2)": "https://bceagles.com/sports/womens-lacrosse/schedule/2026",
            "Syracuse (#3)": "https://cuse.com/sports/womens-lacrosse/schedule/2026",
            "Maryland (#4)": "https://umterps.com/sports/womens-lacrosse/schedule/2026",
            "Michigan (#5)": "https://mgoblue.com/sports/womens-lacrosse/schedule/2026",
            "Notre Dame (#6)": "https://fightingirish.com/sports/wlax/schedule/",
            "Florida (#7)": "https://floridagators.com/sports/womens-lacrosse/schedule/2026",
            "Virginia (#8)": "https://virginiasports.com/sports/womens-lacrosse/schedule/2026",
            "Loyola Maryland (#9)": "https://loyolagreyhounds.com/sports/womens-lacrosse/schedule/2026",
            "Denver (#10)": "https://denverpioneers.com/sports/womens-lacrosse/schedule/2026",
            "James Madison (#11)": "https://jmusports.com/sports/womens-lacrosse/schedule/2026",
            "Penn (#12)": "https://pennathletics.com/sports/womens-lacrosse/schedule/2026",
            "Stony Brook (#13)": "https://stonybrookathletics.com/sports/womens-lacrosse/schedule/2026",
            "Yale (#14)": "https://yalebulldogs.com/sports/womens-lacrosse/schedule/2026",
            "Johns Hopkins (#15)": "https://hopkinssports.com/sports/womens-lacrosse/schedule/2026",
            "North Carolina (#16)": "https://goheels.com/sports/womens-lacrosse/schedule/2026",
            "Princeton (#17)": "https://goprincetontigers.com/sports/womens-lacrosse/schedule/2026",
            "Navy (#18)": "https://navysports.com/sports/womens-lacrosse/schedule/2026",
            "Stanford (#19)": "https://gostanford.com/sports/womens-lacrosse/schedule/2026",
            "Colorado (#20)": "https://cubuffs.com/sports/womens-lacrosse/schedule/2026"
        }
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
        if "fightingirish.com" in url:
            for item in soup.select('.c-event-card'):
                opp = item.select_one('.c-event-card__opponent')
                res = item.select_one('.c-event-card__score')
                loc = item.select_one('.c-event-card__location')
                if opp:
                    v = "Away" if (loc and "at " in loc.text.lower()) else "Home"
                    games.append({"Date": extract_date(item), "Venue": v, "Opponent": opp.text.strip(), "Status": res.text.strip() if res else "Upcoming"})
        else:
            for item in soup.select('.sidearm-schedule-game'):
                opp_el = item.select_one('.sidearm-schedule-game-opponent-name, .sidearm-schedule-game-opponent-name-short')
                res_el = item.select_one('.sidearm-schedule-game-result')
                away_flag = item.select_one('.sidearm-schedule-game-location-is-away, .sidearm-schedule-game-away')
                if opp_el:
                    raw_opp = opp_el.get_text(strip=True).replace("Opponent:", "").strip()
                    is_away = "@" in raw_opp or "at " in raw_opp.lower() or away_flag is not None
                    venue = "Away" if is_away else "Home"
                    clean_opp = raw_opp.replace("@", "").replace("at ", "").strip()
                    games.append({"Date": extract_date(item), "Venue": venue, "Opponent": clean_opp, "Status": res_el.get_text(strip=True) if res_el else "Scheduled"})
        df = pd.DataFrame(games).drop_duplicates()
        if not df.empty:
            df.insert(0, "#", range(1, len(df) + 1))
        return record, df
    except:
        return "N/A", pd.DataFrame()

def apply_styles(styler):
    styler.applymap(lambda x: 'background-color: rgba(70, 130, 180, 0.2); color: #ADD8E6; font-weight: bold; text-align: center;', subset=['#'])
    styler.applymap(lambda x: 'color: #FFA500; font-weight: bold;' if x == "Away" else 'color: #999999;', subset=['Venue'])
    def color_status(val):
        if 'W' in val: return 'background-color: rgba(40, 167, 69, 0.3); color: #90EE90; font-weight: bold;'
        if 'L' in val: return 'background-color: rgba(220, 53, 69, 0.3); color: #FFB6C1;'
        return ''
    styler.applymap(color_status, subset=['Status'])
    return styler

# --- UI ---
st.set_page_config(page_title="simple lax tracker", page_icon="🥍", layout="wide")

st.sidebar.title("🥍 simple lax tracker")
league = st.sidebar.radio("Category", ["Men's Lacrosse", "Women's Lacrosse"])
div = st.sidebar.radio("Division", ["D3", "D1"])

team_options = list(SCHOOL_DATA[league][div].keys())
team = st.sidebar.selectbox("Select Team (Ranked)", team_options)
team_url = SCHOOL_DATA[league][div][team]

st.markdown(f"""
    <div style="line-height: 1.1; margin-bottom: 10px;">
        <span style="font-size: 52px; font-weight: 900; color: #FFFFFF; letter-spacing: -1px;">{team}</span><br>
        <span style="font-size: 14px; font-weight: 400; color: #888888; letter-spacing: 2px; text-transform: uppercase;">{league} {div} Dashboard</span>
    </div>
    """, unsafe_allow_html=True)

with st.spinner(f"Updating..."):
    record, df = get_data(team_url)

if not df.empty:
    st.metric("Season Record", record)
    
    # --- AUTO-FIT COLUMN CONFIGURATION ---
    st.dataframe(
        apply_styles(df.style), 
        use_container_width=True, 
        hide_index=True, 
        height=(len(df) * 35) + 50,
        column_config={
            "#": st.column_config.Column(width="small"),
            "Date": st.column_config.Column(width="small"),
            "Venue": st.column_config.Column(width="small"),
            "Opponent": st.column_config.Column(width="large"), # Takes up the remaining space
            "Status": st.column_config.Column(width="medium")
        }
    )
else:
    st.warning(f"Live data for {team} is currently offline.")
    st.link_button(f"🔗 View {team} Official Schedule", team_url, use_container_width=True)

st.divider()
st.caption(f"Sync attempt at {datetime.now().strftime('%m/%d/%Y %I:%M %p')}.")
