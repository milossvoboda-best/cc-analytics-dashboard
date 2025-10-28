"""
Enhanced Call Timeline Widget - 3-Layer Visualization
Multi-layer timeline with compliance checkpoints, WPM analysis, and sentiment flow
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


# Color scheme
COLORS = {
    'excellent': '#00C853',
    'good': '#64DD17',
    'warning': '#FFA726',
    'critical': '#EF5350',
    'neutral': '#9E9E9E',
    'agent': '#2196F3',
    'customer': '#FF9800',
}


def create_enhanced_timeline(
    segments: List[Dict],
    compliance_checkpoints: List[Dict],
    sentiment_points: List[Dict],
    wpm_data: Dict,
    silence_periods: List[Dict],
    call_duration: float
) -> go.Figure:
    """
    Creates comprehensive call timeline visualization for QA analysts.

    Features:
    - ROW 1: Speaker blocks (Gantt-style) showing when agent/customer speaks
      * Hover over blocks to see transcript text
      * Sentiment gradient background (red→yellow→green) shows customer mood evolution
      * Compliance checkpoints marked at actual occurrence times
      * Pause/hold periods highlighted

    - ROW 2: Speaking rate (WPM) analysis
      * Separate lines for agent and customer speech speed
      * Quality zones (slow/normal/fast/too fast)
      * Real WPM calculated per segment

    Args:
        segments: [{speaker, text, start_time, end_time, word_count}, ...]
        compliance_checkpoints: [{time, type, passed, description}, ...] - at real times
        sentiment_points: [{time, sentiment, label}, ...] - typically 3 points (start/mid/end)
        wpm_data: {
            'agent': [{time, wpm}, ...] - calculated per segment,
            'customer': [{time, wpm}, ...] - calculated per segment
        }
        silence_periods: [{start, end, type}, ...] - pause (3-10s) or hold (>10s)
        call_duration: Total call length in seconds

    Returns:
        Plotly Figure with 2 subplots for complete call analysis
    """
    
    # Create subplot with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        row_heights=[0.6, 0.4],
        subplot_titles=('📞 Call Timeline with Compliance Checkpoints', '🗣️ Speaking Rate (WPM)'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # ============================================================================
    # ROW 1: SPEAKER TIMELINE (Gantt-style) + SENTIMENT BACKGROUND GRADIENT
    # ============================================================================

    # First: Add sentiment gradient as BACKGROUND (Red -> Yellow -> Green transition)
    # This shows customer sentiment evolution throughout the call
    if len(sentiment_points) >= 2:
        times = [p['time'] for p in sentiment_points]
        sentiments = [p['sentiment'] for p in sentiment_points]

        # Interpolate sentiment for smooth gradient
        smooth_times = np.linspace(times[0], times[-1], 50)
        if len(sentiment_points) >= 3:
            coeffs = np.polyfit(times, sentiments, 2)
            smooth_sentiments = np.polyval(coeffs, smooth_times)
        else:
            smooth_sentiments = np.interp(smooth_times, times, sentiments)

        # Add sentiment background as colored rectangles with STRONGER opacity
        for i in range(len(smooth_times) - 1):
            t_start = smooth_times[i]
            t_end = smooth_times[i + 1]
            s_avg = (smooth_sentiments[i] + smooth_sentiments[i + 1]) / 2

            # Map sentiment (-1 to +1) to color with MORE VISIBLE opacity
            # Red (negative) -> Yellow (neutral) -> Green (positive)
            if s_avg >= 0.5:
                bg_color = 'rgba(0, 200, 83, 0.35)'  # Strong Green
            elif s_avg >= 0.2:
                bg_color = 'rgba(100, 221, 23, 0.30)'  # Light green
            elif s_avg >= -0.2:
                bg_color = 'rgba(255, 235, 59, 0.25)'  # Yellow (neutral)
            elif s_avg >= -0.5:
                bg_color = 'rgba(255, 167, 38, 0.30)'  # Orange
            else:
                bg_color = 'rgba(239, 83, 80, 0.35)'  # Strong Red

            fig.add_shape(
                type="rect",
                x0=t_start, x1=t_end,
                y0=-0.4, y1=1.4,
                line=dict(width=0),
                fillcolor=bg_color,
                layer="below",
                row=1, col=1
            )
    
    # Second: Add speaker segments (Gantt bars with transcript text on hover)
    # Each bar represents when agent or customer is speaking
    for seg in segments:
        y_pos = 1 if seg["speaker"] == "AGENT" else 0
        color = COLORS["agent"] if seg["speaker"] == "AGENT" else COLORS["customer"]
        duration = seg["end_time"] - seg["start_time"]

        # Truncate text for hover - shows transcript when hovering
        text_preview = seg.get('text', '')[:300] + ('...' if len(seg.get('text', '')) > 300 else '')

        fig.add_trace(go.Bar(
            x=[duration],
            y=[y_pos],
            base=[seg["start_time"]],
            orientation='h',
            name=seg["speaker"],
            marker=dict(color=color, opacity=0.85, line=dict(width=0.5, color='white')),
            hovertext=f"<b>{seg['speaker']}</b><br>{text_preview}<br>⏱️ {seg['start_time']:.1f}s - {seg['end_time']:.1f}s ({duration:.1f}s)",
            hovertemplate='%{hovertext}<extra></extra>',
            showlegend=False
        ), row=1, col=1)
    
    # Add pause/hold overlays
    for period in silence_periods:
        if period["type"] == "hold":
            # Hold periods as red vertical bars
            fig.add_shape(
                type="rect",
                x0=period["start"], x1=period["end"],
                y0=-0.3, y1=1.3,
                line=dict(width=0),
                fillcolor=COLORS["critical"],
                opacity=0.3,
                layer="above",
                row=1, col=1
            )
        elif period["type"] == "pause":
            # Pause as light gray
            fig.add_shape(
                type="rect",
                x0=period["start"], x1=period["end"],
                y0=-0.3, y1=1.3,
                line=dict(width=0),
                fillcolor=COLORS["neutral"],
                opacity=0.15,
                layer="below",
                row=1, col=1
            )
    
    # Add compliance checkpoints AS TIMESTAMPS (vertical lines at real occurrence times)
    # These show when AI detected compliance events (greeting, verification, etc.)
    for checkpoint in compliance_checkpoints:
        icon = '✅' if checkpoint['passed'] else '❌'
        color = COLORS['excellent'] if checkpoint['passed'] else COLORS['critical']

        # Vertical line marking the exact time
        fig.add_shape(
            type="line",
            x0=checkpoint['time'], x1=checkpoint['time'],
            y0=-0.4, y1=1.4,
            line=dict(color=color, width=3, dash='dot'),
            row=1, col=1
        )

        # Label at bottom with tooltip info
        fig.add_annotation(
            x=checkpoint['time'],
            y=-0.42,
            text=f"<b>{icon} {checkpoint['type']}</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=color,
            ax=0,
            ay=-30,
            font=dict(size=10, color=color, family='Inter'),
            bgcolor='white',
            bordercolor=color,
            borderwidth=1,
            borderpad=3,
            xanchor='center',
            yanchor='top',
            row=1, col=1
        )
    
    # ============================================================================
    # ROW 2: SPEAKING RATE (WPM - Words Per Minute) with quality zones
    # ============================================================================
    # Two separate lines show agent and customer speech speed throughout the call
    # Helps QA analysts identify rushed/slow speech patterns

    # Add WPM reference zones (background rectangles)
    # Slow zone (<100 WPM) - may indicate lack of confidence or hesitation
    fig.add_shape(
        type="rect",
        x0=0, x1=call_duration,
        y0=0, y1=100,
        line=dict(width=0),
        fillcolor='lightblue',
        opacity=0.15,
        layer="below",
        row=2, col=1
    )

    # Normal zone (100-160 WPM) - ideal speaking rate, no background

    # Fast zone (160-200 WPM) - may indicate rushing
    fig.add_shape(
        type="rect",
        x0=0, x1=call_duration,
        y0=160, y1=200,
        line=dict(width=0),
        fillcolor='yellow',
        opacity=0.12,
        layer="below",
        row=2, col=1
    )

    # Too fast zone (>200 WPM) - difficult for customer to follow
    fig.add_shape(
        type="rect",
        x0=0, x1=call_duration,
        y0=200, y1=250,
        line=dict(width=0),
        fillcolor='red',
        opacity=0.12,
        layer="below",
        row=2, col=1
    )

    # Add reference lines with thresholds
    for threshold, label in [(100, 'Slow'), (160, 'Fast'), (200, 'Too Fast')]:
        fig.add_shape(
            type="line",
            x0=0, x1=call_duration,
            y0=threshold, y1=threshold,
            line=dict(color=COLORS['neutral'], width=1, dash='dash'),
            row=2, col=1
        )

    # Plot agent WPM line - calculated per segment
    if wpm_data.get('agent') and len(wpm_data['agent']) > 0:
        agent_df = pd.DataFrame(wpm_data['agent'])
        fig.add_trace(go.Scatter(
            x=agent_df['time'],
            y=agent_df['wpm'],
            mode='lines+markers',
            name='🎧 Agent WPM',
            line=dict(color=COLORS['agent'], width=3),
            marker=dict(size=6, symbol='circle'),
            hovertemplate='<b>Agent</b><br>%{y:.0f} WPM<br>Time: %{x:.1f}s<extra></extra>'
        ), row=2, col=1)

    # Plot customer WPM line - calculated per segment
    if wpm_data.get('customer') and len(wpm_data['customer']) > 0:
        customer_df = pd.DataFrame(wpm_data['customer'])
        fig.add_trace(go.Scatter(
            x=customer_df['time'],
            y=customer_df['wpm'],
            mode='lines+markers',
            name='👤 Customer WPM',
            line=dict(color=COLORS['customer'], width=3),
            marker=dict(size=6, symbol='square'),
            hovertemplate='<b>Customer</b><br>%{y:.0f} WPM<br>Time: %{x:.1f}s<extra></extra>'
        ), row=2, col=1)
    
    
    # ============================================================================
    # LAYOUT CONFIGURATION
    # ============================================================================
    
    # Update axes
    fig.update_xaxes(
        showgrid=True,
        gridcolor='#e5e7eb',
        title_text='Time (seconds)',
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text='',
        tickvals=[0, 1],
        ticktext=['CUSTOMER', 'AGENT'],
        range=[-0.5, 1.5],
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text='WPM',
        range=[50, 250],
        row=2, col=1
    )
    
    # Overall layout
    fig.update_layout(
        height=550,
        margin=dict(l=80, r=40, t=80, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest',
        font=dict(family='Inter', size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def calculate_timeline_stats(
    segments: List[Dict],
    silence_periods: List[Dict],
    wpm_data: Dict,
    sentiment_points: List[Dict]
) -> Dict:
    """
    Calculates summary statistics for timeline.
    
    Returns:
        Dict with summary stats for display below timeline
    """
    
    # Pause/Hold stats
    pause_count = sum(1 for p in silence_periods if p['type'] == 'pause')
    hold_count = sum(1 for p in silence_periods if p['type'] == 'hold')
    pause_total = sum(p['end'] - p['start'] for p in silence_periods if p['type'] == 'pause')
    hold_total = sum(p['end'] - p['start'] for p in silence_periods if p['type'] == 'hold')
    
    # WPM stats
    agent_wpm_values = [p['wpm'] for p in wpm_data.get('agent', [])]
    customer_wpm_values = [p['wpm'] for p in wpm_data.get('customer', [])]
    
    agent_wpm_avg = np.mean(agent_wpm_values) if agent_wpm_values else 0
    agent_wpm_peak = max(agent_wpm_values) if agent_wpm_values else 0
    customer_wpm_avg = np.mean(customer_wpm_values) if customer_wpm_values else 0
    customer_wpm_peak = max(customer_wpm_values) if customer_wpm_values else 0
    
    # Sentiment delta
    if len(sentiment_points) >= 2:
        sentiment_start = sentiment_points[0]['sentiment']
        sentiment_end = sentiment_points[-1]['sentiment']
        sentiment_delta = sentiment_end - sentiment_start
    else:
        sentiment_delta = 0
    
    return {
        'pause_count': pause_count,
        'hold_count': hold_count,
        'pause_total': pause_total,
        'hold_total': hold_total,
        'agent_wpm_avg': agent_wpm_avg,
        'agent_wpm_peak': agent_wpm_peak,
        'customer_wpm_avg': customer_wpm_avg,
        'customer_wpm_peak': customer_wpm_peak,
        'sentiment_delta': sentiment_delta
    }
