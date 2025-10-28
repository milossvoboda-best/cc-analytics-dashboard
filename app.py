"""
═══════════════════════════════════════════════════════════════════════════════
    CC ANALYTICS DASHBOARD V2.0 - Professional Edition
═══════════════════════════════════════════════════════════════════════════════

QUICK START:
-----------
1. python -m venv .venv
2. .venv\Scripts\activate  (Windows) or source .venv/bin/activate (Unix)
3. pip install -r requirements.txt
4. streamlit run app.py

CHANGELOG V2.0:
--------------
✓ High-contrast sidebar, better filters
✓ NEW: Sentiment Transition Matrix (3x3 heatmap)
✓ NEW: Sentiment Improvement KPIs  
✓ NEW: AHT vs Benchmark dumbbell chart
✓ NEW: Volume Pareto analysis
✓ NEW: 7-day Quality Breakdown stacked area
✓ Timeline: Fixed xaxis range, sentiment flags, WPM cards
✓ Cleaner layout, professional UI/UX

Description: 10-widget professional dashboard, syntetické dáta, zero API calls
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

from data_generation import generate_dataset, get_transcript_for_call, detect_silences, detect_interruptions, calculate_speaking_rate
from metrics import (
    compliance_score, compute_sentiment_journey, is_fcr, calculate_fcr_rate,
    quality_binary_score, aes, calculate_aes_for_call, aci, calculate_tre,
    calculate_7day_trend, calculate_volume_distribution, calculate_aht,
    calculate_agent_aggregates, calculate_escalation_prevention_rate, compare_to_benchmark,
    compute_sentiment_improvement_kpis, get_compliance_top_failures
)
from ui_components import (
    create_gauge_chart, create_horizontal_bar_chart, create_trend_line_chart,
    create_timeline_figure, format_duration, format_percentage, create_progress_bar_html,
    mini_metric_card, legend_badge, sentiment_transition_heatmap, sentiment_transition_chart,
    aht_vs_benchmark_dumbbell, volume_pareto_bars, quality_breakdown_trend_7d,
    create_aes_component_chart
)
from timeline_enhanced import create_enhanced_timeline, calculate_timeline_stats
from aes_widget import create_aes_spider_trend, get_aes_status_card, generate_mock_7day_trend
from csj_sankey import create_sentiment_sankey, calculate_sentiment_summary
from quality_trend_widget import create_quality_trend_redesigned
from fcr_widget import create_fcr_dual_gauge, get_fcr_insights
from efficiency_bubble import create_efficiency_bubble_chart, get_efficiency_insights

st.set_page_config(page_title="CC Analytics Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Last updated: 2025-10-22 13:01 UTC+02:00

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Session state
if "calls_df" not in st.session_state: st.session_state.calls_df = None
if "transcripts" not in st.session_state: st.session_state.transcripts = None
if "agents_df" not in st.session_state: st.session_state.agents_df = None
if "config" not in st.session_state:
    st.session_state.config = {"n_calls": 200, "n_agents": 12, "seed": 42, "simulate_interruptions": False}

@st.cache_data
def load_data(n_calls, n_agents, seed, simulate_interruptions):
    return generate_dataset(n_calls, n_agents, seed, simulate_interruptions)

def refresh_data():
    config = st.session_state.config
    calls_df, transcripts, agents_df = load_data(config["n_calls"], config["n_agents"], config["seed"], config["simulate_interruptions"])
    st.session_state.calls_df = calls_df
    st.session_state.transcripts = transcripts
    st.session_state.agents_df = agents_df

if st.session_state.calls_df is None: refresh_data()

# Sidebar
st.sidebar.markdown("# 🎯 Analytics Hub")
st.sidebar.markdown("*Powered by AI Intelligence*")
st.sidebar.markdown("---")

calls_df = st.session_state.calls_df
min_date = calls_df["timestamp"].min().date()
max_date = calls_df["timestamp"].max().date()

st.sidebar.subheader("📅 DATE RANGE")
date_range = st.sidebar.date_input("Select period", value=(min_date, max_date), min_value=min_date, max_value=max_date, label_visibility="collapsed")

all_teams = sorted(calls_df["team"].unique().tolist())
st.sidebar.subheader("👥 TEAM")
selected_teams = st.sidebar.multiselect("Select teams", options=all_teams, default=[], label_visibility="collapsed", placeholder=f"All teams ({len(all_teams)})")

all_agents = sorted(calls_df["agent_name"].unique().tolist())
st.sidebar.subheader("👤 AGENT")
selected_agents = st.sidebar.multiselect("Select agents", options=all_agents, default=[], label_visibility="collapsed", placeholder=f"All agents ({len(all_agents)})")

all_topics = sorted(calls_df["resolution"].apply(lambda x: x["issue_category"]).unique().tolist())
st.sidebar.subheader("🏷️ TOPIC")
selected_topics = st.sidebar.multiselect("Select topics", options=all_topics, default=[], label_visibility="collapsed", placeholder=f"All topics ({len(all_topics)})")

st.sidebar.subheader("📞 DIRECTION")
selected_directions = st.sidebar.multiselect("Select directions", options=["INBOUND", "OUTBOUND"], default=[], label_visibility="collapsed", placeholder="All directions")

st.sidebar.subheader("🌐 LANGUAGE")
selected_languages = st.sidebar.multiselect("Select languages", options=["cs", "sk", "en"], default=[], label_visibility="collapsed", placeholder="All languages")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Filters", use_container_width=True):
    st.rerun()
st.sidebar.markdown("---")

with st.sidebar.expander("⚙️ Dataset Configuration", expanded=False):
    new_n_calls = st.number_input("Number of calls", min_value=10, max_value=1000, value=st.session_state.config["n_calls"])
    new_n_agents = st.number_input("Number of agents", min_value=1, max_value=50, value=st.session_state.config["n_agents"])
    new_seed = st.number_input("Random seed", min_value=0, max_value=9999, value=st.session_state.config["seed"])
    new_simulate_interruptions = st.checkbox("Simulate interruptions", value=st.session_state.config["simulate_interruptions"])
    
    if st.button("🔄 Regenerate Dataset", type="primary"):
        st.session_state.config.update({"n_calls": new_n_calls, "n_agents": new_n_agents, "seed": new_seed, "simulate_interruptions": new_simulate_interruptions})
        load_data.clear()
        refresh_data()
        st.success("Dataset regenerated!")
        st.rerun()

def apply_filters(df):
    filtered = df.copy()
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[(filtered["timestamp"].dt.date >= start_date) & (filtered["timestamp"].dt.date <= end_date)]
    if selected_teams: filtered = filtered[filtered["team"].isin(selected_teams)]
    if selected_agents: filtered = filtered[filtered["agent_name"].isin(selected_agents)]
    if selected_topics: filtered = filtered[filtered["resolution"].apply(lambda x: x["issue_category"] in selected_topics)]
    if selected_directions: filtered = filtered[filtered["direction"].isin(selected_directions)]
    if selected_languages: filtered = filtered[filtered["language"].isin(selected_languages)]
    return filtered

filtered_calls = apply_filters(calls_df)

# Professional Header with Brand Colors
st.markdown("""
<div style='text-align: center; padding: 2rem 0 1rem 0;'>
    <h1 style='font-size: 2.75rem; font-weight: 800; 
               color: #1e3a5f;
               margin-bottom: 0.5rem; letter-spacing: -0.03em;'>
        CC Analytics Platform
    </h1>
    <p style='font-size: 1.1rem; color: #64748b; font-weight: 500; margin-bottom: 0;'>
        AI-Powered Contact Center Intelligence
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='text-align: center; padding: 1rem; 
            background: linear-gradient(135deg, rgba(212, 244, 236, 0.5) 0%, rgba(168, 230, 215, 0.3) 100%);
            border-radius: 12px; margin-bottom: 2rem; 
            border: 1.5px solid #a8e6d7;
            box-shadow: 0 2px 8px rgba(30, 58, 95, 0.04);'>
    <span style='font-weight: 700; color: #1e3a5f;'>{len(filtered_calls):,}</span> calls analyzed | 
    <span style='font-weight: 700; color: #2d4a6f;'>{len(filtered_calls['agent_id'].unique())}</span> agents | 
    <span style='font-weight: 500; color: #64748b;'>{min_date} → {max_date}</span>
</div>
""", unsafe_allow_html=True)

tab_overview, tab_agents, tab_calls, tab_config = st.tabs(["📈 Overview", "👥 Agents", "📞 Calls", "⚙️ Config"])

# === TAB 1: OVERVIEW ===
with tab_overview:
    if len(filtered_calls) == 0:
        st.warning("⚠️ No calls match the selected filters.")
    else:
        filtered_calls["aes"] = filtered_calls.apply(calculate_aes_for_call, axis=1)
        filtered_calls["comp_result"] = filtered_calls["compliance"].apply(compliance_score)
        filtered_calls["quality_score"] = filtered_calls["quality"].apply(quality_binary_score)
        filtered_calls["is_fcr"] = filtered_calls["resolution"].apply(is_fcr)
        
        # ROW 1: AES Spider + Trend
        st.subheader("1️⃣ Agent Effectiveness Score (AES)")
        
        # Calculate component scores
        avg_sentiment_component = ((filtered_calls["sentiment_end"] - filtered_calls["sentiment_start"] + 2) / 4 * 100).mean() * 0.25
        avg_compliance = filtered_calls["comp_result"].apply(lambda x: x["score"]).mean() * 0.30
        avg_resolution = filtered_calls["resolution"].apply(lambda x: 100 if x["resolution_achieved"] == "full" else (50 if x["resolution_achieved"] == "partial" else 0)).mean() * 0.30
        avg_quality = filtered_calls["quality_score"].mean() * 0.15
        avg_aes = filtered_calls["aes"].mean()
        
        # Component scores (without percentages in names)
        components = {
            "Sentiment": avg_sentiment_component,
            "Compliance": avg_compliance,
            "Resolution": avg_resolution,
            "Quality": avg_quality
        }
        
        # Generate 7-day trend data (mock)
        trend_data = generate_mock_7day_trend(avg_aes, variance=2.5)
        
        # Get status card info
        status_info = get_aes_status_card(avg_aes, target=75.0)
        
        # Display big number card
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.metric(
                "Overall AES",
                f"{status_info['score']:.1f}%",
                delta=f"{status_info['delta']:+.1f}% vs target"
            )
        with col2:
            st.markdown(f"### {status_info['status']}")
            st.caption(status_info['description'])
        
        # Create and display spider + trend chart
        fig_aes = create_aes_spider_trend(
            current_components=components,
            trend_data=trend_data,
            overall_aes=avg_aes,
            target=75.0
        )
        st.plotly_chart(fig_aes, use_container_width=True)
        
        st.markdown("---")
        
        # ROW 2: Sentiment Journey Sankey
        st.subheader("2️⃣ Customer Sentiment Journey Analysis")

        # Calculate summary first
        summary = calculate_sentiment_summary(filtered_calls)

        # Layout: Sankey + Tables on left, Summary metrics on right
        col1, col2 = st.columns([2, 1])

        with col1:
            # Create Sankey diagram
            fig_sankey = create_sentiment_sankey(filtered_calls)
            st.plotly_chart(fig_sankey, use_container_width=True)

            # Declining breakdown table BELOW Sankey (within col1)
            if summary['declining_count'] > 0:
                st.markdown("#### 🔴 Worst Performing - Declining Calls")

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("**Worst Topics:**")
                    if summary['declining_by_topic']:
                        topic_data = []
                        for item in summary['declining_by_topic']:
                            topic_data.append({
                                'Topic': item['topic'],
                                'Declining Calls': item['count']
                            })
                        st.dataframe(pd.DataFrame(topic_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("No data")

                with col_b:
                    st.markdown("**Worst Agents:**")
                    if summary['declining_by_agent']:
                        agent_data = []
                        for item in summary['declining_by_agent']:
                            agent_data.append({
                                'Agent': item['agent'],
                                'Declining Calls': item['count']
                            })
                        st.dataframe(pd.DataFrame(agent_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("No data")

        with col2:
            # Summary metrics
            st.markdown("#### 📊 Summary")
            st.metric(
                "😠→😊 IMPROVING",
                f"{summary['improving_pct']}%",
                delta=f"{summary['improving_count']} calls",
                delta_color="normal"
            )
            st.success(f"✅ Strong positive trend")

            st.metric(
                "😐→😐 STABLE",
                f"{summary['stable_pct']}%",
                delta=f"{summary['stable_count']} calls",
                delta_color="off"
            )

            st.metric(
                "😊→😠 DECLINING",
                f"{summary['declining_pct']}%",
                delta=f"{summary['declining_count']} calls",
                delta_color="inverse"
            )
            if summary['declining_pct'] > 10:
                st.warning(f"⚠️ Monitor decline trend")

            st.info(f"💡 Most common: {summary['top_flow']} ({summary['top_flow_count']} calls)")
        
        # ROW 3: First Contact Resolution
        st.subheader("3️⃣ First Contact Resolution (FCR)")
        
        # Calculate both FCR metrics
        fcr_stats = calculate_fcr_rate(filtered_calls)
        fcr_agent = fcr_stats['fcr_rate']
        fcr_computed = (filtered_calls["resolution"].apply(lambda x: not x["callback_needed"])).mean() * 100
        
        # Create dual gauge chart
        fig_fcr = create_fcr_dual_gauge(fcr_agent, fcr_computed)
        st.plotly_chart(fig_fcr, use_container_width=True)
        
        # Get insights
        insights = get_fcr_insights(fcr_agent, fcr_computed)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Alignment", insights['alignment'])
        with col2:
            st.metric("Overall Status", insights['status'])
        with col3:
            st.metric("Avg FCR", f"{insights['avg_fcr']:.1f}%")
        
        st.info(f"💡 **Insight**: {insights['insight']}")
        st.warning(f"📌 **Recommendation**: {insights['recommendation']}")
        st.markdown("---")
        
        # ROW 4: Compliance + EPR
        st.subheader("4️⃣ Compliance & Escalation Management")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Compliance Risk**")
            avg_comp_score = filtered_calls["comp_result"].apply(lambda x: x["score"]).mean()
            fig_comp = create_gauge_chart(avg_comp_score, "Compliance Score", max_value=100, thresholds={"low": 70, "medium": 85})
            st.plotly_chart(fig_comp, use_container_width=True)
            top_failures = get_compliance_top_failures(filtered_calls, top_n=2)
            critical_viol = filtered_calls["comp_result"].apply(lambda x: x["critical_violations_count"]).sum()
            if top_failures:
                st.markdown("**Top Compliance Issues:**")
                for field, count in top_failures:
                    st.markdown(f"- {field.replace('_', ' ').title()}: **{count}** failures")
            if critical_viol > 0:
                st.error(f"🚨 **{critical_viol}** critical violations detected")
        with col2:
            st.markdown("**Escalation Prevention Rate**")
            epr_stats = calculate_escalation_prevention_rate(filtered_calls)
            fig_epr = create_gauge_chart(epr_stats["epr"], "EPR", max_value=100, thresholds={"low": 80, "medium": 90})
            st.plotly_chart(fig_epr, use_container_width=True)
            if epr_stats["reasons_breakdown"]:
                st.markdown("**Escalation Reasons:**")
                for reason, count in epr_stats["reasons_breakdown"].items():
                    pct = 100 * count / epr_stats["escalated_count"] if epr_stats["escalated_count"] > 0 else 0
                    st.markdown(f"- {reason.title()}: **{count}** ({pct:.0f}%)")
            else:
                st.success("✅ No escalations in filtered period!")
        st.markdown("---")
        
        # ROW 5: Efficiency Bubble Chart (Topic Performance Matrix)
        st.subheader("5️⃣ Topic Efficiency Matrix")
        
        # Create bubble chart
        fig_efficiency = create_efficiency_bubble_chart(filtered_calls)
        st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # Get insights
        eff_insights = get_efficiency_insights(filtered_calls)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**⭐ Top Performers (High AES, Low AHT)**")
            for topic in eff_insights['top_performers']:
                st.markdown(f"- **{topic['topic']}**: {topic['aht']:.1f} min AHT, {topic['aes']:.1f} AES ({topic['volume']} calls)")
        
        with col2:
            st.markdown("**🔴 Needs Improvement (Low AES or High AHT)**")
            for topic in eff_insights['needs_improvement']:
                st.markdown(f"- **{topic['topic']}**: {topic['aht']:.1f} min AHT, {topic['aes']:.1f} AES ({topic['volume']} calls)")
        
        st.info(f"💡 **Overall**: Avg AHT = {eff_insights['avg_aht']:.1f} min, Avg AES = {eff_insights['avg_aes']:.1f}. Focus on improving topics in bottom-right quadrant.")
        st.markdown("---")
        
        # ROW 6: QA Controls Trend
        st.subheader("6️⃣ 7-dňový trend QA kontrol")
        fig_quality = create_quality_trend_redesigned(filtered_calls, target=75.0)
        st.plotly_chart(fig_quality, use_container_width=True)
        st.info("💡 Graf zobrazuje úspešnosť 5 hlavných QA komponentov hodnotenia hovorov. Stacked bars ukazujú percentuálny úspech pre každú QA kontrolu.")

# === TAB 2: AGENTS ===
with tab_agents:
    st.header("👥 Agent Performance")
    if len(filtered_calls) == 0:
        st.warning("⚠️ No calls match filters.")
    else:
        agent_agg = calculate_agent_aggregates(filtered_calls, st.session_state.agents_df)
        if len(agent_agg) > 0: st.dataframe(agent_agg, use_container_width=True, hide_index=True)

# === TAB 3: CALLS ===
with tab_calls:
    st.header("📞 Call Details")
    if len(filtered_calls) == 0:
        st.warning("⚠️ No calls match filters.")
    else:
        st.subheader("📋 Calls List")
        calls_display = filtered_calls.copy()
        calls_display["topic"] = calls_display["resolution"].apply(lambda x: x["issue_category"])
        calls_display["risk_level"] = calls_display["comp_result"].apply(lambda x: x["risk_level"])
        calls_display["sentiment_delta"] = calls_display["sentiment_end"] - calls_display["sentiment_start"]
        st.dataframe(calls_display[["call_id", "timestamp", "agent_name", "topic", "duration_sec", "aes", "is_fcr", "risk_level", "sentiment_delta"]].head(50), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Call Detail View")
        selected_call_id = st.selectbox("Select a call to view detailed timeline", options=calls_display["call_id"].tolist())
        
        if selected_call_id:
            call_row = filtered_calls[filtered_calls["call_id"] == selected_call_id].iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Agent", call_row["agent_name"])
            with col2: st.metric("Duration", format_duration(call_row["duration_sec"]))
            with col3: st.metric("AES", f"{call_row['aes']:.1f}")
            with col4: st.metric("FCR", "✅ Yes" if call_row["is_fcr"] else "❌ No")
            
            st.markdown("---")
            st.markdown("### 📊 Enhanced Call Timeline")
            segments = get_transcript_for_call(selected_call_id, st.session_state.transcripts)

            if segments:
                # Detect silences
                silence_periods, _ = detect_silences(segments, call_row["duration_sec"])

                # Prepare compliance checkpoints with REALISTIC TIMES
                # Find actual times when these events occurred in transcript
                comp = call_row["compliance"]

                # Helper function to find agent speech time in specific range
                def find_agent_speech_time(segments, min_pct, max_pct, duration):
                    min_time = duration * min_pct
                    max_time = duration * max_pct
                    agent_segs = [s for s in segments if s["speaker"] == "AGENT" and min_time <= s["start_time"] <= max_time]
                    if agent_segs:
                        return agent_segs[0]["start_time"] + (agent_segs[0]["end_time"] - agent_segs[0]["start_time"]) / 2
                    return (min_time + max_time) / 2

                compliance_checkpoints = []

                # Greeting - should be in first 10% of call
                if comp.get("greeting_proper", True):
                    greeting_time = find_agent_speech_time(segments, 0, 0.1, call_row["duration_sec"])
                    compliance_checkpoints.append({
                        "time": greeting_time,
                        "type": "Greeting",
                        "passed": True,
                        "description": "Agent properly greeted the customer"
                    })

                # Verification - should be in first 20% of call
                if comp.get("customer_verification", False):
                    verification_time = find_agent_speech_time(segments, 0.05, 0.2, call_row["duration_sec"])
                    compliance_checkpoints.append({
                        "time": verification_time,
                        "type": "Verification",
                        "passed": True,
                        "description": "Customer identity verified"
                    })

                # Data Protection - middle 30-60% of call
                if comp.get("data_protection_mentioned", True):
                    data_prot_time = find_agent_speech_time(segments, 0.3, 0.6, call_row["duration_sec"])
                    compliance_checkpoints.append({
                        "time": data_prot_time,
                        "type": "Data Protection",
                        "passed": True,
                        "description": "Data protection policy mentioned"
                    })

                # Call Summary - last 15% of call
                if comp.get("call_summarized", True):
                    summary_time = find_agent_speech_time(segments, 0.85, 1.0, call_row["duration_sec"])
                    compliance_checkpoints.append({
                        "time": summary_time,
                        "type": "Call Summary",
                        "passed": True,
                        "description": "Agent provided call summary"
                    })

                # Prepare sentiment points
                sentiment_points = [
                    {
                        "time": 0,
                        "sentiment": call_row['sentiment_start'],
                        "label": "Start"
                    },
                    {
                        "time": call_row["duration_sec"] / 2,
                        "sentiment": call_row['sentiment_middle'],
                        "label": "Mid"
                    },
                    {
                        "time": call_row["duration_sec"],
                        "sentiment": call_row['sentiment_end'],
                        "label": "End"
                    }
                ]

                # Prepare WPM data - calculate REAL WPM per segment
                import numpy as np

                # Calculate WPM for each segment
                agent_wpm_points = []
                customer_wpm_points = []

                for seg in segments:
                    duration_min = (seg["end_time"] - seg["start_time"]) / 60
                    if duration_min > 0:
                        wpm = seg["word_count"] / duration_min
                        time_point = (seg["start_time"] + seg["end_time"]) / 2

                        if seg["speaker"] == "AGENT":
                            agent_wpm_points.append({"time": time_point, "wpm": round(wpm, 1)})
                        else:
                            customer_wpm_points.append({"time": time_point, "wpm": round(wpm, 1)})

                wpm_data = {
                    "agent": agent_wpm_points,
                    "customer": customer_wpm_points
                }
                
                # Create enhanced timeline
                fig_timeline = create_enhanced_timeline(
                    segments=segments,
                    compliance_checkpoints=compliance_checkpoints,
                    sentiment_points=sentiment_points,
                    wpm_data=wpm_data,
                    silence_periods=silence_periods,
                    call_duration=call_row["duration_sec"]
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)

                # Info box explaining timeline features
                st.info("""
                💡 **Ako čítať timeline:**
                - **Horný graf:** Modré bloky = Agent hovorí, Oranžové bloky = Zákazník hovorí. Prejdite myšou pre text prepisu.
                - **Pozadie:** Farebný prechod (červená→žltá→zelená) ukazuje zmenu sentimentu zákazníka počas hovoru.
                - **Zvislé čiary:** Označujú kde AI identifikovalo povinné body (pozdrav, verifikácia, atď.).
                - **Dolný graf:** Rýchlosť reči (WPM) agenta a zákazníka v reálnom čase.
                """)

                # Summary stats
                stats = calculate_timeline_stats(segments, silence_periods, wpm_data, sentiment_points)
                
                st.markdown("#### 📊 Call Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Pause (3-10s)", 
                        f"{stats['pause_count']} ({stats['pause_total']:.0f}s)",
                        help="Number and total duration of pauses"
                    )
                
                with col2:
                    hold_status = "🔴" if stats['hold_total'] > 30 else "✅"
                    st.metric(
                        "Hold (>10s)", 
                        f"{hold_status} {stats['hold_count']} ({stats['hold_total']:.0f}s)",
                        help="Number and total duration of holds"
                    )
                
                with col3:
                    st.metric(
                        "Agent WPM", 
                        f"Avg: {stats['agent_wpm_avg']:.0f}, Peak: {stats['agent_wpm_peak']:.0f}",
                        help="Average and peak speaking rate"
                    )
                
                with col4:
                    delta_icon = "⬆️" if stats['sentiment_delta'] > 0.2 else ("⬇️" if stats['sentiment_delta'] < -0.2 else "➡️")
                    st.metric(
                        "Sentiment Δ", 
                        f"{delta_icon} {stats['sentiment_delta']:+.2f}",
                        help="Change from start to end"
                    )
                
                # Compliance summary
                passed_count = sum(1 for cp in compliance_checkpoints if cp['passed'])
                total_count = len(compliance_checkpoints)
                comp_pct = (passed_count / total_count) * 100 if total_count > 0 else 0
                
                st.markdown(f"**Compliance Score**: {passed_count}/{total_count} passed ({comp_pct:.0f}%)")
                failed_checkpoints = [cp for cp in compliance_checkpoints if not cp['passed']]
                if failed_checkpoints:
                    st.error(f"❌ Failed: {', '.join([cp['type'] for cp in failed_checkpoints])}")
            else:
                st.info("No transcript available for this call.")
            
            st.markdown("---")
            
            # Detail cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Compliance**")
                comp = call_row["compliance"]
                for k, v in comp.items():
                    if isinstance(v, bool):
                        icon = "✅" if v else "❌"
                        st.markdown(f"{icon} {k.replace('_', ' ').title()}")
            with col2:
                st.markdown("**Resolution**")
                res = call_row["resolution"]
                st.markdown(f"**Status**: {res['resolution_achieved'].title()}")
                st.markdown(f"**Satisfied**: {'✅' if res['customer_satisfied'] else '❌'}")
                st.markdown(f"**Escalated**: {'⚠️ Yes' if res['escalated'] else '✅ No'}")
            with col3:
                st.markdown("**Quality**")
                qual = call_row["quality"]
                st.markdown(f"**Score**: {call_row['quality_score']:.0f}/100")
                if qual.get("positive_moments"):
                    for pm in qual["positive_moments"]:
                        st.success(f"✨ {pm}")
                if qual.get("negative_moments"):
                    for nm in qual["negative_moments"]:
                        st.error(f"⚠️ {nm}")

# === TAB 4: CONFIG ===
with tab_config:
    st.header("⚙️ Configuration & Information")
    st.markdown("**Current Dataset Configuration**")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Calls", st.session_state.config["n_calls"])
    with col2: st.metric("Agents", st.session_state.config["n_agents"])
    with col3: st.metric("Seed", st.session_state.config["seed"])
    with col4: st.metric("Interruptions", "Enabled" if st.session_state.config["simulate_interruptions"] else "Disabled")
    
    st.markdown("---")
    st.markdown("**Metrika Definitions**")
    st.markdown("""
    - **AES (Agent Effectiveness Score)**: Weighted score combining Sentiment (25%), Compliance (30%), Resolution (30%), and Quality (15%)
    - **ACI (Agent Consistency Index)**: Measures performance stability using inverted coefficient of variation (100 - CV×100)
    - **FCR (First Contact Resolution)**: Calls resolved fully without callback or escalation
    - **EPR (Escalation Prevention Rate)**: % of calls not escalated to higher authority
    - **TRE (Topic Resolution Efficiency)**: AHT vs benchmark comparison per topic
    """)
    
    st.markdown("---")
    st.info("📘 **Version 2.0** | Professional UI/UX Edition | All data synthetic, zero API costs")
