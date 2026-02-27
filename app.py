import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- 2026 TOP 20 DIRECTORY ---
SCHOOL_DATA = {
    "Men's Lacrosse": {
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
        },
        "D1": {
            "Notre Dame": "https://fightingirish.com/sports/mlax/schedule/",
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
        }
    },
    "Women's Lacrosse": {
        "D3": {
            "Middlebury": "https://athletics.middlebury.edu/sports/womens-lacrosse/schedule/2026",
            "Tufts": "https://gotuftsjumbos.com/sports/womens-lacrosse/schedule/2026",
            "Salisbury": "https://suseagulls.com/sports/womens-lacrosse/schedule/2026",
            "Colby": "https://colbyathletics.com/sports/womens-lacrosse/schedule/2026",
            "Franklin & Marshall": "https://godiplomats.com/sports/womens-lacrosse/schedule/2026",
            "Stevens": "https://stevensducks.com/sports/womens-lacrosse/schedule/2026",
            "Denison": "https://denisonbigred.com/sports/womens-lacrosse/schedule/2026",
            "Gettysburg": "https://gettysburgsports.com/sports/womens-lacrosse/schedule/2026",
            "William Smith": "https://hwsathletics.com/sports/womens-lacrosse/schedule/2026",
            "Wesleyan": "https://athletics.wesleyan.edu/sports/womens-lacrosse/schedule/2026",
            "Washington and Lee": "https://generalssports.com/sports/womens-lacrosse/schedule/2026",
            "York": "https://ycpspartans.com/sports/womens-lacrosse/schedule/2026",
            "Amherst": "https://athletics.amherst.edu/sports/womens-lacrosse/schedule/2026",
            "Babson": "https://babsonathletics.com/sports/womens-lacrosse/schedule/2026",
            "St. John Fisher": "https://athletics.sjf.edu/sports/womens-lacrosse/schedule/2026",
            "MIT": "https://mitathletics.com/sports/womens-lacrosse/schedule/2026",
            "Pomona-Pitzer": "https://sagehens.com/sports/womens-lacrosse/schedule/2026",
            "TCNJ": "https://tcnjathletics.com/sports/womens-lacrosse/schedule/2026",
            "Christopher Newport": "https://cnusports.com/sports/womens-lacrosse/schedule/2026",
            "Scranton": "https://athletics.scranton.edu/sports/womens-lacrosse/schedule/2026"
        },
        "D1": {
            "North Carolina": "https://goheels.com/sports/womens-lacrosse/schedule/2026",
            "Northwestern": "https://nusports.com/sports/womens-lacrosse/schedule/2026",
            "Boston College": "https://bceagles.com/sports/womens-lacrosse/schedule/2026",
            "Florida": "https://floridagators.com/sports/womens-lacrosse/schedule/2026",
            "Stanford": "https://gostanford.com/sports/womens-lacrosse/schedule/2026",
            "Princeton": "https://goprincetontigers.com/sports/womens-lacrosse/schedule/2026",
            "Maryland": "https://umterps.com/sports/womens-lacrosse/schedule/2026",
            "Johns Hopkins": "https://hopkinssports.com/sports/womens-lacrosse/schedule/2026",
            "Penn": "https://pennathletics.com/sports/womens-lacrosse/schedule/2026",
            "Virginia": "https://virginiasports.com/sports/womens-lacrosse/schedule/2026",
            "Yale": "https://yalebulldogs.com/sports/womens-lacrosse/schedule/2026",
            "Clemson": "https://clemsontigers.com/sports/womens-lacrosse/schedule/2026",
            "Syracuse": "https://cuse.com/sports/womens-lacrosse/schedule/2026",
            "Duke": "https://goduke.com/sports/womens-lacrosse/schedule/2026",
            "Michigan": "https://mgoblue.com/sports/womens-lacrosse/schedule/2026",
            "Navy": "https://navysports.com/sports/womens-lacrosse/schedule/2026",
            "Stony Brook": "https://stonybrookathletics.com/sports/womens-lacrosse/schedule/2026",
            "Loyola Maryland": "https://loyolagreyhounds.com/sports/womens-lacrosse/schedule/2026",
            "James Madison": "https://jmusports.com/sports/womens-lacrosse/schedule/2026",
            "Denver": "https://denverpioneers.com/sports/womens-lacrosse/schedule/2026"
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

        # Logic for Fighting Irish/Standard Sites
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
st.set_page_config(page_title="LaxTracker 2026 Pro", page_icon="🥍", layout="wide")

st.sidebar.title("🥍 LaxTracker Pro")
league = st.sidebar.radio("Category", ["Men's Lacrosse", "Women's Lacrosse"])
div = st.sidebar.radio("Division", ["D3", "D1"]) # D3 Priority

# Filter teams for selected div and league
team_options = sorted(list(SCHOOL_DATA[league][div].keys()))
team = st.sidebar.selectbox("Select Team", team_options)
team_url = SCHOOL_DATA[league][div][team]

st.markdown(f"""
    <div style="line-height: 1.1; margin-bottom: 10px;">
        <span style="font-size: 52px; font-weight: 900; color: #FFFFFF; letter-spacing: -1px;">{team}</span><br>
        <span style="font-size: 16px; font-weight: 400; color: #888888; letter-spacing: 3px; text-transform: uppercase;">{league} {div} Top 20 Dashboard</span>
    </div>
    """, unsafe_allow_html=True)

with st.spinner("Syncing 2026 Data..."):
    record, df = get_data(team_url)

if not df.empty:
    st.metric("Season Record", record)
    st.dataframe(apply_styles(df.style), use_container_width=True, hide_index=True, height=(len(df) * 35) + 50)
else:
    st.warning(f"Live data for {team} is currently offline.")
    st.link_button(f"🔗 View {team} Official Schedule", team_url, use_container_width=True)

st.divider()
st.caption(f"Sync attempt at {datetime.now().strftime('%m/%d/%Y %I:%M %p')}. 2026 Rankings source: USILA/IWLCA.")
