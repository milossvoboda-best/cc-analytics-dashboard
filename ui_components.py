"""
CC Analytics - UI Components Module
Helper funkcie pre vizualizácie a UI widgety
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List


# ============================================================================
# COLORS & STYLING
# ============================================================================

COLOR_SCHEME = {
    "primary": "#2d4a6f",
    "secondary": "#1e3a5f",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "mint": "#7dd3c0",
    "mint_light": "#a8e6d7",
    "pink": "#e85d75",
    "agent": "#2d4a6f",
    "customer": "#f59e0b",
    "silence": "#d1d5db",
    "hold": "#ef4444",
}


# ============================================================================
# GAUGE CHARTS
# ============================================================================

def create_gauge_chart(
    value: float,
    title: str,
    max_value: float = 100,
    thresholds: Dict = None
) -> go.Figure:
    """
    Vytvorí gauge chart (ciferník).
    
    Args:
        value: Hodnota metriky
        title: Názov metriky
        max_value: Maximálna hodnota škály
        thresholds: Dict s {"low": 40, "medium": 70} - hranice pre farby
        
    Returns:
        Plotly Figure
    """
    if thresholds is None:
        thresholds = {"low": 40, "medium": 70}
    
    # Farba podľa hodnoty
    if value >= thresholds.get("medium", 70):
        bar_color = COLOR_SCHEME["success"]
    elif value >= thresholds.get("low", 40):
        bar_color = COLOR_SCHEME["warning"]
    else:
        bar_color = COLOR_SCHEME["danger"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 18, 'color': '#1e293b'}},
        number={'font': {'size': 40, 'color': '#1e293b'}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, thresholds.get("low", 40)], 'color': '#fee2e2'},
                {'range': [thresholds.get("low", 40), thresholds.get("medium", 70)], 'color': '#fef3c7'},
                {'range': [thresholds.get("medium", 70), max_value], 'color': '#dcfce7'}
            ],
            'threshold': {
                'line': {'color': bar_color, 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="white",
        font={'family': "Arial, sans-serif"}
    )
    
    return fig


# ============================================================================
# AES COMPONENT BREAKDOWN (HORIZONTAL BARS)
# ============================================================================

def create_aes_component_chart(components: Dict[str, float]) -> go.Figure:
    """
    Vytvorí horizontal bar chart pre AES component breakdown.
    
    Args:
        components: Dict s názvami a hodnotami {"Sentiment": 18.6, "Compliance": 27.1, ...}
        
    Returns:
        Plotly Figure
    """
    names = list(components.keys())
    values = list(components.values())
    colors = [COLOR_SCHEME["mint"], COLOR_SCHEME["primary"], COLOR_SCHEME["warning"], COLOR_SCHEME["info"]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=values,
        y=names,
        orientation='h',
        marker=dict(
            color=colors[:len(names)],
            line=dict(color='white', width=2)
        ),
        text=[f"{v:.1f}" for v in values],
        textposition='inside',
        textfont=dict(size=14, color='white', family='Inter'),
        hovertemplate='%{y}: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='#e5e7eb',
            range=[0, 35],
            title_text="Score",
            title_font=dict(size=12, color='#64748b')
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=12, family='Inter', color='#1e3a5f')
        ),
        font=dict(family='Inter'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter"
        )
    )
    
    return fig


# ============================================================================
# SENTIMENT JOURNEY CHART
# ============================================================================

def create_sentiment_journey_chart(journey: List[tuple]) -> go.Figure:
    """
    Vytvorí line chart pre sentiment journey.
    
    Args:
        journey: List of (label, sentiment, position) tuples
        
    Returns:
        Plotly Figure
    """
    labels = [j[0] for j in journey]
    sentiments = [j[1] for j in journey]
    positions = [j[2] for j in journey]
    
    # Farba podľa trendu
    colors = []
    for s in sentiments:
        if s >= 0.3:
            colors.append(COLOR_SCHEME["success"])
        elif s >= 0:
            colors.append(COLOR_SCHEME["info"])
        elif s >= -0.3:
            colors.append(COLOR_SCHEME["warning"])
        else:
            colors.append(COLOR_SCHEME["danger"])
    
    fig = go.Figure()
    
    # Line
    fig.add_trace(go.Scatter(
        x=positions,
        y=sentiments,
        mode='lines+markers',
        line=dict(color=COLOR_SCHEME["primary"], width=3),
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=2, color='white')
        ),
        text=labels,
        hovertemplate='<b>%{text}</b><br>Sentiment: %{y:.3f}<extra></extra>'
    ))
    
    # Zero reference line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="Customer Sentiment Journey",
        xaxis_title="Call Progress (%)",
        yaxis_title="Sentiment Score",
        height=300,
        margin=dict(l=40, r=20, t=50, b=40),
        yaxis=dict(range=[-1.1, 1.1], tickformat=".2f"),
        xaxis=dict(tickvals=positions, ticktext=labels),
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    
    return fig


# ============================================================================
# BAR CHARTS
# ============================================================================

def create_horizontal_bar_chart(
    data: Dict,
    title: str,
    x_label: str = "Count",
    color: str = None
) -> go.Figure:
    """
    Horizontálny bar chart.
    
    Args:
        data: Dict {label: value}
        title: Nadpis
        x_label: Label X osi
        color: Farba (ak None, použije primary)
        
    Returns:
        Plotly Figure
    """
    if color is None:
        color = COLOR_SCHEME["primary"]
    
    df = pd.DataFrame(list(data.items()), columns=["Category", "Value"])
    df = df.sort_values("Value", ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df["Value"],
        y=df["Category"],
        orientation='h',
        marker=dict(color=color),
        text=df["Value"],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        height=max(250, len(data) * 40),
        margin=dict(l=120, r=40, t=50, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=False)
    
    return fig


# ============================================================================
# PIE CHARTS
# ============================================================================

def create_pie_chart(data: Dict, title: str) -> go.Figure:
    """
    Pie chart pre distribúcie.
    
    Args:
        data: Dict {category: count}
        title: Nadpis
        
    Returns:
        Plotly Figure
    """
    labels = list(data.keys())
    values = list(data.values())
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Donut style
        marker=dict(
            colors=px.colors.qualitative.Set3
        ),
        textinfo='label+percent',
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='white'
    )
    
    return fig


# ============================================================================
# LINE CHARTS
# ============================================================================

def create_trend_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    y_label: str = "Value"
) -> go.Figure:
    """
    Line chart pre trendy.
    
    Args:
        df: DataFrame
        x_col: Názov X stĺpca (napr. date)
        y_col: Názov Y stĺpca (metrika)
        title: Nadpis
        y_label: Label Y osi
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        line=dict(color=COLOR_SCHEME["primary"], width=2),
        marker=dict(size=8, color=COLOR_SCHEME["secondary"]),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label,
        height=300,
        margin=dict(l=40, r=20, t=50, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    
    return fig


# ============================================================================
# TIMELINE / GANTT CHART
# ============================================================================

def create_timeline_figure(
    segments: List[Dict],
    silence_periods: List[Dict],
    markers: List[Dict],
    interruptions: List[Dict] = None
) -> go.Figure:
    """
    Vytvorí timeline vizualizáciu hovoru.
    
    Args:
        segments: List segmentov {speaker, text, start_time, end_time}
        silence_periods: List tichých období {start, end, type}
        markers: List sentiment markers {time, label, sentiment}
        interruptions: List prerušení {time, interrupter, interrupted}
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # 1. Segmenty ako horizontálne bars
    for seg in segments:
        y_pos = 1 if seg["speaker"] == "AGENT" else 0
        color = COLOR_SCHEME["agent"] if seg["speaker"] == "AGENT" else COLOR_SCHEME["customer"]
        
        duration = seg["end_time"] - seg["start_time"]
        
        fig.add_trace(go.Bar(
            x=[duration],
            y=[y_pos],
            base=[seg["start_time"]],
            orientation='h',
            name=seg["speaker"],
            marker=dict(color=color, opacity=0.8),
            hovertext=f"{seg['speaker']}: {seg['text']}",
            hovertemplate='%{hovertext}<br>Time: %{base:.1f}s - %{x:.1f}s<extra></extra>',
            showlegend=False
        ))
    
    # 2. Silence overlays ako shapes
    for s in silence_periods:
        color = "lightgrey" if s["type"] == "pause" else COLOR_SCHEME["hold"]
        opacity = 0.2 if s["type"] == "pause" else 0.3
        
        fig.add_shape(
            type="rect",
            x0=s["start"], x1=s["end"],
            y0=-0.4, y1=1.4,
            line=dict(width=0),
            fillcolor=color,
            opacity=opacity,
            layer="below"
        )
    
    # 3. Sentiment markers ako scatter points
    for m in markers:
        # Farba podľa sentimentu
        sentiment = m.get("sentiment", 0)
        if sentiment >= 0.3:
            marker_color = COLOR_SCHEME["success"]
        elif sentiment >= 0:
            marker_color = COLOR_SCHEME["info"]
        elif sentiment >= -0.3:
            marker_color = COLOR_SCHEME["warning"]
        else:
            marker_color = COLOR_SCHEME["danger"]
        
        fig.add_trace(go.Scatter(
            x=[m["time"]],
            y=[1.3],
            mode="markers+text",
            marker=dict(size=12, color=marker_color, symbol="star"),
            text=[m["label"]],
            textposition="top center",
            textfont=dict(size=10, color="#1e293b"),
            hovertext=f"{m['label']}: {sentiment:.2f}",
            hovertemplate='%{hovertext}<extra></extra>',
            showlegend=False
        ))
    
    # 4. Interruptions (ak sú)
    if interruptions:
        for intr in interruptions:
            # Blesk symbol
            color = COLOR_SCHEME["danger"] if intr["interrupter"] == "AGENT" else COLOR_SCHEME["warning"]
            
            fig.add_trace(go.Scatter(
                x=[intr["time"]],
                y=[0.5],
                mode="markers",
                marker=dict(size=14, color=color, symbol="diamond", line=dict(width=2, color="white")),
                hovertext=f"Interruption: {intr['interrupter']} → {intr['interrupted']}",
                hovertemplate='%{hovertext}<extra></extra>',
                showlegend=False
            ))
    
    # Layout
    fig.update_layout(
        barmode='overlay',
        height=300,
        margin=dict(l=80, r=40, t=40, b=50),
        xaxis_title="Time (seconds)",
        yaxis=dict(
            tickvals=[0, 1],
            ticktext=["CUSTOMER", "AGENT"],
            range=[-0.5, 1.6]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=False)
    
    return fig


# ============================================================================
# TABLE / DATAFRAME STYLING
# ============================================================================

def style_risk_level(level: str) -> str:
    """
    HTML span s farbou pre risk level.
    
    Args:
        level: "Low" | "Medium" | "High"
        
    Returns:
        HTML string
    """
    class_map = {
        "Low": "risk-low",
        "Medium": "risk-medium",
        "High": "risk-high"
    }
    
    css_class = class_map.get(level, "risk-medium")
    return f'<span class="{css_class}">{level}</span>'


def format_duration(seconds: float) -> str:
    """
    Formátuje dĺžku z sekúnd na mm:ss.
    
    Args:
        seconds: Počet sekúnd
        
    Returns:
        Formatted string "5:23"
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formátuje číslo na percentá.
    
    Args:
        value: Hodnota (0-100)
        decimals: Počet desatinných miest
        
    Returns:
        "85.3%"
    """
    return f"{value:.{decimals}f}%"


# ============================================================================
# PROGRESS BARS (HTML)
# ============================================================================

def create_progress_bar_html(
    label: str,
    value: float,
    max_value: float = 100,
    color: str = None
) -> str:
    """
    HTML progress bar.
    
    Args:
        label: Názov
        value: Hodnota
        max_value: Maximum
        color: Farba (hex)
        
    Returns:
        HTML string
    """
    if color is None:
        color = COLOR_SCHEME["primary"]
    
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    
    html = f"""
    <div style="margin-bottom: 0.5rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span style="font-size: 0.875rem; font-weight: 500; color: #475569;">{label}</span>
            <span style="font-size: 0.875rem; color: #64748b;">{value:.1f} / {max_value}</span>
        </div>
        <div style="width: 100%; background-color: #e2e8f0; border-radius: 9999px; height: 8px; overflow: hidden;">
            <div style="width: {percentage}%; background-color: {color}; height: 100%; border-radius: 9999px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """
    
    return html


# ============================================================================
# METRIC CARDS (HTML)
# ============================================================================

def create_metric_card_html(title: str, value: str, delta: str = None, icon: str = "📊") -> str:
    """
    HTML metric card.
    
    Args:
        title: Názov metriky
        value: Hodnota
        delta: Delta (zmena)
        icon: Emoji ikona
        
    Returns:
        HTML string
    """
    delta_html = ""
    if delta:
        delta_color = COLOR_SCHEME["success"] if "+" in delta or "↑" in delta else COLOR_SCHEME["danger"]
        delta_html = f'<div style="font-size: 0.875rem; color: {delta_color}; font-weight: 600;">{delta}</div>'
    
    html = f"""
    <div class="metric-card">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-size: 0.875rem; color: #64748b; font-weight: 500;">{title}</span>
            <span style="font-size: 1.5rem;">{icon}</span>
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 0.25rem;">{value}</div>
        {delta_html}
    </div>
    """
    
    return html


# ============================================================================
# NEW UI COMPONENTS FOR V2
# ============================================================================

def mini_metric_card(title: str, value: str, delta: str = None, color: str = "#667eea") -> str:
    """
    Mini HTML metric card.
    
    Args:
        title: Názov
        value: Hodnota
        delta: Voliteľná delta
        color: Border farba
        
    Returns:
        HTML string
    """
    delta_html = ""
    if delta:
        delta_html = f'<div class="text-small text-muted">{delta}</div>'
    
    return f"""
    <div class="mini-card" style="border-left-color: {color};">
        <div class="mini-card-title">{title}</div>
        <div class="mini-card-value">{value}</div>
        {delta_html}
    </div>
    """


def legend_badge(label: str, color: str) -> str:
    """
    HTML badge pre legendu.
    
    Args:
        label: Text
        color: Farba pozadia
        
    Returns:
        HTML string
    """
    return f'<span class="badge" style="background-color: {color}; color: #0f172a; margin-right: 0.5rem;">{label}</span>'


def sentiment_transition_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    3x3 heatmap sentiment transition matrix (Start → End).
    
    Args:
        df: DataFrame s start_bucket a end_bucket stĺpcami
        
    Returns:
        Plotly Figure
    """
    from metrics import compute_sentiment_buckets
    
    transitions = compute_sentiment_buckets(df)
    
    if len(transitions) == 0:
        # Empty heatmap
        fig = go.Figure()
        fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300, margin=dict(l=40, r=20, t=40, b=40))
        return fig
    
    # Create 3x3 matrix
    buckets = ["Neg", "Neutral", "Pos"]
    matrix = [[0 for _ in range(3)] for _ in range(3)]
    hover_text = [["" for _ in range(3)] for _ in range(3)]
    
    for _, row in transitions.iterrows():
        start_idx = buckets.index(row["start_bucket"])
        end_idx = buckets.index(row["end_bucket"])
        matrix[start_idx][end_idx] = row["pct"]
        hover_text[start_idx][end_idx] = f"{row['count']} calls ({row['pct']}%)"
    
    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=buckets,
        y=buckets,
        colorscale="Blues",
        text=[[f"{val:.1f}%" if val > 0 else "" for val in row] for row in matrix],
        texttemplate="%{text}",
        textfont={"size": 14, "color": "#0f172a"},
        hovertext=hover_text,
        hovertemplate='Start: %{y}<br>End: %{x}<br>%{hovertext}<extra></extra>',
        showscale=False
    ))
    
    fig.update_layout(
        title="Sentiment Transition Matrix",
        xaxis_title="End Sentiment",
        yaxis_title="Start Sentiment",
        height=320,
        margin=dict(l=60, r=20, t=50, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(side="bottom")
    fig.update_yaxes(autorange="reversed")
    
    return fig


def sentiment_transition_chart(df: pd.DataFrame) -> go.Figure:
    """
    Stacked bar chart showing sentiment flow (compact).
    """
    from metrics import compute_sentiment_buckets
    
    transitions = compute_sentiment_buckets(df)
    
    if len(transitions) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=250, margin=dict(l=40, r=20, t=20, b=40))
        return fig
    
    buckets = ["Neg", "Neutral", "Pos"]
    colors_map = {"Neg": "#ef4444", "Neutral": "#f59e0b", "Pos": "#10b981"}
    
    fig = go.Figure()
    
    for end_bucket in buckets:
        values = []
        for start_bucket in buckets:
            row = transitions[(transitions["start_bucket"] == start_bucket) & (transitions["end_bucket"] == end_bucket)]
            val = row["pct"].values[0] if len(row) > 0 else 0
            values.append(val)
        
        fig.add_trace(go.Bar(
            name=end_bucket,
            x=buckets,
            y=values,
            marker=dict(color=colors_map[end_bucket]),
            text=[f"{v:.0f}%" if v > 2 else "" for v in values],
            textposition='inside',
            textfont=dict(size=11, color='white')
        ))
    
    fig.update_layout(
        barmode='stack',
        height=280,
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_text="Start Sentiment", tickfont=dict(size=12)),
        yaxis=dict(title_text="% of Calls", tickfont=dict(size=12)),
        legend=dict(
            title_text="End State",
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1
        ),
        font=dict(family='Inter')
    )
    
    return fig


def aht_vs_benchmark_dumbbell(tre_df: pd.DataFrame) -> go.Figure:
    """
    Dumbbell/lollipop chart: AHT vs Benchmark by topic.
    
    Args:
        tre_df: DataFrame s topic, avg_time, benchmark
        
    Returns:
        Plotly Figure
    """
    if len(tre_df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300, margin=dict(l=40, r=20, t=40, b=40))
        return fig
    
    tre_df = tre_df.sort_values("avg_time", ascending=True)
    
    fig = go.Figure()
    
    # Draw lines connecting benchmark to actual
    for _, row in tre_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["benchmark"], row["avg_time"]],
            y=[row["topic"], row["topic"]],
            mode="lines",
            line=dict(color="#cbd5e1", width=2),
            showlegend=False,
            hoverinfo="skip"
        ))
    
    # Benchmark markers
    fig.add_trace(go.Scatter(
        x=tre_df["benchmark"],
        y=tre_df["topic"],
        mode="markers",
        marker=dict(size=10, color="#94a3b8", symbol="line-ns-open", line=dict(width=2)),
        name="Benchmark",
        hovertemplate='%{y}<br>Benchmark: %{x:.0f}s<extra></extra>'
    ))
    
    # Actual AHT markers
    colors = [COLOR_SCHEME["success"] if row["avg_time"] <= row["benchmark"] else COLOR_SCHEME["danger"] 
              for _, row in tre_df.iterrows()]
    
    fig.add_trace(go.Scatter(
        x=tre_df["avg_time"],
        y=tre_df["topic"],
        mode="markers",
        marker=dict(size=14, color=colors),
        name="Actual AHT",
        hovertemplate='%{y}<br>Actual: %{x:.0f}s<br>Variance: %{customdata:.1f}%<extra></extra>',
        customdata=[(row["avg_time"] - row["benchmark"]) / row["benchmark"] * 100 for _, row in tre_df.iterrows()]
    ))
    
    fig.update_layout(
        title="AHT vs Benchmark by Topic",
        xaxis_title="Time (seconds)",
        height=max(250, len(tre_df) * 45),
        margin=dict(l=120, r=40, t=50, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=False)
    
    return fig


def volume_pareto_bars(df: pd.DataFrame) -> go.Figure:
    """
    Pareto chart: Volume by topic s kumulatívnou čiarou.
    
    Args:
        df: DataFrame s calls
        
    Returns:
        Plotly Figure
    """
    from metrics import calculate_volume_distribution
    
    volume_dist = calculate_volume_distribution(df, "topic")
    
    if not volume_dist:
        fig = go.Figure()
        fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300, margin=dict(l=40, r=20, t=40, b=40))
        return fig
    
    # Sort descending
    sorted_items = sorted(volume_dist.items(), key=lambda x: x[1], reverse=True)
    topics = [item[0].capitalize() for item in sorted_items]
    counts = [item[1] for item in sorted_items]
    
    # Calculate cumulative percentage
    total = sum(counts)
    cumulative = []
    cumsum = 0
    for count in counts:
        cumsum += count
        cumulative.append(cumsum / total * 100)
    
    fig = go.Figure()
    
    # Bar chart
    fig.add_trace(go.Bar(
        x=topics,
        y=counts,
        name="Call Count",
        marker=dict(color=COLOR_SCHEME["primary"]),
        text=counts,
        textposition="outside",
        yaxis="y"
    ))
    
    # Cumulative line
    fig.add_trace(go.Scatter(
        x=topics,
        y=cumulative,
        name="Cumulative %",
        mode="lines+markers",
        line=dict(color=COLOR_SCHEME["danger"], width=3),
        marker=dict(size=8),
        yaxis="y2"
    ))
    
    # 80% reference line
    fig.add_hline(y=80, line_dash="dash", line_color="gray", opacity=0.5, yref="y2", 
                  annotation_text="80%", annotation_position="right")
    
    fig.update_layout(
        title="Call Volume Pareto Analysis",
        xaxis_title="Topic",
        yaxis=dict(title="Call Count", side="left"),
        yaxis2=dict(title="Cumulative %", side="right", overlaying="y", range=[0, 100]),
        height=350,
        margin=dict(l=60, r=60, t=50, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(showgrid=False, tickangle=-45)
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    
    return fig


def quality_breakdown_trend_7d(df: pd.DataFrame) -> go.Figure:
    """
    Stacked area chart: 7-day trend 4 QA komponentov + AES overlay.
    
    Args:
        df: DataFrame s quality_components_daily
        
    Returns:
        Plotly Figure
    """
    from metrics import compute_quality_components_daily
    
    daily = compute_quality_components_daily(df)
    
    if len(daily) == 0:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data (need 7 days)", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=350, margin=dict(l=40, r=20, t=40, b=40))
        return fig
    
    fig = go.Figure()
    
    # Stacked area for QA components
    qa_components = [
        ("Active Listening", "active_listening_pct", "#10b981"),
        ("Empathy", "empathy_pct", "#3b82f6"),
        ("Solution Offered", "solution_pct", "#f59e0b"),
        ("Professional Tone", "professional_pct", "#8b5cf6")
    ]
    
    for name, col, color in qa_components:
        fig.add_trace(go.Scatter(
            x=daily["date"],
            y=daily[col],
            name=name,
            mode="lines",
            stackgroup="one",
            fillcolor=color,
            line=dict(width=0),
            hovertemplate=f'{name}: %{{y:.1f}}%<extra></extra>'
        ))
    
    # AES overlay line (secondary axis)
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["aes_avg"],
        name="AES",
        mode="lines+markers",
        line=dict(color="#0f172a", width=3, dash="dash"),
        marker=dict(size=8, color="#0f172a"),
        yaxis="y2",
        hovertemplate='AES: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="7-Day Quality Breakdown Trend",
        xaxis_title="Date",
        yaxis=dict(title="QA Components (%)", side="left", range=[0, 100]),
        yaxis2=dict(title="AES Score", side="right", overlaying="y", range=[0, 100]),
        height=350,
        margin=dict(l=60, r=60, t=50, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    
    return fig
