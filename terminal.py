import streamlit as st
import yfinance as yf

# --- 0. THE BIOMETRIC GUARD (STEP 1) ---
# This stops the script unless the user's hardware verifies their identity
if not st.experimental_user.is_logged_in:
    st.set_page_config(page_title="YN_SECURE_GATE", layout="centered")
    st.markdown("""
        <style>
        .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
        .gate-card {
            border: 2px solid #00ff41; padding: 40px; border-radius: 15px;
            text-align: center; background: rgba(0, 255, 65, 0.05);
            box-shadow: 0 0 20px #00ff41;
        }
        </style>
        <div class="gate-card">
            <h1>🔒 SOVEREIGN_ACCESS_LOCKED</h1>
            <p>Hardware-bound Biometric Recognition Required.</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("INITIALIZE_FINGERPRINT_SCAN", use_container_width=True):
        # Triggers the Hanko Passkey flow via OIDC
        st.login("hanko")
    st.stop()

# --- 1. TERMINAL UI & CSS (ONLY LOADS AFTER AUTH) ---
def inject_terminal_css():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; color: #e0e0e0; }
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 65, 0.2);
            padding: 15px; border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
        }
        h1, h2, h3 { font-family: 'Courier New', monospace; color: #00ff41 !important; text-shadow: 0 0 8px #00ff41; }
        .stTabs [data-baseweb="tab"] { background-color: rgba(255, 255, 255, 0.05); color: #888; }
        .stTabs [aria-selected="true"] { background-color: rgba(0, 255, 65, 0.1) !important; color: #00ff41 !important; }
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="SOVEREIGN_V46")
inject_terminal_css()

# --- 2. COMMAND CENTER LOGIC ---
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

with st.sidebar:
    st.title("COMMAND_CENTER")
    st.info(f"VERIFIED_USER: {st.experimental_user.email}")
    st.session_state.ticker = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()
    if st.button("TERMINATE_SESSION"):
        st.logout()

st.markdown(f"<h1>// SECURITY_MASTER: {st.session_state.ticker}</h1>", unsafe_allow_html=True)

stock = yf.Ticker(st.session_state.ticker)
info = stock.info

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("**PRIMARY_IDS**")
    st.code(f"Ticker: {st.session_state.ticker}\nISIN: {info.get('isin')}\nCUSIP: {info.get('cusip')}")
with col2:
    st.write("**EXCHANGE_DATA**")
    st.code(f"Exchange: {info.get('exchange')}\nMIC: {info.get('exchangeTimezoneName')}\nCurrency: {info.get('currency')}")
with col3:
    st.write("**ASSET_CLASS**")
    st.code(f"Type: {info.get('quoteType')}\nSector: {info.get('sector')}\nCountry: {info.get('country')}")
with col4:
    st.write("**PROPRIETARY_SCORES**")
    st.metric("LIQUIDITY", "HIGH", "98.2")
    st.metric("B_FAIR_VALUE", f"${info.get('targetMedianPrice')}")
