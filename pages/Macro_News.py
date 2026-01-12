# --- REPLACEMENT NEWS LOOP FOR Macro_News.py ---
st.markdown("### // LIVE_NEWS_FEED")
news_data = yf.Ticker(st.session_state.ticker).news

if news_data:
    for item in news_data[:8]:  # Show top 8 stories
        # Use .get() to avoid KeyError if a field is missing
        title = item.get('title', 'Headline Unavailable')
        link = item.get('link', '#')
        
        # In 2026, yfinance sometimes nests publisher info
        publisher = item.get('publisher', 'Financial Wire')
        
        # Majestic News Card
        st.markdown(f"""
            <div style="border-left: 3px solid #00ff41; padding-left: 15px; margin-bottom: 20px;">
                <p style="font-size: 12px; color: #00f0ff; margin-bottom: 5px;">{publisher.upper()}</p>
                <a href="{link}" target="_blank" style="text-decoration: none; color: #00ff41; font-weight: bold; font-size: 16px;">
                    {title}
                </a>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("NO_NEWS_DATA_AVAILABLE: The wires are currently silent for this symbol.")
