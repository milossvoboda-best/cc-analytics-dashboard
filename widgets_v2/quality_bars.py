"""
Widget 9: Quality Components Breakdown
Layout: Horizontal bar chart with 8 quality components + trend indicators
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List


COLORS = {
    'excellent': '#10B981',     # 85-100%
    'good': '#84CC16',          # 70-84%
    'fair': '#F59E0B',          # 60-69%
    'poor': '#EF4444',          # <60%
    'neutral': '#6B7280',
}


# 8 Quality Components (from Quality Assessment)
QUALITY_COMPONENTS = [
    'greeting_id',
    'active_listening',
    'empathy',
    'solution_offered',
    'professional_tone',
    'positive_language',
    'call_control',
    'proper_closing'
]

COMPONENT_LABELS = {
    'greeting_id': 'Greeting & ID',
    'active_listening': 'Active Listening',
    'empathy': 'Empathy',
    'solution_offered': 'Solution Offered',
    'professional_tone': 'Professional Tone',
    'positive_language': 'Positive Language',
    'call_control': 'Call Control',
    'proper_closing': 'Proper Closing'
}


def calculate_quality_components(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates percentage pass rate for each quality component.
    
    Returns:
        DataFrame with component, score, label
    """
    
    components = []
    
    for comp_key in QUALITY_COMPONENTS:
        # Map component key to quality dict field
        quality_field_map = {
            'greeting_id': 'greeting_and_introduction',
            'active_listening': 'active_listening',
            'empathy': 'empathy_shown',
            'solution_offered': 'solution_offered',
            'professional_tone': 'tone_appropriate',
            'positive_language': 'positive_language_used',
            'call_control': 'call_control_maintained',
            'proper_closing': 'closing_proper'
        }
        
        quality_field = quality_field_map.get(comp_key, comp_key)
        
        # Calculate pass rate
        pass_rate = df['quality'].apply(
            lambda x: x.get(quality_field, False) if isinstance(x.get(quality_field), bool) else False
        ).sum() / len(df) * 100
        
        components.append({
            'component': comp_key,
            'label': COMPONENT_LABELS[comp_key],
            'score': round(pass_rate, 1)
        })
    
    df_components = pd.DataFrame(components)
    
    # Sort by score (descending)
    df_components = df_components.sort_values('score', ascending=True)  # Ascending for horizontal bars (bottom to top)
    
    return df_components


def calculate_quality_trends(current_df: pd.DataFrame, prev_df: pd.DataFrame = None) -> Dict:
    """
    Calculates trend indicators for each component.
    
    Returns:
        Dict with component -> trend info
    """
    
    if prev_df is None or len(prev_df) == 0:
        return {comp: {'arrow': '➡️', 'pct': 0, 'color': COLORS['neutral']} 
                for comp in QUALITY_COMPONENTS}
    
    current_scores = calculate_quality_components(current_df)
    prev_scores = calculate_quality_components(prev_df)
    
    trends = {}
    
    for comp_key in QUALITY_COMPONENTS:
        current_score = current_scores[current_scores['component'] == comp_key]['score'].iloc[0]
        prev_score = prev_scores[prev_scores['component'] == comp_key]['score'].iloc[0]
        
        delta = current_score - prev_score
        
        if delta > 2:
            arrow = '⬆️'
            color = COLORS['excellent']
        elif delta < -2:
            arrow = '⬇️'
            color = COLORS['poor']
        else:
            arrow = '➡️'
            color = COLORS['neutral']
        
        trends[comp_key] = {
            'arrow': arrow,
            'pct': round(delta, 1),
            'color': color
        }
    
    return trends


def get_bar_color(score: float) -> str:
    """Returns color based on score."""
    if score >= 85:
        return COLORS['excellent']
    elif score >= 70:
        return COLORS['good']
    elif score >= 60:
        return COLORS['fair']
    else:
        return COLORS['poor']


def create_quality_bars(df: pd.DataFrame, prev_period_df: pd.DataFrame = None) -> go.Figure:
    """
    Creates horizontal bar chart for quality components.
    
    Args:
        df: Current period calls DataFrame
        prev_period_df: Previous period DataFrame for trends
        
    Returns:
        Plotly Figure with horizontal bars
    """
    
    components = calculate_quality_components(df)
    trends = calculate_quality_trends(df, prev_period_df)
    
    # Create figure
    fig = go.Figure()
    
    # Add horizontal bars
    colors = [get_bar_color(score) for score in components['score']]
    
    fig.add_trace(go.Bar(
        y=components['label'],
        x=components['score'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='white', width=1)
        ),
        text=[f"{score:.0f}%" for score in components['score']],
        textposition='outside',
        textfont=dict(size=12, family='Inter', weight=600),
        hovertemplate='%{y}<br>%{x:.1f}%<extra></extra>',
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Quality Components Breakdown",
            font=dict(size=16, family='Inter', weight=600)
        ),
        xaxis=dict(
            title="% Calls Passing",
            range=[0, 105],
            showgrid=True,
            gridcolor='#F3F4F6',
            ticksuffix='%'
        ),
        yaxis=dict(
            title="",
            showgrid=False
        ),
        height=400,
        margin=dict(l=150, r=80, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12)
    )
    
    return fig


def get_quality_insights(df: pd.DataFrame, prev_period_df: pd.DataFrame = None) -> str:
    """
    Generates insights about quality trends.
    
    Returns:
        HTML string with key insights
    """
    
    components = calculate_quality_components(df)
    trends = calculate_quality_trends(df, prev_period_df)
    
    # Calculate overall AutoQA score
    overall_autoqa = df['autoqa_score'].mean()
    
    # Find declining components
    declining = [(comp, trends[comp]) for comp in QUALITY_COMPONENTS 
                 if trends[comp]['pct'] < -2]
    
    # Find improving components
    improving = [(comp, trends[comp]) for comp in QUALITY_COMPONENTS 
                 if trends[comp]['pct'] > 2]
    
    # Find lowest scoring component
    lowest = components.nsmallest(1, 'score').iloc[0]
    
    html = f"""
    <div style='background-color: #F9FAFB; padding: 15px; border-radius: 6px; border-top: 3px solid #3B82F6; margin-top: 15px;'>
        <div style='font-size: 14px; color: #1E3A8A; margin-bottom: 10px;'>
            <b>Overall AutoQA Score:</b> <span style='font-size: 18px; font-weight: 700;'>{overall_autoqa:.1f}%</span>
            <span style='margin-left: 10px; color: {"#10B981" if overall_autoqa >= 80 else "#F59E0B"}'>
                {"✅ Good" if overall_autoqa >= 80 else "⚠️ Needs Improvement"}
            </span>
        </div>
        
        <hr style='border: none; border-top: 1px solid #E5E7EB; margin: 10px 0;'>
        
        <div style='font-size: 13px; color: #374151; line-height: 1.8;'>
            <b>💡 Key Insight:</b><br>
    """
    
    if declining:
        comp_key, trend = declining[0]
        label = COMPONENT_LABELS[comp_key]
        html += f"<div style='color: #EF4444; margin-top: 5px;'>• <b>{label}</b> declining ({trend['pct']:.1f}%) → Priority for coaching</div>"
    
    if improving:
        comp_key, trend = improving[0]
        label = COMPONENT_LABELS[comp_key]
        html += f"<div style='color: #10B981; margin-top: 5px;'>• <b>{label}</b> improving (+{trend['pct']:.1f}%) → Good progress</div>"
    
    if lowest['score'] < 70:
        html += f"<div style='color: #F59E0B; margin-top: 5px;'>• <b>{lowest['label']}</b> needs attention ({lowest['score']:.0f}%)</div>"
    
    if not declining and not improving and lowest['score'] >= 70:
        html += "<div style='color: #10B981; margin-top: 5px;'>• All components stable and performing well ✅</div>"
    
    html += """
        </div>
    </div>
    """
    
    return html
