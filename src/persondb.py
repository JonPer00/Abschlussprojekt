from person import Person

class PersonDB:
    """
    Datenbank-Klasse für die Verwaltung mehrerer Personen und deren EKG-Tests.
    """

    def __init__(self, persons_list):
        """
        Initialisiert die PersonDB mit einer Liste von Personen.

        Args:
            persons_list (list): Liste von Dictionaries mit Personendaten.
        """
        self.persons = [Person(p) for p in persons_list]

    def get_names(self):
        """
        Gibt eine Liste aller Namen (Vorname Nachname) zurück.

        Returns:
            list: Liste der Namen.
        """
        return [f"{p.firstname} {p.lastname}" for p in self.persons]

    def get_person_by_name(self, name):
        """
        Sucht eine Person anhand des Namens.

        Args:
            name (str): Name im Format "Vorname Nachname".

        Returns:
            Person: Das gefundene Person-Objekt oder None.
        """
        return next((p for p in self.persons if f"{p.firstname} {p.lastname}" == name), None)

    def get_person_by_id(self, person_id):
        """
        Sucht eine Person anhand der ID.

        Args:
            person_id (str): Die Personen-ID.

        Returns:
            Person: Das gefundene Person-Objekt oder None.
        """
        return next((p for p in self.persons if p.id == person_id), None)