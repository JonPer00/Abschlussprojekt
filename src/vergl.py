import streamlit as st
import json

def show_vergleich_page(person_db):
    """
    Zeigt eine Vergleichsseite für zwei Probanten und deren EKGs inkl. editierbarer Diagnosen.
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
        .divider {
            border-left: 3px solid #1f77b4;
            height: 100%;
            margin: 0 1em;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-title">🔬 EKG-Vergleich</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Vergleichen Sie zwei Probanten und deren EKGs.</div>', unsafe_allow_html=True)
    st.write("---")

    if not person_db.persons or len(person_db.persons) < 2:
        st.warning("Mindestens zwei Probanten werden benötigt.")
        return

    names = person_db.get_names()

    col_left, col_div, col_right = st.columns([5, 1, 5])
    with col_left:
        st.markdown("#### Probant 1")
        person1_name = st.selectbox("Probant 1 auswählen", names, key="vergleich_person1")
        person1 = person_db.get_person_by_name(person1_name)
        ekg1 = None
        if person1:
            ekg1_options = [f"{e.test_id}: {e.date}" for e in person1.ekg_tests]
            ekg1_sel = st.selectbox("EKG von Probant 1 auswählen", ekg1_options, key="vergleich_ekg1")
            ekg1_id = ekg1_sel.split(":")[0]
            ekg1 = next((e for e in person1.ekg_tests if str(e.test_id) == ekg1_id), None)

    with col_div:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("#### Probant 2")
        # Person 2 darf nicht Person 1 sein
        names2 = [n for n in names if n != person1_name]
        person2_name = st.selectbox("Probant 2 auswählen", names2, key="vergleich_person2")
        person2 = person_db.get_person_by_name(person2_name)
        ekg2 = None
        if person2:
            ekg2_options = [f"{e.test_id}: {e.date}" for e in person2.ekg_tests]
            ekg2_sel = st.selectbox("EKG von Probant 2 auswählen", ekg2_options, key="vergleich_ekg2")
            ekg2_id = ekg2_sel.split(":")[0]
            ekg2 = next((e for e in person2.ekg_tests if str(e.test_id) == ekg2_id), None)

    st.write("---")

    col_left, col_div, col_right = st.columns([5, 1, 5])
    with col_left:
        if person1 and ekg1:
            st.markdown(f"**Test-ID:** {ekg1.test_id}")
            st.markdown(f"**Datum:** {ekg1.date}")
            try:
                fig1, num_peaks1, bpm1 = ekg1.plot()
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown(f"**Anzahl der Peaks:** {num_peaks1}")
                st.markdown(f"**Herzfrequenz:** {int(round(bpm1))} bpm")
            except Exception as e:
                st.error(f"Fehler beim Plotten: {e}")

            # Diagnosefeld für EKG1
            diagnosis1 = ""
            with open("../data/person_db.json", "r", encoding="utf-8") as f:
                persons_list = json.load(f)
            for p in persons_list:
                if str(p["id"]) == str(person1.id):
                    for test in p.get("ekg_tests", []):
                        if str(test["id"]) == str(ekg1.test_id):
                            diagnosis1 = test.get("diagnosis", "")

            new_diag1 = st.text_area("Diagnose zu diesem EKG-Test", value=diagnosis1, key=f"vergleich_diag1_{ekg1.test_id}")
            if st.button("Diagnose speichern (links)", key=f"vergleich_save_diag1_{ekg1.test_id}"):
                for p in persons_list:
                    if str(p["id"]) == str(person1.id):
                        for test in p.get("ekg_tests", []):
                            if str(test["id"]) == str(ekg1.test_id):
                                test["diagnosis"] = new_diag1
                with open("../data/person_db.json", "w", encoding="utf-8") as f:
                    json.dump(persons_list, f, ensure_ascii=False, indent=2)
                st.success("Diagnose gespeichert!")
                st.rerun()
            if diagnosis1:
                st.markdown(
                    f'<div class="diag-box"><span class="diag-label">Gespeicherte Diagnose:</span><br>{diagnosis1}</div>',
                    unsafe_allow_html=True
                )
                if st.button("Diagnose löschen (links)", key=f"vergleich_del_diag1_{ekg1.test_id}"):
                    for p in persons_list:
                        if str(p["id"]) == str(person1.id):
                            for test in p.get("ekg_tests", []):
                                if str(test["id"]) == str(ekg1.test_id):
                                    test["diagnosis"] = ""
                    with open("../data/person_db.json", "w", encoding="utf-8") as f:
                        json.dump(persons_list, f, ensure_ascii=False, indent=2)
                    st.success("Diagnose gelöscht!")
                    st.rerun()

    with col_div:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with col_right:
        if person2 and ekg2:
            st.markdown(f"**Test-ID:** {ekg2.test_id}")
            st.markdown(f"**Datum:** {ekg2.date}")
            try:
                fig2, num_peaks2, bpm2 = ekg2.plot()
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown(f"**Anzahl der Peaks:** {num_peaks2}")
                st.markdown(f"**Herzfrequenz:** {int(round(bpm2))} bpm")
            except Exception as e:
                st.error(f"Fehler beim Plotten: {e}")

            # Diagnosefeld für EKG2
            diagnosis2 = ""
            with open("../data/person_db.json", "r", encoding="utf-8") as f:
                persons_list = json.load(f)
            for p in persons_list:
                if str(p["id"]) == str(person2.id):
                    for test in p.get("ekg_tests", []):
                        if str(test["id"]) == str(ekg2.test_id):
                            diagnosis2 = test.get("diagnosis", "")

            new_diag2 = st.text_area("Diagnose zu diesem EKG-Test", value=diagnosis2, key=f"vergleich_diag2_{ekg2.test_id}")
            if st.button("Diagnose speichern (rechts)", key=f"vergleich_save_diag2_{ekg2.test_id}"):
                for p in persons_list:
                    if str(p["id"]) == str(person2.id):
                        for test in p.get("ekg_tests", []):
                            if str(test["id"]) == str(ekg2.test_id):
                                test["diagnosis"] = new_diag2
                with open("../data/person_db.json", "w", encoding="utf-8") as f:
                    json.dump(persons_list, f, ensure_ascii=False, indent=2)
                st.success("Diagnose gespeichert!")
                st.rerun()
            if diagnosis2:
                st.markdown(
                    f'<div class="diag-box"><span class="diag-label">Gespeicherte Diagnose:</span><br>{diagnosis2}</div>',
                    unsafe_allow_html=True
                )
                if st.button("Diagnose löschen (rechts)", key=f"vergleich_del_diag2_{ekg2.test_id}"):
                    for p in persons_list:
                        if str(p["id"]) == str(person2.id):
                            for test in p.get("ekg_tests", []):
                                if str(test["id"]) == str(ekg2.test_id):
                                    test["diagnosis"] = ""
                    with open("../data/person_db.json", "w", encoding="utf-8") as f:
                        json.dump(persons_list, f, ensure_ascii=False, indent=2)
                    st.success("Diagnose gelöscht!")
                    st.rerun()

    st.write("---")
    st.button("Zurück zur Startseite", on_click=lambda: st.session_state.update(state="start"))