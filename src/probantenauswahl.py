import streamlit as st
import json
import io

def show_probantenauswahl(person_db):
    """
    Zeigt die Probantenauswahlseite an und ermöglicht die Auswahl eines EKG-Tests.
    """
    # --- Theme und Layout ---
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .stButton>button {
            background-color: #1f77b4;
            color: white;
            font-size: 1.1em;
            border-radius: 8px;
            padding: 0.4em 1.5em;
            margin: 0.3em 0;
        }
        .stButton>button:hover {
            background-color: #105a8b;
            color: #fff;
        }
        .big-title {
            font-size: 2em;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 0.2em;
        }
        .subtitle {
            font-size: 1.1em;
            color: #333;
            margin-bottom: 1.2em;
        }
        .diag-box {
            background-color: #e9ecef;
            border-radius: 8px;
            padding: 1em;
            margin-bottom: 1em;
        }
        .diag-label {
            font-weight: bold;
            color: #1f77b4;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-title">👤 Probantenauswahl</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Wählen Sie einen Probanten aus und sehen Sie sich die EKG-Tests an.</div>', unsafe_allow_html=True)

    st.write("---")
    if not person_db.persons:
        st.warning("Keine Probanten verfügbar.")
        return

    names = person_db.get_names()
    auswahl = st.selectbox("Probant auswählen:", names)
    person = person_db.get_person_by_name(auswahl)

    if person:
        col1, col2 = st.columns([1, 3])
        with col1:
            if person.picture_path:
                st.image(f"../{person.picture_path}", caption="Probantenbild", width=150)
        with col2:
            st.markdown(f"**ID:** {person.id}")
            st.markdown(f"**Name:** {person.firstname} {person.lastname}")
            st.markdown(f"**Geburtsjahr:** {person.date_of_birth}")
            st.markdown("### EKG-Tests:")
            for ekg_test in person.ekg_tests:
                try:
                    ekg_test.load_data()
                    ms = ekg_test.time[-1] - ekg_test.time[0]
                    minuten = ms / 1000 / 60
                except Exception:
                    minuten = None

                button_label = f"Ergebnis anzeigen (ID: {ekg_test.test_id}) - {ekg_test.date}"
                if minuten is not None:
                    button_label += f" | Dauer: {minuten:.1f} min"
                else:
                    button_label += " | Dauer: unbekannt"

                if st.button(button_label, key=f"plot_{ekg_test.test_id}"):
                    st.session_state.selected_ekg_id = ekg_test.test_id
                    st.session_state.selected_person_id = person.id
                    st.session_state.state = "plot"
                    st.rerun()

    st.write("---")
    st.button("Zurück zur Startseite", on_click=lambda: st.session_state.update(state="start"))

def show_plot_page(person_db):
    """
    Zeigt die Plot-Seite für das ausgewählte EKG an.
    Fügt ein Diagnosefeld hinzu, das mit der EKG-Test-ID in der JSON gespeichert wird.
    Bereits gespeicherte Diagnosen werden angezeigt und können gelöscht werden.
    """
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .big-title {
            font-size: 2em;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 0.2em;
        }
        .diag-box {
            background-color: #e9ecef;
            border-radius: 8px;
            padding: 1em;
            margin-bottom: 1em;
        }
        .diag-label {
            font-weight: bold;
            color: #1f77b4;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-title">📈 EKG-Daten Plot</div>', unsafe_allow_html=True)

    ekg_id = st.session_state.get("selected_ekg_id")
    person_id = st.session_state.get("selected_person_id")
    if not ekg_id or not person_id:
        st.warning("Kein Test ausgewählt.")
        return

    # Diagnose immer aus JSON laden, damit sie aktuell ist
    with open("../data/person_db.json", "r", encoding="utf-8") as f:
        persons_list = json.load(f)

    diagnosis = ""
    for p in persons_list:
        if str(p["id"]) == str(person_id):
            for test in p.get("ekg_tests", []):
                if str(test["id"]) == str(ekg_id):
                    diagnosis = test.get("diagnosis", "")

    person = person_db.get_person_by_id(person_id)
    ekg_test = next((e for e in person.ekg_tests if str(e.test_id) == str(ekg_id)), None)
    if not ekg_test:
        st.warning("Kein EKG gefunden.")
        return

    st.markdown(f"**Test-ID:** {ekg_test.test_id}")
    st.markdown(f"**Datum:** {ekg_test.date}")

    try:
        fig, num_peaks, bpm = ekg_test.plot()
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**Anzahl der Peaks:** {num_peaks}")
        st.markdown(f"**Herzfrequenz:** {int(round(bpm))} bpm")

        # Download-Button für den Plot als PNG
        buf = io.StringIO()
        fig.write_html(buf)
        st.download_button(
            label="Plot als HTML herunterladen",
            data=buf.getvalue(),
            file_name=f"ekg_plot_{ekg_test.test_id}.html",
            mime="text/html"
    )

    except Exception as e:
        st.error(f"Fehler beim Laden oder Plotten der EKG-Daten: {e}")


    st.write("---")

    # Diagnose anzeigen und bearbeiten
    new_diagnosis = st.text_area(
        "Diagnose zu diesem EKG-Test",
        value=diagnosis,
        key=f"diag_{ekg_id}"
    )

    if st.button("Diagnose speichern", key=f"save_diag_{ekg_id}"):
        # Diagnose in JSON speichern
        for p in persons_list:
            if str(p["id"]) == str(person_id):
                for test in p.get("ekg_tests", []):
                    if str(test["id"]) == str(ekg_id):
                        test["diagnosis"] = new_diagnosis
        with open("../data/person_db.json", "w", encoding="utf-8") as f:
            json.dump(persons_list, f, ensure_ascii=False, indent=2)
        st.success("Diagnose gespeichert!")
        st.rerun()

    st.write("---")
    
    # Diagnose immer aktuell anzeigen
    if diagnosis:
        st.markdown(
            f'<div class="diag-box"><span class="diag-label">Gespeicherte Diagnose:</span><br>{diagnosis}</div>',
            unsafe_allow_html=True
        )
        if st.button("Diagnose löschen", key=f"del_diag_{ekg_id}"):
            # Diagnose in JSON löschen
            for p in persons_list:
                if str(p["id"]) == str(person_id):
                    for test in p.get("ekg_tests", []):
                        if str(test["id"]) == str(ekg_id):
                            test["diagnosis"] = ""
            with open("../data/person_db.json", "w", encoding="utf-8") as f:
                json.dump(persons_list, f, ensure_ascii=False, indent=2)
            st.success("Diagnose gelöscht!")
            st.rerun()

    st.write("---")
    st.button("Zurück zur Probantenauswahl", on_click=lambda: st.session_state.update(state="probantenauswahl"))