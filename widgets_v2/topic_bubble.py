"""
Widget 7: Topic Efficiency Matrix (Bubble Chart)
Layout: Bubble chart with topics on Y-axis, AHT on X-axis, volume as size
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List


COLORS = {
    'efficient': '#10B981',    # Green (AHT < benchmark)
    'acceptable': '#F59E0B',   # Yellow (AHT within ±10% benchmark)
    'critical': '#EF4444',     # Red (AHT > benchmark)
    'neutral': '#6B7280',
}


def calculate_topic_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates efficiency metrics by topic.
    
    Returns:
        DataFrame with topic, calls, avg_aht, benchmark_aht, total_talk_time, efficiency_status
    """
    
    # Extract topic from resolution
    df = df.copy()
    df['topic'] = df['resolution'].apply(lambda x: x.get('issue_category', 'Unknown'))
    
    # Group by topic
    topic_stats = []
    
    for topic, group in df.groupby('topic'):
        avg_aht = group['duration_sec'].mean() / 60  # Minutes
        benchmark_aht = group['benchmark_aht'].iloc[0]  # Minutes
        total_talk_time = group['duration_sec'].sum() / 3600  # Hours
        call_count = len(group)
        
        # Determine efficiency status
        pct_diff = ((avg_aht - benchmark_aht) / benchmark_aht) * 100
        
        if pct_diff < -10:
            status = 'efficient'
            color = COLORS['efficient']
        elif pct_diff > 10:
            status = 'critical'
            color = COLORS['critical']
        else:
            status = 'acceptable'
            color = COLORS['acceptable']
        
        topic_stats.append({
            'topic': topic.replace('_', ' ').title(),
            'calls': call_count,
            'avg_aht': round(avg_aht, 2),
            'benchmark_aht': round(benchmark_aht, 2),
            'total_talk_time': round(total_talk_time, 2),
            'pct_diff': round(pct_diff, 1),
            'status': status,
            'color': color
        })
    
    df_topics = pd.DataFrame(topic_stats)
    
    # Sort by total talk time (descending)
    df_topics = df_topics.sort_values('total_talk_time', ascending=False)
    
    return df_topics


def create_topic_bubble_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates bubble chart for topic efficiency analysis.
    
    Y-axis: Topic categories
    X-axis: Average Handling Time (minutes)
    Bubble size: Total talk time (all calls)
    Bubble color: Efficiency vs benchmark
    
    Args:
        df: Filtered calls DataFrame
        
    Returns:
        Plotly Figure with bubble chart
    """
    
    topic_stats = calculate_topic_efficiency(df)
    
    if len(topic_stats) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No topic data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#6B7280')
        )
        fig.update_layout(height=400)
        return fig
    
    # Create bubble chart
    fig = go.Figure()
    
    # Add bubbles for each topic
    for _, row in topic_stats.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['avg_aht']],
            y=[row['topic']],
            mode='markers+text',
            marker=dict(
                size=row['total_talk_time'] * 20,  # Scale for visibility
                sizemode='area',
                sizemin=4,
                color=row['color'],
                line=dict(width=2, color='white'),
                opacity=0.7
            ),
            text=f"{row['calls']}",
            textposition='middle center',
            textfont=dict(color='white', size=10, family='Inter', weight=600),
            hovertemplate=(
                f"<b>{row['topic']}</b><br>" +
                f"Calls: {row['calls']}<br>" +
                f"Avg AHT: {row['avg_aht']:.1f} min<br>" +
                f"Benchmark: {row['benchmark_aht']:.1f} min<br>" +
                f"Total Time: {row['total_talk_time']:.1f} hours<br>" +
                f"vs Benchmark: {row['pct_diff']:+.0f}%<br>" +
                "<extra></extra>"
            ),
            showlegend=False
        ))
    
    # Add median AHT reference line
    median_aht = topic_stats['avg_aht'].median()
    
    fig.add_vline(
        x=median_aht,
        line_dash="dash",
        line_color=COLORS['neutral'],
        line_width=2,
        annotation_text=f"Median: {median_aht:.1f} min",
        annotation_position="top"
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Topic Efficiency Matrix",
            font=dict(size=16, family='Inter', weight=600)
        ),
        xaxis=dict(
            title="Average Handling Time (minutes)",
            showgrid=True,
            gridcolor='#F3F4F6',
            range=[0, topic_stats['avg_aht'].max() * 1.2]
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor='#F3F4F6',
            categoryorder='total ascending'
        ),
        height=400,
        margin=dict(l=120, r=40, t=60, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest',
        font=dict(family='Inter', size=12)
    )
    
    return fig


def get_topic_insights(df: pd.DataFrame) -> str:
    """
    Generates insights about topic efficiency.
    
    Returns:
        HTML string with priority actions
    """
    
    topic_stats = calculate_topic_efficiency(df)
    
    if len(topic_stats) == 0:
        return "<div>No data available</div>"
    
    # Get critical topics (over benchmark)
    critical = topic_stats[topic_stats['status'] == 'critical'].nlargest(1, 'total_talk_time')
    
    # Get optimal topics (under benchmark)
    optimal = topic_stats[topic_stats['status'] == 'efficient'].nlargest(1, 'total_talk_time')
    
    html = "<div style='font-size: 13px; margin-top: 15px;'>"
    
    if len(critical) > 0:
        row = critical.iloc[0]
        html += f"""
        <div style='background-color: #FEE2E2; border-left: 4px solid #EF4444; padding: 12px; border-radius: 4px; margin-bottom: 10px;'>
            <b style='color: #991B1B;'>🔴 URGENT: {row['topic']}</b><br>
            <span style='color: #7F1D1D; font-size: 12px;'>
            {row['calls']} calls, {row['avg_aht']:.1f} min avg, {row['total_talk_time']:.1f}h total<br>
            → {abs(row['pct_diff']):.0f}% over benchmark<br>
            → <b>Action:</b> Review top 3 {row['topic'].lower()} issues
            </span>
        </div>
        """
    
    if len(optimal) > 0:
        row = optimal.iloc[0]
        html += f"""
        <div style='background-color: #D1FAE5; border-left: 4px solid #10B981; padding: 12px; border-radius: 4px;'>
            <b style='color: #065F46;'>✅ OPTIMAL: {row['topic']}</b><br>
            <span style='color: #047857; font-size: 12px;'>
            {row['calls']} calls, {row['avg_aht']:.1f} min avg, {row['total_talk_time']:.1f}h total<br>
            → {abs(row['pct_diff']):.0f}% under benchmark<br>
            → <b>Action:</b> Use as training example
            </span>
        </div>
        """
    
    html += "</div>"
    
    return html
