"""
Customer Sentiment Journey (CSJ) - Sankey Diagram
Flow visualization showing sentiment changes from start to end
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List


COLORS = {
    'negative': '#EF5350',
    'neutral': '#9E9E9E',
    'positive': '#00C853',
    'improvement': '#00C853',
    'decline': '#EF5350',
}


def create_sentiment_sankey(df: pd.DataFrame) -> go.Figure:
    """
    Creates Sankey diagram showing sentiment flow from Start to End.
    
    Args:
        df: DataFrame with sentiment_start and sentiment_end columns
        
    Returns:
        Plotly Sankey diagram
    """
    
    # Define sentiment buckets
    def bucket_sentiment(s):
        if s < -0.3:
            return 'Negative'
        elif s < 0.3:
            return 'Neutral'
        else:
            return 'Positive'
    
    # Bucket start and end sentiments
    df = df.copy()
    df['start_bucket'] = df['sentiment_start'].apply(bucket_sentiment)
    df['end_bucket'] = df['sentiment_end'].apply(bucket_sentiment)
    
    # Count transitions
    transitions = df.groupby(['start_bucket', 'end_bucket']).size().reset_index(name='count')
    total_calls = len(df)
    transitions['pct'] = (transitions['count'] / total_calls) * 100
    
    # Define nodes (6 total: 3 start + 3 end)
    buckets = ['Negative', 'Neutral', 'Positive']
    node_labels = [
        '😠 Negative Start',
        '😐 Neutral Start',
        '😊 Positive Start',
        '😠 Negative End',
        '😐 Neutral End',
        '😊 Positive End'
    ]
    
    node_colors = [
        COLORS['negative'],  # Negative Start
        COLORS['neutral'],   # Neutral Start
        COLORS['positive'],  # Positive Start
        COLORS['negative'],  # Negative End
        COLORS['neutral'],   # Neutral End
        COLORS['positive'],  # Positive End
    ]
    
    # Create mapping from bucket names to node indices
    start_indices = {bucket: i for i, bucket in enumerate(buckets)}
    end_indices = {bucket: i + 3 for i, bucket in enumerate(buckets)}
    
    # Prepare links (flows)
    sources = []
    targets = []
    values = []
    link_colors = []
    link_labels = []
    
    for _, row in transitions.iterrows():
        start_bucket = row['start_bucket']
        end_bucket = row['end_bucket']
        count = row['count']
        pct = row['pct']
        
        source_idx = start_indices[start_bucket]
        target_idx = end_indices[end_bucket]
        
        sources.append(source_idx)
        targets.append(target_idx)
        values.append(count)
        
        # Determine link color based on improvement/decline
        if start_bucket == 'Negative' and end_bucket in ['Neutral', 'Positive']:
            color = COLORS['improvement']  # Green - improvement
        elif start_bucket == 'Neutral' and end_bucket == 'Positive':
            color = COLORS['improvement']  # Green - improvement
        elif start_bucket == 'Positive' and end_bucket in ['Neutral', 'Negative']:
            color = COLORS['decline']  # Red - decline
        elif start_bucket == 'Neutral' and end_bucket == 'Negative':
            color = COLORS['decline']  # Red - decline
        else:
            color = COLORS['neutral']  # Gray - no change
        
        # Make color semi-transparent for link
        if color == COLORS['improvement']:
            link_color = 'rgba(0, 200, 83, 0.4)'
        elif color == COLORS['decline']:
            link_color = 'rgba(239, 83, 80, 0.4)'
        else:
            link_color = 'rgba(158, 158, 158, 0.3)'
        
        link_colors.append(link_color)
        link_labels.append(f"{start_bucket} → {end_bucket}: {pct:.1f}% ({count} calls)")
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color='white', width=2),
            label=node_labels,
            color=node_colors,
            hovertemplate='%{label}<br>%{value} calls<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate='%{label}<extra></extra>',
            label=link_labels
        )
    )])
    
    fig.update_layout(
        title=dict(
            text='Sentiment Flow: Start → End',
            font=dict(size=16, family='Inter', color='#1e3a5f')
        ),
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(size=12, family='Inter'),
        paper_bgcolor='white'
    )
    
    return fig


def calculate_sentiment_summary(df: pd.DataFrame) -> Dict:
    """
    Calculates summary metrics for sentiment journey.
    
    Args:
        df: DataFrame with sentiment_start and sentiment_end columns
        
    Returns:
        Dict with:
            - improving_pct: % of calls with improvement
            - stable_pct: % of calls with no change
            - declining_pct: % of calls with decline
            - top_flow: Most common transition
            - declining_by_topic: Top topics for declining calls
            - declining_by_agent: Top agents for declining calls
    """
    
    # Classify each call
    df = df.copy()
    df['delta'] = df['sentiment_end'] - df['sentiment_start']
    
    improving = (df['delta'] > 0.2).sum()
    stable = ((df['delta'] >= -0.2) & (df['delta'] <= 0.2)).sum()
    declining = (df['delta'] < -0.2).sum()
    
    total = len(df)
    
    # Find most common flow
    def bucket_sentiment(s):
        if s < -0.3:
            return 'Negative'
        elif s < 0.3:
            return 'Neutral'
        else:
            return 'Positive'
    
    df['start_bucket'] = df['sentiment_start'].apply(bucket_sentiment)
    df['end_bucket'] = df['sentiment_end'].apply(bucket_sentiment)
    df['flow'] = df['start_bucket'] + ' → ' + df['end_bucket']
    
    top_flow = df['flow'].value_counts().iloc[0] if len(df) > 0 else 'N/A'
    top_flow_count = df['flow'].value_counts().iloc[0] if len(df) > 0 else 0
    
    # Breakdown declining calls
    declining_calls = df[df['delta'] < -0.2]
    
    if len(declining_calls) > 0:
        # Top topics
        if 'resolution' in declining_calls.columns:
            topic_counts = declining_calls['resolution'].apply(lambda x: x.get('issue_category', 'Unknown')).value_counts()
            top_topics = [{'topic': topic, 'count': count} for topic, count in topic_counts.head(3).items()]
        else:
            top_topics = []
        
        # Top agents
        if 'agent_name' in declining_calls.columns:
            agent_counts = declining_calls['agent_name'].value_counts()
            top_agents = [{'agent': agent, 'count': count} for agent, count in agent_counts.head(3).items()]
        else:
            top_agents = []
    else:
        top_topics = []
        top_agents = []
    
    return {
        'improving_pct': round((improving / total) * 100, 1) if total > 0 else 0,
        'stable_pct': round((stable / total) * 100, 1) if total > 0 else 0,
        'declining_pct': round((declining / total) * 100, 1) if total > 0 else 0,
        'improving_count': improving,
        'stable_count': stable,
        'declining_count': declining,
        'top_flow': top_flow,
        'top_flow_count': top_flow_count,
        'declining_by_topic': top_topics,
        'declining_by_agent': top_agents
    }
