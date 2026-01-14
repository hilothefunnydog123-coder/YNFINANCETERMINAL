import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai

# 1. VIBRANT THEME INJECTION
def apply_vibrant_theme():
    st.markdown("""
    <style>
        .stApp { background: #f0f2f6; color: #1e1e1e; }
        [data-testid="stSidebar"] { background-color: #ffffff; }
        .st-key-card {
            background: #ffffff; border-radius: 20px;
            padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            margin-bottom: 20px; border: none;
        }
        .rank-badge {
            background: linear-gradient(90deg, #6C5CE7, #a29bfe);
            color: white; padding: 4px 12px; border-radius: 50px;
            font-size: 12px; font-weight: bold;
        }
        h1, h2, h3 { color: #2d3436; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. THE TOP 500 RANKER (Section 1)
def render_top_500():
    st.markdown("## 🏆 Global Top 500: Today's Best Buys")
    # Simulation of AI Ranking Logic
    recommendations = [
        {"rank": 1, "ticker": "NVDA", "score": "98/100", "reason": "AI Infrastructure dominance & 40% margin growth."},
        {"rank": 2, "ticker": "MSFT", "score": "94/100", "reason": "Cloud integration and enterprise AI leadership."},
        {"rank": 3, "ticker": "ASML", "score": "92/100", "reason": "Monopoly on EUV lithography for next-gen chips."}
    ]
    
    for rec in recommendations:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 4, 2])
            c1.markdown(f"<div class='rank-badge'>#{rec['rank']}</div>", unsafe_allow_html=True)
            c2.markdown(f"**{rec['ticker']}** — {rec['reason']}")
            c3.metric("AI Score", rec['score'])

# 3. PORTFOLIO SCANNER (Section 2)
def render_portfolio_scanner():
    st.markdown("## 🔍 AI Portfolio Health-Check")
    st.info("AI Analysis: Your portfolio is 70% Tech. We recommend adding **Healthcare (VHT)** or **Real Estate (VNQ)** to lower volatility.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ BUY: JNJ (Healthcare Stability)")
    with col2:
        st.error("⚠️ SELL: TSLA (Overextended Valuation)")

# 4. CIRCLE CHART (Section 3)
def render_ideal_chart():
    st.markdown("## 📊 Ideal Allocation")
    # Donut Chart for beginners
    labels = ['Tech', 'Healthcare', 'Finance', 'Energy', 'Cash']
    values = [40, 20, 15, 10, 15]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, 
                                 marker_colors=['#6C5CE7', '#00CEC9', '#FDCB6E', '#E17055', '#B2BEC3'])])
    fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

# --- EXECUTION ---
apply_vibrant_theme()
st.title("Welcome to Vanguard AI ✨")
st.write("Your simplified, smart path to wealth.")

tab1, tab2, tab3 = st.tabs(["Recommendations", "Portfolio Scanner", "My Ideal Portfolio"])
with tab1: render_top_500()
with tab2: render_portfolio_scanner()
with tab3: render_ideal_chart()
