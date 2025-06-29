# EKG Analyse-Tool

Willkommen zum Abschlussprojekt von John & Sophia!  
Dieses Tool ermöglicht die Verwaltung, Analyse und den Vergleich von EKG-Daten mit einer modernen, benutzerfreundlichen Oberfläche.

---

## Installation & Setup

1. **Repository klonen oder herunterladen**
2. **Python 3.8+ installieren**
3. **Abhängigkeiten installieren**  
   Öffne ein Terminal im Projektordner und führe aus:
   - streamlit
    - plotly
    - pandas
    - numpy
4. **Projekt starten**  
Rechtsklick auf main.py und "run with streamlit"

5. **Webbrowser öffnet sich automatisch**  
Falls nicht, öffne die angezeigte URL (meist http://localhost:8501) im Browser.

---

## Schritte zur Nutzung

1. **Startseite:**  
Übersicht und Navigation zu allen Funktionen.

2. **Probantenauswahl:**  
- Wähle eine Person und einen EKG-Test aus.
- Sieh Geburtsjahr, Name und Bild der Person.
- Bei mehreren Tests: Auswahlmöglichkeit für den gewünschten Test.

3. **EKG-Analyse:**  
- Testdatum und Länge der Zeitreihe in Minuten werden angezeigt.
- Plot des EKG-Signals mit auswählbarem Zeitbereich.
- Herzrate (bpm) und gleitender Durchschnitt werden angezeigt.
- Diagnosefeld für Nutzer:innen.
- Plot kann als PNG oder HTML heruntergeladen werden.

4. **Probantenverwaltung:**  
- Neue Personen und Tests hinzufügen (inkl. Bild und CSV- oder TXT-Upload).
- Bestehende Personen und alle Attribute bearbeiten.
- Personen löschen.

5. **Vergleich:**  
- Vergleiche zwei Tests oder zwei Personen direkt miteinander.

---

## Hinweise für den Betrieb

- **Datenquellen:**  
  - EKG-Daten können als `.txt` oder `.csv` hochgeladen werden.
  - Bilder werden im Ordner `data/bilder/` gespeichert.
- **Deployment:**  
  - Für Deployment auf Heroku oder Streamlit Cloud:  
 - Stelle sicher, dass alle Abhängigkeiten in `requirements.txt` stehen.
 - Lade das Projekt auf die jeweilige Plattform hoch.

---

## Erfüllte Anforderungen

- **Geburtsjahr, Name und Bild der Personen wird angezeigt** (2 Pkt)
- **Auswahlmöglichkeit für Tests, sofern mehr als ein Test bei einer Person vorliegt** (4 Pkt)
- **Anzeigen des Testdatums und der gesamten Länge der Zeitreihe in Minuten** (4 Pkt)
- **EKG-Daten werden beim Einlesen sinnvoll verarbeitet, um Ladezeiten zu verkürzen** (z.B. durch Reduktion der Auflösung oder vermeiden unnötigen Aufrufes rechenintensiver Funktionen) (2 Pkt)
- **Docstrings für Klassen, Methoden und Funktionen** (2 Pkt)
- **Sinnvolle Berechnung der Herzrate über den gesamten Zeitraum wird angezeigt** (2 Pkt)
- **Stil: Namenskonventionen, sinnvolle Aufteilung in Module, Objektorientierung ohne nicht-notwendigen Legacy-Code** (4 Pkt)
- **Nutzer:in kann sinnvollen Zeitbereich für Plots auswählen und dies geschieht in einer nutzerfreundlichen Art und Weise** (2 Pkt)
- **Neue Personen und Tests können hinzugefügt werden** (4 Pkt)
- **Bestehende Personen können editiert werden (alle Attribute und Bild)** (4 Pkt)
- **Design für Computer Bildschirm optimiert und optisch ansprechend** (2 Pkt)
- **Deployment auf Heroku oder Streamlit Sharing, ggf. müssen sie hierzu ihre Dependencies in eine requirements.txt übertragen** (4 Pkt)
- **Herzrate im sinnvollen gleitenden Durchschnitt als Plot anzeigen** (2 Pkt)
- **Diagnosefeld für Nutzer**
- **Startseite**
- **Vergleich zweier Tests oder Personen**
- **Daten aus einer anderen Datenquelle einlesen (CSV)** (4 Pkt)
- **Plot – Download**

---

## Support

Bei Fragen oder Problemen:  
Bitte kontaktiere John & Sophia oder öffne ein Issue im Repository.

Viel Spaß beim Ausprobieren!