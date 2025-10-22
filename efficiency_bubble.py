"""
Efficiency Bubble Chart - Topic Performance Visualization
Shows topic performance: AHT vs Volume with AES as bubble size
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List


COLORS = {
    'excellent': '#00C853',
    'good': '#64DD17',
    'warning': '#FFA726',
    'critical': '#EF5350',
}


def create_efficiency_bubble_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates bubble chart showing topic efficiency.
    
    X-axis: Average Handling Time (AHT)
    Y-axis: Call Volume (% of total)
    Bubble size: Average AES for that topic
    Bubble color: Performance tier
    
    Args:
        df: DataFrame with calls
        
    Returns:
        Plotly scatter plot with bubbles
    """
    
    # Aggregate by topic
    topic_stats = []
    
    for topic, group in df.groupby(df['resolution'].apply(lambda x: x.get('issue_category', 'Unknown'))):
        stats = {
            'topic': topic,
            'volume': len(group),
            'volume_pct': (len(group) / len(df)) * 100,
            'aht': group['duration_sec'].mean() / 60,  # Convert to minutes
            'aes': group['aes'].mean() if 'aes' in group.columns else 70
        }
        topic_stats.append(stats)
    
    df_topics = pd.DataFrame(topic_stats)
    
    # Sort by volume
    df_topics = df_topics.sort_values('volume', ascending=False)
    
    # Determine color based on efficiency quadrant
    # Efficient = Low AHT + High AES
    # Inefficient = High AHT + Low AES
    
    median_aht = df_topics['aht'].median()
    median_aes = df_topics['aes'].median()
    
    colors = []
    labels = []
    
    for _, row in df_topics.iterrows():
        if row['aes'] >= median_aes and row['aht'] <= median_aht:
            colors.append(COLORS['excellent'])
            labels.append('⭐ High Efficiency')
        elif row['aes'] >= median_aes and row['aht'] > median_aht:
            colors.append(COLORS['good'])
            labels.append('✅ Good AES, Slow')
        elif row['aes'] < median_aes and row['aht'] <= median_aht:
            colors.append(COLORS['warning'])
            labels.append('⚠️ Fast but Low Quality')
        else:
            colors.append(COLORS['critical'])
            labels.append('🔴 Needs Improvement')
    
    df_topics['color'] = colors
    df_topics['label'] = labels
    
    # Create bubble chart
    fig = go.Figure()
    
    # Add bubbles
    fig.add_trace(go.Scatter(
        x=df_topics['aht'],
        y=df_topics['volume_pct'],
        mode='markers+text',
        marker=dict(
            size=df_topics['aes'],
            sizemode='diameter',
            sizeref=2,
            color=df_topics['color'],
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=df_topics['topic'],
        textposition='top center',
        textfont=dict(size=10, family='Inter'),
        hovertemplate=(
            '<b>%{text}</b><br>' +
            'AHT: %{x:.1f} min<br>' +
            'Volume: %{y:.1f}%<br>' +
            'AES: %{marker.size:.1f}<br>' +
            '<extra></extra>'
        ),
        showlegend=False
    ))
    
    # Add reference lines (median)
    fig.add_vline(
        x=median_aht,
        line_dash="dash",
        line_color=COLORS['warning'],
        annotation_text=f"Median AHT: {median_aht:.1f} min",
        annotation_position="top"
    )
    
    fig.add_hline(
        y=df_topics['volume_pct'].median(),
        line_dash="dash",
        line_color=COLORS['warning'],
        annotation_text="Median Volume",
        annotation_position="right"
    )
    
    # Update layout
    fig.update_layout(
        title="Topic Performance Matrix",
        xaxis=dict(
            title="Average Handling Time (minutes)",
            showgrid=True,
            gridcolor='#e5e7eb'
        ),
        yaxis=dict(
            title="Call Volume (%)",
            showgrid=True,
            gridcolor='#e5e7eb'
        ),
        height=500,
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        hovermode='closest'
    )
    
    return fig


def get_efficiency_insights(df: pd.DataFrame) -> Dict:
    """
    Analyzes efficiency patterns and returns insights.
    
    Returns:
        Dict with top performers and improvement areas
    """
    
    # Aggregate by topic
    topic_stats = []
    
    for topic, group in df.groupby(df['resolution'].apply(lambda x: x.get('issue_category', 'Unknown'))):
        stats = {
            'topic': topic,
            'volume': len(group),
            'aht': group['duration_sec'].mean() / 60,
            'aes': group['aes'].mean() if 'aes' in group.columns else 70,
            'efficiency_score': 0  # Will calculate
        }
        # Efficiency = High AES / Low AHT
        # Normalize: (AES / 100) / (AHT / median_aht)
        stats['efficiency_score'] = stats['aes'] / stats['aht']
        topic_stats.append(stats)
    
    df_topics = pd.DataFrame(topic_stats)
    df_topics = df_topics.sort_values('efficiency_score', ascending=False)
    
    # Top 3 performers
    top_performers = df_topics.head(3)[['topic', 'aht', 'aes', 'volume']].to_dict('records')
    
    # Bottom 3 (needs improvement)
    needs_improvement = df_topics.tail(3)[['topic', 'aht', 'aes', 'volume']].to_dict('records')
    
    # Overall stats
    avg_aht = df_topics['aht'].mean()
    avg_aes = df_topics['aes'].mean()
    
    return {
        'top_performers': top_performers,
        'needs_improvement': needs_improvement,
        'avg_aht': avg_aht,
        'avg_aes': avg_aes,
        'total_topics': len(df_topics)
    }
