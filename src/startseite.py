import streamlit as st

def show_start_page():
    st.title("Willkommen zur EKG-Datenanalyse")
    st.write("Analyse und Verwaltung von EKG-Daten und Probanten.")
    st.button("Zur Auswahl", on_click=lambda: st.session_state.update(state="probantenauswahl"))
    st.image("../data/pictures/startgif.gif", use_container_width=True, caption="EKG-Datenanalyse")