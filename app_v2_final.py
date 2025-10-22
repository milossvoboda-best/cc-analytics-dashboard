"""
CC Analytics Dashboard - FINAL CLEAN VERSION
Professional one-page layout inspired by CXone dashboard
"""

import streamlit as st
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(__file__))
from data_generation import generate_dataset

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="CC Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ULTRA COMPACT CSS
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 0.7rem;
    }
    
    [data-testid="metric-container"] {
        background-color: white;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #E5E7EB;
    }
    
    h1 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2196F3;
    }
    
    h2, h3 {
        font-size: 1rem;
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
        font-weight: 600;
    }
    
    .element-container {
        margin-bottom: 0rem;
    }
    
    .stPlotlyChart {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 4px;
        padding: 0.3rem;
    }
    
    hr {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    calls_df, transcripts, agents_df = generate_dataset(n_calls=200, n_agents=12, seed=42)
    return calls_df, transcripts, agents_df

calls_df, transcripts, agents_df = load_data()

# ============================================================================
# HEADER
# ============================================================================
st.title("📊 CC Analytics Dashboard")

# ============================================================================
# TOP KPI ROW - BIG NUMBERS IN A ROW (like CXone)
# ============================================================================

from widgets_v2.aes_card import calculate_aes_components
from widgets_v2.compliance_card import calculate_compliance_score
from widgets_v2.sales_card import calculate_sales_metrics
from widgets_v2.fcr_gauges import calculate_fcr_metrics
from widgets_v2.escalation_card import calculate_escalation_metrics

aes = calculate_aes_components(calls_df)
comp = calculate_compliance_score(calls_df)
sales = calculate_sales_metrics(calls_df)
fcr = calculate_fcr_metrics(calls_df)
esc = calculate_escalation_metrics(calls_df)

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7, kpi8 = st.columns(8)

with kpi1:
    st.metric("AES Score", f"{aes['overall_aes_pct']:.1f}%", "+2.4%")

with kpi2:
    st.metric("Compliance", f"{comp['score']:.1f}%", "+1.2%")

with kpi3:
    st.metric("FCR Rate", f"{fcr['fcr_validated']:.1f}%", "-2.5%", delta_color="inverse")

with kpi4:
    st.metric("EPR", f"{esc['epr']:.1f}%", "+3.1%")

with kpi5:
    st.metric("Avg AHT", "5m 24s", "-12s")

with kpi6:
    st.metric("Sales Conv", f"{sales['conversion_rate']:.1f}%", "+5.2%")

with kpi7:
    st.metric("Sentiment Δ", "+0.6", "+0.2")

with kpi8:
    autoqa = calls_df['autoqa_score'].mean()
    st.metric("AutoQA", f"{autoqa:.1f}%", "+4.3%")

st.markdown("---")

# ============================================================================
# GRID LAYOUT - COMPACT WIDGETS (2-3 per row like CXone)
# ============================================================================

# ROW 1: AES Spider + Compliance Details + Sales Performance
col1, col2, col3 = st.columns([1.2, 1, 1])

with col1:
    st.markdown("**Agent Effectiveness Score**")
    from widgets_v2.aes_card import create_aes_card
    fig = create_aes_card(calls_df, target=75.0, prev_period_aes=72.5)
    fig.update_layout(height=220, margin=dict(l=5, r=5, t=20, b=5))
    st.plotly_chart(fig, use_container_width=True, key='aes')

with col2:
    st.markdown("**Compliance Breakdown**")
    st.write(f"**Score:** {comp['score']:.1f}%")
    st.write(f"**Critical Issues:** {comp['critical_violations']}")
    st.write(f"**Risk Level:** {comp['risk_level']}")
    st.write("")
    st.write("**Top Issues:**")
    st.write("• Customer verification: 23%")
    st.write("• Data protection: 12%")
    st.write("• Script adherence: 8%")

with col3:
    st.markdown("**Sales Performance**")
    st.write(f"**Conversion:** {sales['conversion_rate']:.1f}%")
    st.write(f"**Total Value:** €{sales['total_value']:,.0f}")
    st.write("")
    st.write("**Breakdown:**")
    st.write(f"• Upsell: {sales['upsell_success']}/{sales['upsell_count']} (€{sales['upsell_success']*500:,.0f})")
    st.write(f"• Cross-sell: {sales['cross_sell_success']}/{sales['cross_sell_count']} (€{sales['cross_sell_success']*377:,.0f})")
    st.write(f"• Closing: {sales['closing_success']}/{sales['closing_count']}")

st.markdown("---")

# ROW 2: Sentiment Sankey + FCR Gauges
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("**Customer Sentiment Journey**")
    from widgets_v2.sentiment_sankey import create_sentiment_sankey, calculate_sentiment_flows
    fig = create_sentiment_sankey(calls_df)
    fig.update_layout(height=200, margin=dict(l=5, r=5, t=10, b=5))
    st.plotly_chart(fig, use_container_width=True, key='sankey')
    
    flows = calculate_sentiment_flows(calls_df)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Improving", f"{flows['improving_count']}", f"{flows['improving_pct']:.0f}%")
    with c2:
        st.metric("Stable", f"{flows['stable_count']}", f"{flows['stable_pct']:.0f}%")
    with c3:
        st.metric("Declining", f"{flows['declining_count']}", f"{flows['declining_pct']:.0f}%")

with col2:
    st.markdown("**FCR Analysis**")
    from widgets_v2.fcr_gauges import create_fcr_gauges
    fig = create_fcr_gauges(calls_df, target=75.0)
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True, key='fcr')
    
    gap = fcr['fcr_predicted'] - fcr['fcr_validated']
    st.write(f"**Gap:** {gap:+.1f}% ({'⚠️ AI premature' if gap < -10 else '✅ Aligned'})")

st.markdown("---")

# ROW 3: Performance Trend + Quality Bars
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("**Performance Trend (30 Days)**")
    
    tab1, tab2, tab3, tab4 = st.tabs(["AES", "AutoQA", "FCR", "Sentiment"])
    
    from widgets_v2.performance_trend import create_performance_trend
    
    with tab1:
        fig = create_performance_trend(calls_df, metric='AES', target=75.0, days=30)
        fig.update_layout(height=180, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_aes')
    
    with tab2:
        fig = create_performance_trend(calls_df, metric='AutoQA', target=80.0, days=30)
        fig.update_layout(height=180, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_autoqa')
    
    with tab3:
        fig = create_performance_trend(calls_df, metric='FCR', target=75.0, days=30)
        fig.update_layout(height=180, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_fcr')
    
    with tab4:
        fig = create_performance_trend(calls_df, metric='Sentiment', target=60.0, days=30)
        fig.update_layout(height=180, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_sent')

with col2:
    st.markdown("**Quality Components**")
    from widgets_v2.quality_bars import create_quality_bars
    fig = create_quality_bars(calls_df, prev_period_df=None)
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=40))
    st.plotly_chart(fig, use_container_width=True, key='quality')

st.markdown("---")

# ROW 4: Topic Efficiency + Escalation + Timeline
col1, col2, col3 = st.columns([1.2, 1, 1])

with col1:
    st.markdown("**Topic Efficiency**")
    from widgets_v2.topic_bubble import create_topic_bubble_chart, calculate_topic_efficiency
    fig = create_topic_bubble_chart(calls_df)
    fig.update_layout(height=200, margin=dict(l=20, r=10, t=10, b=30))
    st.plotly_chart(fig, use_container_width=True, key='topic')
    
    topics = calculate_topic_efficiency(calls_df)
    critical = topics[topics['status'] == 'critical'].nlargest(1, 'total_talk_time')
    if len(critical) > 0:
        row = critical.iloc[0]
        st.caption(f"🔴 **Alert:** {row['topic']} ({row['avg_aht']:.1f} min, +{abs(row['pct_diff']):.0f}% vs benchmark)")

with col2:
    st.markdown("**Escalation Management**")
    st.metric("Prevention Rate", f"{esc['epr']:.1f}%", "+3.1%")
    st.write(f"**Escalated:** {esc['escalated_count']} / {esc['total_calls']}")
    st.write("")
    st.write("**Top Reasons:**")
    if esc['reasons']:
        for reason, count in list(esc['reasons'].items())[:3]:
            st.write(f"• {reason.replace('_', ' ').title()}: {count}")

with col3:
    st.markdown("**Call Timeline**")
    from widgets_v2.timeline_simple import calculate_timeline_summary
    timeline = calculate_timeline_summary(calls_df)
    
    st.write(f"**Avg Duration:** {timeline['avg_duration_str']}")
    st.write(f"**Agent Talk:** {timeline['agent_ratio']:.0f}%")
    st.write(f"**Customer Talk:** {timeline['customer_ratio']:.0f}%")
    st.write(f"**Silence:** {timeline['silence_ratio']:.0f}%")
    st.write(f"**Sentiment Δ:** {timeline['sentiment_delta']:+.2f}")
    st.write(f"**Compliance:** {timeline['compliance_pass_rate']:.0f}%")

st.markdown("---")
st.caption("✅ Dashboard V2 | All metrics current as of last sync")
