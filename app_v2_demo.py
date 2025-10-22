"""
CC Analytics Dashboard V3 - CLEAN PROFESSIONAL VERSION
With sidebar filters, proper layout, and all required visualizations
"""

import streamlit as st
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from data_generation import generate_dataset

# Page config
st.set_page_config(
    page_title="CC Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    calls_df, transcripts, agents_df = generate_dataset(n_calls=200, n_agents=12, seed=42)
    return calls_df, transcripts, agents_df

calls_df, transcripts, agents_df = load_data()

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================

with st.sidebar:
    st.title("🎛️ Filters")
    
    st.markdown("### 📅 Time Period")
    period = st.selectbox("Select Period", ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"])
    
    st.markdown("### 👥 Team")
    # Get unique teams safely
    if 'team' in calls_df.columns:
        teams = ["All Teams"] + sorted(calls_df['team'].unique().tolist())
    else:
        teams = ["All Teams", "Sales", "Support", "Technical"]
    selected_team = st.selectbox("Select Team", teams)
    
    st.markdown("### 📞 Line")
    lines = ["All Lines", "Customer Service", "Sales", "Technical Support"]
    selected_line = st.selectbox("Select Line", lines)
    
    st.markdown("### 👤 Agent")
    agents = ["All Agents"] + sorted(calls_df['agent_id'].unique().tolist())
    selected_agent = st.selectbox("Select Agent", agents)
    
    st.markdown("---")
    st.caption("Last updated: Just now")

# Filter data
filtered_df = calls_df.copy()
if selected_team != "All Teams" and 'team' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['team'] == selected_team]
if selected_agent != "All Agents":
    filtered_df = filtered_df[filtered_df['agent_id'] == selected_agent]

# ============================================================================
# HEADER
# ============================================================================

st.title("📊 CC Analytics Dashboard")
st.caption(f"Showing {len(filtered_df)} calls | {period}")

# ============================================================================
# TOP KPI ROW - IN BOXES
# ============================================================================

st.markdown("### Key Performance Indicators")

from widgets_v2.aes_card import calculate_aes_components
from widgets_v2.compliance_card import calculate_compliance_score
from widgets_v2.sales_card import calculate_sales_metrics
from widgets_v2.fcr_gauges import calculate_fcr_metrics
from widgets_v2.escalation_card import calculate_escalation_metrics

aes = calculate_aes_components(filtered_df)
comp = calculate_compliance_score(filtered_df)
sales = calculate_sales_metrics(filtered_df)
fcr = calculate_fcr_metrics(filtered_df)
esc = calculate_escalation_metrics(filtered_df)
autoqa = filtered_df['autoqa_score'].mean()

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7, kpi8 = st.columns(8)

with kpi1:
    st.metric("AES Score", f"{aes['overall_aes_pct']:.1f}%", "+2.4%")
with kpi2:
    st.metric("Compliance", f"{comp['score']:.1f}%", "+1.2%")
with kpi3:
    st.metric("FCR Rate", f"{fcr['fcr_validated']:.1f}%", "-2.5%")
with kpi4:
    st.metric("EPR", f"{esc['epr']:.1f}%", "+3.1%")
with kpi5:
    from widgets_v2.timeline_simple import calculate_timeline_summary
    timeline = calculate_timeline_summary(filtered_df)
    st.metric("Avg AHT", timeline['avg_duration_str'], "-12s")
with kpi6:
    st.metric("Sales Conv", f"{sales['conversion_rate']:.1f}%", "+5.2%")
with kpi7:
    st.metric("Sentiment Δ", f"{timeline['sentiment_delta']:+.1f}", "+0.2")
with kpi8:
    st.metric("AutoQA", f"{autoqa:.1f}%", "+4.3%")

st.divider()

# ============================================================================
# ROW 1: AES + COMPLIANCE + SALES
# ============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Agent Effectiveness Score (AES)")
    st.caption("📊 Composite metric: Sentiment (25%) + Compliance (30%) + Resolution (30%) + Quality (15%)")
    
    from widgets_v2.aes_card import create_aes_card
    fig = create_aes_card(filtered_df, target=75.0, prev_period_aes=72.5)
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"**Components:** Sentiment: {aes['sentiment']:.1f} | Compliance: {aes['compliance']:.1f} | Resolution: {aes['resolution']:.1f} | Quality: {aes['quality']:.1f}")

with col2:
    st.markdown("#### Compliance Breakdown")
    st.caption("🔍 Policy adherence and regulatory requirements")
    
    st.metric("Score", f"{comp['score']:.1f}%", delta="+1.2%")
    st.write(f"**Risk Level:** {comp['risk_level']}")
    st.write(f"**Critical Issues:** {comp['critical_violations']}")
    st.write("**Top Issues:**")
    st.write("• Customer verification (23%)")
    st.write("• Data protection (12%)")
    st.write("• Script adherence (8%)")

with col3:
    st.markdown("#### Sales Performance")
    st.caption("💰 Conversion rates and revenue impact")
    
    st.metric("Conversion Rate", f"{sales['conversion_rate']:.1f}%", "+5.2%")
    st.write(f"**Total Value:** €{sales['total_value']:,.0f}")
    st.write("**Breakdown:**")
    st.write(f"• Upsell: {sales['upsell_success']}/{sales['upsell_count']}")
    st.write(f"• Cross-sell: {sales['cross_sell_success']}/{sales['cross_sell_count']}")
    st.write(f"• Closing: {sales['closing_success']}/{sales['closing_count']}")

st.divider()

# ============================================================================
# ROW 2: SENTIMENT + FCR
# ============================================================================

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("#### Customer Sentiment Journey")
    from widgets_v2.sentiment_sankey import create_sentiment_sankey, calculate_sentiment_flows
    fig = create_sentiment_sankey(filtered_df)
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)
    
    flows = calculate_sentiment_flows(filtered_df)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("😠→😊 Improving", flows['improving_count'], f"{flows['improving_pct']:.0f}%")
    with c2:
        st.metric("😐 Stable", flows['stable_count'], f"{flows['stable_pct']:.0f}%")
    with c3:
        st.metric("😊→😠 Declining", flows['declining_count'], f"{flows['declining_pct']:.0f}%")

with col2:
    st.markdown("#### First Contact Resolution (FCR)")
    st.caption("🎯 Comparison: AI prediction vs actual callback rate")
    
    from widgets_v2.fcr_gauges import create_fcr_gauges
    fig = create_fcr_gauges(filtered_df, target=75.0)
    fig.update_layout(height=220)
    st.plotly_chart(fig, use_container_width=True)
    
    gap = fcr['fcr_predicted'] - fcr['fcr_validated']
    if abs(gap) > 10:
        st.warning(f"⚠️ **Gap: {gap:+.1f}%** - AI predicts premature call closing. Review resolution quality.")
    else:
        st.success(f"✅ **Gap: {gap:+.1f}%** - Good alignment between prediction and actual FCR.")

st.divider()

# ============================================================================
# ROW 3: PERFORMANCE TREND + TOPIC EFFICIENCY
# ============================================================================

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("#### Performance Trend (30 Days)")
    
    tab1, tab2, tab3, tab4 = st.tabs(["AES", "AutoQA", "FCR", "Sentiment"])
    
    from widgets_v2.performance_trend import create_performance_trend
    
    with tab1:
        fig = create_performance_trend(filtered_df, metric='AES', target=75.0, days=30)
        fig.update_layout(height=220, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_aes')
    
    with tab2:
        fig = create_performance_trend(filtered_df, metric='AutoQA', target=80.0, days=30)
        fig.update_layout(height=220, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_autoqa')
    
    with tab3:
        fig = create_performance_trend(filtered_df, metric='FCR', target=75.0, days=30)
        fig.update_layout(height=220, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_fcr')
    
    with tab4:
        fig = create_performance_trend(filtered_df, metric='Sentiment', target=60.0, days=30)
        fig.update_layout(height=220, margin=dict(l=30, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, key='trend_sent')

with col2:
    st.markdown("#### Topic Efficiency")
    st.caption("🎯 Call duration vs benchmark by topic category")
    
    from widgets_v2.topic_bubble import create_topic_bubble_chart, calculate_topic_efficiency
    fig = create_topic_bubble_chart(filtered_df)
    fig.update_layout(height=280)
    st.plotly_chart(fig, use_container_width=True)
    
    topics = calculate_topic_efficiency(filtered_df)
    critical = topics[topics['status'] == 'critical'].nlargest(1, 'total_talk_time')
    if len(critical) > 0:
        row = critical.iloc[0]
        st.error(f"🔴 **{row['topic']}**: {row['avg_aht']:.1f} min avg (+{abs(row['pct_diff']):.0f}% vs benchmark)")

st.divider()

# ============================================================================
# ROW 4: CALL TIMELINE VISUALIZATION
# ============================================================================

st.markdown("#### Average Call Timeline Analysis")
st.caption("📞 Detailed breakdown of call structure, sentiment progression, and speaking dynamics")

# Create multi-layer timeline visualization
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.15, 0.3, 0.3, 0.25],
    subplot_titles=('Speaker Distribution', 'Sentiment Progression', 'Speaking Rate (WPM)', 'Compliance Checkpoints')
)

# LAYER 1: Speaker Distribution (Horizontal Stacked Bar)
fig.add_trace(go.Bar(
    x=[timeline['agent_ratio']], y=[''], orientation='h',
    name='Agent', marker=dict(color='#2196F3'),
    text=[f"Agent: {timeline['agent_ratio']:.0f}%"],
    textposition='inside',
    hovertemplate='Agent Talk Time: %{x:.1f}%<extra></extra>'
), row=1, col=1)

fig.add_trace(go.Bar(
    x=[timeline['customer_ratio']], y=[''], orientation='h',
    name='Customer', marker=dict(color='#FF9800'),
    text=[f"Customer: {timeline['customer_ratio']:.0f}%"],
    textposition='inside',
    hovertemplate='Customer Talk Time: %{x:.1f}%<extra></extra>'
), row=1, col=1)

fig.add_trace(go.Bar(
    x=[timeline['silence_ratio']], y=[''], orientation='h',
    name='Silence', marker=dict(color='#9E9E9E'),
    text=[f"Silence: {timeline['silence_ratio']:.0f}%"],
    textposition='inside',
    hovertemplate='Silence: %{x:.1f}%<extra></extra>'
), row=1, col=1)

# LAYER 2: Sentiment Progression (Area Chart)
time_pct = [0, 20, 40, 60, 80, 100]
sentiment_values = [-0.4, -0.3, -0.1, 0.0, 0.15, 0.2]

# Create gradient fill
fig.add_trace(go.Scatter(
    x=time_pct, y=sentiment_values,
    fill='tozeroy',
    fillgradient=dict(
        type='vertical',
        colorscale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']]
    ),
    line=dict(color='#059669', width=3),
    mode='lines+markers',
    name='Sentiment',
    marker=dict(size=8, color='#059669'),
    hovertemplate='Time: %{x}%<br>Sentiment: %{y:.2f}<extra></extra>'
), row=2, col=1)

# Add sentiment zone lines
fig.add_hline(y=0.3, line_dash='dash', line_color='green', annotation_text='Positive', row=2, col=1)
fig.add_hline(y=-0.3, line_dash='dash', line_color='red', annotation_text='Negative', row=2, col=1)
fig.add_hline(y=0, line_dash='dot', line_color='gray', row=2, col=1)

# LAYER 3: Speaking Rate (WPM - Two Lines)
agent_wpm = [140, 145, 152, 148, 143, 145]
customer_wpm = [130, 135, 138, 140, 136, 138]

fig.add_trace(go.Scatter(
    x=time_pct, y=agent_wpm,
    mode='lines+markers',
    name='Agent WPM',
    line=dict(color='#2196F3', width=3),
    marker=dict(size=7),
    hovertemplate='Agent WPM: %{y}<extra></extra>'
), row=3, col=1)

fig.add_trace(go.Scatter(
    x=time_pct, y=customer_wpm,
    mode='lines+markers',
    name='Customer WPM',
    line=dict(color='#FF9800', width=3),
    marker=dict(size=7),
    hovertemplate='Customer WPM: %{y}<extra></extra>'
), row=3, col=1)

# Add WPM zone lines
fig.add_hline(y=180, line_dash='dash', line_color='red', annotation_text='Too Fast', row=3, col=1)
fig.add_hline(y=150, line_dash='dash', line_color='orange', annotation_text='Fast', row=3, col=1)
fig.add_hline(y=120, line_dash='dash', line_color='blue', annotation_text='Slow', row=3, col=1)

# LAYER 4: Compliance Checkpoints (Scatter with Status)
checkpoint_times = [5, 30, 70, 95]
checkpoint_names = ['Greeting & ID', 'Active Listening', 'Solution Offered', 'Proper Closing']
checkpoint_status = [1, 1, 0, 1]  # 1 = pass, 0 = fail

for i, (time, name, status) in enumerate(zip(checkpoint_times, checkpoint_names, checkpoint_status)):
    fig.add_trace(go.Scatter(
        x=[time], y=[i],
        mode='markers+text',
        marker=dict(
            size=20,
            color='#10B981' if status else '#EF4444',
            symbol='circle',
            line=dict(width=2, color='white')
        ),
        text=['✓' if status else '✗'],
        textposition='middle center',
        textfont=dict(color='white', size=14, family='Arial Black'),
        name=name,
        hovertemplate=f'{name}<br>Status: {"✓ Pass" if status else "✗ Fail"}<extra></extra>',
        showlegend=False
    ), row=4, col=1)

# Update layout
fig.update_xaxes(range=[0, 100], title_text='Call Progress (%)', row=4, col=1)
fig.update_yaxes(showticklabels=False, row=1, col=1)
fig.update_yaxes(range=[-1, 1], title_text='Score', row=2, col=1)
fig.update_yaxes(range=[100, 200], title_text='WPM', row=3, col=1)
fig.update_yaxes(showticklabels=False, range=[-0.5, 3.5], row=4, col=1)

fig.update_layout(
    height=600,
    showlegend=True,
    legend=dict(orientation='h', yanchor='top', y=-0.05),
    hovermode='x unified',
    barmode='stack'
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ESCALATION STATS
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Escalation Prevention Rate", f"{esc['epr']:.1f}%", "+3.1%")
    st.caption(f"Escalated: {esc['escalated_count']} / {esc['total_calls']}")

with col2:
    if esc['reasons']:
        st.write("**Top Escalation Reasons:**")
        for reason, count in list(esc['reasons'].items())[:3]:
            st.write(f"• {reason.replace('_', ' ').title()}: {count}")

with col3:
    st.write("**Call Volume:** 200 calls")
    st.write(f"**Avg Duration:** {timeline['avg_duration_str']}")
    st.write(f"**Compliance Rate:** {timeline['compliance_pass_rate']:.0f}%")

st.success("✅ Dashboard V3 - Professional Analytics with Full Context")
