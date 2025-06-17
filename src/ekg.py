import numpy as np
import pandas as pd
import plotly.express as px

class EKGTest:
    """
    Repräsentiert einen einzelnen EKG-Test mit Methoden zur Analyse und Visualisierung.
    """

    def __init__(self, test_id, date, result_link):
        """
        Initialisiert ein EKGTest-Objekt.

        Args:
            test_id (str): Die eindeutige ID des EKG-Tests.
            date (str): Das Testdatum.
            result_link (str): Pfad zur EKG-Datendatei.
        """
        self.test_id = test_id
        self.date = date
        self.result_link = result_link
        self.voltage = None
        self.time = None
        self.peaks = None

    def load_data(self):
        """
        Lädt die EKG-Daten aus der Datei und setzt die Zeitachse auf 0.
        """
        data = np.loadtxt(self.result_link, delimiter='\t')
        self.voltage = data[:, 0]
        #self.time = data[:, 1] - data[:, 1][0]
        # mittels numpy linspace time bei 0 starten und in zweier schritte erhöhen
        self.time = np.linspace(0, len(self.voltage) * 2, len(self.voltage), dtype=int)

    def find_peaks(self, threshold=350):
        """
        Findet Peaks im EKG-Signal, die über dem Schwellwert liegen und mindestens 400 ms Abstand haben.

        Args:
            threshold (float): Schwellwert für die Peak-Erkennung.

        Returns:
            list: Indizes der gefundenen Peaks.
        """
        if self.voltage is None or self.time is None:
            self.load_data()
        peak_indices = []
        for i in range(1, len(self.voltage) - 1):
            if (
                self.voltage[i] >= self.voltage[i - 1]
                and self.voltage[i] >= self.voltage[i + 1]
                and self.voltage[i] > threshold
            ):
                peak_indices.append(i)
        filtered_peaks = []
        last_peak_time = -np.inf
        for idx in peak_indices:
            if self.time[idx] - last_peak_time >= 400:
                filtered_peaks.append(idx)
                last_peak_time = self.time[idx]
        self.peaks = filtered_peaks
        return filtered_peaks

    def bpm(self):
        """
        Berechnet die Herzfrequenz (bpm) basierend auf den gefundenen Peaks.

        Returns:
            float: Herzfrequenz in bpm.
        """
        if self.peaks is None:
            self.find_peaks()
        num_peaks = len(self.peaks)
        if num_peaks > 1:
            dauer_ms = self.time[self.peaks[-1]] - self.time[self.peaks[0]]
            dauer_min = dauer_ms / 1000 / 60
            bpm = num_peaks / dauer_min if dauer_min > 0 else 0
        else:
            bpm = 0
        return bpm

    def plot(self, n=5000, threshold=350):
        """
        Plottet das EKG-Signal mit markierten Peaks.

        Args:
            n (int): Standardlänge für den Plot-Ausschnitt.
            threshold (float): Schwellwert für die Peak-Erkennung.

        Returns:
            tuple: (Plotly-Figure, Anzahl Peaks, Herzfrequenz)
        """
        if self.voltage is None or self.time is None:
            self.load_data()
        if self.peaks is None:
            self.find_peaks(threshold)
        num_peaks = len(self.peaks)
        if num_peaks >= 5:
            start_idx = max(self.peaks[0] - 200, 0)
            end_idx = min(self.peaks[4] + 200, len(self.voltage))
            x_range = [self.time[start_idx], self.time[end_idx-1]]
        elif num_peaks > 0:
            start_idx = max(self.peaks[0] - 200, 0)
            end_idx = min(self.peaks[-1] + 200, len(self.voltage))
            x_range = [self.time[start_idx], self.time[end_idx-1]]
        else:
            start_idx = 0
            end_idx = min(n, len(self.voltage))
            x_range = None

        is_peak = np.zeros_like(self.voltage, dtype=bool)
        for idx in self.peaks:
            is_peak[idx] = True

        df_plot = pd.DataFrame({
            'Time in ms': self.time,
            'Voltage in mV': self.voltage,
            'is_peak': is_peak
        })

        df_plot_down = df_plot.iloc[::4].copy()
        df_peaks = df_plot[df_plot['is_peak']]

        fig = px.line(df_plot_down, x='Time in ms', y='Voltage in mV', title="EKG Signal")
        fig.add_scatter(
            x=df_peaks['Time in ms'],
            y=df_peaks['Voltage in mV'],
            mode='markers',
            name='Peaks',
            marker=dict(color='red', size=8)
        )
        if x_range is not None:
            fig.update_layout(xaxis_range=x_range)
        return fig, num_peaks, self.bpm()
    



    