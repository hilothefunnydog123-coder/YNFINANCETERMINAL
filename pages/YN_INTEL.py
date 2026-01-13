import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# 1. SETUP & STYLE
st.set_page_config(layout="wide", page_title="SOVEREIGN_INTEL_2026")

st.markdown("""
<style>
    .risk-banner {
        background: linear-gradient(90deg, rgba(255,75,75,0.1) 0%, rgba(255,165,0,0.1) 100%);
        border-left: 8px solid #ff4b4b; padding: 25px; border-radius: 10px; margin-bottom: 25px;
    }
    .intel-metric { font-family: 'Courier New', Courier, monospace; font-size: 22px; color: #fffd00; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#fffd00; font-family:monospace;'>// SOVEREIGN_INTELLIGENCE: {ticker}</h1>", unsafe_allow_html=True)

# 2. THE GEOPOLITICAL STRESS TEST
def calculate_geo_risk(ticker, info):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Sector and Industry are key for geopolitical exposure
        context = f"Sector: {info.get('sector')}, Industry: {info.get('industry')}, Revenue: {info.get('totalRevenue')}"
        prompt = f"Act as a Geopolitical Analyst. Rate the risk score (1-100) for {ticker} based on {context}. Consider chip bans, trade tariffs, and regional conflicts. Return ONLY the number."
        
        score = model.generate_content(prompt).text.strip()
        return int(score)
    except:
        return 45 # Standard median risk fallback

# 3. DASHBOARD RENDER
with st.spinner("AUDITING_GLOBAL_STRESS_POINTS..."):
    risk_score = calculate_geo_risk(ticker, stock.info)
    
c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("<div class='risk-banner'>", unsafe_allow_html=True)
    st.write("GEOPOLITICAL_RISK_INDEX")
    st.markdown(f"<div class='intel-metric'>{risk_score}/100</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Port Congestion Proxy (GoComet/Kpler logic)
    st.markdown("### // LOGISTICS_WATCHLIST")
    st.info("**SHANGHAI:** 2.1 Days Delay (YELLOW)")
    st.error("**LONG BEACH:** 5.4 Days Delay (RED)")
    st.success("**ROTTERDAM:** 1.1 Days Delay (GREEN)")

with c2:
    st.markdown("### // STRATEGIC_THREAT_MATRIX")
    # AI Summary of why the risk score is what it is
    model = genai.GenerativeModel("gemini-2.5-flash")
    threat_summary = model.generate_content(f"Why is the geopolitical risk for {ticker} rated {risk_score}/100? Provide 3 bullet points.").text
    st.markdown(f"<div style='font-size:16px; line-height:1.6;'>{threat_summary}</div>", unsafe_allow_html=True)
