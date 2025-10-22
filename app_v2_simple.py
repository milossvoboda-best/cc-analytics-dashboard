"""
CC Analytics Dashboard - Redesign V2 SIMPLIFIED
Clean version without complex HTML - uses Streamlit native components
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data_generation import generate_dataset
from widgets_v2 import (
    create_aes_card, 
    create_sentiment_sankey,
    create_fcr_gauges,
    create_performance_trend,
    create_topic_bubble_chart,
    create_quality_bars
)

# Page config
st.set_page_config(
    page_title="CC Analytics Dashboard V2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Generate data
@st.cache_data
def load_data():
    calls_df, transcripts, agents_df = generate_dataset(n_calls=200, n_agents=12, seed=42)
    return calls_df, transcripts, agents_df

calls_df, transcripts, agents_df = load_data()

# Header
st.title("📊 CC Analytics Dashboard V2")
st.caption(f"Period: Last 30 days | {len(calls_df)} calls | {len(agents_df)} agents")
st.divider()

# ============================================================================
# ROW 1: AES + Compliance + Sales
# ============================================================================
st.subheader("ROW 1: Key Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    # Widget 1: AES Card
    fig_aes = create_aes_card(calls_df, target=75.0, prev_period_aes=72.5)
    st.plotly_chart(fig_aes, use_container_width=True, key='aes_chart')
    
    # AES Breakdown
    from widgets_v2.aes_card import calculate_aes_components
    aes = calculate_aes_components(calls_df)
    st.write(f"**Component Breakdown:**")
    st.write(f"• Sentiment: {aes['sentiment']:.1f}")
    st.write(f"• Compliance: {aes['compliance']:.1f}")
    st.write(f"• Resolution: {aes['resolution']:.1f}")
    st.write(f"• Quality: {aes['quality']:.1f}")

with col2:
    # Widget 2: Compliance Card
    from widgets_v2.compliance_card import calculate_compliance_score
    comp = calculate_compliance_score(calls_df)
    
    st.metric("Compliance Score", f"{comp['score']:.1f}%", delta="+2.2%")
    st.write(f"**Critical Violations:** {comp['critical_violations']}")
    st.write(f"**Risk Level:** {comp['risk_level']}")

with col3:
    # Widget 3: Sales Summary
    from widgets_v2.sales_card import calculate_sales_metrics
    sales = calculate_sales_metrics(calls_df)
    
    st.write("**Sales Performance**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Upsell", f"{sales['upsell_success']}/{sales['upsell_count']}")
    with c2:
        st.metric("Cross-sell", f"{sales['cross_sell_success']}/{sales['cross_sell_count']}")
    with c3:
        st.metric("Closing", f"{sales['closing_success']}/{sales['closing_count']}")
    
    st.write(f"**Conversion:** {sales['conversion_rate']:.1f}%")
    st.write(f"**Total Value:** €{sales['total_value']:,.0f}")

st.divider()

# ============================================================================
# ROW 2: Sentiment + FCR
# ============================================================================
st.subheader("ROW 2: Customer Experience Metrics")

col1, col2 = st.columns([2, 1])

with col1:
    # Widget 4: Sentiment Sankey
    fig_sankey = create_sentiment_sankey(calls_df)
    st.plotly_chart(fig_sankey, use_container_width=True, key='sankey_chart')

with col2:
    # Sentiment Summary
    from widgets_v2.sentiment_sankey import calculate_sentiment_flows
    flows = calculate_sentiment_flows(calls_df)
    
    st.metric("😠→😊 Improving", f"{flows['improving_pct']:.1f}%", 
              delta=f"{flows['improving_count']} calls")
    st.metric("😐→😐 Stable", f"{flows['stable_pct']:.1f}%",
              delta=f"{flows['stable_count']} calls")  
    st.metric("😊→😠 Declining", f"{flows['declining_pct']:.1f}%",
              delta=f"-{flows['declining_count']} calls", delta_color="inverse")

st.divider()

# Widget 5: FCR Analysis
st.subheader("Widget 5: FCR Analysis")

col1, col2 = st.columns([3, 1])

with col1:
    # FCR Gauges
    fig_fcr = create_fcr_gauges(calls_df, target=75.0)
    st.plotly_chart(fig_fcr, use_container_width=True, key='fcr_gauges')

with col2:
    # FCR Summary
    from widgets_v2.fcr_gauges import calculate_fcr_metrics
    fcr = calculate_fcr_metrics(calls_df)
    
    st.metric("Predicted FCR", f"{fcr['fcr_predicted']:.1f}%")
    st.metric("Validated FCR", f"{fcr['fcr_validated']:.1f}%")
    gap = fcr['fcr_predicted'] - fcr['fcr_validated']
    st.write(f"**Gap:** {gap:.1f}%")
    st.write(f"**Target:** 75.0%")

st.divider()

# ============================================================================
# ROW 3: Performance Trend (Switchable)
# ============================================================================
st.subheader("ROW 3: Performance Trend Analysis")

# Tabs for metric selection
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 AES", "🔍 AutoQA", "✅ FCR", "💭 Sentiment", "⏱️ AHT"])

with tab1:
    fig = create_performance_trend(calls_df, metric='AES', target=75.0, days=30)
    st.plotly_chart(fig, use_container_width=True, key='trend_aes')

with tab2:
    fig = create_performance_trend(calls_df, metric='AutoQA', target=80.0, days=30)
    st.plotly_chart(fig, use_container_width=True, key='trend_autoqa')

with tab3:
    fig = create_performance_trend(calls_df, metric='FCR', target=75.0, days=30)
    st.plotly_chart(fig, use_container_width=True, key='trend_fcr')

with tab4:
    fig = create_performance_trend(calls_df, metric='Sentiment', target=60.0, days=30)
    st.plotly_chart(fig, use_container_width=True, key='trend_sentiment')

with tab5:
    fig = create_performance_trend(calls_df, metric='AHT', target=None, days=30)
    st.plotly_chart(fig, use_container_width=True, key='trend_aht')

st.divider()

# ============================================================================
# ROW 4: Efficiency & Escalation
# ============================================================================
st.subheader("ROW 4: Efficiency & Escalation Management")

col1, col2 = st.columns([2, 1])

with col1:
    # Widget 7: Topic Bubble Chart
    fig = create_topic_bubble_chart(calls_df)
    st.plotly_chart(fig, use_container_width=True, key='topic_bubble')
    
    # Topic insights
    from widgets_v2.topic_bubble import calculate_topic_efficiency
    topics = calculate_topic_efficiency(calls_df)
    critical = topics[topics['status'] == 'critical'].nlargest(1, 'total_talk_time')
    if len(critical) > 0:
        row = critical.iloc[0]
        st.warning(f"🔴 **{row['topic']}**: {row['avg_aht']:.1f} min avg ({abs(row['pct_diff']):.0f}% over benchmark)")

with col2:
    # Widget 8: Escalation Card
    from widgets_v2.escalation_card import calculate_escalation_metrics
    esc = calculate_escalation_metrics(calls_df)
    
    st.metric("Escalation Prevention Rate", f"{esc['epr']:.1f}%", delta="+0.8%")
    st.write(f"**Escalations:** {esc['escalated_count']} / {esc['total_calls']}")
    
    if esc['reasons']:
        st.write("**Top Reasons:**")
        for reason, count in list(esc['reasons'].items())[:3]:
            st.write(f"• {reason.replace('_', ' ').title()}: {count}")

st.divider()

# ============================================================================
# ROW 5: Quality Breakdown
# ============================================================================
st.subheader("ROW 5: Quality Components Analysis")

# Widget 9: Quality Bars
fig = create_quality_bars(calls_df, prev_period_df=None)
st.plotly_chart(fig, use_container_width=True, key='quality_bars')

# Quality insights
autoqa = calls_df['autoqa_score'].mean()
st.info(f"**Overall AutoQA Score:** {autoqa:.1f}% {'✅ Good' if autoqa >= 80 else '⚠️ Needs Improvement'}")

st.divider()

# ============================================================================
# ROW 6: Call Timeline Summary
# ============================================================================
st.subheader("ROW 6: Average Call Timeline")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    from widgets_v2.timeline_simple import calculate_timeline_summary
    timeline = calculate_timeline_summary(calls_df)
    
    st.metric("Avg Duration", timeline['avg_duration_str'])
    st.write(f"**Agent Talk:** {timeline['agent_ratio']:.1f}%")
    st.write(f"**Customer Talk:** {timeline['customer_ratio']:.1f}%")
    st.write(f"**Hold Time:** {timeline['silence_ratio']:.1f}%")
    st.write(f"**Sentiment Δ:** {timeline['sentiment_delta']:+.2f}")

with col2:
    st.write("**📊 Key Insights**")
    sentiment_improving = (calls_df['sentiment_end'] > calls_df['sentiment_start']).sum()
    pct_improving = sentiment_improving / len(calls_df) * 100
    
    st.write(f"• Sentiment improves in **{pct_improving:.0f}%** of calls")
    st.write(f"• Average AES score: **{aes['overall_aes_pct']:.1f}%**")
    st.write(f"• Compliance rate: **{timeline['compliance_pass_rate']:.1f}%**")
    st.write(f"• Sales conversion: **{sales['conversion_rate']:.1f}%**")

with col3:
    st.write("**✅ Quick Actions**")
    st.write("→ Review **Technical** topic efficiency")
    st.write("→ Coach agents on **Active Listening**")
    st.write("→ Monitor escalation trend")
    st.write("→ Replicate Sales team success")
    st.write("→ Analyze declining sentiment calls")

st.divider()
st.success("🎉 **ALL 10 WIDGETS COMPLETE!** Dashboard Redesign V2")
