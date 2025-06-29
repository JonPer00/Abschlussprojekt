import numpy as np
import pandas as pd
import plotly.express as px
import os

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
        self.filetype = None  # "txt" oder "csv"

    def load_data(self):
        """
        Lädt die EKG-Daten aus der Datei und setzt die Zeitachse.
        Erkennt automatisch das Dateiformat (txt oder csv).
        """
        _, ext = os.path.splitext(self.result_link)
        ext = ext.lower()
        self.filetype = ext.replace('.', '')

        if self.filetype == "csv":
            df = pd.read_csv(self.result_link)
            if df.shape[1] >= 2:
                self.time = df.iloc[:, 0].values * 1000  # Sekunden -> ms
                self.voltage = df.iloc[:, 1].values
            else:
                raise ValueError("CSV-Datei hat nicht mindestens 2 Spalten.")
        elif self.filetype == "txt":
            data = np.loadtxt(self.result_link, delimiter='\t')
            self.voltage = data[:, 0]
            self.time = np.linspace(0, len(self.voltage) * 2, len(self.voltage), dtype=int)
        else:
            raise ValueError("Unbekanntes Dateiformat: " + ext)

    def find_peaks(self, threshold=350, min_distance_ms=400):
        """
        Findet Peaks im EKG-Signal, die über dem Schwellwert liegen und mindestens 400 ms Abstand haben.

        Args:
            threshold (float): Schwellwert für die Peak-Erkennung.
            min_distance_ms (int): Minimaler Abstand zwischen Peaks in ms.

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
            if self.time[idx] - last_peak_time >= min_distance_ms:
                filtered_peaks.append(idx)
                last_peak_time = self.time[idx]
        self.peaks = filtered_peaks
        return filtered_peaks

    def find_peaks_csv(self, threshold=0.3, min_distance_ms=400):
        """
        Findet Peaks im EKG-Signal für CSV-Dateien (mV-Bereich), die über dem Schwellwert liegen und mindestens min_distance_ms Abstand haben.
        """
        if self.voltage is None or self.time is None:
            self.load_data()
        if len(self.time) < 2:
            return []
        dt = np.median(np.diff(self.time))
        min_distance_samples = int(min_distance_ms / dt)
        peaks = []
        last_peak = -min_distance_samples
        for i in range(1, len(self.voltage) - 1):
            if (
                self.voltage[i] > threshold and
                self.voltage[i] > self.voltage[i - 1] and
                self.voltage[i] > self.voltage[i + 1] and
                (i - last_peak) >= min_distance_samples
            ):
                peaks.append(i)
                last_peak = i
        self.peaks = np.array(peaks)
        return self.peaks

    def bpm(self, threshold=350):
        """
        Berechnet die Herzfrequenz (bpm) basierend auf den gefundenen Peaks.
        """
        if self.filetype == "csv":
            if self.peaks is None:
                self.find_peaks_csv()
            peaks = self.peaks
        else:
            if self.peaks is None:
                self.find_peaks()
            peaks = self.peaks

        num_peaks = len(peaks)
        if num_peaks > 1:
            dauer_ms = self.time[peaks[-1]] - self.time[peaks[0]]
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
        import streamlit as st

        if self.voltage is None or self.time is None:
            self.load_data()
        if self.filetype == "csv":
            if self.peaks is None:
                self.find_peaks_csv()
            # Interaktives Zeitfenster für CSV
            total_len = len(self.voltage)
            max_start = max(total_len - n, 0)
            start_idx = 0
            if max_start > 0:
                start_idx = int(st.slider("Zeitfenster verschieben (Startindex)", 0, max_start, 0, step=100))
            end_idx = min(start_idx + n, total_len)
            is_peak = np.zeros_like(self.voltage, dtype=bool)
            for idx in self.peaks:
                if start_idx <= idx < end_idx:
                    is_peak[idx] = True
            df_plot = pd.DataFrame({
                'Time in ms': self.time[start_idx:end_idx],
                'Voltage in mV': self.voltage[start_idx:end_idx],
                'is_peak': is_peak[start_idx:end_idx]
            })
        else:
            if self.peaks is None:
                self.find_peaks()
            # Für TXT: wie früher, immer die ersten n Werte
            start_idx = 0
            end_idx = min(n, len(self.voltage))
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
        if self.filetype != "csv":
            # Nur für TXT: Zoom auf die ersten Peaks
            num_peaks = len(self.peaks)
            if num_peaks >= 5:
                start_idx = max(self.peaks[0] - 200, 0)
                end_idx = min(self.peaks[4] + 200, len(self.voltage))
                x_range = [self.time[start_idx], self.time[end_idx-1]]
                fig.update_layout(xaxis_range=x_range)
            elif num_peaks > 0:
                start_idx = max(self.peaks[0] - 200, 0)
                end_idx = min(self.peaks[-1] + 200, len(self.voltage))
                x_range = [self.time[start_idx], self.time[end_idx-1]]
                fig.update_layout(xaxis_range=x_range)
        fig.update_layout(xaxis_title="Time in ms", yaxis_title="Voltage in mV")
        return fig, len(self.peaks), self.bpm()