"""
CC Analytics Dashboard - Redesign V2 DEMO
Shows first 3 rows (6 widgets) for testing
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data_generation import generate_dataset
from widgets_v2 import (
    create_aes_card, get_aes_component_breakdown,
    create_compliance_card_html,
    create_sales_card_html,
    create_sentiment_sankey, create_sentiment_summary_html,
    create_fcr_gauges, create_fcr_summary_html, get_fcr_insights,
    create_performance_trend, create_trend_summary_html
)

# Page config
st.set_page_config(
    page_title="CC Analytics Dashboard V2 - DEMO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean look
st.markdown("""
<style>
    .main {
        background-color: #F9FAFB;
    }
    .stPlotlyChart {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    h1 {
        font-family: 'Inter', sans-serif;
        color: #1E3A8A;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    h2 {
        font-family: 'Inter', sans-serif;
        color: #1E3A8A;
        font-size: 20px;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .metric-header {
        font-family: 'Inter', sans-serif;
        color: #6B7280;
        font-size: 12px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Generate data
@st.cache_data
def load_data():
    calls_df, transcripts, agents_df = generate_dataset(n_calls=200, n_agents=12, seed=42)
    return calls_df, transcripts, agents_df

calls_df, transcripts, agents_df = load_data()

# Header
st.title("📊 CC Analytics Dashboard V2 - DEMO")
st.markdown(f"<p style='color: #6B7280; font-size: 14px;'>Period: Last 30 days | {len(calls_df)} calls | {len(agents_df)} agents</p>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# ROW 1: AES + Compliance + Sales
# ============================================================================
st.markdown("## ROW 1: Key Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    # Widget 1: AES Card
    fig_aes = create_aes_card(calls_df, target=75.0, prev_period_aes=72.5)
    st.plotly_chart(fig_aes, use_container_width=True, key='aes_chart')
    st.markdown(get_aes_component_breakdown(calls_df), unsafe_allow_html=True)

with col2:
    # Widget 2: Compliance Card
    html_compliance = create_compliance_card_html(calls_df, prev_period_score=90.1)
    st.markdown(html_compliance, unsafe_allow_html=True)

with col3:
    # Widget 3: Sales Summary
    html_sales = create_sales_card_html(calls_df, prev_period_df=None)
    st.markdown(html_sales, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# ROW 2: Sentiment + FCR
# ============================================================================
st.markdown("## ROW 2: Customer Experience Metrics")

col1, col2 = st.columns([2, 1])

with col1:
    # Widget 4: Sentiment Sankey
    fig_sankey = create_sentiment_sankey(calls_df)
    st.plotly_chart(fig_sankey, use_container_width=True, key='sankey_chart')

with col2:
    # Sentiment Summary
    html_sentiment_summary = create_sentiment_summary_html(calls_df)
    st.markdown(html_sentiment_summary, unsafe_allow_html=True)

st.markdown("---")

# Widget 5: FCR Analysis
st.markdown("### Widget 5: FCR Analysis")

col1, col2 = st.columns([3, 1])

with col1:
    # FCR Gauges
    fig_fcr = create_fcr_gauges(calls_df, target=75.0)
    st.plotly_chart(fig_fcr, use_container_width=True, key='fcr_gauges')

with col2:
    # FCR Summary
    html_fcr_summary = create_fcr_summary_html(calls_df, target=75.0)
    st.markdown(html_fcr_summary, unsafe_allow_html=True)

# FCR Insights
from widgets_v2.fcr_gauges import calculate_fcr_metrics
metrics = calculate_fcr_metrics(calls_df)
html_fcr_insights = get_fcr_insights(metrics, calls_df)
st.markdown(html_fcr_insights, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# ROW 3: Performance Trend (Switchable)
# ============================================================================
st.markdown("## ROW 3: Performance Trend Analysis")

# Tabs for metric selection
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 AES", "🔍 AutoQA", "✅ FCR", "💭 Sentiment", "⏱️ AHT"])

with tab1:
    fig_trend_aes = create_performance_trend(calls_df, metric='AES', target=75.0, days=30)
    st.plotly_chart(fig_trend_aes, use_container_width=True, key='trend_aes')
    html_summary_aes = create_trend_summary_html(calls_df, metric='AES', days=30)
    st.markdown(html_summary_aes, unsafe_allow_html=True)

with tab2:
    fig_trend_autoqa = create_performance_trend(calls_df, metric='AutoQA', target=80.0, days=30)
    st.plotly_chart(fig_trend_autoqa, use_container_width=True, key='trend_autoqa')
    html_summary_autoqa = create_trend_summary_html(calls_df, metric='AutoQA', days=30)
    st.markdown(html_summary_autoqa, unsafe_allow_html=True)

with tab3:
    fig_trend_fcr = create_performance_trend(calls_df, metric='FCR', target=75.0, days=30)
    st.plotly_chart(fig_trend_fcr, use_container_width=True, key='trend_fcr')
    html_summary_fcr = create_trend_summary_html(calls_df, metric='FCR', days=30)
    st.markdown(html_summary_fcr, unsafe_allow_html=True)

with tab4:
    fig_trend_sentiment = create_performance_trend(calls_df, metric='Sentiment', target=60.0, days=30)
    st.plotly_chart(fig_trend_sentiment, use_container_width=True, key='trend_sentiment')
    html_summary_sentiment = create_trend_summary_html(calls_df, metric='Sentiment', days=30)
    st.markdown(html_summary_sentiment, unsafe_allow_html=True)

with tab5:
    fig_trend_aht = create_performance_trend(calls_df, metric='AHT', target=None, days=30)
    st.plotly_chart(fig_trend_aht, use_container_width=True, key='trend_aht')
    html_summary_aht = create_trend_summary_html(calls_df, metric='AHT', days=30)
    st.markdown(html_summary_aht, unsafe_allow_html=True)

st.markdown("---")
st.info("✅ **DEMO**: First 3 rows (6 widgets) complete! ROW 4-6 coming next...")
