import streamlit as st
import os
import json
from src.person import Person

def show_probdel(person_db):
    """
    Seite zum Hinzufügen und Löschen von Probanten.
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
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-title">🗑️ Probantenverwaltung</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Hier können Sie neue Probanten anlegen oder bestehende löschen.</div>', unsafe_allow_html=True)

    # --- Neue Person mit EKG-Test hinzufügen ---
    st.write("---")
    st.subheader("Neue Person mit EKG-Test hinzufügen")

    with st.form("add_person_form"):
        firstname = st.text_input("Vorname")
        lastname = st.text_input("Nachname")
        date_of_birth = st.text_input("Geburtsjahr")
        ekg_test_date = st.text_input("EKG-Test-Datum")
        ekg_file = st.file_uploader("EKG-Datei (.txt oder .csv) hochladen", type=["txt", "csv"])
        picture_file = st.file_uploader("Bild hochladen (optional)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Hinzufügen")

        if submitted:
            # Bild speichern, falls vorhanden
            picture_path = ""
            if picture_file is not None:
                picture_folder = "../data/bilder/"
                os.makedirs(picture_folder, exist_ok=True)
                picture_path = os.path.join(picture_folder, picture_file.name)
                with open(picture_path, "wb") as f:
                    f.write(picture_file.getbuffer())

            # EKG-Datei speichern
            ekg_result_link = ""
            if ekg_file is not None:
                ekg_folder = "../data/ekg/"
                os.makedirs(ekg_folder, exist_ok=True)
                ekg_result_link = os.path.join(ekg_folder, ekg_file.name)
                with open(ekg_result_link, "wb") as f:
                    f.write(ekg_file.getbuffer())

            # Für die JSON: immer relativer Pfad ab ../data/...
            json_picture_path = picture_path.replace("\\", "/").replace("../", "")
            json_ekg_result_link = ekg_result_link if not ekg_result_link else os.path.normpath(ekg_result_link).replace("\\", "/")

            # Fortlaufende Personen-ID bestimmen
            if person_db.persons:
                try:
                    max_id = max([int(p.id) for p in person_db.persons if str(p.id).isdigit()])
                    next_person_id = str(max_id + 1)
                except Exception:
                    next_person_id = "1"
            else:
                next_person_id = "1"

            # Fortlaufende EKG-ID bestimmen (über alle Personen hinweg)
            all_ekg_ids = []
            for p in person_db.persons:
                for t in p.ekg_tests:
                    if hasattr(t, "test_id"):
                        try:
                            all_ekg_ids.append(int(t.test_id))
                        except Exception:
                            pass
                    elif isinstance(t, dict) and "id" in t:
                        try:
                            all_ekg_ids.append(int(t["id"]))
                        except Exception:
                            pass
            ekg_id = str(max(all_ekg_ids) + 1) if all_ekg_ids else "1"

            new_person_dict = {
                "id": next_person_id,
                "firstname": firstname,
                "lastname": lastname,
                "date_of_birth": date_of_birth,
                "picture_path": json_picture_path,
                "ekg_tests": [
                    {
                        "id": ekg_id,
                        "date": ekg_test_date,
                        "result_link": json_ekg_result_link
                    }
                ],
                "fixed": False  # Neue Personen sind nicht fixiert
            }
            new_person = Person(new_person_dict)
            person_db.persons.append(new_person)

            # --- In JSON speichern ---
            persons_as_dicts = []
            for p in person_db.persons:
                persons_as_dicts.append({
                    "id": p.id,
                    "firstname": p.firstname,
                    "lastname": p.lastname,
                    "date_of_birth": p.date_of_birth,
                    "picture_path": p.picture_path,
                    "ekg_tests": [
                        {
                            "id": t.test_id,
                            "date": t.date,
                            "result_link": t.result_link
                        } for t in p.ekg_tests
                    ],
                    "fixed": getattr(p, "fixed", False)
                })
            with open("../data/person_db.json", "w", encoding="utf-8") as f:
                json.dump(persons_as_dicts, f, ensure_ascii=False, indent=2)

            st.success(f"Person {firstname} {lastname} wurde hinzugefügt!")
            st.rerun()

    # --- Probant löschen ---
    st.write("---")
    st.subheader("Probant löschen")

    # Nur nicht-fixierte Probanten anzeigen
    deletable_persons = [p for p in person_db.persons if not getattr(p, "fixed", False)]
    delete_names = [f"{p.firstname} {p.lastname}" for p in deletable_persons]

    if deletable_persons:
        delete_selection = st.selectbox("Probant zum Löschen auswählen", delete_names, key="delete_select_probant")
        # Sicherheitsabfrage vor dem Löschen
        if st.button("Probant löschen"):
            st.session_state.confirm_delete = delete_selection

        if "confirm_delete" in st.session_state and st.session_state.confirm_delete:
            st.warning(f"Möchtest du den Probanten '{st.session_state.confirm_delete}' wirklich löschen?")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("Ja, löschen"):
                    person_to_delete = next((p for p in deletable_persons if f"{p.firstname} {p.lastname}" == st.session_state.confirm_delete), None)
                    if person_to_delete:
                        person_db.persons.remove(person_to_delete)
                        # Auch aus JSON löschen
                        persons_as_dicts = []
                        for p in person_db.persons:
                            persons_as_dicts.append({
                                "id": p.id,
                                "firstname": p.firstname,
                                "lastname": p.lastname,
                                "date_of_birth": p.date_of_birth,
                                "picture_path": p.picture_path,
                                "ekg_tests": [
                                    {
                                        "id": t.test_id,
                                        "date": t.date,
                                        "result_link": t.result_link
                                    } for t in p.ekg_tests
                                ],
                                "fixed": getattr(p, "fixed", False)
                            })
                        with open("../data/person_db.json", "w", encoding="utf-8") as f:
                            json.dump(persons_as_dicts, f, ensure_ascii=False, indent=2)
                        st.success(f"Probant {st.session_state.confirm_delete} wurde gelöscht!")
                        st.session_state.confirm_delete = None
                        st.rerun()
            with col_cancel:
                if st.button("Abbrechen"):
                    st.session_state.confirm_delete = None
    else:
        st.info("Keine löschbaren Probanten vorhanden.")

    st.write("---")
    st.button("Zurück zur Startseite", on_click=lambda: st.session_state.update(state="start"))