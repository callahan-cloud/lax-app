import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

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

# --- DATA HELPERS ---

def get_team_record(soup):
    """Attempts to find the team record (e.g., 4-1) in the header or sidebar."""
    record_text = "Record: N/A"
    # Common Sidearm/WMT patterns for records
    targets = soup.find_all(text=re.compile(r'\d+-\d+'))
    for t in targets:
        if "Overall" in t.parent.text or "Record" in t.parent.text:
            return t.parent.text.strip()
    return record_text

def clean_date_logic(item):
    date_stack = item.select_one('.sidearm-schedule-game-upcoming-date, .sidearm-schedule-game-date')
    if date_stack:
        text = date_stack.get_text(" ", strip=True)
        if len(text) < 5 or text.isdigit():
             label = item.get('aria-label', '')
             match = re.search(r'[A-Z][a-z]{2}\s\d{1,2}', label)
             return match.group(0) if match else text
        return text
    return "TBD"

def get_school_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        record = get_team_record(soup)
        games = []

        # UNC - TEXT TABLE
        if "goheels.com" in url:
            table = soup.find('table')
            if table:
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        games.append({"Date": cols[0].get_text(strip=True), 
                                      "Opponent": cols[3].get_text(strip=True), 
                                      "Status": cols[6].get_text(strip=True) or "Scheduled"})
        
        # NOTRE DAME - WMT
        elif "fightingirish.com" in url:
            for item in soup.select('.c-event-card'):
                opp = item.select_one('.c-event-card__opponent')
                date = item.select_one('.c-event-card__date')
                res = item.select_one('.c-event-card__score')
                if opp:
                    games.append({"Date": date.text.strip() if date else "TBD", 
                                  "Opponent": opp.text.strip(), 
                                  "Status": res.text.strip() if res else "Upcoming"})

        # SIDEARM (D1/D3)
        else:
            for item in soup.select('.sidearm-schedule-game'):
                opp = item.select_one('.sidearm-schedule-game-opponent-name')
                res = item.select_one('.sidearm-schedule-game-result')
                game_date = clean_date_logic(item)
                if opp:
                    games.append({
                        "Date": game_date,
                        "Opponent": opp.get_text(strip=True).replace("Opponent:", "").strip(),
                        "Status": res.get_text(strip=True) if res else "Scheduled"
                    })
        
        return record, pd.DataFrame(games).drop_duplicates()
    except:
        return "Record: N/A", pd.DataFrame()

# --- COLOR CODING LOGIC ---

def style_status(val):
    """Applies colors: Green for Wins, Red for Losses, Yellow for Live/Upcoming."""
    color = 'white'
    if 'W' in val: color = '#28a745' # Green
    elif 'L' in val: color = '#dc3545' # Red
    elif any(x in val.upper() for x in ['AM', 'PM', 'LIVE', 'TBD']): color = '#ffc107' # Yellow/Gold
    return f
