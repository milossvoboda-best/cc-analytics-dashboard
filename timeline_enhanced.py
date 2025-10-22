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
    Creates simple Gantt-style timeline with sentiment background gradient.
    
    Args:
        segments: [{speaker, text, start_time, end_time}, ...]
        compliance_checkpoints: [{time, type, passed, description}, ...]
        sentiment_points: [{time, sentiment, label}, ...] - typically 3 points
        wpm_data: {
            'agent': [{time, wpm}, ...],
            'customer': [{time, wpm}, ...]
        }
        silence_periods: [{start, end, type}, ...]
        call_duration: Total call length in seconds
        
    Returns:
        Plotly Figure with 2 subplots
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
    
    # First: Add sentiment gradient as BACKGROUND
    if len(sentiment_points) >= 2:
        times = [p['time'] for p in sentiment_points]
        sentiments = [p['sentiment'] for p in sentiment_points]
        
        # Interpolate sentiment for smooth gradient
        smooth_times = np.linspace(times[0], times[-1], 100)
        if len(sentiment_points) >= 3:
            coeffs = np.polyfit(times, sentiments, 2)
            smooth_sentiments = np.polyval(coeffs, smooth_times)
        else:
            smooth_sentiments = np.interp(smooth_times, times, sentiments)
        
        # Add sentiment background as colored rectangles
        for i in range(len(smooth_times) - 1):
            t_start = smooth_times[i]
            t_end = smooth_times[i + 1]
            s_avg = (smooth_sentiments[i] + smooth_sentiments[i + 1]) / 2
            
            # Determine color
            if s_avg >= 0.3:
                bg_color = 'rgba(0, 200, 83, 0.15)'  # Green
            elif s_avg >= 0:
                bg_color = 'rgba(100, 221, 23, 0.15)'  # Light green
            elif s_avg >= -0.3:
                bg_color = 'rgba(255, 167, 38, 0.15)'  # Orange
            else:
                bg_color = 'rgba(239, 83, 80, 0.15)'  # Red
            
            fig.add_shape(
                type="rect",
                x0=t_start, x1=t_end,
                y0=-0.4, y1=1.4,
                line=dict(width=0),
                fillcolor=bg_color,
                layer="below",
                row=1, col=1
            )
    
    # Second: Add speaker segments (Gantt bars)
    for seg in segments:
        y_pos = 1 if seg["speaker"] == "AGENT" else 0
        color = COLORS["agent"] if seg["speaker"] == "AGENT" else COLORS["customer"]
        duration = seg["end_time"] - seg["start_time"]
        
        # Truncate text for hover
        text_preview = seg.get('text', '')[:200] + ('...' if len(seg.get('text', '')) > 200 else '')
        
        fig.add_trace(go.Bar(
            x=[duration],
            y=[y_pos],
            base=[seg["start_time"]],
            orientation='h',
            name=seg["speaker"],
            marker=dict(color=color, opacity=0.9, line=dict(width=0.5, color='white')),
            hovertext=f"<b>{seg['speaker']}</b><br>{text_preview}<br>Time: {seg['start_time']:.1f}s - {seg['end_time']:.1f}s",
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
    
    # Add compliance checkpoints AS TIMESTAMPS (vertical lines with labels)
    for checkpoint in compliance_checkpoints:
        icon = '✅' if checkpoint['passed'] else '❌'
        color = COLORS['excellent'] if checkpoint['passed'] else COLORS['critical']
        
        # Vertical line
        fig.add_shape(
            type="line",
            x0=checkpoint['time'], x1=checkpoint['time'],
            y0=-0.3, y1=1.3,
            line=dict(color=color, width=2, dash='dot'),
            row=1, col=1
        )
        
        # Label at bottom
        fig.add_annotation(
            x=checkpoint['time'],
            y=-0.35,
            text=f"{icon} {checkpoint['type']}",
            showarrow=False,
            font=dict(size=10, color=color, family='Inter'),
            textangle=-45,
            xanchor='right',
            yanchor='top',
            row=1, col=1
        )
    
    # ============================================================================
    # ROW 2: SPEAKING RATE (WPM) with zones
    # ============================================================================
    
    # Add WPM reference zones (background rectangles)
    # Slow zone (<100 WPM)
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
    
    # Normal zone (100-160 WPM) - no background
    
    # Fast zone (160-200 WPM)
    fig.add_shape(
        type="rect",
        x0=0, x1=call_duration,
        y0=160, y1=200,
        line=dict(width=0),
        fillcolor='yellow',
        opacity=0.1,
        layer="below",
        row=2, col=1
    )
    
    # Too fast zone (>200 WPM)
    fig.add_shape(
        type="rect",
        x0=0, x1=call_duration,
        y0=200, y1=250,
        line=dict(width=0),
        fillcolor='red',
        opacity=0.1,
        layer="below",
        row=2, col=1
    )
    
    # Add reference lines
    for threshold, label in [(100, 'Slow'), (160, 'Fast'), (200, 'Too Fast')]:
        fig.add_shape(
            type="line",
            x0=0, x1=call_duration,
            y0=threshold, y1=threshold,
            line=dict(color=COLORS['neutral'], width=1, dash='dash'),
            row=2, col=1
        )
    
    # Plot agent WPM line
    if wpm_data.get('agent'):
        agent_df = pd.DataFrame(wpm_data['agent'])
        fig.add_trace(go.Scatter(
            x=agent_df['time'],
            y=agent_df['wpm'],
            mode='lines+markers',
            name='Agent WPM',
            line=dict(color=COLORS['agent'], width=2),
            marker=dict(size=5),
            hovertemplate='Agent: %{y:.0f} WPM<br>Time: %{x:.1f}s<extra></extra>'
        ), row=2, col=1)
    
    # Plot customer WPM line
    if wpm_data.get('customer'):
        customer_df = pd.DataFrame(wpm_data['customer'])
        fig.add_trace(go.Scatter(
            x=customer_df['time'],
            y=customer_df['wpm'],
            mode='lines+markers',
            name='Customer WPM',
            line=dict(color=COLORS['customer'], width=2),
            marker=dict(size=5),
            hovertemplate='Customer: %{y:.0f} WPM<br>Time: %{x:.1f}s<extra></extra>'
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
