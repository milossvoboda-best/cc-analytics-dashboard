"""
Widget 1: Agent Effectiveness Score (AES)
Layout: Spider chart + Status box side-by-side
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Tuple


COLORS = {
    'primary': '#1E3A8A',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'neutral': '#6B7280',
}


def calculate_aes_components(df: pd.DataFrame) -> Dict:
    """
    Calculates AES component scores from call data.
    
    Components (exact weights from spec):
    - Sentiment (25%): Customer mood improvement
    - Compliance (30%): Regulatory adherence
    - Resolution (30%): Issue resolution rate
    - Quality (15%): Communication quality
    
    Returns:
        Dict with component scores and overall AES
    """
    
    # Sentiment component (25%)
    sentiment_delta = df['sentiment_end'] - df['sentiment_start']
    # Normalize to 0-25 scale
    sentiment_score = ((sentiment_delta + 2) / 4 * 25).mean()
    
    # Compliance component (30%)
    # Count passing compliance checks
    def count_compliance(comp_dict):
        return sum(1 for k, v in comp_dict.items() 
                  if isinstance(v, bool) and v) / 9 * 30
    
    compliance_score = df['compliance'].apply(count_compliance).mean()
    
    # Resolution component (30%)
    def resolution_score(res_dict):
        if res_dict['resolution_achieved'] == 'full':
            return 30.0
        elif res_dict['resolution_achieved'] == 'partial':
            return 15.0
        else:
            return 0.0
    
    resolution_score_val = df['resolution'].apply(resolution_score).mean()
    
    # Quality component (15%)
    quality_score = df['quality'].apply(lambda x: x['quality_score'] / 100 * 15).mean()
    
    # Overall AES (sum of components)
    overall_aes = sentiment_score + compliance_score + resolution_score_val + quality_score
    
    return {
        'sentiment': round(sentiment_score, 2),
        'compliance': round(compliance_score, 2),
        'resolution': round(resolution_score_val, 2),
        'quality': round(quality_score, 2),
        'overall_aes': round(overall_aes, 1),
        'overall_aes_pct': round(overall_aes, 1)  # Already 0-100
    }


def get_aes_status(aes_pct: float, target: float = 75.0) -> Tuple[str, str, str]:
    """
    Returns status badge, emoji, and description.
    
    Score Ranges:
    - 85-100%: ⭐ Excellent
    - 70-84%:  ✅ Good
    - 50-69%:  ⚠️ Needs coaching
    - <50%:    🔴 Urgent intervention
    """
    
    if aes_pct >= 85:
        return "⭐ Excellent", COLORS['success'], "Outstanding performance"
    elif aes_pct >= 70:
        return "✅ Good", COLORS['success'], "On track, meeting standards"
    elif aes_pct >= 50:
        return "⚠️ Needs Coaching", COLORS['warning'], "Improvement required"
    else:
        return "🔴 Urgent", COLORS['danger'], "Immediate intervention needed"


def create_aes_card(df: pd.DataFrame, target: float = 75.0, prev_period_aes: float = None) -> go.Figure:
    """
    Creates AES card with spider chart + status box.
    
    Layout:
    - LEFT: Spider chart (4 axes)
    - RIGHT: Status box (overall score, trend, vs target)
    
    Args:
        df: Filtered calls DataFrame
        target: Target AES benchmark (default 75%)
        prev_period_aes: Previous period AES for trend calculation
        
    Returns:
        Plotly Figure with subplot
    """
    
    # Calculate components
    components = calculate_aes_components(df)
    
    # Get status
    status_label, status_color, status_desc = get_aes_status(components['overall_aes_pct'], target)
    
    # Calculate trends
    vs_target = components['overall_aes_pct'] - target
    vs_target_text = f"+{vs_target:.1f}%" if vs_target >= 0 else f"{vs_target:.1f}%"
    
    if prev_period_aes:
        vs_prev = components['overall_aes_pct'] - prev_period_aes
        trend_arrow = "⬆️" if vs_prev > 0 else ("⬇️" if vs_prev < 0 else "➡️")
        vs_prev_text = f"{trend_arrow} {abs(vs_prev):.1f}%"
    else:
        vs_prev_text = "N/A"
    
    # Create subplot: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.5, 0.5],
        specs=[[{'type': 'scatterpolar'}, {'type': 'xy'}]],
        horizontal_spacing=0.15
    )
    
    # LEFT: Spider chart
    categories = ['Sentiment<br>(25%)', 'Compliance<br>(30%)', 'Resolution<br>(30%)', 'Quality<br>(15%)']
    values = [
        components['sentiment'],
        components['compliance'],
        components['resolution'],
        components['quality']
    ]
    
    # Add max values (for reference)
    max_values = [25, 30, 30, 15]
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the shape
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.3)',  # Green with alpha
        line=dict(color=COLORS['success'], width=2),
        name='Current',
        hovertemplate='%{theta}<br>Score: %{r:.1f}<extra></extra>'
    ), row=1, col=1)
    
    # Add target line (if different from current)
    target_values = [max_val * (target / 100) for max_val in max_values]
    fig.add_trace(go.Scatterpolar(
        r=target_values + [target_values[0]],
        theta=categories + [categories[0]],
        fill=None,
        line=dict(color=COLORS['neutral'], width=1, dash='dash'),
        name=f'Target ({target}%)',
        hovertemplate='Target: %{r:.1f}<extra></extra>'
    ), row=1, col=1)
    
    # Configure spider chart
    fig.update_polars(
        radialaxis=dict(
            visible=True,
            range=[0, 30],  # Max possible score
            showticklabels=True,
            ticks='',
            gridcolor='#E5E7EB',
            gridwidth=1
        ),
        angularaxis=dict(
            gridcolor='#E5E7EB',
            gridwidth=1
        )
    )
    
    # RIGHT: Status box (using annotations)
    # Add invisible trace
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers',
        marker=dict(size=0, color='rgba(0,0,0,0)'),
        showlegend=False,
        hoverinfo='skip'
    ), row=1, col=2)
    
    # Add annotations
    fig.add_annotation(
        text=f"<b>{components['overall_aes_pct']:.1f}%</b>",
        xref="x2", yref="y2",
        x=0, y=0.7,
        showarrow=False,
        font=dict(size=36, color=status_color, family='Inter'),
        xanchor='center'
    )
    
    fig.add_annotation(
        text=f"<b>{status_label}</b>",
        xref="x2", yref="y2",
        x=0, y=0.5,
        showarrow=False,
        font=dict(size=18, color=status_color, family='Inter'),
        xanchor='center'
    )
    
    fig.add_annotation(
        text=status_desc,
        xref="x2", yref="y2",
        x=0, y=0.3,
        showarrow=False,
        font=dict(size=14, color='#6B7280', family='Inter'),
        xanchor='center'
    )
    
    fig.add_annotation(
        text=f"vs Target: {vs_target_text}",
        xref="x2", yref="y2",
        x=0, y=0.1,
        showarrow=False,
        font=dict(size=12, color='#6B7280', family='Inter'),
        xanchor='center'
    )
    
    fig.add_annotation(
        text=f"vs Last Week: {vs_prev_text}",
        xref="x2", yref="y2",
        x=0, y=-0.05,
        showarrow=False,
        font=dict(size=12, color='#6B7280', family='Inter'),
        xanchor='center'
    )
    
    # Hide axes on right subplot
    fig.update_xaxes(visible=False, showgrid=False, zeroline=False, row=1, col=2)
    fig.update_yaxes(visible=False, showgrid=False, zeroline=False, row=1, col=2)
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        font=dict(family='Inter', size=12),
        title=dict(
            text="Agent Effectiveness Score (AES)",
            font=dict(size=16, family='Inter', weight=600),
            x=0.0,
            xanchor='left'
        )
    )
    
    return fig


def get_aes_component_breakdown(df: pd.DataFrame) -> str:
    """
    Returns HTML string with component breakdown table.
    
    Returns:
        HTML string for Streamlit markdown
    """
    
    components = calculate_aes_components(df)
    
    html = """
    <div style='font-size: 12px; color: #6B7280; margin-top: 10px;'>
        <b>Component Breakdown:</b><br>
        • Sentiment (25%): {:.1f} / 25.0<br>
        • Compliance (30%): {:.1f} / 30.0<br>
        • Resolution (30%): {:.1f} / 30.0<br>
        • Quality (15%): {:.1f} / 15.0
    </div>
    """.format(
        components['sentiment'],
        components['compliance'],
        components['resolution'],
        components['quality']
    )
    
    return html
