"""
Widget 8: Escalation Prevention Rate (EPR)
Layout: Big number + status + escalation reasons breakdown
"""

import pandas as pd
from typing import Dict


COLORS = {
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'neutral': '#6B7280',
    'primary': '#1E3A8A',
}


def calculate_escalation_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculates escalation prevention rate and breakdown.
    
    EPR = (1 - escalated_calls / total_calls) * 100
    
    Returns:
        Dict with EPR, escalation counts, and reasons
    """
    
    # Check if escalation data exists
    if 'resolution' not in df.columns:
        return {
            'epr': 0,
            'escalated_count': 0,
            'prevented_count': 0,
            'total_calls': 0,
            'reasons': {}
        }
    
    total_calls = len(df)
    
    # Count escalations (escalated field in resolution)
    escalated_calls = df[df['resolution'].apply(
        lambda x: x.get('escalated', False)
    )]
    
    escalated_count = len(escalated_calls)
    prevented_count = total_calls - escalated_count
    
    epr = (prevented_count / total_calls * 100) if total_calls > 0 else 0
    
    # Breakdown by escalation reason
    reasons = {}
    if escalated_count > 0:
        reason_counts = escalated_calls['resolution'].apply(
            lambda x: x.get('escalation_reason', 'unknown')
        ).value_counts()
        
        reasons = reason_counts.to_dict()
    
    return {
        'epr': round(epr, 1),
        'escalated_count': escalated_count,
        'prevented_count': prevented_count,
        'total_calls': total_calls,
        'reasons': reasons
    }


def get_epr_status(epr: float) -> tuple:
    """
    Returns status label and color based on EPR value.
    
    Status Ranges:
    - 90%+: ⭐ Excellent
    - 80-89%: ✅ Good
    - 70-79%: ⚠️ Fair
    - <70%: 🔴 Poor
    """
    
    if epr >= 90:
        return "⭐ Excellent", COLORS['success']
    elif epr >= 80:
        return "✅ Good", COLORS['success']
    elif epr >= 70:
        return "⚠️ Fair", COLORS['warning']
    else:
        return "🔴 Poor", COLORS['danger']


def create_escalation_card_html(df: pd.DataFrame, prev_period_epr: float = None) -> str:
    """
    Creates HTML for escalation prevention rate card.
    
    Args:
        df: Filtered calls DataFrame
        prev_period_epr: Previous period EPR for trend
        
    Returns:
        HTML string for Streamlit markdown
    """
    
    metrics = calculate_escalation_metrics(df)
    status_label, status_color = get_epr_status(metrics['epr'])
    
    # Calculate trend
    if prev_period_epr:
        trend_delta = metrics['epr'] - prev_period_epr
        if trend_delta > 0:
            trend_arrow = "⬆️"
            trend_color = COLORS['success']
        elif trend_delta < 0:
            trend_arrow = "⬇️"
            trend_color = COLORS['danger']
        else:
            trend_arrow = "➡️"
            trend_color = COLORS['neutral']
        
        trend_text = f"{trend_arrow} {abs(trend_delta):.1f}%"
    else:
        trend_text = "➡️ Stable"
        trend_color = COLORS['neutral']
    
    html = f"""
    <div style='background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 380px;'>
        <h3 style='font-family: Inter; font-size: 16px; font-weight: 600; color: {COLORS['primary']}; margin: 0 0 20px 0;'>
            Escalation Stats
        </h3>
        
        <div style='text-align: center; margin: 30px 0;'>
            <div style='font-size: 12px; color: {COLORS['neutral']}; margin-bottom: 5px;'>
                Prevention Rate:
            </div>
            <div style='font-size: 48px; font-weight: 700; color: {status_color}; margin-bottom: 10px;'>
                {metrics['epr']:.1f}%
            </div>
            <div style='font-size: 18px; font-weight: 600; color: {status_color}; margin-bottom: 20px;'>
                {status_label}
            </div>
        </div>
        
        <div style='font-size: 14px; color: {COLORS['neutral']}; line-height: 1.8; margin-bottom: 20px;'>
            <div style='margin-bottom: 8px;'>
                <b>Escalations:</b> {metrics['escalated_count']} / {metrics['total_calls']}
            </div>
            <div style='margin-bottom: 8px;'>
                <b>Trend:</b> <span style='color: {trend_color}'>{trend_text}</span>
            </div>
        </div>
        
        <div style='font-size: 13px; color: {COLORS['neutral']}; line-height: 1.6;'>
            <b>Top Reasons:</b><br>
    """
    
    # Add top 3 reasons
    if metrics['reasons']:
        sorted_reasons = sorted(metrics['reasons'].items(), key=lambda x: x[1], reverse=True)[:3]
        for reason, count in sorted_reasons:
            pct = (count / metrics['escalated_count'] * 100) if metrics['escalated_count'] > 0 else 0
            html += f"<div style='margin-top: 5px;'>• {reason.replace('_', ' ').title()}: <b>{count}</b> ({pct:.0f}%)</div>"
    else:
        html += "<div style='margin-top: 5px; color: #10B981;'>✅ No escalations!</div>"
    
    html += """
        </div>
    </div>
    """
    
    return html
