"""
Widgets V2 - Redesigned Dashboard Components
Clean, professional business dashboard widgets
"""

from .aes_card import create_aes_card, calculate_aes_components, get_aes_component_breakdown
from .compliance_card import create_compliance_card_html, calculate_compliance_score
from .sales_card import create_sales_card_html, calculate_sales_metrics
from .sentiment_sankey import create_sentiment_sankey, create_sentiment_summary_html, calculate_sentiment_flows
from .fcr_gauges import create_fcr_gauges, create_fcr_summary_html, get_fcr_insights, calculate_fcr_metrics
from .performance_trend import create_performance_trend, create_trend_summary_html, prepare_trend_data

__all__ = [
    # ROW 1
    'create_aes_card',
    'calculate_aes_components',
    'get_aes_component_breakdown',
    'create_compliance_card_html',
    'calculate_compliance_score',
    'create_sales_card_html',
    'calculate_sales_metrics',
    # ROW 2
    'create_sentiment_sankey',
    'create_sentiment_summary_html',
    'calculate_sentiment_flows',
    'create_fcr_gauges',
    'create_fcr_summary_html',
    'get_fcr_insights',
    'calculate_fcr_metrics',
    # ROW 3
    'create_performance_trend',
    'create_trend_summary_html',
    'prepare_trend_data',
]
