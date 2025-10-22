"""
Widget 6: Performance Trend (Switchable Line Chart)
Layout: 5 tabs (AES | AutoQA | FCR | Sentiment | AHT) with trend line
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


COLORS = {
    'AES': '#3B82F6',        # Blue
    'AutoQA': '#8B5CF6',     # Purple
    'FCR': '#10B981',        # Green
    'Sentiment': '#14B8A6',  # Teal
    'AHT': '#F59E0B',        # Amber
    'target': '#9CA3AF',     # Gray
}


def prepare_trend_data(df: pd.DataFrame, metric: str, days: int = 30) -> pd.DataFrame:
    """
    Prepares daily aggregated data for trend chart.
    
    Args:
        df: Calls DataFrame
        metric: One of 'AES', 'AutoQA', 'FCR', 'Sentiment', 'AHT'
        days: Number of days to include
        
    Returns:
        DataFrame with daily values
    """
    
    # Ensure date column
    if 'date' not in df.columns:
        df = df.copy()
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Filter to last N days
    end_date = df['date'].max()
    start_date = end_date - timedelta(days=days-1)
    df_filtered = df[df['date'] >= start_date].copy()
    
    # Calculate metric by day
    if metric == 'AES':
        # AES from components
        df_filtered['sentiment_score'] = ((df_filtered['sentiment_end'] - df_filtered['sentiment_start'] + 2) / 4 * 25)
        df_filtered['compliance_score'] = df_filtered['compliance'].apply(lambda x: sum(1 for k,v in x.items() if isinstance(v, bool) and v) / 9 * 30)
        df_filtered['resolution_score'] = df_filtered['resolution'].apply(lambda x: 30 if x['resolution_achieved']=='full' else (15 if x['resolution_achieved']=='partial' else 0))
        df_filtered['quality_score_scaled'] = df_filtered['quality'].apply(lambda x: x['quality_score'] / 100 * 15)
        df_filtered['aes_value'] = (df_filtered['sentiment_score'] + df_filtered['compliance_score'] + 
                                    df_filtered['resolution_score'] + df_filtered['quality_score_scaled'])
        daily = df_filtered.groupby('date')['aes_value'].mean().reset_index()
        daily.columns = ['date', 'value']
        
    elif metric == 'AutoQA':
        # AutoQA score
        daily = df_filtered.groupby('date')['autoqa_score'].mean().reset_index()
        daily.columns = ['date', 'value']
        
    elif metric == 'FCR':
        # FCR (full resolution achieved)
        df_filtered['fcr_value'] = df_filtered['resolution'].apply(lambda x: 100 if x['resolution_achieved']=='full' else 0)
        daily = df_filtered.groupby('date')['fcr_value'].mean().reset_index()
        daily.columns = ['date', 'value']
        
    elif metric == 'Sentiment':
        # Sentiment delta (end - start)
        df_filtered['sentiment_delta'] = df_filtered['sentiment_end'] - df_filtered['sentiment_start']
        df_filtered['sentiment_normalized'] = ((df_filtered['sentiment_delta'] + 2) / 4 * 100)  # Normalize to 0-100
        daily = df_filtered.groupby('date')['sentiment_normalized'].mean().reset_index()
        daily.columns = ['date', 'value']
        
    elif metric == 'AHT':
        # Average Handling Time (minutes)
        df_filtered['aht_minutes'] = df_filtered['duration_sec'] / 60
        daily = df_filtered.groupby('date')['aht_minutes'].mean().reset_index()
        daily.columns = ['date', 'value']
    
    # Sort by date
    daily = daily.sort_values('date')
    
    # Format date for display
    daily['date_str'] = pd.to_datetime(daily['date']).dt.strftime('%b %d')
    
    return daily


def calculate_trend_stats(daily_data: pd.DataFrame) -> Dict:
    """
    Calculates trend statistics (current, start, change, peak, low).
    
    Returns:
        Dict with trend stats
    """
    
    if len(daily_data) == 0:
        return {
            'current': 0,
            'start': 0,
            'change': 0,
            'change_pct': 0,
            'peak': 0,
            'peak_date': 'N/A',
            'low': 0,
            'low_date': 'N/A',
            'trend_arrow': '➡️'
        }
    
    current = daily_data['value'].iloc[-1]
    start = daily_data['value'].iloc[0]
    change = current - start
    change_pct = (change / start * 100) if start != 0 else 0
    
    peak_idx = daily_data['value'].idxmax()
    peak = daily_data.loc[peak_idx, 'value']
    peak_date = daily_data.loc[peak_idx, 'date_str']
    
    low_idx = daily_data['value'].idxmin()
    low = daily_data.loc[low_idx, 'value']
    low_date = daily_data.loc[low_idx, 'date_str']
    
    trend_arrow = '⬆️' if change > 0 else ('⬇️' if change < 0 else '➡️')
    
    return {
        'current': round(current, 1),
        'start': round(start, 1),
        'change': round(change, 1),
        'change_pct': round(change_pct, 1),
        'peak': round(peak, 1),
        'peak_date': peak_date,
        'low': round(low, 1),
        'low_date': low_date,
        'trend_arrow': trend_arrow
    }


def create_performance_trend(df: pd.DataFrame, metric: str = 'AES', target: float = None, days: int = 30) -> go.Figure:
    """
    Creates performance trend line chart for selected metric.
    
    Args:
        df: Calls DataFrame
        metric: One of 'AES', 'AutoQA', 'FCR', 'Sentiment', 'AHT'
        target: Target benchmark line (optional)
        days: Number of days to show
        
    Returns:
        Plotly Figure with line chart
    """
    
    # Prepare data
    daily_data = prepare_trend_data(df, metric, days)
    
    if len(daily_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#6B7280')
        )
        fig.update_layout(height=300)
        return fig
    
    # Get metric color
    color = COLORS.get(metric, COLORS['AES'])
    
    # Create figure
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=daily_data['date_str'],
        y=daily_data['value'],
        mode='lines+markers',
        name=metric,
        line=dict(color=color, width=3),
        marker=dict(size=6, color=color),
        fill='tonexty' if metric != 'AHT' else None,
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
        hovertemplate='%{x}<br>%{y:.1f}<extra></extra>'
    ))
    
    # Add target line if provided
    if target:
        fig.add_trace(go.Scatter(
            x=daily_data['date_str'],
            y=[target] * len(daily_data),
            mode='lines',
            name=f'Target ({target})',
            line=dict(color=COLORS['target'], width=2, dash='dash'),
            hovertemplate=f'Target: {target}<extra></extra>'
        ))
    
    # Calculate stats
    stats = calculate_trend_stats(daily_data)
    
    # Add current value annotation
    fig.add_annotation(
        x=daily_data['date_str'].iloc[-1],
        y=stats['current'],
        text=f"<b>{stats['current']:.1f}</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=color,
        ax=30,
        ay=-30,
        font=dict(size=14, color=color, family='Inter'),
        bgcolor='white',
        bordercolor=color,
        borderwidth=2
    )
    
    # Determine Y-axis range and title
    if metric == 'AHT':
        y_title = 'Minutes'
        y_range = [0, max(daily_data['value'].max() * 1.2, 10)]
    else:
        y_title = 'Score (%)'
        y_range = [0, 100]
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Performance Trend: {metric}",
            font=dict(size=16, family='Inter', weight=600)
        ),
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridcolor='#F3F4F6'
        ),
        yaxis=dict(
            title=y_title,
            range=y_range,
            showgrid=True,
            gridcolor='#F3F4F6'
        ),
        height=300,
        margin=dict(l=60, r=40, t=60, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        font=dict(family='Inter', size=12),
        showlegend=False
    )
    
    return fig


def create_trend_summary_html(df: pd.DataFrame, metric: str, days: int = 30) -> str:
    """
    Creates HTML summary for trend statistics.
    
    Returns:
        HTML string with stats
    """
    
    daily_data = prepare_trend_data(df, metric, days)
    stats = calculate_trend_stats(daily_data)
    
    change_color = '#10B981' if stats['change'] > 0 else ('#EF4444' if stats['change'] < 0 else '#6B7280')
    unit = 'min' if metric == 'AHT' else '%'
    
    html = f"""
    <div style='background-color: #F9FAFB; padding: 15px; border-radius: 6px; font-size: 13px; color: #374151; margin-top: 10px;'>
        <b>Current:</b> {stats['current']:.1f}{unit} &nbsp;|&nbsp; 
        <b>Start:</b> {stats['start']:.1f}{unit} &nbsp;|&nbsp; 
        <b>Change:</b> <span style='color: {change_color}'>{stats['trend_arrow']} {abs(stats['change']):.1f}{unit} ({stats['change_pct']:+.1f}%)</span>
        <br>
        <b>Peak:</b> {stats['peak']:.1f}{unit} ({stats['peak_date']}) &nbsp;|&nbsp; 
        <b>Low:</b> {stats['low']:.1f}{unit} ({stats['low_date']})
    </div>
    """
    
    return html
