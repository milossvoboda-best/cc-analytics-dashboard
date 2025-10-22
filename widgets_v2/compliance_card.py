"""
Widget 2: Compliance Score
Layout: Big number + status + trend + risk indicators
"""

import pandas as pd
from typing import Dict, Tuple


COLORS = {
    'primary': '#1E3A8A',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'neutral': '#6B7280',
}


def calculate_compliance_score(df: pd.DataFrame) -> Dict:
    """
    Calculates compliance score and related metrics.
    
    Returns:
        Dict with score, critical violations, risk level, trend
    """
    
    # Count passing compliance checks
    def count_passing(comp_dict):
        passing = sum(1 for k, v in comp_dict.items() 
                     if isinstance(v, bool) and v)
        return (passing / 9) * 100  # 9 compliance fields
    
    compliance_scores = df['compliance'].apply(count_passing)
    avg_compliance = compliance_scores.mean()
    
    # Critical violations count
    critical_violations = df['compliance'].apply(
        lambda x: len(x.get('critical_violations', []))
    ).sum()
    
    # Risk level assessment
    if avg_compliance >= 95:
        risk_level = "🟢 Low"
        risk_color = COLORS['success']
    elif avg_compliance >= 85:
        risk_level = "🟡 Medium"
        risk_color = COLORS['warning']
    else:
        risk_level = "🔴 High"
        risk_color = COLORS['danger']
    
    return {
        'score': round(avg_compliance, 1),
        'critical_violations': int(critical_violations),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'total_calls': len(df)
    }


def get_compliance_status(score: float) -> Tuple[str, str]:
    """
    Returns status badge and color.
    
    Status Ranges:
    - 95-100%: ✅ Excellent
    - 85-94%:  ✅ Good
    - 75-84%:  ⚠️ Fair
    - <75%:    🔴 Poor
    """
    
    if score >= 95:
        return "✅ Excellent", COLORS['success']
    elif score >= 85:
        return "✅ Good", COLORS['success']
    elif score >= 75:
        return "⚠️ Fair", COLORS['warning']
    else:
        return "🔴 Poor", COLORS['danger']


def create_compliance_card_html(df: pd.DataFrame, prev_period_score: float = None) -> str:
    """
    Creates HTML for compliance card (big number style).
    
    Args:
        df: Filtered calls DataFrame
        prev_period_score: Previous period score for trend
        
    Returns:
        HTML string for Streamlit markdown
    """
    
    metrics = calculate_compliance_score(df)
    status_label, status_color = get_compliance_status(metrics['score'])
    
    # Calculate trend
    if prev_period_score:
        trend_delta = metrics['score'] - prev_period_score
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
        trend_text = "N/A"
        trend_color = COLORS['neutral']
    
    html = f"""
    <div style='background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 280px;'>
        <h3 style='font-family: Inter; font-size: 16px; font-weight: 600; color: {COLORS['primary']}; margin: 0 0 20px 0;'>
            Compliance Score
        </h3>
        
        <div style='text-align: center; margin: 30px 0;'>
            <div style='font-size: 48px; font-weight: 700; color: {status_color}; margin-bottom: 10px;'>
                {metrics['score']:.1f}%
            </div>
            <div style='font-size: 18px; font-weight: 600; color: {status_color}; margin-bottom: 20px;'>
                {status_label}
            </div>
        </div>
        
        <div style='font-size: 14px; color: {COLORS['neutral']}; line-height: 1.8;'>
            <div style='margin-bottom: 8px;'>
                <b>Critical Violations:</b> <span style='color: {"#EF4444" if metrics["critical_violations"] > 0 else "#10B981"}'>{metrics['critical_violations']}</span>
            </div>
            <div style='margin-bottom: 8px;'>
                <b>Risk Level:</b> <span style='color: {metrics["risk_color"]}'>{metrics['risk_level']}</span>
            </div>
            <div style='margin-bottom: 8px;'>
                <b>Trend:</b> <span style='color: {trend_color}'>{trend_text}</span> (vs last week)
            </div>
        </div>
    </div>
    """
    
    return html
