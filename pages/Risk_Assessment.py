import streamlit as st
import yfinance as yf
import google.generativeai as genai

# 1. STYLE & LAYOUT
st.set_page_config(layout="wide", page_title="RISK_AUDIT_2026")

st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; max-width: 95% !important; }
    .risk-card {
        background: rgba(255, 75, 75, 0.05);
        border: 1px solid rgba(255, 75, 75, 0.2);
        padding: 25px; border-radius: 15px; margin-bottom: 20px;
    }
    .safe-card {
        background: rgba(0, 255, 65, 0.05);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 25px; border-radius: 15px; margin-bottom: 20px;
    }
    .risk-header { color: #ff4b4b; font-family: monospace; font-weight: bold; }
    .audit-text { font-family: 'Source Serif Pro', serif; line-height: 1.6; color: #eee; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color:#ff4b4b; font-family:monospace;'>// RISK_ASSESSMENT: {ticker}</h1>", unsafe_allow_html=True)

# 2. QUANT RISK METRICS
c1, c2, c3 = st.columns(3)

with c1:
    debt_equity = info.get('debtToEquity', 0)
    st.metric("DEBT_TO_EQUITY", f"{debt_equity:.2f}", delta="HIGH_LEVERAGE" if debt_equity > 100 else "STABLE", delta_color="inverse")

with c2:
    short_ratio = info.get('shortRatio', 0)
    st.metric("SHORT_RATIO", f"{short_ratio:.2f}", delta="SQUEEZE_RISK" if short_ratio > 5 else "NORMAL", delta_color="inverse")

with c3:
    current_ratio = info.get('currentRatio', 0)
    st.metric("CURRENT_RATIO (LIQUIDITY)", f"{current_ratio:.2f}", delta="CASH_POOR" if current_ratio < 1 else "LIQUID")

# 3. THE AI SOVEREIGN AUDIT (Gemini 3 Flash)
st.markdown("### // AI_SOVEREIGN_AUDIT")

def run_risk_audit(ticker, data):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash") # 2026 Stable
        prompt = f"""
        Act as a Senior Risk Officer. Perform a brutal 'Red Flag' audit for {ticker}.
        Context: Debt/Equity {data.get('debtToEquity')}, Profit Margin {data.get('profitMargins')}, 
        Beta {data.get('beta')}, and Price-to-Book {data.get('priceToBook')}.
        Identify 3 specific potential failure points or 'Red Flags'. 
        Be captivating, professional, and concise (100 words).
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return f"AUDIT_SIGNAL_INTERRUPTED: {str(e)}"

with st.spinner("INITIATING_DEEP_SCAN..."):
    audit_report = run_risk_audit(ticker, info)

# Visual conditional formatting for the AI report
st.markdown(f"""
    <div class="risk-card">
        <div class="risk-header">CRITICAL_AUDIT_FINDINGS:</div>
        <div class="audit-text">{audit_report}</div>
    </div>
""", unsafe_allow_html=True)

# 4. INSIDER ALERTS (Category 15)
st.markdown("### // INSIDER_VELOCITY")
insiders = stock.insider_transactions
if insiders is not None and not insiders.empty:
    st.dataframe(insiders.head(10), use_container_width=True)
else:
    st.info("No recent insider transactions detected in the SEC feed.")
