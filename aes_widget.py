"""
AES Widget - Spider Chart + 7-Day Trend Visualization
Redesigned according to UX requirements
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta


COLORS = {
    'excellent': '#00C853',
    'good': '#64DD17',
    'warning': '#FFA726',
    'critical': '#EF5350',
    'neutral': '#9E9E9E',
}


def create_aes_spider_trend(
    current_components: Dict[str, float],
    trend_data: List[Dict],
    overall_aes: float,
    target: float = 75.0
) -> go.Figure:
    """
    Creates side-by-side Spider Chart + 7-Day Trend visualization.
    
    Args:
        current_components: {
            'Sentiment': 16.6,
            'Compliance': 27.1,
            'Resolution': 22.0,
            'Quality': 11.1
        }
        trend_data: [
            {'date': '2025-10-16', 'aes': 72.5},
            {'date': '2025-10-17', 'aes': 74.2},
            ...
        ]
        overall_aes: Current overall AES score (76.9)
        target: Target benchmark (default 75.0)
        
    Returns:
        Plotly Figure with 2 subplots
    """
    
    # Create subplot: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scatterpolar'}, {'type': 'scatter'}]],
        subplot_titles=('Current State', '7-Day Trend'),
        horizontal_spacing=0.15
    )
    
    # ============================================================================
    # LEFT: SPIDER/RADAR CHART (Current State)
    # ============================================================================
    
    # Component names and max values
    components = {
        'Sentiment': {'value': current_components.get('Sentiment', 0), 'max': 25},
        'Compliance': {'value': current_components.get('Compliance', 0), 'max': 30},
        'Resolution': {'value': current_components.get('Resolution', 0), 'max': 30},
        'Quality': {'value': current_components.get('Quality', 0), 'max': 15}
    }
    
    # Prepare data for radar chart
    categories = list(components.keys())
    values = [comp['value'] for comp in components.values()]
    max_values = [comp['max'] for comp in components.values()]
    
    # Close the polygon by repeating first value
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    max_values_closed = max_values + [max_values[0]]
    
    # Determine color based on overall AES
    if overall_aes >= 85:
        fill_color = COLORS['excellent']
        status = '⭐ Excellent'
    elif overall_aes >= 70:
        fill_color = COLORS['good']
        status = '✅ Good'
    elif overall_aes >= 50:
        fill_color = COLORS['warning']
        status = '⚠️ Needs Coaching'
    else:
        fill_color = COLORS['critical']
        status = '🔴 Urgent'
    
    # Add max reference (gray outline)
    fig.add_trace(go.Scatterpolar(
        r=max_values_closed,
        theta=categories_closed,
        fill=None,
        line=dict(color=COLORS['neutral'], width=1, dash='dash'),
        name='Max Possible',
        showlegend=True,
        hovertemplate='%{theta}<br>Max: %{r:.1f}<extra></extra>'
    ), row=1, col=1)
    
    # Add actual values (filled)
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor=f'rgba({int(fill_color[1:3], 16)}, {int(fill_color[3:5], 16)}, {int(fill_color[5:7], 16)}, 0.3)',
        line=dict(color=fill_color, width=3),
        name='Current',
        showlegend=True,
        hovertemplate='%{theta}<br>Current: %{r:.1f}<extra></extra>'
    ), row=1, col=1)
    
    # Update polar layout
    fig.update_polars(
        radialaxis=dict(
            visible=True,
            range=[0, max(max_values)],
            showticklabels=True,
            tickfont=dict(size=10),
            gridcolor='#e5e7eb'
        ),
        angularaxis=dict(
            tickfont=dict(size=12, family='Inter', color='#1e3a5f')
        ),
        row=1, col=1
    )
    
    # ============================================================================
    # RIGHT: 7-DAY TREND LINE CHART
    # ============================================================================
    
    if trend_data and len(trend_data) > 0:
        df_trend = pd.DataFrame(trend_data)
        
        # Sort by date
        df_trend['date'] = pd.to_datetime(df_trend['date'])
        df_trend = df_trend.sort_values('date')
        
        # Format dates
        df_trend['date_str'] = df_trend['date'].dt.strftime('%b %d')
        
        # Determine if improving or declining
        if len(df_trend) >= 2:
            first_value = df_trend['aes'].iloc[0]
            last_value = df_trend['aes'].iloc[-1]
            is_improving = last_value > first_value
            fill_color_trend = COLORS['excellent'] if is_improving else COLORS['critical']
        else:
            is_improving = True
            fill_color_trend = COLORS['neutral']
        
        # Add area fill (green if improving, red if declining)
        fig.add_trace(go.Scatter(
            x=df_trend['date_str'],
            y=df_trend['aes'],
            fill='tozeroy',
            fillcolor=f'rgba({int(fill_color_trend[1:3], 16)}, {int(fill_color_trend[3:5], 16)}, {int(fill_color_trend[5:7], 16)}, 0.2)',
            line=dict(color=fill_color_trend, width=3),
            mode='lines+markers',
            marker=dict(size=8, symbol='circle'),
            name='AES',
            showlegend=False,
            hovertemplate='Date: %{x}<br>AES: %{y:.1f}%<extra></extra>'
        ), row=1, col=2)
        
        # Add benchmark line
        fig.add_trace(go.Scatter(
            x=df_trend['date_str'],
            y=[target] * len(df_trend),
            mode='lines',
            line=dict(color=COLORS['neutral'], width=2, dash='dash'),
            name=f'Target ({target}%)',
            showlegend=True,
            hovertemplate=f'Target: {target}%<extra></extra>'
        ), row=1, col=2)
        
        # Calculate trend percentage
        if len(df_trend) >= 2:
            pct_change = ((last_value - first_value) / first_value) * 100
            trend_arrow = '⬆️' if pct_change > 0 else '⬇️'
            trend_text = f'{trend_arrow} {abs(pct_change):.1f}% vs 7 days ago'
        else:
            trend_text = 'Insufficient data'
        
        # Add trend annotation
        fig.add_annotation(
            x=0.5, y=1.1,
            xref='x2 domain', yref='y2 domain',
            text=trend_text,
            showarrow=False,
            font=dict(size=12, color=fill_color_trend, family='Inter'),
            xanchor='center'
        )
    
    # Update x-axis for trend chart
    fig.update_xaxes(
        title_text='Date',
        showgrid=True,
        gridcolor='#e5e7eb',
        row=1, col=2
    )
    
    # Update y-axis for trend chart
    fig.update_yaxes(
        title_text='AES Score',
        range=[0, 100],
        showgrid=True,
        gridcolor='#e5e7eb',
        row=1, col=2
    )
    
    # Overall layout
    fig.update_layout(
        height=400,
        margin=dict(l=40, r=40, t=80, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter', size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def get_aes_status_card(overall_aes: float, target: float = 75.0) -> Dict:
    """
    Returns status information for AES big number display.
    
    Args:
        overall_aes: Current overall AES score
        target: Target benchmark
        
    Returns:
        Dict with status info: {
            'score': 76.9,
            'delta': +1.9,
            'status': '✅ Good',
            'color': '#64DD17',
            'description': 'Performance is above target'
        }
    """
    
    delta = overall_aes - target
    
    if overall_aes >= 85:
        status = '⭐ Excellent'
        color = COLORS['excellent']
        description = 'Outstanding performance! Agents consistently exceed expectations.'
    elif overall_aes >= 70:
        status = '✅ Good'
        color = COLORS['good']
        description = 'Performance is solid and above target. Keep monitoring.'
    elif overall_aes >= 50:
        status = '⚠️ Needs Coaching'
        color = COLORS['warning']
        description = 'Performance below target. Review training materials and provide coaching.'
    else:
        status = '🔴 Urgent'
        color = COLORS['critical']
        description = 'Critical performance issues. Immediate intervention required.'
    
    return {
        'score': overall_aes,
        'delta': delta,
        'status': status,
        'color': color,
        'description': description
    }


def generate_mock_7day_trend(current_aes: float, variance: float = 3.0) -> List[Dict]:
    """
    Generates mock 7-day trend data for testing.
    
    Args:
        current_aes: Current AES score (will be the last day)
        variance: Max random variance per day
        
    Returns:
        List of {date, aes} dicts
    """
    from datetime import datetime, timedelta
    
    trend = []
    today = datetime.now()
    
    # Generate 7 days of data with slight variance
    for i in range(7):
        date = today - timedelta(days=6-i)
        # Gradual increase/decrease towards current_aes
        progress = i / 6
        base_value = current_aes - (1 - progress) * np.random.uniform(-5, 5)
        daily_aes = base_value + np.random.uniform(-variance, variance)
        daily_aes = max(0, min(100, daily_aes))  # Clamp to 0-100
        
        trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'aes': round(daily_aes, 1)
        })
    
    return trend
