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
# ROW 4: ENHANCED CALL TIMELINE VISUALIZATION
# ============================================================================

st.markdown("#### 📞 Call Timeline with Compliance Checkpoints")

# Call selector
call_ids = filtered_df['call_id'].tolist()
selected_call_id = st.selectbox("Select Call to Analyze:", call_ids, key='call_selector')

# Get call data
selected_call = filtered_df[filtered_df['call_id'] == selected_call_id].iloc[0]
call_transcript = [t for t in transcripts if t['call_id'] == selected_call_id]

if call_transcript:
    transcript = call_transcript[0]
    segments = transcript['segments']
    
    # Create Gantt chart + WPM overlay with sentiment gradient background
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.35, 0.65],
        subplot_titles=('Speaker Timeline (Gantt Chart)', 'Call Timeline with Compliance Checkpoints')
    )

    # TOP: Gantt Chart - Speaker Timeline
    call_duration = selected_call['duration_sec']
    
    for seg in segments:
        start_time = seg['start']
        end_time = seg['end']
        speaker = seg['speaker']
        text_preview = seg['text'][:30] + "..." if len(seg['text']) > 30 else seg['text']
        wpm = seg.get('wpm', 140)
        
        speaker_row = 'AGENT' if speaker == 'Agent' else 'CUSTOMER'
        color = '#2196F3' if speaker == 'Agent' else '#FF9800'
        
        fig.add_trace(go.Bar(
            x=[end_time - start_time],
            y=[speaker_row],
            base=start_time,
            orientation='h',
            name=speaker,
            marker=dict(color=color, line=dict(width=0)),
            text=[f"{wpm} WPM"],
            textposition='inside',
            hovertemplate=f'<b>{speaker}</b><br>Time: {start_time:.1f}s - {end_time:.1f}s<br>Duration: {end_time-start_time:.1f}s<br>WPM: {wpm}<br>Text: {text_preview}<extra></extra>',
            showlegend=False
        ), row=1, col=1)
    
    # BOTTOM: WPM Lines with Sentiment Gradient Background + Compliance Checkpoints
    
    # Create sentiment gradient background rectangles
    num_zones = 20
    zone_width = call_duration / num_zones
    
    for i in range(num_zones):
        x_start = i * zone_width
        x_end = (i + 1) * zone_width
        
        # Sentiment progression (starts negative, ends positive)
        progress = i / num_zones
        sentiment = selected_call['sentiment_start'] + (selected_call['sentiment_end'] - selected_call['sentiment_start']) * progress
        
        # Color based on sentiment
        if sentiment < -0.3:
            color = 'rgba(239, 68, 68, 0.15)'  # Red
        elif sentiment < 0:
            color = 'rgba(251, 191, 36, 0.15)'  # Orange
        elif sentiment < 0.3:
            color = 'rgba(34, 197, 94, 0.1)'  # Light green
        else:
            color = 'rgba(22, 163, 74, 0.2)'  # Dark green
        
        fig.add_shape(
            type='rect',
            x0=x_start, x1=x_end,
            y0=100, y1=200,
            fillcolor=color,
            line=dict(width=0),
            layer='below',
            row=2, col=1
        )
    
    # WPM lines from segments
    agent_times = []
    agent_wpms = []
    customer_times = []
    customer_wpms = []
    
    for seg in segments:
        mid_time = (seg['start'] + seg['end']) / 2
        wpm = seg.get('wpm', 140)
        
        if seg['speaker'] == 'Agent':
            agent_times.append(mid_time)
            agent_wpms.append(wpm)
        else:
            customer_times.append(mid_time)
            customer_wpms.append(wpm)
    
    # Agent WPM line
    if agent_times:
        fig.add_trace(go.Scatter(
            x=agent_times, y=agent_wpms,
            mode='lines+markers',
            name='Agent WPM',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=6),
            hovertemplate='Agent WPM: %{y}<extra></extra>'
        ), row=2, col=1)
    
    # Customer WPM line
    if customer_times:
        fig.add_trace(go.Scatter(
            x=customer_times, y=customer_wpms,
            mode='lines+markers',
            name='Customer WPM',
            line=dict(color='#FF9800', width=3),
            marker=dict(size=6),
            hovertemplate='Customer WPM: %{y}<extra></extra>'
        ), row=2, col=1)
    
    # WPM reference lines
    fig.add_hline(y=180, line_dash='dash', line_color='#EF4444', line_width=1, annotation_text='Too Fast', row=2, col=1)
    fig.add_hline(y=150, line_dash='dash', line_color='#F59E0B', line_width=1, annotation_text='Normal', row=2, col=1)
    fig.add_hline(y=120, line_dash='dash', line_color='#3B82F6', line_width=1, annotation_text='Slow', row=2, col=1)
    
    # Compliance checkpoints as vertical lines
    compliance = selected_call['compliance']
    checkpoints = [
        ('Greeting', compliance.get('greeting_proper', False), call_duration * 0.05),
        ('Identification', compliance.get('identification', False), call_duration * 0.1),
        ('Verification', compliance.get('customer_verification', False), call_duration * 0.15),
        ('Solution', compliance.get('clear_communication', False), call_duration * 0.7),
        ('Closing', compliance.get('proper_closing', False), call_duration * 0.95)
    ]
    
    for name, status, time_pos in checkpoints:
        color = '#10B981' if status else '#EF4444'
        symbol = '✓' if status else '✗'
        
        fig.add_vline(
            x=time_pos,
            line_dash='dot',
            line_color=color,
            line_width=2,
            annotation_text=f"{symbol} {name}",
            annotation_position='top',
            annotation_font=dict(size=10, color=color),
            row=2, col=1
        )
    
    # Update axes
    fig.update_xaxes(title_text='Time (seconds)', range=[0, call_duration], row=2, col=1)
    fig.update_xaxes(title_text='', range=[0, call_duration], row=1, col=1)
    fig.update_yaxes(title_text='', row=1, col=1)
    fig.update_yaxes(title_text='WPM', range=[100, 200], row=2, col=1)
    
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(orientation='h', yanchor='top', y=-0.08),
        hovermode='x unified',
        barmode='stack',
        margin=dict(l=80, r=20, t=60, b=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Call stats below
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Duration", f"{int(call_duration // 60)}:{int(call_duration % 60):02d}")
        st.caption(f"Agent: {selected_call['agent_talk_sec']:.0f}s | Customer: {selected_call['customer_talk_sec']:.0f}s")
    with col2:
        st.metric("Sentiment Δ", f"{selected_call['sentiment_end'] - selected_call['sentiment_start']:+.2f}")
        st.caption(f"Start: {selected_call['sentiment_start']:.2f} → End: {selected_call['sentiment_end']:.2f}")
    with col3:
        passed = sum([1 for _, status, _ in checkpoints if status])
        st.metric("Compliance", f"{passed}/{len(checkpoints)}")
        st.caption(f"AES: {selected_call['aes_score']:.1f}% | AutoQA: {selected_call['autoqa_score']:.1f}%")

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
