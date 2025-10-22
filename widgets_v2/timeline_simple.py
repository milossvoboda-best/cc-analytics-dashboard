"""
Widget 10: Call Timeline Analysis (Simplified)
Shows average call timeline statistics - can be expanded to full timeline later
"""

import pandas as pd
from typing import Dict


COLORS = {
    'agent': '#3B82F6',
    'customer': '#F97316',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
}


def calculate_timeline_summary(df: pd.DataFrame) -> Dict:
    """
    Calculates average timeline statistics across all calls.
    
    Returns:
        Dict with avg duration, talk ratios, sentiment delta, etc.
    """
    
    # Average duration
    avg_duration = df['duration_sec'].mean()
    avg_duration_min = int(avg_duration // 60)
    avg_duration_sec = int(avg_duration % 60)
    
    # Talk time ratios
    total_agent_talk = df['agent_talk_sec'].sum()
    total_customer_talk = df['customer_talk_sec'].sum()
    total_silence = df.apply(lambda x: x['duration_sec'] * x['silence_ratio'], axis=1).sum()
    total_time = df['duration_sec'].sum()
    
    agent_ratio = (total_agent_talk / total_time * 100) if total_time > 0 else 0
    customer_ratio = (total_customer_talk / total_time * 100) if total_time > 0 else 0
    silence_ratio = (total_silence / total_time * 100) if total_time > 0 else 0
    
    # Sentiment improvement
    sentiment_delta = (df['sentiment_end'] - df['sentiment_start']).mean()
    
    # Compliance pass rate (from compliance checkpoints)
    compliance_fields = [
        'greeting_proper', 'identification', 'customer_verification',
        'data_protection_mentioned', 'call_recording_notice',
        'clear_communication', 'no_misleading_info', 'proper_closing'
    ]
    
    compliance_pass_counts = []
    for field in compliance_fields:
        pass_count = df['compliance'].apply(lambda x: x.get(field, False)).sum()
        compliance_pass_counts.append(pass_count)
    
    avg_compliance_pass = sum(compliance_pass_counts) / (len(compliance_fields) * len(df)) * 100
    
    return {
        'avg_duration_min': avg_duration_min,
        'avg_duration_sec': avg_duration_sec,
        'avg_duration_str': f"{avg_duration_min}:{avg_duration_sec:02d}",
        'agent_ratio': round(agent_ratio, 1),
        'customer_ratio': round(customer_ratio, 1),
        'silence_ratio': round(silence_ratio, 1),
        'sentiment_delta': round(sentiment_delta, 2),
        'compliance_pass_rate': round(avg_compliance_pass, 1),
        'total_calls': len(df)
    }


def get_sentiment_delta_label(delta: float) -> tuple:
    """Returns label and color for sentiment improvement."""
    if delta >= 0.5:
        return "Strong Improvement ⬆️", COLORS['success']
    elif delta >= 0.2:
        return "Moderate Improvement ⬆️", COLORS['success']
    elif delta >= -0.2:
        return "Stable ➡️", COLORS['warning']
    else:
        return "Declining ⬇️", COLORS['danger']


def create_timeline_summary_html(df: pd.DataFrame) -> str:
    """
    Creates HTML summary card for average timeline stats.
    
    This is a simplified version - can be expanded to full timeline widget.
    
    Returns:
        HTML string for Streamlit markdown
    """
    
    stats = calculate_timeline_summary(df)
    sentiment_label, sentiment_color = get_sentiment_delta_label(stats['sentiment_delta'])
    
    html = f"""
    <div style='background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
        <h3 style='font-family: Inter; font-size: 16px; font-weight: 600; color: #1E3A8A; margin: 0 0 20px 0;'>
            📞 Average Call Timeline
        </h3>
        
        <div style='font-size: 13px; color: #374151; line-height: 2.0;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                <span><b>Avg Duration:</b></span>
                <span style='font-size: 18px; font-weight: 700; color: #1E3A8A;'>{stats['avg_duration_str']} min</span>
            </div>
            
            <hr style='border: none; border-top: 1px solid #E5E7EB; margin: 15px 0;'>
            
            <div style='margin-bottom: 8px;'>
                <b>Agent Talk:</b> 
                <span style='color: {COLORS['agent']}'>{stats['agent_ratio']:.1f}%</span>
                <span style='margin-left: 5px; color: #9CA3AF;'>({int(stats['avg_duration_min'] * stats['agent_ratio'] / 100)}:{int(stats['avg_duration_sec'] * stats['agent_ratio'] / 100):02d} min)</span>
            </div>
            
            <div style='margin-bottom: 8px;'>
                <b>Customer Talk:</b> 
                <span style='color: {COLORS['customer']}'>{stats['customer_ratio']:.1f}%</span>
                <span style='margin-left: 5px; color: #9CA3AF;'>({int(stats['avg_duration_min'] * stats['customer_ratio'] / 100)}:{int(stats['avg_duration_sec'] * stats['customer_ratio'] / 100):02d} min)</span>
            </div>
            
            <div style='margin-bottom: 8px;'>
                <b>Hold Time:</b> 
                <span style='color: #6B7280'>{stats['silence_ratio']:.1f}%</span>
                <span style='margin-left: 5px; color: #9CA3AF;'>({int(stats['avg_duration_sec'] * stats['silence_ratio'] / 100)} sec)</span>
            </div>
            
            <hr style='border: none; border-top: 1px solid #E5E7EB; margin: 15px 0;'>
            
            <div style='margin-bottom: 8px;'>
                <b>Sentiment Delta:</b> 
                <span style='color: {sentiment_color}; font-weight: 600;'>{stats['sentiment_delta']:+.2f}</span>
                <span style='margin-left: 5px; font-size: 11px;'>({sentiment_label})</span>
            </div>
            
            <div style='margin-bottom: 8px;'>
                <b>Compliance Pass Rate:</b> 
                <span style='color: {COLORS["success"] if stats["compliance_pass_rate"] >= 80 else COLORS["warning"]}; font-weight: 600;'>
                    {stats['compliance_pass_rate']:.1f}%
                </span>
            </div>
        </div>
        
        <div style='background-color: #EFF6FF; padding: 10px; border-radius: 4px; margin-top: 15px; font-size: 11px; color: #1E40AF;'>
            ℹ️ Based on {stats['total_calls']} calls analyzed. Detailed timeline view available in Calls tab.
        </div>
    </div>
    """
    
    return html
