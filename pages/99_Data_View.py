import streamlit as st
import google.generativeai as genai

# 1. ORACLE CONFIGURATION
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_oracle_insight(metric_name, value, ticker):
    prompt = f"""
    You are a world-class hedge fund analyst. Explain the financial metric '{metric_name}' 
    which currently stands at {value} for {ticker}. 
    1. Define it simply but powerfully.
    2. Explain what a move in this number could lead to (the 'So What?').
    3. Make it captivating and high-stakes. Use terminal-style language.
    Keep it under 100 words.
    """
    response = model.generate_content(prompt)
    return response.text

# 2. SESSION STATE FOR PERSISTENCE
if 'oracle_response' not in st.session_state:
    st.session_state.oracle_response = "SELECT A DATA POINT TO DECODE THE SIGNAL..."

# 3. MAJESTIC GRID WITH CLICKABLE TILES
st.markdown(f"<h1>// DATA_MATRIX_ORACLE: {st.session_state.get('matrix_label')}</h1>", unsafe_allow_html=True)

# SIDEBAR FOR AI INSIGHTS
with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ORACLE_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='summary-box'>{st.session_state.oracle_response}</div>", unsafe_allow_html=True)

# THE DATA LATTICE
df = st.session_state.get('matrix_data')
if df is not None:
    latest = df.iloc[:, 0]
    cols = st.columns(4)
    for i, (k, v) in enumerate(latest.items()):
        with cols[i % 4]:
            # Each tile is now a button that triggers Gemini
            if st.button(f"{k}\n{v:,.2f}" if isinstance(v, (int, float)) else f"{k}\n{v}", key=f"btn_{i}"):
                with st.spinner(f"DECODING {k}..."):
                    st.session_state.oracle_response = get_oracle_insight(k, v, "THIS_TICKER")
                    st.rerun() # Refresh to show response in sidebar
