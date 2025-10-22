"""
7-Day Quality Breakdown Trend Widget
Two-part visualization: Line chart (AES) + Stacked bars (components)
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


COLORS = {
    'sentiment': '#1f77b4',
    'compliance': '#ff7f0e',
    'resolution': '#2ca02c',
    'quality': '#d62728',
    'aes_line': '#1e3a5f',
    'target': '#9E9E9E',
}


def create_quality_trend_redesigned(df: pd.DataFrame, target: float = 75.0) -> go.Figure:
    """
    Creates two-part quality breakdown visualization.
    
    TOP: Overall AES Trend (Line chart)
    BOTTOM: Component Breakdown (Stacked bar chart)
    
    Args:
        df: DataFrame with call data (must have date, aes, components)
        target: Target AES benchmark
        
    Returns:
        Plotly Figure with 2 subplots
    """
    
    # Prepare daily aggregated data
    daily_data = prepare_7day_data(df)
    
    if len(daily_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data (need at least 1 day of data)",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#64748b')
        )
        fig.update_layout(height=450, margin=dict(l=40, r=20, t=40, b=40))
        return fig
    
    # Create subplot: 2 rows, 1 column
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.4, 0.6],
        vertical_spacing=0.15,
        subplot_titles=('Overall AES Trend', 'Component Breakdown (% of Total AES)')
    )
    
    # ============================================================================
    # TOP: AES TREND LINE
    # ============================================================================
    
    # Add AES line
    fig.add_trace(go.Scatter(
        x=daily_data['date_str'],
        y=daily_data['aes'],
        mode='lines+markers',
        name='AES',
        line=dict(color=COLORS['aes_line'], width=3),
        marker=dict(size=8, color=COLORS['aes_line']),
        hovertemplate='%{x}<br>AES: %{y:.1f}%<extra></extra>'
    ), row=1, col=1)
    
    # Add target line
    fig.add_trace(go.Scatter(
        x=daily_data['date_str'],
        y=[target] * len(daily_data),
        mode='lines',
        name=f'Target ({target}%)',
        line=dict(color=COLORS['target'], width=2, dash='dash'),
        hovertemplate=f'Target: {target}%<extra></extra>'
    ), row=1, col=1)
    
    # Calculate trend
    if len(daily_data) >= 2:
        first_aes = daily_data['aes'].iloc[0]
        last_aes = daily_data['aes'].iloc[-1]
        pct_change = ((last_aes - first_aes) / first_aes) * 100
        trend_arrow = '⬆️' if pct_change > 0 else '⬇️'
        trend_text = f'{trend_arrow} {abs(pct_change):.1f}% vs {len(daily_data)} days ago'
        trend_color = '#00C853' if pct_change > 0 else '#EF5350'
        
        # Add trend annotation
        fig.add_annotation(
            x=0.5, y=1.15,
            xref='x domain', yref='y domain',
            text=trend_text,
            showarrow=False,
            font=dict(size=12, color=trend_color, family='Inter'),
            xanchor='center',
            row=1, col=1
        )
    
    # ============================================================================
    # BOTTOM: COMPONENT STACKED BARS
    # ============================================================================
    
    components = [
        ('Sentiment', 'sentiment_component', COLORS['sentiment']),
        ('Compliance', 'compliance_component', COLORS['compliance']),
        ('Resolution', 'resolution_component', COLORS['resolution']),
        ('Quality', 'quality_component', COLORS['quality'])
    ]
    
    for name, col, color in components:
        fig.add_trace(go.Bar(
            x=daily_data['date_str'],
            y=daily_data[col],
            name=name,
            marker=dict(color=color),
            hovertemplate=f'{name}: %{{y:.1f}} points<extra></extra>',
            width=0.6
        ), row=2, col=1)
    
    # Update layout
    fig.update_xaxes(
        showgrid=True,
        gridcolor='#e5e7eb',
        title_text='Date',
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text='AES Score (%)',
        range=[0, 100],
        showgrid=True,
        gridcolor='#e5e7eb',
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text='Component Score',
        range=[0, 100],
        showgrid=True,
        gridcolor='#e5e7eb',
        row=2, col=1
    )
    
    # Overall layout
    fig.update_layout(
        height=500,
        margin=dict(l=60, r=40, t=60, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        font=dict(family='Inter', size=12),
        hovermode='x unified'
    )
    
    return fig


def prepare_7day_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares 7-day aggregated data with AES and component breakdown.
    
    Args:
        df: Raw calls dataframe
        
    Returns:
        DataFrame with daily aggregates
    """
    
    # Ensure we have date column
    if 'date' not in df.columns:
        # Generate mock dates for last 7 days
        today = datetime.now()
        dates = [(today - timedelta(days=6-i)).date() for i in range(7)]
        df = df.copy()
        df['date'] = np.random.choice(dates, size=len(df))
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Calculate component scores per call
    df['sentiment_component'] = ((df["sentiment_end"] - df["sentiment_start"] + 2) / 4 * 100) * 0.25
    df['compliance_component'] = df["comp_result"].apply(lambda x: x["score"]) * 0.30
    df['resolution_component'] = df["resolution"].apply(
        lambda x: 100 if x["resolution_achieved"] == "full" else (50 if x["resolution_achieved"] == "partial" else 0)
    ) * 0.30
    df['quality_component'] = df["quality_score"] * 0.15
    
    # Group by date
    daily = df.groupby('date').agg({
        'aes': 'mean',
        'sentiment_component': 'mean',
        'compliance_component': 'mean',
        'resolution_component': 'mean',
        'quality_component': 'mean'
    }).reset_index()
    
    # Sort by date
    daily = daily.sort_values('date')
    
    # Format date for display
    daily['date_str'] = pd.to_datetime(daily['date']).dt.strftime('%b %d')
    
    return daily
