"""
CC Analytics Dashboard - ONE PAGE VERSION
Complete redesign: All widgets fit on single screen (1920x1080) without scrolling
"""

import streamlit as st
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data_generation import generate_dataset

# ============================================================================
# PAGE CONFIG + GLOBAL CSS
# ============================================================================

st.set_page_config(
    page_title="CC Analytics Dashboard V2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# STEP 1: GLOBAL CSS FOR COMPACT LAYOUT
st.markdown("""
<style>
    /* Reduce padding/margins globally */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Reduce space between widgets */
    .element-container {
        margin-bottom: 0.3rem;
    }
    
    /* Smaller fonts for captions */
    .caption {
        font-size: 0.75rem;
    }
    
    /* Reduce header sizes */
    h1 {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.3rem;
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
    }
    
    h3 {
        font-size: 1.1rem;
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }
    
    /* Reduce chart margins */
    .js-plotly-plot {
        margin-bottom: 0rem;
    }
    
    /* Compact metric cards */
    [data-testid="metric-container"] {
        padding: 0.3rem;
    }
    
    /* Hide extra spacing */
    .stMarkdown {
        margin-bottom: 0rem;
    }
</style>
""", unsafe_allow_html=True)

# Generate data
@st.cache_data
def load_data():
    calls_df, transcripts, agents_df = generate_dataset(n_calls=200, n_agents=12, seed=42)
    return calls_df, transcripts, agents_df

calls_df, transcripts, agents_df = load_data()

# ============================================================================
# HEADER (80px)
# ============================================================================
st.title("📊 CC Analytics Dashboard")
st.caption(f"Last 30 days | {len(calls_df)} calls | {len(agents_df)} agents")

# ============================================================================
# ROW 1: KEY PERFORMANCE INDICATORS (150px)
# ============================================================================

col1, col2 = st.columns([1, 1])

with col1:
    # AES Spider Chart
    from widgets_v2.aes_card import create_aes_card
    fig_aes = create_aes_card(calls_df, target=75.0, prev_period_aes=72.5)
    fig_aes.update_layout(height=140, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_aes, use_container_width=True, key='aes')

with col2:
    # STEP 2: FIX ROW 1 - SALES PERFORMANCE KPI CARDS
    st.markdown("**Sales Performance**")
    
    from widgets_v2.sales_card import calculate_sales_metrics
    sales = calculate_sales_metrics(calls_df)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(
            label="Upsale",
            value=f"{sales['upsell_success']}",
            delta=f"+12% vs period"
        )
        st.caption(f"€{sales['upsell_success'] * 500:,.0f} value")
    
    with c2:
        st.metric(
            label="Cross-sale",
            value=f"{sales['cross_sell_success']}",
            delta=f"+8% vs period"
        )
        st.caption(f"€{sales['cross_sell_success'] * 377:,.0f} value")
    
    with c3:
        st.metric(
            label="Closing Rate",
            value=f"{sales['conversion_rate']:.1f}%",
            delta=f"+5.2% vs period"
        )
        st.caption(f"{sales['closing_success']} conversions")

# ============================================================================
# ROW 2: CUSTOMER EXPERIENCE METRICS (140px)
# ============================================================================

col1, col2 = st.columns([2, 1])

with col1:
    # Sentiment Sankey
    from widgets_v2.sentiment_sankey import create_sentiment_sankey
    fig_sankey = create_sentiment_sankey(calls_df)
    fig_sankey.update_layout(height=120, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_sankey, use_container_width=True, key='sankey')

with col2:
    st.markdown("**Summary**")
    from widgets_v2.sentiment_sankey import calculate_sentiment_flows
    flows = calculate_sentiment_flows(calls_df)
    
    st.metric("😠→😊 Improving", f"{flows['improving_pct']:.0f}%", 
              delta=f"{flows['improving_count']} calls")
    st.metric("😐→😐 Stable", f"{flows['stable_pct']:.0f}%")
    st.metric("😊→😠 Declining", f"{flows['declining_pct']:.0f}%", delta_color="inverse")

# ============================================================================
# ROW 3: FCR ANALYSIS + COMPLIANCE/EPR (130px)
# ============================================================================

# STEP 3: FIX ROW 3 - FCR WITH GAP ANALYSIS
st.markdown("**FCR Analysis**")

col1, col2, col3 = st.columns([2, 1, 2])

from widgets_v2.fcr_gauges import calculate_fcr_metrics
fcr = calculate_fcr_metrics(calls_df)

with col1:
    st.caption("**AI-Predicted FCR**")
    st.caption("*From transcript analysis*")
    
    # Simple gauge using metric
    color = "🔴" if fcr['fcr_predicted'] < 60 else ("⚠️" if fcr['fcr_predicted'] < 75 else "✅")
    st.metric("Predicted", f"{fcr['fcr_predicted']:.1f}%")
    st.caption(f"{color} {'Below' if fcr['fcr_predicted'] < 75 else 'At'} Target")

with col2:
    st.caption("**Gap Analysis**")
    gap = fcr['fcr_predicted'] - fcr['fcr_validated']
    st.markdown(f"<h1 style='text-align: center; color: orange; margin: 0;'>Δ {gap:+.0f}%</h1>", 
                unsafe_allow_html=True)
    st.caption("AI predicts premature closing" if gap < 0 else "Good alignment")

with col3:
    st.caption("**Actual FCR**")
    st.caption("*No callback in 48h*")
    
    color = "🔴" if fcr['fcr_validated'] < 60 else ("⚠️" if fcr['fcr_validated'] < 75 else "✅")
    st.metric("Validated", f"{fcr['fcr_validated']:.1f}%")
    st.caption(f"{color} {'Good' if fcr['fcr_validated'] >= 75 else 'Below Target'}")

st.info("💡 INSIGHT: Gap indicates agents may be closing calls without full resolution. Review callback patterns.")

# STEP 4: FIX ROW 3 - COMPLIANCE & EPR SIDE BY SIDE
col1, col2 = st.columns(2)

with col1:
    from widgets_v2.compliance_card import calculate_compliance_score
    comp = calculate_compliance_score(calls_df)
    
    st.metric(
        label="Compliance Score",
        value=f"{comp['score']:.1f}%",
        delta="+1.2% vs period"
    )
    st.caption(f"✅ Good | {comp['critical_violations']} critical issues")

with col2:
    from widgets_v2.escalation_card import calculate_escalation_metrics
    esc = calculate_escalation_metrics(calls_df)
    
    st.metric(
        label="Escalation Prevention Rate",
        value=f"{esc['epr']:.1f}%",
        delta="+3.1% vs period"
    )
    st.caption(f"✅ Good | {esc['escalated_count']} escalated")

# ============================================================================
# ROW 4: PERFORMANCE TREND + TOPIC EFFICIENCY (180px)
# ============================================================================

col1, col2 = st.columns([3, 2])

with col1:
    # STEP 5: FIX ROW 4 - PERFORMANCE TREND (ONLY LINE CHART)
    st.markdown("**Performance Trend**")
    
    metric_options = ['AES', 'AutoQA', 'FCR', 'Sentiment', 'AHT']
    selected = st.selectbox("Select Metric:", metric_options, label_visibility="collapsed")
    
    from widgets_v2.performance_trend import create_performance_trend
    
    target_map = {'AES': 75.0, 'AutoQA': 80.0, 'FCR': 75.0, 'Sentiment': 60.0, 'AHT': None}
    fig_trend = create_performance_trend(calls_df, metric=selected, target=target_map[selected], days=30)
    fig_trend.update_layout(height=140, margin=dict(l=30, r=10, t=10, b=30))
    st.plotly_chart(fig_trend, use_container_width=True, key='trend')

with col2:
    # Topic Efficiency Bubble
    st.markdown("**Topic Efficiency**")
    from widgets_v2.topic_bubble import create_topic_bubble_chart, calculate_topic_efficiency
    
    fig_topic = create_topic_bubble_chart(calls_df)
    fig_topic.update_layout(height=140, margin=dict(l=30, r=10, t=10, b=30))
    st.plotly_chart(fig_topic, use_container_width=True, key='topic')
    
    topics = calculate_topic_efficiency(calls_df)
    critical = topics[topics['status'] == 'critical'].nlargest(1, 'total_talk_time')
    if len(critical) > 0:
        row = critical.iloc[0]
        st.caption(f"🔴 {row['topic']}: {row['avg_aht']:.1f} min avg ({abs(row['pct_diff']):.0f}% over)")

# ============================================================================
# ROW 5: QUALITY COMPONENTS ANALYSIS (160px)
# ============================================================================

st.markdown("**Quality Components Analysis**")

# STEP 6: FIX ROW 5 - SPIDER CHART + STACKED BARS
col1, col2 = st.columns([2, 3])

with col1:
    st.caption("**Current Quality State**")
    
    # Spider/Radar chart
    categories = ['Greeting', 'Listening', 'Empathy', 'Solution', 
                  'Professional', 'Positive', 'Control', 'Closing']
    
    # Calculate from data
    values = [
        calls_df['quality'].apply(lambda x: x.get('greeting_and_introduction', False)).mean() * 100,
        calls_df['quality'].apply(lambda x: x.get('active_listening', False)).mean() * 100,
        calls_df['quality'].apply(lambda x: x.get('empathy_shown', False)).mean() * 100,
        calls_df['quality'].apply(lambda x: x.get('solution_offered', False)).mean() * 100,
        calls_df['quality'].apply(lambda x: x.get('professional_tone', False)).mean() * 100,
        calls_df['quality'].apply(lambda x: x.get('positive_language_used', False)).mean() * 100,
        calls_df['quality'].apply(lambda x: x.get('call_control_maintained', False)).mean() * 100,
        calls_df['quality'].apply(lambda x: x.get('closing_proper', False)).mean() * 100,
    ]
    
    fig_spider = go.Figure()
    
    fig_spider.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(33, 150, 243, 0.3)',
        line=dict(color='#2196F3', width=2),
        name='Current'
    ))
    
    fig_spider.add_trace(go.Scatterpolar(
        r=[80] * len(categories),
        theta=categories,
        mode='lines',
        line=dict(color='#FF9800', width=2, dash='dash'),
        name='Target'
    ))
    
    fig_spider.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], showticklabels=False)),
        showlegend=True,
        height=120,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation='h', yanchor='top', y=-0.1, xanchor='center', x=0.5)
    )
    
    st.plotly_chart(fig_spider, use_container_width=True, key='spider')
    
    overall = sum(values) / len(values)
    st.caption(f"**Overall: {overall:.1f}%**")

with col2:
    st.caption("**Quality Trend (Last 4 Weeks)**")
    
    # Simulated weekly data
    weeks = ['W1', 'W2', 'W3', 'W4']
    
    fig_stack = go.Figure()
    
    colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', 
              '#FFC107', '#FF9800', '#FF5722', '#F44336']
    
    for i, cat in enumerate(categories):
        # Simulate trend data
        base = values[i]
        weekly = [base-2, base-1, base, base+1]
        
        fig_stack.add_trace(go.Bar(
            x=weeks,
            y=weekly,
            name=cat,
            marker_color=colors[i]
        ))
    
    fig_stack.update_layout(
        barmode='stack',
        height=120,
        showlegend=True,
        legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5, font=dict(size=9)),
        yaxis=dict(range=[0, 650], title='Score'),
        margin=dict(l=30, r=10, t=10, b=50),
        xaxis=dict(title='Week')
    )
    
    st.plotly_chart(fig_stack, use_container_width=True, key='stack')

# ============================================================================
# ROW 6: AVERAGE CALL TIMELINE (160px)
# ============================================================================

st.markdown("**Average Call Timeline**")

# STEP 7: FIX ROW 6 - MULTI-LAYER VISUALIZATION
col1, col2 = st.columns([7, 3])

with col1:
    from widgets_v2.timeline_simple import calculate_timeline_summary
    timeline = calculate_timeline_summary(calls_df)
    
    # Create multi-layer subplot
    fig_timeline = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.2, 0.4, 0.4],
        subplot_titles=('Speaker Distribution', 'Sentiment Flow', 'Speaking Rate (WPM)')
    )
    
    # LAYER 1: Speaker Distribution
    fig_timeline.add_trace(go.Bar(
        x=[timeline['agent_ratio']],
        y=[''],
        orientation='h',
        name='Agent',
        marker=dict(color='#2196F3'),
        showlegend=True
    ), row=1, col=1)
    
    fig_timeline.add_trace(go.Bar(
        x=[timeline['customer_ratio']],
        y=[''],
        orientation='h',
        name='Customer',
        marker=dict(color='#FF9800'),
        showlegend=True
    ), row=1, col=1)
    
    fig_timeline.add_trace(go.Bar(
        x=[timeline['silence_ratio']],
        y=[''],
        orientation='h',
        name='Silence',
        marker=dict(color='#9E9E9E'),
        showlegend=True
    ), row=1, col=1)
    
    fig_timeline.update_xaxes(range=[0, 100], row=1, col=1)
    fig_timeline.update_yaxes(showticklabels=False, row=1, col=1)
    
    # LAYER 2: Sentiment Flow
    time_pct = [0, 25, 50, 75, 100]
    sentiment_values = [-0.4, -0.2, -0.1, 0.1, 0.2]
    
    fig_timeline.add_trace(go.Scatter(
        x=time_pct,
        y=sentiment_values,
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.3)',
        line=dict(color='#4CAF50', width=2),
        name='Sentiment'
    ), row=2, col=1)
    
    fig_timeline.update_yaxes(range=[-1, 1], row=2, col=1)
    
    # LAYER 3: Speaking Rate
    time_segments = [0, 20, 40, 60, 80, 100]
    agent_wpm = [140, 145, 150, 148, 142, 145]
    customer_wpm = [135, 138, 140, 136, 134, 138]
    
    fig_timeline.add_trace(go.Scatter(
        x=time_segments,
        y=agent_wpm,
        mode='lines+markers',
        name='Agent WPM',
        line=dict(color='#2196F3', width=2),
        marker=dict(size=4)
    ), row=3, col=1)
    
    fig_timeline.add_trace(go.Scatter(
        x=time_segments,
        y=customer_wpm,
        mode='lines+markers',
        name='Customer WPM',
        line=dict(color='#FF9800', width=2),
        marker=dict(size=4)
    ), row=3, col=1)
    
    fig_timeline.update_yaxes(range=[100, 180], row=3, col=1)
    
    fig_timeline.update_layout(
        height=130,
        showlegend=True,
        legend=dict(orientation='h', yanchor='top', y=-0.15, font=dict(size=9)),
        hovermode='x unified',
        barmode='stack',
        margin=dict(l=40, r=10, t=30, b=50)
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True, key='timeline')

with col2:
    st.caption("**Average Call Stats**")
    st.caption(f"**Duration:** {timeline['avg_duration_str']}")
    st.caption("")
    st.caption("**Speaker Time:**")
    st.caption(f"• Agent: {timeline['agent_ratio']:.0f}%")
    st.caption(f"• Customer: {timeline['customer_ratio']:.0f}%")
    st.caption(f"• Silence: {timeline['silence_ratio']:.0f}%")
    st.caption("")
    st.caption("**Sentiment:**")
    st.caption(f"😠 → 😊 Δ {timeline['sentiment_delta']:+.2f}")
    st.caption("⬆️ Improvement" if timeline['sentiment_delta'] > 0 else "⬇️ Decline")
    st.caption("")
    st.caption("**Compliance:**")
    st.caption(f"✅ {timeline['compliance_pass_rate']:.0f}%")

st.success("✅ **Dashboard V2** - All widgets on one page!")
