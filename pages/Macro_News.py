import streamlit as st
from google import genai
from google.genai import types
def apply_majestic_theme():
    st.markdown("""
        <style>
        /* Global Background & Text */
        .stApp { background-color: #0d0d0d; color: #ffffff; }
        
        /* Glassmorphism Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 65, 0.2);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
        }
        
        /* Neon Glow Titles */
        .terminal-header {
            color: #00ff41;
            text-shadow: 0 0 10px #00ff41;
            font-family: 'Courier New', monospace;
            border-bottom: 2px solid #00ff41;
            padding-bottom: 10px;
        }

        /* Cyberpunk Divider */
        hr { border: 0; height: 1px; background: linear-gradient(to right, #00ff41, transparent); }
        </style>
    """, unsafe_allow_html=True)

apply_majestic_theme()

# 1. CORE AUTH
try:
    # Use the 2026 google-genai library for native search tools
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_KEY)
    ticker = st.session_state.get('ticker', 'NVDA')
except Exception:
    st.error("SYSTEM_OFFLINE: Ensure GEMINI_API_KEY is in your Streamlit Cloud Secrets.")
    st.stop()

st.title(f"// AI_MACRO_PULSE: {ticker}")

# 2. GEMINI SEARCH ENGINE (Grounding)
def fetch_ai_intelligence(symbol):
    prompt = f"""
    Search for the top 5 most critical financial news stories today for {symbol}.
    For each story, provide:
    1. A 'No-BS' Serious Summary (Institutional style).
    2. A 'Cynical/Funny' Take (Hedge fund humor style).
    3. The probable impact on the stock price.
    """
    
    # Enable the 'google_search' tool for real-time web access
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Use the 2026 stable model
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
            )
        )
        return response.text
    except Exception as e:
        return f"INTELLIGENCE_BLACKOUT: {str(e)}"

# 3. RENDER WORKSPACE
st.markdown("### // LIVE_INTELLIGENCE_FEED")

with st.spinner("COMMUNING_WITH_THE_NETWORK..."):
    intelligence = fetch_ai_intelligence(ticker)

# Split view for high-density information
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(intelligence)

with col2:
    st.markdown("### // SYSTEM_VISUALS")
    st.write("Current Market Sentiment Landscape:")
    # Diagram injections to explain the current macro context
    
    st.write("Inflation vs. Interest Rate Corridors:")
    
    st.write("Sector Rotation Intelligence:")
