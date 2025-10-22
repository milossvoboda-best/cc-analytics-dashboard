"""
Widget 5: First Contact Resolution (FCR) Analysis
Layout: 2 gauges (Predicted vs Validated) + insights
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Tuple


COLORS = {
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'neutral': '#6B7280',
}


def calculate_fcr_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculates both FCR metrics.
    
    FCR Predicted: From call analysis (resolution_achieved == 'full')
    FCR Validated: No callback within 48h (callback_needed == False)
    
    Returns:
        Dict with both FCR values and gap analysis
    """
    
    # FCR Predicted (from agent/analysis assessment)
    fcr_predicted = (df['resolution'].apply(
        lambda x: x['resolution_achieved'] == 'full'
    ).sum() / len(df) * 100)
    
    # FCR Validated (no callback needed)
    fcr_validated = (df['resolution'].apply(
        lambda x: not x.get('callback_needed', True)
    ).sum() / len(df) * 100)
    
    # Combined FCR (average of both)
    combined_fcr = (fcr_predicted + fcr_validated) / 2
    
    # Gap analysis
    gap = combined_fcr - 75.0  # Target is 75%
    
    return {
        'fcr_predicted': round(fcr_predicted, 1),
        'fcr_validated': round(fcr_validated, 1),
        'combined_fcr': round(combined_fcr, 1),
        'gap': round(gap, 1),
        'total_calls': len(df)
    }


def get_fcr_insights(metrics: Dict, df: pd.DataFrame) -> str:
    """
    Generates actionable insights based on FCR metrics.
    
    Returns:
        HTML string with insights and recommendations
    """
    
    # Check for discrepancy between predicted and validated
    discrepancy = abs(metrics['fcr_predicted'] - metrics['fcr_validated'])
    
    if discrepancy > 10:
        if metrics['fcr_predicted'] > metrics['fcr_validated']:
            insight = "⚠️ Predicted FCR higher than validated - agents may be over-optimistic. Customers calling back despite 'resolved' status."
        else:
            insight = "ℹ️ Validated FCR higher than predicted - agents may be conservative in assessments."
    else:
        insight = "✅ Metrics are aligned - good calibration between agent assessment and actual outcomes."
    
    # Find top issues (topics with low FCR)
    topic_fcr = df.groupby(
        df['resolution'].apply(lambda x: x.get('issue_category', 'Unknown'))
    ).apply(
        lambda g: (g['resolution'].apply(lambda x: x['resolution_achieved'] == 'full').sum() / len(g) * 100)
    ).sort_values()
    
    if len(topic_fcr) > 0:
        worst_topic = topic_fcr.index[0]
        worst_fcr = topic_fcr.iloc[0]
        worst_count = len(df[df['resolution'].apply(lambda x: x.get('issue_category') == worst_topic)])
        
        action = f"→ Action: Review <b>{worst_topic}</b> knowledge base ({worst_fcr:.0f}% FCR, {worst_count} calls)"
    else:
        action = "→ Continue monitoring"
    
    html = f"""
    <div style='background-color: #F9FAFB; padding: 15px; border-radius: 6px; border-left: 4px solid #3B82F6; margin-top: 15px;'>
        <div style='font-size: 14px; font-weight: 600; color: #1E3A8A; margin-bottom: 10px;'>
            💡 Insight:
        </div>
        <div style='font-size: 13px; color: #374151; line-height: 1.6;'>
            {insight}<br><br>
            <b>Top Issue:</b><br>
            {action}
        </div>
    </div>
    """
    
    return html


def create_fcr_gauges(df: pd.DataFrame, target: float = 75.0) -> go.Figure:
    """
    Creates dual gauge chart for FCR analysis.
    
    Args:
        df: Filtered calls DataFrame
        target: Target FCR percentage
        
    Returns:
        Plotly Figure with 2 gauges
    """
    
    metrics = calculate_fcr_metrics(df)
    
    # Create subplot with 2 gauges
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=('FCR (Predicted)', 'FCR (Validated)'),
        horizontal_spacing=0.15
    )
    
    # Define gauge color based on value
    def get_gauge_color(value):
        if value >= 75:
            return COLORS['success']
        elif value >= 60:
            return COLORS['warning']
        else:
            return COLORS['danger']
    
    # LEFT: FCR Predicted
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics['fcr_predicted'],
        number={'suffix': '%', 'font': {'size': 32}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': get_gauge_color(metrics['fcr_predicted']), 'thickness': 0.75},
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [60, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ],
            'threshold': {
                'line': {'color': COLORS['neutral'], 'width': 3},
                'thickness': 0.8,
                'value': target
            }
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ), row=1, col=1)
    
    # RIGHT: FCR Validated
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics['fcr_validated'],
        number={'suffix': '%', 'font': {'size': 32}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': get_gauge_color(metrics['fcr_validated']), 'thickness': 0.75},
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [60, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ],
            'threshold': {
                'line': {'color': COLORS['neutral'], 'width': 3},
                'thickness': 0.8,
                'value': target
            }
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ), row=1, col=2)
    
    # Add annotations for labels
    fig.add_annotation(
        text="From call analysis",
        xref="x domain", yref="y domain",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=11, color=COLORS['neutral']),
        xanchor='center'
    )
    
    fig.add_annotation(
        text="No callback within 48h",
        xref="x2 domain", yref="y2 domain",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=11, color=COLORS['neutral']),
        xanchor='center'
    )
    
    # Update layout
    fig.update_layout(
        height=280,
        margin=dict(l=40, r=40, t=60, b=60),
        paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        title=dict(
            text="First Contact Resolution (FCR)",
            font=dict(size=16, family='Inter', weight=600),
            x=0.5,
            xanchor='center'
        )
    )
    
    return fig


def create_fcr_summary_html(df: pd.DataFrame, target: float = 75.0) -> str:
    """
    Creates HTML summary for FCR metrics.
    
    Returns:
        HTML string with combined FCR and gap analysis
    """
    
    metrics = calculate_fcr_metrics(df)
    
    gap_color = COLORS['success'] if metrics['gap'] >= 0 else COLORS['danger']
    gap_icon = "✅" if metrics['gap'] >= 0 else "🔴"
    
    html = f"""
    <div style='background-color: white; padding: 15px; border-radius: 6px; text-align: center;'>
        <div style='font-size: 13px; color: #6B7280; margin-bottom: 8px;'>
            Combined FCR:
        </div>
        <div style='font-size: 28px; font-weight: 700; color: #1E3A8A; margin-bottom: 8px;'>
            {metrics['combined_fcr']:.1f}%
        </div>
        <div style='font-size: 12px; color: #6B7280; margin-bottom: 5px;'>
            Target: {target}%
        </div>
        <div style='font-size: 14px; font-weight: 600; color: {gap_color};'>
            {gap_icon} Gap: {metrics['gap']:+.1f}%
        </div>
    </div>
    """
    
    return html
