import streamlit as st
import yfinance as yf
def inject_terminal_css():
    st.markdown("""
        <style>
        /* Main Background */
        .stApp { background-color: #050505; color: #e0e0e0; }
        
        /* Majestic Glass Card */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 65, 0.2);
            padding: 15px; border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
        }
        
        /* Techy Typography */
        h1, h2, h3 { font-family: 'Courier New', monospace; color: #00ff41 !important; text-shadow: 0 0 8px #00ff41; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px 5px 0 0; padding: 10px 20px; color: #888;
        }
        .stTabs [aria-selected="true"] { background-color: rgba(0, 255, 65, 0.1) !important; color: #00ff41 !important; border-bottom: 2px solid #00ff41 !important; }
        </style>
    """, unsafe_allow_html=True)

# Global majestic theme logic
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46")

if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

st.sidebar.title("COMMAND_CENTER")
st.session_state.ticker = st.sidebar.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()

# --- CATEGORY 1: SECURITY IDENTIFICATION ---
st.markdown(f"<h1 style='color: #00ff41;'>// SECURITY_MASTER: {st.session_state.ticker}</h1>", unsafe_allow_html=True)

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
    st.write("**PROPRIETARY_SCORES (Cat 20)**")
    st.metric("LIQUIDITY", "HIGH", "98.2")
    st.metric("B_FAIR_VALUE", f"${info.get('targetMedianPrice')}")
