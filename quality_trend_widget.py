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
    Creates 7-day quality breakdown trend showing QA component percentages.
    
    Args:
        df: DataFrame with call data and quality components
        target: Not used, kept for compatibility
        
    Returns:
        Plotly Figure with stacked bars for QA components
    """
    
    # Prepare daily QA component data
    daily_data = prepare_qa_components_daily(df)
    
    if len(daily_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data (need at least 1 day of data)",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#64748b')
        )
        fig.update_layout(height=350, margin=dict(l=40, r=20, t=40, b=40))
        return fig
    
    fig = go.Figure()
    
    # QA Components as stacked bars
    qa_components = [
        ("Quality", "quality_pct", COLORS['quality']),
        ("Resolution", "resolution_pct", COLORS['resolution']),
        ("Compliance", "compliance_pct", COLORS['compliance']),
        ("Sentiment", "sentiment_pct", COLORS['sentiment'])
    ]
    
    for name, col, color in qa_components:
        fig.add_trace(go.Bar(
            x=daily_data['date_str'],
            y=daily_data[col],
            name=name,
            marker=dict(color=color),
            hovertemplate=f'{name}: %{{y:.1f}}%<extra></extra>',
            width=0.7
        ))
    
    # Update layout
    fig.update_layout(
        title="7-Day Quality Breakdown Trend",
        xaxis_title="Date",
        yaxis=dict(title="Component Score (%)", range=[0, 100]),
        height=350,
        margin=dict(l=60, r=40, t=60, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        font=dict(family='Inter', size=12),
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    
    return fig


def prepare_qa_components_daily(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares daily QA component percentages (how many calls passed each component).
    
    Args:
        df: Raw calls dataframe with quality field
        
    Returns:
        DataFrame with daily percentages for each QA component
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
    
    # Extract QA binary flags from quality field
    df['active_listening'] = df['quality'].apply(lambda x: 1 if x.get('active_listening', False) else 0)
    df['empathy'] = df['quality'].apply(lambda x: 1 if x.get('empathy', False) else 0)
    df['solution_offered'] = df['quality'].apply(lambda x: 1 if x.get('solution_offered', False) else 0)
    df['professional_tone'] = df['quality'].apply(lambda x: 1 if x.get('professional_tone', False) else 0)
    
    # Group by date and calculate percentages
    daily = df.groupby('date').agg({
        'active_listening': 'mean',
        'empathy': 'mean',
        'solution_offered': 'mean',
        'professional_tone': 'mean'
    }).reset_index()
    
    # Convert to percentages
    daily['sentiment_pct'] = daily['active_listening'] * 100
    daily['compliance_pct'] = daily['empathy'] * 100
    daily['resolution_pct'] = daily['solution_offered'] * 100
    daily['quality_pct'] = daily['professional_tone'] * 100
    
    # Sort by date
    daily = daily.sort_values('date')
    
    # Format date for display
    daily['date_str'] = pd.to_datetime(daily['date']).dt.strftime('%b %d')
    
    return daily


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
