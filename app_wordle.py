import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import json
import altair as alt

def plot_player_attempts(player_df):
    # Vytvořím dataframe s počtem pokusů 1–6 (i pokud je počet 0)
    all_attempts = pd.DataFrame({'Attempt': list(range(1,7))})
    counts = player_df['score'].value_counts().reset_index()
    counts.columns = ['Attempt', 'Count']
    counts['Attempt'] = counts['Attempt'].astype(int)
    chart_df = all_attempts.merge(counts, on='Attempt', how='left').fillna(0)

    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X('Attempt:O', title='Attempt Number'),
            y=alt.Y('Count:Q', title='Count', scale=alt.Scale(domain=[0, chart_df['Count'].max()+1])),
            tooltip=['Attempt', 'Count']
        )
        .properties(width=400, height=200)
        .configure_axis(grid=False)
    )
    return chart

creds_dict = st.secrets["gcp_service_account"]

# Nastavení přístupu
scope = ["https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Otevři sheet
sheet = client.open("wordle_scores").sheet1

players = ["Ondra", "Lucie", "Tomáš"]

st.title("Wordle Score Tracker")

# Načti data jako DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

for player in players:
    st.header(player)

    score_input = st.selectbox(
    f"Zadej skóre pro {player} (1–6 nebo Nevyšlo)", 
    options=["–", 1, 2, 3, 4, 5, 6], 
    key=f"score_{player}"
    )
    
    if st.button(f"Přidat skóre pro {player}", key=f"add_{player}"):
        cesky_cas = datetime.utcnow() + timedelta(hours=2)
        timestamp = cesky_cas.strftime("%d.%m.%Y %H:%M:%S")
        score_to_save = 0 if score_input == "–" else int(score_input)
        sheet.append_row([player, score_to_save, timestamp])
        st.success("Záznam přidán!")
            
    player_df = df[df["player"] == player]
    scores = player_df["score"].astype(int).tolist()
    total = len([s for s in scores if s > 0])
    skipped = len([s for s in scores if s == 0])
    avg = round(sum([s for s in scores if s > 0]) / total, 2) if total else 0
    last5 = [s if s > 0 else "–" for s in scores[-5:]]

    st.write(f"Počet odehraných her: {total}")
    st.write(f"Počet dnů, kdy Wordle nevyšel: {skipped}")
    st.write(f"Průměr: {avg}")
    st.write(f"Posledních 5: {last5 if last5 else '—'}")

    # Graf podle počtu pokusů
    chart_df = player_df["score"].value_counts().sort_index().reset_index()
    chart_df.columns = ["Attempt", "Count"]
    if not player_df.empty:
        st.altair_chart(plot_player_attempts(player_df), use_container_width=True)

    st.markdown("---")
