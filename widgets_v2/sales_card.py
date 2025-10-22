"""
Widget 3: Sales Performance Summary
Layout: 3 metrics (Upsell/Cross-sell/Closing) with trends
"""

import pandas as pd
from typing import Dict


COLORS = {
    'primary': '#1E3A8A',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'neutral': '#6B7280',
}


def calculate_sales_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculates sales performance metrics from calls.
    
    Only counts calls from Sales team with sales_opportunity data.
    
    Returns:
        Dict with upsell, cross_sell, closing counts and success rates
    """
    
    # Filter only Sales team calls with opportunities
    sales_calls = df[
        (df['team'] == 'Sales') & 
        (df['sales_opportunity'].notna())
    ].copy()
    
    if len(sales_calls) == 0:
        return {
            'upsell_count': 0,
            'cross_sell_count': 0,
            'closing_count': 0,
            'upsell_success': 0,
            'cross_sell_success': 0,
            'closing_success': 0,
            'total_opportunities': 0,
            'total_success': 0,
            'conversion_rate': 0.0,
            'total_value': 0.0
        }
    
    # Count by type
    upsell_opps = sales_calls[sales_calls['sales_opportunity'].apply(lambda x: x['type'] == 'upsell')]
    cross_sell_opps = sales_calls[sales_calls['sales_opportunity'].apply(lambda x: x['type'] == 'cross_sell')]
    closing_opps = sales_calls[sales_calls['sales_opportunity'].apply(lambda x: x['type'] == 'closing')]
    
    # Count successes
    upsell_success = upsell_opps[upsell_opps['sales_opportunity'].apply(lambda x: x['success'])].shape[0]
    cross_sell_success = cross_sell_opps[cross_sell_opps['sales_opportunity'].apply(lambda x: x['success'])].shape[0]
    closing_success = closing_opps[closing_opps['sales_opportunity'].apply(lambda x: x['success'])].shape[0]
    
    total_opportunities = len(sales_calls)
    total_success = upsell_success + cross_sell_success + closing_success
    conversion_rate = (total_success / total_opportunities * 100) if total_opportunities > 0 else 0.0
    
    # Calculate total value (only successful)
    total_value = sales_calls[
        sales_calls['sales_opportunity'].apply(lambda x: x['success'])
    ]['sales_opportunity'].apply(lambda x: x['value']).sum()
    
    return {
        'upsell_count': len(upsell_opps),
        'cross_sell_count': len(cross_sell_opps),
        'closing_count': len(closing_opps),
        'upsell_success': upsell_success,
        'cross_sell_success': cross_sell_success,
        'closing_success': closing_success,
        'total_opportunities': total_opportunities,
        'total_success': total_success,
        'conversion_rate': round(conversion_rate, 1),
        'total_value': round(total_value, 2)
    }


def calculate_sales_trends(current_metrics: Dict, prev_metrics: Dict = None) -> Dict:
    """
    Calculates trend indicators (% change vs previous period).
    
    Returns:
        Dict with trend arrows and % changes
    """
    
    if not prev_metrics:
        return {
            'upsell_trend': '➡️ 0%',
            'cross_sell_trend': '➡️ 0%',
            'closing_trend': '➡️ 0%',
            'upsell_color': COLORS['neutral'],
            'cross_sell_color': COLORS['neutral'],
            'closing_color': COLORS['neutral']
        }
    
    def calc_trend(current, previous):
        if previous == 0:
            return '⬆️ +100%' if current > 0 else '➡️ 0%', COLORS['success'] if current > 0 else COLORS['neutral']
        
        pct_change = ((current - previous) / previous) * 100
        
        if pct_change > 0:
            return f'⬆️ +{pct_change:.0f}%', COLORS['success']
        elif pct_change < 0:
            return f'⬇️ {pct_change:.0f}%', COLORS['danger']
        else:
            return '➡️ 0%', COLORS['neutral']
    
    upsell_trend, upsell_color = calc_trend(current_metrics['upsell_success'], prev_metrics.get('upsell_success', 0))
    cross_sell_trend, cross_sell_color = calc_trend(current_metrics['cross_sell_success'], prev_metrics.get('cross_sell_success', 0))
    closing_trend, closing_color = calc_trend(current_metrics['closing_success'], prev_metrics.get('closing_success', 0))
    
    return {
        'upsell_trend': upsell_trend,
        'cross_sell_trend': cross_sell_trend,
        'closing_trend': closing_trend,
        'upsell_color': upsell_color,
        'cross_sell_color': cross_sell_color,
        'closing_color': closing_color
    }


def create_sales_card_html(df: pd.DataFrame, prev_period_df: pd.DataFrame = None) -> str:
    """
    Creates HTML for sales performance card.
    
    Args:
        df: Current period filtered calls DataFrame
        prev_period_df: Previous period DataFrame for trends
        
    Returns:
        HTML string for Streamlit markdown
    """
    
    metrics = calculate_sales_metrics(df)
    
    # Calculate trends
    prev_metrics = calculate_sales_metrics(prev_period_df) if prev_period_df is not None else None
    trends = calculate_sales_trends(metrics, prev_metrics)
    
    html = f"""
    <div style='background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 280px;'>
        <h3 style='font-family: Inter; font-size: 16px; font-weight: 600; color: {COLORS['primary']}; margin: 0 0 20px 0;'>
            Sales Performance
        </h3>
        
        <div style='font-size: 14px; color: {COLORS['neutral']}; line-height: 2.2;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span><b>Upsell:</b></span>
                <span>
                    <b style='font-size: 18px; color: {COLORS['primary']}'>{metrics['upsell_success']}</b>
                    <span style='margin-left: 10px; font-size: 12px; color: {trends['upsell_color']}'>{trends['upsell_trend']}</span>
                </span>
            </div>
            
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span><b>Cross-sell:</b></span>
                <span>
                    <b style='font-size: 18px; color: {COLORS['primary']}'>{metrics['cross_sell_success']}</b>
                    <span style='margin-left: 10px; font-size: 12px; color: {trends['cross_sell_color']}'>{trends['cross_sell_trend']}</span>
                </span>
            </div>
            
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
                <span><b>Closing:</b></span>
                <span>
                    <b style='font-size: 18px; color: {COLORS['primary']}'>{metrics['closing_success']}</b>
                    <span style='margin-left: 10px; font-size: 12px; color: {trends['closing_color']}'>{trends['closing_trend']}</span>
                </span>
            </div>
            
            <hr style='border: none; border-top: 1px solid #E5E7EB; margin: 15px 0;'>
            
            <div style='margin-top: 15px;'>
                <div style='margin-bottom: 8px;'>
                    <b>Total Opportunities:</b> {metrics['total_opportunities']}
                </div>
                <div style='margin-bottom: 8px;'>
                    <b>Conversion Rate:</b> <span style='color: {COLORS['success'] if metrics['conversion_rate'] >= 50 else COLORS['warning']}'>{metrics['conversion_rate']:.1f}%</span>
                </div>
                <div>
                    <b>Total Value:</b> €{metrics['total_value']:,.2f}
                </div>
            </div>
        </div>
    </div>
    """
    
    return html
