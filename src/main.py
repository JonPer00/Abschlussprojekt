import streamlit as st
import json
from startseite import show_start_page
from probantenauswahl import show_probantenauswahl, show_plot_page
from persondb import PersonDB
from probdel import show_probdel  # <--- NEU

def main():
    """
    Hauptfunktion der Streamlit-App. Steuert die Navigation zwischen den Seiten.
    """
    if "state" not in st.session_state:
        st.session_state.state = "start"
    if "selected_ekg_id" not in st.session_state:
        st.session_state.selected_ekg_id = None
    if "selected_person_id" not in st.session_state:
        st.session_state.selected_person_id = None

    with open("../data/person_db.json", "r", encoding="utf-8") as f:
        persons_list = json.load(f)
    person_db = PersonDB(persons_list)

    if st.session_state.state == "start":
        show_start_page()
    elif st.session_state.state == "probantenauswahl":
        show_probantenauswahl(person_db)
    elif st.session_state.state == "plot":
        show_plot_page(person_db)
    elif st.session_state.state == "probdel":  # <--- NEU
        show_probdel(person_db)
    elif st.session_state.state == "vergl":
        from vergl import show_vergleich_page
        show_vergleich_page(person_db)

if __name__ == "__main__":
    main()