
from src.ekg import EKGTest

class Person:
    """
    Repräsentiert eine Person mit persönlichen Daten und einer Liste von EKG-Tests.
    """

    def __init__(self, person_dict):
        """
        Initialisiert ein Person-Objekt.

        Args:
            person_dict (dict): Dictionary mit Personendaten und EKG-Tests.
        """
        self.id = person_dict['id']
        self.firstname = person_dict['firstname']
        self.lastname = person_dict['lastname']
        self.date_of_birth = person_dict['date_of_birth']
        self.picture_path = person_dict.get('picture_path')
        self.fixed = person_dict.get('fixed', False)  # <--- NEU
        self.ekg_tests = [
            EKGTest(test['id'], test['date'], test['result_link'])
            for test in person_dict.get('ekg_tests', [])
        ]