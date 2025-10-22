"""
Widget 4: Customer Sentiment Journey (Sankey Diagram)
Layout: Sankey diagram with summary stats on the right
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List


COLORS = {
    'improvement': '#10B981',  # Green
    'stable': '#6B7280',       # Gray
    'decline': '#EF4444',      # Red
    'negative': '#EF4444',
    'neutral': '#F59E0B',
    'positive': '#10B981',
}


def categorize_sentiment(value: float) -> str:
    """Categorizes sentiment value into Negative/Neutral/Positive."""
    if value < -0.3:
        return 'Negative'
    elif value < 0.3:
        return 'Neutral'
    else:
        return 'Positive'


def get_sentiment_emoji(category: str) -> str:
    """Returns emoji for sentiment category."""
    return {'Negative': '😠', 'Neutral': '😐', 'Positive': '😊'}[category]


def calculate_sentiment_flows(df: pd.DataFrame) -> Dict:
    """
    Calculates sentiment flow statistics for Sankey diagram.
    
    Returns:
        Dict with flow counts, percentages, and summary stats
    """
    
    # Categorize start and end sentiments
    df = df.copy()
    df['start_category'] = df['sentiment_start'].apply(categorize_sentiment)
    df['end_category'] = df['sentiment_end'].apply(categorize_sentiment)
    
    # Count flows
    flows = df.groupby(['start_category', 'end_category']).size().reset_index(name='count')
    
    total_calls = len(df)
    
    # Add percentages
    flows['pct'] = (flows['count'] / total_calls * 100).round(1)
    
    # Determine flow type (improvement/stable/decline)
    sentiment_order = {'Negative': 0, 'Neutral': 1, 'Positive': 2}
    
    def get_flow_type(row):
        start_val = sentiment_order[row['start_category']]
        end_val = sentiment_order[row['end_category']]
        
        if end_val > start_val:
            return 'improvement'
        elif end_val == start_val:
            return 'stable'
        else:
            return 'decline'
    
    flows['flow_type'] = flows.apply(get_flow_type, axis=1)
    
    # Summary stats
    improving_calls = df[df['sentiment_end'] > df['sentiment_start']]
    stable_calls = df[df['sentiment_end'] == df['sentiment_start']]
    declining_calls = df[df['sentiment_end'] < df['sentiment_start']]
    
    improving_pct = len(improving_calls) / total_calls * 100
    stable_pct = len(stable_calls) / total_calls * 100
    declining_pct = len(declining_calls) / total_calls * 100
    
    # Most common flow
    most_common_flow = flows.nlargest(1, 'count').iloc[0]
    
    return {
        'flows': flows,
        'improving_pct': round(improving_pct, 1),
        'improving_count': len(improving_calls),
        'stable_pct': round(stable_pct, 1),
        'stable_count': len(stable_calls),
        'declining_pct': round(declining_pct, 1),
        'declining_count': len(declining_calls),
        'most_common_flow': f"{most_common_flow['start_category']} → {most_common_flow['end_category']}",
        'most_common_count': int(most_common_flow['count']),
        'total_calls': total_calls
    }


def create_sentiment_sankey(df: pd.DataFrame) -> go.Figure:
    """
    Creates Sankey diagram for sentiment journey.
    
    Args:
        df: Filtered calls DataFrame
        
    Returns:
        Plotly Figure with Sankey diagram
    """
    
    stats = calculate_sentiment_flows(df)
    flows = stats['flows']
    
    # Define nodes
    categories = ['Negative', 'Neutral', 'Positive']
    nodes = [f"{cat} {get_sentiment_emoji(cat)}" for cat in categories]  # Start nodes
    nodes += [f"{cat} {get_sentiment_emoji(cat)}" for cat in categories]  # End nodes
    
    node_colors = [COLORS['negative'], COLORS['neutral'], COLORS['positive']] * 2
    
    # Build links
    source = []
    target = []
    value = []
    link_colors = []
    
    for _, row in flows.iterrows():
        start_idx = categories.index(row['start_category'])
        end_idx = categories.index(row['end_category']) + 3  # Offset for end nodes
        
        source.append(start_idx)
        target.append(end_idx)
        value.append(row['count'])
        
        # Color based on flow type
        if row['flow_type'] == 'improvement':
            link_colors.append('rgba(16, 185, 129, 0.4)')  # Green
        elif row['flow_type'] == 'stable':
            link_colors.append('rgba(107, 114, 128, 0.4)')  # Gray
        else:
            link_colors.append('rgba(239, 68, 68, 0.4)')  # Red
    
    # Create Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='white', width=2),
            label=nodes,
            color=node_colors,
            customdata=[f"{pct}%" for pct in [33, 33, 34] * 2],  # Dummy percentages
            hovertemplate='%{label}<br>%{value} calls<extra></extra>'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,
            hovertemplate='%{value} calls<br>%{source.label} → %{target.label}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text="Customer Sentiment Journey",
            font=dict(size=16, family='Inter', weight=600)
        ),
        font=dict(size=12, family='Inter'),
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


def create_sentiment_summary_html(df: pd.DataFrame) -> str:
    """
    Creates HTML summary for sentiment journey stats.
    
    Returns:
        HTML string for display next to Sankey
    """
    
    stats = calculate_sentiment_flows(df)
    
    html = f"""
    <div style='background-color: white; padding: 20px; border-radius: 8px; height: 350px;'>
        <h4 style='font-family: Inter; font-size: 14px; font-weight: 600; color: #1E3A8A; margin: 0 0 20px 0;'>
            📊 Summary
        </h4>
        
        <div style='margin-bottom: 20px;'>
            <div style='font-size: 12px; color: #6B7280; margin-bottom: 5px;'>😠→😊 IMPROVING</div>
            <div style='font-size: 24px; font-weight: 700; color: #10B981; margin-bottom: 5px;'>
                {stats['improving_pct']}%
            </div>
            <div style='font-size: 12px; color: #6B7280;'>{stats['improving_count']} calls</div>
            <div style='background-color: #D1FAE5; color: #065F46; padding: 5px 10px; border-radius: 4px; font-size: 11px; margin-top: 5px; display: inline-block;'>
                ✅ Strong positive trend
            </div>
        </div>
        
        <div style='margin-bottom: 20px;'>
            <div style='font-size: 12px; color: #6B7280; margin-bottom: 5px;'>😐→😐 STABLE</div>
            <div style='font-size: 24px; font-weight: 700; color: #6B7280; margin-bottom: 5px;'>
                {stats['stable_pct']}%
            </div>
            <div style='font-size: 12px; color: #6B7280;'>{stats['stable_count']} calls</div>
        </div>
        
        <div style='margin-bottom: 20px;'>
            <div style='font-size: 12px; color: #6B7280; margin-bottom: 5px;'>😊→😠 DECLINING</div>
            <div style='font-size: 24px; font-weight: 700; color: #EF4444; margin-bottom: 5px;'>
                {stats['declining_pct']}%
            </div>
            <div style='font-size: 12px; color: #6B7280;'>{stats['declining_count']} calls</div>
            {f'''<div style='background-color: #FEE2E2; color: #991B1B; padding: 5px 10px; border-radius: 4px; font-size: 11px; margin-top: 5px; display: inline-block;'>
                ⚠️ Monitor decline trend
            </div>''' if stats['declining_pct'] > 10 else ''}
        </div>
        
        <div style='background-color: #EFF6FF; padding: 10px; border-radius: 4px; font-size: 12px; color: #1E40AF;'>
            💡 Most common: <b>{stats['most_common_flow']}</b> ({stats['most_common_count']} calls)
        </div>
    </div>
    """
    
    return html
