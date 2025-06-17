import streamlit as st


def show_probantenauswahl(person_db):
    """
    Zeigt die Probantenauswahlseite an und ermöglicht die Auswahl eines EKG-Tests.
    Ermöglicht außerdem das Hinzufügen neuer Personen mit EKG-Test (inkl. Speichern in JSON)
    und das Löschen nicht-fixierter Probanten.
    Args:
        person_db (PersonDB): Die Personen-Datenbank.
    """
    st.title("Probantenauswahl")
    st.write("Bitte wählen Sie einen Probanten aus:")
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
            st.write(f"**ID:** {person.id}")
            st.write(f"**Name:** {person.firstname} {person.lastname}")
            st.write(f"**Geburtsjahr:** {person.date_of_birth}")
            st.write("### EKG-Tests:")
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

    st.button("Zurück zur Startseite", on_click=lambda: st.session_state.update(state="start"))

    # --- Neue Person mit EKG-Test hinzufügen ---
    st.write("---")
    st.subheader("Neue Person mit EKG-Test hinzufügen")

    with st.form("add_person_form"):
        firstname = st.text_input("Vorname")
        lastname = st.text_input("Nachname")
        date_of_birth = st.text_input("Geburtsjahr")
        ekg_test_id = st.text_input("EKG-Test-ID")
        ekg_test_date = st.text_input("EKG-Test-Datum")
        ekg_file = st.file_uploader("EKG-Datei (.txt) hochladen", type=["txt"])
        picture_file = st.file_uploader("Bild hochladen (optional)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Hinzufügen")

        if submitted:
            from person import Person
            import uuid
            import json
            import os

            # Bild speichern, falls vorhanden
            picture_path = ""
            if picture_file is not None:
                picture_folder = "../data/bilder/"
                os.makedirs(picture_folder, exist_ok=True)
                picture_path = os.path.join(picture_folder, picture_file.name)
                with open(picture_path, "wb") as f:
                    f.write(picture_file.getbuffer())
                # Für die Speicherung im JSON ggf. relativen Pfad verwenden:
                picture_path = f"bilder/{picture_file.name}"

            # EKG-Datei speichern
            ekg_result_link = ""
            if ekg_file is not None:
                ekg_folder = "../data/ekg/"
                os.makedirs(ekg_folder, exist_ok=True)
                ekg_result_link = os.path.join(ekg_folder, ekg_file.name)
                with open(ekg_result_link, "wb") as f:
                    f.write(ekg_file.getbuffer())
                ekg_result_link = f"ekg/{ekg_file.name}"

            new_person_dict = {
                "id": str(uuid.uuid4()),
                "firstname": firstname,
                "lastname": lastname,
                "date_of_birth": date_of_birth,
                "picture_path": picture_path,
                "ekg_tests": [
                    {
                        "id": ekg_test_id,
                        "date": ekg_test_date,
                        "result_link": ekg_result_link
                    }
                ],
                "fixed": False
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
            # Passe ggf. den Pfad an!
            with open("../data/person_db.json", "w", encoding="utf-8") as f:
                json.dump(persons_as_dicts, f, ensure_ascii=False, indent=2)
            # ------------------------

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
        if st.button("Probant löschen"):
            person_to_delete = next((p for p in deletable_persons if f"{p.firstname} {p.lastname}" == delete_selection), None)
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
                    import json
                    json.dump(persons_as_dicts, f, ensure_ascii=False, indent=2)
                st.success(f"Probant {delete_selection} wurde gelöscht!")
                st.rerun()
    else:
        st.info("Keine löschbaren Probanten vorhanden.")

def show_plot_page(person_db):
    """
    Zeigt die Plot-Seite für das ausgewählte EKG an.

    Args:
        person_db (PersonDB): Die Personen-Datenbank.
    """
    st.title("EKG-Daten Plot")
    ekg_id = st.session_state.get("selected_ekg_id")
    person_id = st.session_state.get("selected_person_id")
    if not ekg_id or not person_id:
        st.warning("Kein Test ausgewählt.")
        return

    person = person_db.get_person_by_id(person_id)
    ekg_test = next((e for e in person.ekg_tests if e.test_id == ekg_id), None)
    if not ekg_test:
        st.warning("Kein EKG gefunden.")
        return

    st.write(f"**Test-ID:** {ekg_test.test_id}")
    st.write(f"**Datum:** {ekg_test.date}")

    try:
        fig, num_peaks, bpm = ekg_test.plot()
        st.plotly_chart(fig)
        st.write(f"**Anzahl der Peaks:** {num_peaks}")
        st.write(f"**Herzfrequenz:** {int(round(bpm))} bpm")
    except Exception as e:
        st.error(f"Fehler beim Laden oder Plotten der EKG-Daten: {e}")
    st.button("Zurück zur Probantenauswahl", on_click=lambda: st.session_state.update(state="probantenauswahl"))