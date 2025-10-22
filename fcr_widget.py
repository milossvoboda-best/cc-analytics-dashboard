"""
FCR (First Contact Resolution) Widget - Dual Display
Shows FCR from two perspectives: Agent notes vs Computed data
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict


COLORS = {
    'excellent': '#00C853',
    'good': '#64DD17',
    'warning': '#FFA726',
    'critical': '#EF5350',
}


def create_fcr_dual_gauge(fcr_agent: float, fcr_computed: float) -> go.Figure:
    """
    Creates dual gauge chart for FCR comparison.
    
    Args:
        fcr_agent: FCR % from agent notes
        fcr_computed: FCR % computed from data (no callback within 48h)
        
    Returns:
        Plotly Figure with 2 gauge charts side-by-side
    """
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=('FCR (Agent Notes)', 'FCR (Computed - No Callback 48h)')
    )
    
    # LEFT: FCR from agent notes
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=fcr_agent,
        delta={'reference': 70, 'increasing': {'color': COLORS['excellent']}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': get_fcr_color(fcr_agent)},
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 83, 80, 0.1)'},
                {'range': [50, 70], 'color': 'rgba(255, 167, 38, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(0, 200, 83, 0.1)'}
            ],
            'threshold': {
                'line': {'color': COLORS['critical'], 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        },
        number={'suffix': '%', 'font': {'size': 40}},
        title={'text': 'Based on resolution annotations', 'font': {'size': 14}}
    ), row=1, col=1)
    
    # RIGHT: FCR computed
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=fcr_computed,
        delta={'reference': 70, 'increasing': {'color': COLORS['excellent']}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': get_fcr_color(fcr_computed)},
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 83, 80, 0.1)'},
                {'range': [50, 70], 'color': 'rgba(255, 167, 38, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(0, 200, 83, 0.1)'}
            ],
            'threshold': {
                'line': {'color': COLORS['critical'], 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        },
        number={'suffix': '%', 'font': {'size': 40}},
        title={'text': 'No repeat contact within 48 hours', 'font': {'size': 14}}
    ), row=1, col=2)
    
    fig.update_layout(
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor='white',
        font=dict(family='Inter', size=12)
    )
    
    return fig


def get_fcr_color(fcr_value: float) -> str:
    """Returns color based on FCR value."""
    if fcr_value >= 80:
        return COLORS['excellent']
    elif fcr_value >= 70:
        return COLORS['good']
    elif fcr_value >= 50:
        return COLORS['warning']
    else:
        return COLORS['critical']


def get_fcr_insights(fcr_agent: float, fcr_computed: float) -> Dict:
    """
    Analyzes FCR metrics and provides insights.
    
    Returns:
        Dict with insights and recommendations
    """
    
    delta = fcr_agent - fcr_computed
    
    if abs(delta) <= 5:
        alignment = '✅ ALIGNED'
        insight = 'Agent assessments match computed data. Good calibration.'
        color = COLORS['excellent']
    elif delta > 5:
        alignment = '⚠️ OVER-REPORTING'
        insight = f'Agents reporting {abs(delta):.1f}% higher FCR than actual. Review resolution criteria.'
        color = COLORS['warning']
    else:
        alignment = '⚠️ UNDER-REPORTING'
        insight = f'Agents reporting {abs(delta):.1f}% lower FCR than actual. Possible training gap.'
        color = COLORS['warning']
    
    # Overall status
    avg_fcr = (fcr_agent + fcr_computed) / 2
    
    if avg_fcr >= 80:
        status = '⭐ Excellent'
        recommendation = 'Maintain current practices. Share best practices across team.'
    elif avg_fcr >= 70:
        status = '✅ Good'
        recommendation = 'On track. Focus on consistency and reducing callbacks.'
    elif avg_fcr >= 50:
        status = '⚠️ Needs Improvement'
        recommendation = 'Review call handling procedures. Increase training on common issues.'
    else:
        status = '🔴 Critical'
        recommendation = 'Urgent action needed. Audit recent calls and identify root causes.'
    
    return {
        'alignment': alignment,
        'insight': insight,
        'color': color,
        'delta': delta,
        'status': status,
        'recommendation': recommendation,
        'avg_fcr': avg_fcr
    }
