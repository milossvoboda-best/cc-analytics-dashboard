# CC Analytics Dashboard - Redesign V2

## 🎯 Overview

Complete redesign of the dashboard with **10 professional business widgets** across **6 rows**.

**Branch:** `redesign-v2`  
**Original Version:** Preserved in `main` branch

---

## ✅ What's Implemented

### 📦 **Enhanced Mock Data** (Phase 1)
- ✅ **WPM** in each transcript segment (real calculation)
- ✅ **Sales Opportunities** (only for Sales team)
  - Types: Upsell, Cross-sell, Closing
  - Success rates & values (EUR)
- ✅ **AutoQA Score** (0-100, separate from quality_score)
- ✅ **Benchmark AHT** per topic

### 🎨 **All 10 Widgets Complete** (Phase 2-4)

#### **ROW 1: Key Performance Indicators**
1. ✅ **AES Card** - Spider chart (4 axes) + Status box
   - Sentiment (25%), Compliance (30%), Resolution (30%), Quality (15%)
   - Status badges, trends vs target & last week
   
2. ✅ **Compliance Card** - Big number display
   - Critical violations count, Risk level, Trend arrow
   
3. ✅ **Sales Summary** - NEW! 
   - Upsell/Cross-sell/Closing metrics with trends
   - Total opportunities, Conversion rate, Total value (EUR)

#### **ROW 2: Customer Experience**
4. ✅ **Sentiment Sankey** - Journey visualization
   - Flow from start → end sentiment
   - Summary stats (improving/stable/declining)
   
5. ✅ **FCR Gauges** - Dual display
   - Predicted FCR (from analysis)
   - Validated FCR (no callback 48h)
   - Gap analysis & insights

#### **ROW 3: Performance Trends**
6. ✅ **Performance Trend** - Switchable tabs
   - 5 tabs: AES | AutoQA | FCR | Sentiment | AHT
   - 30-day line charts with trends
   - Peak/Low indicators

#### **ROW 4: Efficiency & Escalation**
7. ✅ **Topic Bubble Chart** - Matrix view
   - Y-axis = Topics
   - X-axis = Average Handling Time
   - Bubble size = Total call volume
   - Color-coded vs benchmark (green/yellow/red)
   
8. ✅ **Escalation Card** - EPR metrics
   - Escalation Prevention Rate (big number)
   - Top 3 escalation reasons
   - Trend vs last week

#### **ROW 5: Quality Breakdown**
9. ✅ **Quality Bars** - 8 component analysis
   - Horizontal bars for: Greeting, Listening, Empathy, Solution, Tone, Language, Control, Closing
   - Color-coded scores, Trend indicators

#### **ROW 6: Timeline**
10. ✅ **Timeline Summary** - Average stats
    - Avg duration, Talk ratios (agent/customer/hold)
    - Sentiment delta, Compliance pass rate
    - *(Can be expanded to full Gantt-style timeline)*

---

## 📂 File Structure

```
cc_analytics_demo/
├── widgets_v2/              # ✅ NEW: All redesigned widgets
│   ├── __init__.py
│   ├── aes_card.py
│   ├── compliance_card.py
│   ├── sales_card.py       # ✅ NEW!
│   ├── sentiment_sankey.py
│   ├── fcr_gauges.py
│   ├── performance_trend.py # ✅ NEW!
│   ├── topic_bubble.py
│   ├── escalation_card.py
│   ├── quality_bars.py
│   └── timeline_simple.py
│
├── data_generation.py       # ✅ ENHANCED with sales & WPM
├── app_v2_demo.py          # ✅ Demo showing first 3 rows (6 widgets)
├── REDESIGN_PLAN.md        # Implementation plan
└── README_REDESIGN.md      # This file

# Original files (unchanged in this branch):
├── app.py                  # Original dashboard
├── styles.css              # Original CSS
└── [other widgets]         # Original widget files
```

---

## 🎨 Design System

### Colors
- **Primary:** #1E3A8A (Dark blue)
- **Success:** #10B981 (Green)
- **Warning:** #F59E0B (Amber)
- **Danger:** #EF4444 (Red)
- **Neutral:** #6B7280 (Gray)

### Typography
- **Font:** Inter
- **Headers:** 16px Bold
- **Labels:** 12px Medium
- **Big numbers:** 24-48px SemiBold

### Layout
- **Cards:** White bg, 8px border-radius, subtle shadow
- **Spacing:** 8-16px padding
- **Compact design:** NO SCROLL on 1920px desktop

---

## 🚀 How to Run

### Demo (First 6 widgets)
```bash
streamlit run app_v2_demo.py
```

### Full App (Coming soon)
```bash
streamlit run app_v2.py  # Not yet created
```

---

## 📊 Data Schema Changes

### New Call Fields
```python
call = {
    # ... existing fields ...
    
    'sales_opportunity': {      # None if not Sales team
        'type': 'upsell' | 'cross_sell' | 'closing',
        'success': bool,
        'value': float,         # EUR
        'product': str
    },
    'autoqa_score': float,      # 0-100 (separate from quality_score)
    'benchmark_aht': float,     # Minutes (per topic)
}
```

### New Transcript Segment Fields
```python
segment = {
    # ... existing fields ...
    'wpm': int,  # ✅ Real WPM calculated from segment duration & word count
}
```

---

## 🎯 Next Steps

### Immediate
- [ ] Create full `app_v2.py` with all 10 widgets
- [ ] Add CSS styling (`styles_v2.css`)
- [ ] Test on different screen sizes

### Future Enhancements
- [ ] Full timeline widget (Gantt-style with WPM curves)
- [ ] Expand Timeline to show individual call selection
- [ ] Add agent-level drilldown
- [ ] Export to PDF/Excel functionality

---

## 🔄 Git Workflow

### View Redesign
```bash
git checkout redesign-v2
streamlit run app_v2_demo.py
```

### View Original
```bash
git checkout main
streamlit run app.py
```

### Merge When Ready
```bash
git checkout main
git merge redesign-v2
```

---

## 📝 Notes

- **Original dashboard preserved** in `main` branch (backup for management)
- **All widgets modular** - can be reused independently
- **Mock data generation enhanced** - more realistic & complete
- **Design follows spec** - clean professional business look

---

## 🐛 Known Issues / TODO

- [ ] Escalation data needs to be added to mock generation (currently using placeholder)
- [ ] Issue category mapping needs refinement
- [ ] Timeline widget simplified (full version TBD)
- [ ] Add filtering by date range, team, agent

---

**Status:** ✅ All 10 widgets complete, ready for integration testing  
**Last Updated:** 2025-10-22 15:10 UTC+02:00
