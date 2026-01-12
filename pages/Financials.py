import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# --- 1. PRO DATA ENGINE (STABLE 2026) ---
@st.cache_data(ttl=3600)
def fetch_startup_financials(ticker, api_key):
    # FMP Stable Endpoint (Updated for 2026)
    # NOTE: We try the 'stable' path first to bypass legacy blocks
    fmp_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=12&apikey={api_key}"
    
    try:
        response = requests.get(fmp_url)
        data = response.json()
        
        # Check if FMP returned data or a 'Legacy' error dictionary
        if isinstance(data, list) and len(data) > 0:
            return pd.DataFrame(data), "FMP_PRO_STREAM"
        
        # BACKUP: Fallback to yfinance if API is blocked or limit reached
        ticker_obj = yf.Ticker(ticker)
        yf_data = ticker_obj.quarterly_financials.T
        if not yf_data.empty:
            yf_data = yf_data.reset_index().rename(columns={'index': 'date', 'Total Revenue': 'revenue', 'Net Income': 'netIncome'})
            return yf_data, "YF_BACKUP_STREAM"
            
    except Exception as e:
        return None, f"CONNECTION_ERROR: {e}"
    
    return None, "NO_DATA_AVAILABLE"

# --- 2. MAJESTIC UI RENDERING ---
ticker = st.session_state.ticker
st.title(f"// FINANCIAL_MATRIX: {ticker}")

try:
    fmp_key = st.secrets["FMP_KEY"]
    df, source = fetch_startup_financials(ticker, fmp_key)
except Exception:
    st.error("SYSTEM_OFFLINE: Ensure FMP_KEY is in Streamlit Secrets.")
    st.stop()

if df is not None:
    # HUD: Data Source Status
    st.caption(f"CONNECTED_VIA: {source}")
    
    # Majestic Charting: Revenue vs Net Income
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['date'], y=df['revenue'], 
        name="REVENUE", marker_color='#00ff41',
        hovertemplate='Rev: $%{y:.2s}<extra></extra>'
    ))
    # Handling Net Income if available in the stream
    if 'netIncome' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['netIncome'], 
            name="NET_INCOME", line=dict(color='#ff00ff', width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        template="plotly_dark", 
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    

    # The Bloomberg "Data Grid" (High-Density Layout)
    st.markdown("### // INSTITUTIONAL_DATA_GRID")
    
    # Dynamically select available columns to prevent errors
    cols_to_show = [c for c in ['date', 'revenue', 'grossProfit', 'ebitda', 'operatingIncome', 'netIncome', 'eps'] if c in df.columns]
    st.dataframe(df[cols_to_show].set_index('date'), use_container_width=True)

else:
    st.warning(f"CRITICAL_DATA_FAILURE: Terminal could not sync with FMP or Backup streams.")
