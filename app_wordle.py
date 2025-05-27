import streamlit as st
import pandas as pd
import altair as alt

players = ["Ondra", "Lucie", "Tomáš"]

if "scores" not in st.session_state:
    st.session_state.scores = {p: [] for p in players}

st.title("Wordle Score Tracker")

for player in players:
    st.header(player)
    score_input = st.number_input(
        f"Add score for {player} (1-6)", min_value=1, max_value=6, step=1, key=f"input_{player}"
    )
    if st.button(f"Add score {player}", key=f"add_{player}"):
        st.session_state.scores[player].append(score_input)

    if st.button(f"Remove last score {player}", key=f"remove_{player}"):
        if st.session_state.scores[player]:
            st.session_state.scores[player].pop()

    scores = st.session_state.scores[player]
    last_5 = scores[-5:]
    total_games = len(scores)
    avg = round(sum(scores) / total_games, 2) if total_games > 0 else 0

    st.write(f"Last 5 Scores: {last_5 if last_5 else '—'}")
    st.write(f"Total Games: {total_games}")
    st.write(f"Average Score: {avg}")

    # Data pro graf
    counts = {i: 0 for i in range(1, 7)}
    for s in scores:
        counts[s] += 1
    df = pd.DataFrame({
        "Attempt": list(counts.keys()),
        "Count": list(counts.values())
    })

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Attempt:O', title='Attempt Number'),
        y=alt.Y('Count:Q', title='Number of Completions'),
        tooltip=['Attempt', 'Count']
    ).properties(width=600, height=200)

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")  # oddělovač mezi hráči
