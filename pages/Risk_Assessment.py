import streamlit as st
import yfinance as yf
import google.generativeai as genai

# 1. THE LAYOUT ENGINE
st.set_page_config(layout="wide", page_title="RISK_AUDIT_2026")

# 2. MAJESTIC RISK CSS
st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; max-width: 98% !important; }
    
    .risk-bento-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .audit-card {
        background: rgba(255, 75, 75, 0.05);
        border: 1px solid rgba(255, 75, 75, 0.2);
        padding: 30px;
        border-radius: 25px;
        backdrop-filter: blur(10px);
    }
    
    .severity-pill {
        background: #ff4b4b;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 15px;
        display: inline-block;
    }
    
    .audit-title {
        color: #ff4b4b;
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .audit-body {
        color: #e0e0e0;
        font-family: 'Source Serif Pro', serif;
        line-height: 1.6;
        font-size: 17px;
    }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color:#ff4b4b; font-family:monospace;'>// RISK_SURVEILLANCE: {ticker}</h1>", unsafe_allow_html=True)

# 3. AI AUDITOR (Updated to Gemini 2.5 Flash)
def run_ai_audit(ticker, data):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # FIX: Updated to 2026 Stable Model
        model = genai.GenerativeModel("gemini-2.5-flash") 
        
        prompt = f"""
        Act as a Quantitative Risk Auditor. Perform a brutal 'Red Flag' scan for {ticker}.
        Financial Context: Debt/Equity {data.get('debtToEquity')}, Profit Margin {data.get('profitMargins')}, 
        Quick Ratio {data.get('quickRatio')}, Beta {data.get('beta')}.
        Identify the single biggest threat to this company's survival or stock price in the next 12 months.
        Tone: Sophisticated, skeptical, and razor-sharp. Max 80 words.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AUDIT_ERROR: Model connection timed out. Manual review required. ({str(e)})"

# --- THE UI RENDER ---

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("DEBT_LOAD", f"{info.get('debtToEquity', 0):.2f}", "CRITICAL" if info.get('debtToEquity', 0) > 100 else "STABLE", delta_color="inverse")
with c2:
    st.metric("CASH_RUNWAY", f"{info.get('quickRatio', 0):.2f}", "LOW_LIQUIDITY" if info.get('quickRatio', 0) < 1 else "SAFE", delta_color="normal")
with c3:
    st.metric("BETA_VOL", f"{info.get('beta', 0):.2f}", "HYPER_VOL" if info.get('beta', 0) > 1.5 else "STABLE", delta_color="inverse")
with c4:
    st.metric("SHORT_INT", f"{info.get('shortRatio', 0):.2f}", "SQUEEZE_PROB" if info.get('shortRatio', 0) > 8 else "LOW", delta_color="normal")

st.markdown("---")

# The AI Bento Card
with st.spinner("INITIATING_DEEP_AI_SCAN..."):
    audit_finding = run_ai_audit(ticker, info)

st.markdown(f"""
    <div class="audit-card">
        <div class="severity-pill">High Severity Alert</div>
        <div class="audit-title">The Sovereign Risk Verdict</div>
        <div class="audit-body">{audit_finding}</div>
    </div>
""", unsafe_allow_html=True)

# Insider Signals (Replaces the spreadsheet with clean tags)
st.markdown("### // INSIDER_VELOCITY_ALERTS")
insiders = stock.insider_transactions
if insiders is not None and not insiders.empty:
    for index, row in insiders.head(5).iterrows():
        st.error(f"**{row['Text']}** | Date: {row['Start Date']} | Shares: {row['Shares']}")
else:
    st.success("CLEAR_SIGNAL: No major insider dumping detected in the 30-day window.")
