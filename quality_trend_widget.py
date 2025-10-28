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
    'call_opening': '#1f77b4',
    'needs_assessment': '#ff7f0e',
    'problem_resolution': '#2ca02c',
    'professional_communication': '#d62728',
    'call_closing': '#9467bd',
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

    # QA Components as stacked bars - 5 hlavných QA hodnotení
    qa_components = [
        ("Otvorenie hovoru", "call_opening_pct", COLORS['call_opening']),
        ("Zisťovanie potrieb", "needs_assessment_pct", COLORS['needs_assessment']),
        ("Riešenie problému", "problem_resolution_pct", COLORS['problem_resolution']),
        ("Profesionálna komunikácia", "professional_communication_pct", COLORS['professional_communication']),
        ("Uzavretie hovoru", "call_closing_pct", COLORS['call_closing'])
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
        title="7-dňový trend QA kontrol",
        xaxis_title="Dátum",
        yaxis=dict(title="Úspešnosť QA komponentov (%)", range=[0, 100]),
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

    Extrahuje 5 hlavných QA hodnotení z quality objektu:
    1. Otvorenie hovoru (call_opening)
    2. Zisťovanie potrieb (needs_assessment)
    3. Riešenie problému (problem_resolution)
    4. Profesionálna komunikácia (professional_communication)
    5. Uzavretie hovoru (call_closing)

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

    # Extract QA components from quality field (5 hlavných hodnotení)
    df['call_opening'] = df['quality'].apply(lambda x: 1 if x.get('call_opening', False) else 0)
    df['needs_assessment'] = df['quality'].apply(lambda x: 1 if x.get('needs_assessment', False) else 0)
    df['problem_resolution'] = df['quality'].apply(lambda x: 1 if x.get('problem_resolution', False) else 0)
    df['professional_communication'] = df['quality'].apply(lambda x: 1 if x.get('professional_communication', False) else 0)
    df['call_closing'] = df['quality'].apply(lambda x: 1 if x.get('call_closing', False) else 0)

    # Group by date and calculate percentages
    daily = df.groupby('date').agg({
        'call_opening': 'mean',
        'needs_assessment': 'mean',
        'problem_resolution': 'mean',
        'professional_communication': 'mean',
        'call_closing': 'mean'
    }).reset_index()

    # Convert to percentages
    daily['call_opening_pct'] = daily['call_opening'] * 100
    daily['needs_assessment_pct'] = daily['needs_assessment'] * 100
    daily['problem_resolution_pct'] = daily['problem_resolution'] * 100
    daily['professional_communication_pct'] = daily['professional_communication'] * 100
    daily['call_closing_pct'] = daily['call_closing'] * 100

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
