# CC Analytics Dashboard - Redesign V2 Implementation Plan

## 🎯 Objective
Complete redesign based on detailed visual specification.
**10 widgets in 6 rows** - NO SCROLL, compact business dashboard.

## 📋 Implementation Phases

### Phase 1: Data Layer (PRIORITY)
- [ ] Add SALES data to mock generation (upsell/cross-sell/closing)
- [ ] Add AutoQA score field (separate from quality_score)
- [ ] Ensure all metrics have proper historical data (7-30 days)
- [ ] Add benchmark data for topics

### Phase 2: Core Layout (ROW 1-3)
- [ ] **ROW 1**: Three KPI cards
  - [ ] Widget 1: AES (Spider + Status Box side-by-side)
  - [ ] Widget 2: Compliance Score (Big number + trend)
  - [ ] Widget 3: Sales Summary (3 metrics + trends)

- [ ] **ROW 2**: Sentiment + FCR
  - [ ] Widget 4: Customer Sentiment Journey (Sankey + Summary)
  - [ ] Widget 5: FCR Analysis (2 gauges + insights)

- [ ] **ROW 3**: Performance Trend
  - [ ] Widget 6: Switchable Line Chart (5 tabs: AES/AutoQA/FCR/Sentiment/AHT)

### Phase 3: Analytics Widgets (ROW 4-5)
- [ ] **ROW 4**: Efficiency + Escalation
  - [ ] Widget 7: Topic Efficiency Matrix (Bubble: Y=topics, X=AHT)
  - [ ] Widget 8: Escalation Prevention Rate (Big number + reasons)

- [ ] **ROW 5**: Quality Breakdown
  - [ ] Widget 9: Quality Components (Horizontal bars + trends)

### Phase 4: Timeline (ROW 6)
- [ ] **ROW 6**: Call Timeline Analysis
  - [ ] Option A: Average Timeline (default)
  - [ ] Option B: Single Call dropdown
  - [ ] Collapsible section

## 🎨 Design System

### Colors
```python
COLORS = {
    'primary': '#1E3A8A',      # Dark blue
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Amber
    'danger': '#EF4444',       # Red
    'neutral': '#6B7280',      # Gray
    'bg': '#F9FAFB',          # Light gray
    'card': '#FFFFFF',         # White
}
```

### Typography
- Headers: Inter Bold 16px
- Labels: Inter Medium 12px
- Big numbers: Inter SemiBold 24-36px
- Body: Inter Regular 12px

### Layout
- Cards: 16px padding, subtle shadow
- Spacing: 8px between elements
- Compact, NO SCROLL on 1920px desktop

## 📦 New Widget Files

### To Create:
1. `widgets_v2/aes_card.py` - AES Spider + Box
2. `widgets_v2/compliance_card.py` - Compliance big number
3. `widgets_v2/sales_card.py` - Sales 3 metrics (NEW!)
4. `widgets_v2/sentiment_sankey.py` - Refactor existing
5. `widgets_v2/fcr_gauges.py` - 2 gauges side-by-side
6. `widgets_v2/performance_trend.py` - Switchable chart (NEW!)
7. `widgets_v2/topic_bubble.py` - Y-axis = topics (FIX!)
8. `widgets_v2/escalation_card.py` - EPR big number + list
9. `widgets_v2/quality_bars.py` - Horizontal bars + trends
10. `widgets_v2/timeline_avg.py` - Average timeline option

### Main Files:
- `app_v2.py` - New main app with 6-row layout
- `data_generation_v2.py` - Enhanced with sales data
- `styles_v2.css` - Refined clean design

## ⚙️ Technical Requirements

### Data Schema Extensions
```python
# Add to calls DataFrame:
calls = {
    ...existing fields...
    'autoqa_score': float,        # 0-100 (separate from quality)
    'sales_opportunity': dict,     # {type, success, value}
    'benchmark_aht': float,        # For topic comparison
}

# Sales opportunity structure:
{
    'type': 'upsell' | 'cross_sell' | 'closing',
    'success': bool,
    'value': float,  # EUR
    'product': str
}
```

### Widget Interface Standard
```python
def create_widget_X(df: pd.DataFrame, **kwargs) -> go.Figure | str:
    """
    Creates widget X.
    
    Args:
        df: Filtered calls DataFrame
        **kwargs: Widget-specific parameters
        
    Returns:
        Plotly Figure or HTML string
    """
    pass
```

## 🚀 Deployment Strategy

### Branch Structure:
- `main` - Original dashboard (backup)
- `redesign-v2` - New redesign (current)

### Streamlit Apps:
1. **Original**: `https://cc-analytics-dashboard.streamlit.app` (main branch)
2. **Redesign V2**: Deploy as new app or on redesign-v2 branch

### Testing Checklist:
- [ ] All 10 widgets render correctly
- [ ] No scroll on 1920px desktop
- [ ] Responsive on 1024px tablet
- [ ] Load time < 2s
- [ ] All interactions work (tabs, dropdowns, hovers)

## 📝 Notes

- Keep `main` branch intact as fallback
- All new code in `redesign-v2` branch
- Focus on COMPACT layout first
- Mock data must support all new metrics
- Follow exact visual spec from document

## 🎯 Success Criteria

✅ Dashboard matches visual spec exactly
✅ All 10 widgets present and functional
✅ NO SCROLL on main overview
✅ Clean, professional business look
✅ Fast load and interactions
✅ Original version preserved in `main`

---

**Status**: Phase 1 - Data Layer preparation
**Next**: Extend mock data with sales opportunities
