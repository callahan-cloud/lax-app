import streamlit as st
import pandas as pd

# 1. Setup
st.set_page_config(page_title="LaxHub", page_icon="🥍")
st.title("🥍 LaxScore: Ad-Free Hub")

# 2. Sidebar for Updating (You can hide this!)
with st.sidebar:
    st.header("Admin: Update Polls")
    st.info("Paste the Top 20 here once a week to update the app for your phone.")
    raw_input = st.text_area("Paste Team Names (One per line):", 
                            "Notre Dame\nDuke\nVirginia\nMaryland\nCornell")
    
    if st.button("Save Rankings"):
        st.success("Rankings Updated!")

# 3. Processing the Data
teams = raw_input.split('\n')
df = pd.DataFrame({
    "Rank": range(1, len(teams) + 1),
    "Team": teams
})

# 4. The Mobile UI
tab1, tab2 = st.tabs(["📊 Top 20 Polls", "⏱️ Live Scores"])

with tab1:
    div = st.pills("Division", ["D1", "D2", "D3"], default="D1")
    st.subheader(f"{div} USILA Coaches Poll")
    
    # Beautiful display for mobile
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Live Scoreboard")
    st.warning("Automatic live scores are currently restricted by the source site.")
    st.info("Tip: Most fans use this app to see the Top 20 clean, then tap a link for the ESPN+ stream.")
    
    # Button to link to the clean NCAA scoreboard
    st.link_button("Go to Official Clean Scoreboard", 
                   "https://www.ncaa.com/scoreboard/lacrosse-men/d1")

st.divider()
st.caption("No Ads. No Tracking. Just Lacrosse.")
