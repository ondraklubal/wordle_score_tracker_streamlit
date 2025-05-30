import streamlit as st
import gspread
from google.oauth2.service_account import Credentialsimport pandas as pd
from datetime import datetime

import json
creds_dict = st.secrets["gcp_service_account"]

# Nastavení přístupu
scope = ["https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Otevři sheet
sheet = client.open("wordle_scores").sheet1

players = ["Ondra", "Lucie", "Tomáš"]

st.title("Wordle Score Tracker (Google Sheets)")

# Načti data jako DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

for player in players:
    st.header(player)

    score_input = st.number_input(
        f"Add score for {player} (1-6)", min_value=1, max_value=6, step=1, key=f"score_{player}"
    )
    if st.button(f"Přidat skóre pro {player}", key=f"add_{player}"):
        timestamp = datetime.now().isoformat()
        sheet.append_row([player, int(score_input), timestamp])
        st.success("Skóre přidáno!")

    player_df = df[df["player"] == player]
    scores = player_df["score"].astype(int).tolist()
    total = len(scores)
    avg = round(sum(scores)/total, 2) if total else 0
    last5 = scores[-5:]

    st.write(f"Počet her: {total}")
    st.write(f"Průměr: {avg}")
    st.write(f"Posledních 5: {last5 if last5 else '—'}")

    # Graf podle počtu pokusů
    chart_df = player_df["score"].value_counts().sort_index().reset_index()
    chart_df.columns = ["Attempt", "Count"]
    st.bar_chart(chart_df.set_index("Attempt"))

    st.markdown("---")
