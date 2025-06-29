import streamlit as st

def show_start_page():
    """
    Zeigt die Startseite der Anwendung mit modernem Design.
    """
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-size: 1.2em;
        border-radius: 8px;
        padding: 0.5em 2em;
        margin: 0.5em 0 2em 0;  /* Oben | Rechts | Unten | Links */
    }
    .stButton>button:hover {
        background-color: #105a8b;
        color: #fff;
    }
    .big-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.2em;
    }
    .subtitle {
        font-size: 1.3em;
        color: #333;
        margin-bottom: 1.5em;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-title">💓 EKG Analyse-Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Willkommen! Analysieren Sie EKG-Daten, verwalten Sie Probanten und visualisieren Sie Herzaktivitäten.</div>', unsafe_allow_html=True)

    st.image("data/bilder/ekg.png", width=500)

    st.write("---")
    st.markdown("### Was möchten Sie tun?")

    col1, spacer1, col2, spacer2, col3 = st.columns([2, 1, 2, 1, 2])
    with col1:
        if st.button("👤 Probantenauswahl"):
            st.session_state.state = "probantenauswahl"
            st.rerun()
    with col2:
        if st.button("🗑️ Probantenverwaltung"):
            st.session_state.state = "probdel"
            st.rerun()
    with col3:
        if st.button("🔬 Probantenvergleichen"):
            st.session_state.state = "vergl"
            st.rerun()

    st.write("---")
    st.markdown("**Tipp:** Nutzen Sie die Navigation oben, um zwischen den Funktionen zu wechseln.")