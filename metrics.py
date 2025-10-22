"""
CC Analytics - Metrics Computation Module
Čisté Python funkcie pre výpočet všetkých KPI a metrík
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


# ============================================================================
# COMPLIANCE METRICS
# ============================================================================

# Kritické polia a váhy
CRITICAL_COMPLIANCE_FIELDS = {
    "data_protection_mentioned",
    "customer_verification",
    "no_misleading_info"
}

COMPLIANCE_WEIGHTS = {
    "call_recording_notice": 3,
    "proper_closing": 2,
    "greeting_proper": 1,
}


def compliance_score(comp: Dict) -> Dict:
    """
    Vypočíta compliance score a risk level.
    
    Args:
        comp: Dict s boolean polami compliance
        
    Returns:
        Dict s: score (%), risk_points, risk_level
    """
    # Získaj všetky boolean polia
    bool_items = [k for k, v in comp.items() if isinstance(v, bool)]
    
    if not bool_items:
        return {"score": 0.0, "risk_points": 100, "risk_level": "High"}
    
    passed = sum(1 for k in bool_items if comp[k])
    score = round(100 * passed / len(bool_items), 1)
    
    # Risk points
    risk_points = 0
    
    # Kritické polia = 5 bodov každé
    for critical_field in CRITICAL_COMPLIANCE_FIELDS:
        if not comp.get(critical_field, False):
            risk_points += 5
    
    # Vážené polia
    for field, weight in COMPLIANCE_WEIGHTS.items():
        if not comp.get(field, False):
            risk_points += weight
    
    # Kritické violations = 7 bodov
    critical_violations = comp.get("critical_violations", [])
    if critical_violations:
        risk_points += 7
    
    # Risk level
    if risk_points < 5:
        risk_level = "Low"
    elif risk_points < 15:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    return {
        "score": score,
        "risk_points": risk_points,
        "risk_level": risk_level,
        "critical_violations_count": len(critical_violations)
    }


# ============================================================================
# SENTIMENT METRICS
# ============================================================================

def compute_sentiment_journey(s_start: float, s_mid: float, s_end: float) -> Dict:
    """
    Vypočíta sentiment journey metriky.
    
    Args:
        s_start: Sentiment na začiatku (-1 až +1)
        s_mid: Sentiment v strede
        s_end: Sentiment na konci
        
    Returns:
        Dict s: delta, trend, recovery_rate, journey (list of tuples)
    """
    delta = s_end - s_start
    
    # Trend classification
    if delta > 0.3:
        trend = "Strong Improvement"
    elif delta > 0.1:
        trend = "Slight Improvement"
    elif delta < -0.1:
        trend = "Deterioration"
    else:
        trend = "Stable"
    
    # Recovery rate (len ak začíname v negatíve)
    if s_start < 0:
        recovery_rate = (delta / abs(s_start)) * 100
    elif delta > 0:
        recovery_rate = 100.0
    else:
        recovery_rate = 0.0
    
    journey = [
        ("Start", s_start, 0),
        ("Middle", s_mid, 50),
        ("End", s_end, 100)
    ]
    
    return {
        "delta": round(delta, 3),
        "trend": trend,
        "recovery_rate": round(recovery_rate, 1),
        "journey": journey
    }


# ============================================================================
# RESOLUTION METRICS
# ============================================================================

def is_fcr(res: Dict) -> bool:
    """
    First Contact Resolution check.
    
    Args:
        res: Resolution dict
        
    Returns:
        True ak je FCR (full resolution, no callback, no escalation)
    """
    return (
        res.get("resolution_achieved") == "full" and
        not res.get("callback_needed", False) and
        not res.get("escalated", False)
    )


def calculate_fcr_rate(calls_df: pd.DataFrame) -> Dict:
    """
    Vypočíta FCR rate pre dataset.
    
    Returns:
        Dict s: fcr_rate (%), fcr_count, total_calls
    """
    total = len(calls_df)
    if total == 0:
        return {"fcr_rate": 0.0, "fcr_count": 0, "total_calls": 0}
    
    fcr_count = sum(is_fcr(row["resolution"]) for _, row in calls_df.iterrows())
    fcr_rate = round(100 * fcr_count / total, 1)
    
    return {
        "fcr_rate": fcr_rate,
        "fcr_count": fcr_count,
        "total_calls": total
    }


def calculate_escalation_prevention_rate(calls_df: pd.DataFrame) -> Dict:
    """
    EPR - Escalation Prevention Rate.
    
    Returns:
        Dict s: epr (%), prevented_count, escalated_count, reasons_breakdown
    """
    total = len(calls_df)
    if total == 0:
        return {"epr": 0.0, "prevented_count": 0, "escalated_count": 0, "reasons_breakdown": {}}
    
    escalated_count = sum(row["resolution"].get("escalated", False) for _, row in calls_df.iterrows())
    prevented_count = total - escalated_count
    
    epr = round(100 * prevented_count / total, 1)
    
    # Reasons breakdown
    reasons = {}
    for _, row in calls_df.iterrows():
        if row["resolution"].get("escalated", False):
            reason = row["resolution"].get("escalation_reason", "unknown")
            reasons[reason] = reasons.get(reason, 0) + 1
    
    return {
        "epr": epr,
        "prevented_count": prevented_count,
        "escalated_count": escalated_count,
        "reasons_breakdown": reasons
    }


# ============================================================================
# QUALITY METRICS
# ============================================================================

def quality_binary_score(q: Dict) -> float:
    """
    Vypočíta quality score z boolean polí (%).
    
    Args:
        q: Quality dict
        
    Returns:
        Score 0-100
    """
    binary_items = [
        q.get("active_listening", False),
        q.get("empathy_shown", False),
        q.get("solution_offered", False),
        q.get("professional_tone", False),
    ]
    
    score = round(100 * sum(bool(x) for x in binary_items) / len(binary_items), 1)
    return score


# ============================================================================
# AGENT EFFECTIVENESS SCORE (AES)
# ============================================================================

def aes(
    sentiment_start: float,
    sentiment_end: float,
    comp_score: float,
    res_achieved: str,
    quality_score: float
) -> float:
    """
    Agent Effectiveness Score.
    
    Weights:
        - Sentiment: 25%
        - Compliance: 30%
        - Resolution: 30%
        - Quality: 15%
    
    Args:
        sentiment_start: -1 až +1
        sentiment_end: -1 až +1
        comp_score: 0-100
        res_achieved: "full" | "partial" | "none"
        quality_score: 0-100
        
    Returns:
        AES score 0-100
    """
    # Sentiment component: scale (-1, +1) delta to (0, 100)
    sentiment_delta = sentiment_end - sentiment_start
    sentiment_component = ((sentiment_delta + 2) / 4) * 100  # range: -2..+2 → 0..100
    sentiment_component = max(0, min(100, sentiment_component))
    
    # Resolution component
    if res_achieved == "full":
        resolution_component = 100
    elif res_achieved == "partial":
        resolution_component = 50
    else:
        resolution_component = 0
    
    # Weighted sum
    score = (
        0.25 * sentiment_component +
        0.30 * comp_score +
        0.30 * resolution_component +
        0.15 * quality_score
    )
    
    return round(score, 1)


def calculate_aes_for_call(row: pd.Series) -> float:
    """Helper na výpočet AES pre jeden riadok DataFrame"""
    comp = compliance_score(row["compliance"])
    qual = quality_binary_score(row["quality"])
    
    return aes(
        row["sentiment_start"],
        row["sentiment_end"],
        comp["score"],
        row["resolution"]["resolution_achieved"],
        qual
    )


# ============================================================================
# AGENT CONSISTENCY INDEX (ACI)
# ============================================================================

def aci(aes_series: List[float]) -> Dict:
    """
    Agent Consistency Index - invertovaný coefficient of variation.
    
    Args:
        aes_series: List AES hodnôt pre agenta
        
    Returns:
        Dict s: aci (0-100), stability (label), std, mean
    """
    if len(aes_series) < 2:
        val = aes_series[0] if aes_series else 0.0
        return {
            "aci": 100.0,
            "stability": "N/A",
            "std": 0.0,
            "mean": round(val, 1)
        }
    
    mean = float(np.mean(aes_series))
    std = float(np.std(aes_series))
    
    # Coefficient of variation
    cv = (std / mean) if mean > 0 else 0
    
    # ACI = 100 - (CV * 100)
    score = max(0.0, 100.0 - 100.0 * cv)
    
    # Stability classification
    if score >= 85:
        stability = "Very Stable"
    elif score >= 70:
        stability = "Stable"
    elif score >= 50:
        stability = "Unstable"
    else:
        stability = "Highly Unstable"
    
    return {
        "aci": round(score, 1),
        "stability": stability,
        "std": round(std, 1),
        "mean": round(mean, 1)
    }


# ============================================================================
# TOPIC RESOLUTION EFFICIENCY (TRE)
# ============================================================================

def calculate_tre(calls_df: pd.DataFrame) -> pd.DataFrame:
    """
    Topic Resolution Efficiency - porovnanie AHT s benchmarkom.
    
    Returns:
        DataFrame s: topic, avg_time, benchmark, efficiency %, resolution_rate %, status
    """
    from data_generation import TOPICS
    
    # Benchmarky z TOPICS
    topic_stats = []
    
    for topic in TOPICS.keys():
        topic_calls = calls_df[calls_df["resolution"].apply(lambda x: x["issue_category"] == topic)]
        
        if len(topic_calls) == 0:
            continue
        
        avg_time = topic_calls["duration_sec"].mean()
        benchmark = TOPICS[topic]["avg_duration"]
        
        # Efficiency: nižší čas = lepšie (ak je pod benchmarkom)
        if avg_time <= benchmark:
            efficiency = 100.0
        else:
            efficiency = max(0, 100 * (1 - (avg_time - benchmark) / benchmark))
        
        # Resolution rate
        resolved = sum(topic_calls["resolution"].apply(lambda x: x["resolution_achieved"] == "full"))
        resolution_rate = round(100 * resolved / len(topic_calls), 1)
        
        # Status
        if efficiency >= 90 and resolution_rate >= 80:
            status = "Excellent"
        elif efficiency >= 70 and resolution_rate >= 70:
            status = "Good"
        elif efficiency >= 50:
            status = "Needs Improvement"
        else:
            status = "Critical"
        
        topic_stats.append({
            "topic": topic.capitalize(),
            "avg_time": round(avg_time, 1),
            "benchmark": benchmark,
            "efficiency": round(efficiency, 1),
            "resolution_rate": resolution_rate,
            "status": status,
            "call_count": len(topic_calls)
        })
    
    return pd.DataFrame(topic_stats)


# ============================================================================
# TIME-SERIES & TRENDS
# ============================================================================

def calculate_7day_trend(calls_df: pd.DataFrame, metric_col: str = "aes") -> pd.DataFrame:
    """
    Vypočíta 7-dňový trend pre danú metriku.
    
    Args:
        calls_df: DataFrame s timestamp
        metric_col: názov stĺpca metriky
        
    Returns:
        DataFrame s: date, metric_avg
    """
    if metric_col not in calls_df.columns:
        # Musíme vypočítať
        if metric_col == "aes":
            calls_df["aes"] = calls_df.apply(calculate_aes_for_call, axis=1)
    
    # Groupby date
    calls_df["date"] = pd.to_datetime(calls_df["timestamp"]).dt.date
    
    daily = calls_df.groupby("date")[metric_col].mean().reset_index()
    daily.columns = ["date", "metric_avg"]
    daily["metric_avg"] = daily["metric_avg"].round(1)
    
    # Posledných 7 dní
    daily = daily.sort_values("date").tail(7)
    
    return daily


def calculate_volume_distribution(calls_df: pd.DataFrame, group_by: str = "topic") -> Dict:
    """
    Volume distribution podľa daného atribútu.
    
    Args:
        group_by: "topic", "team", "language", atď.
        
    Returns:
        Dict s counts
    """
    if group_by == "topic":
        counts = calls_df["resolution"].apply(lambda x: x["issue_category"]).value_counts().to_dict()
    elif group_by in calls_df.columns:
        counts = calls_df[group_by].value_counts().to_dict()
    else:
        counts = {}
    
    return counts


# ============================================================================
# AGGREGATE METRICS
# ============================================================================

def calculate_aht(calls_df: pd.DataFrame) -> Dict:
    """
    Average Handle Time.
    
    Returns:
        Dict s: aht (seconds), aht_minutes, target, variance
    """
    if len(calls_df) == 0:
        return {"aht": 0.0, "aht_minutes": 0.0, "target": 300, "variance": 0.0}
    
    aht = calls_df["duration_sec"].mean()
    target = 300  # 5 min benchmark
    variance = aht - target
    
    return {
        "aht": round(aht, 1),
        "aht_minutes": round(aht / 60, 2),
        "target": target,
        "variance": round(variance, 1),
        "variance_pct": round(100 * variance / target, 1) if target > 0 else 0.0
    }


def calculate_agent_aggregates(calls_df: pd.DataFrame, agents_df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-agent agregované metriky.
    
    Returns:
        DataFrame s: agent_id, agent_name, aes_avg, aci, fcr_rate, comp_avg, aht_avg, call_count
    """
    # Vypočítať AES pre všetky hovory
    calls_df["aes"] = calls_df.apply(calculate_aes_for_call, axis=1)
    calls_df["comp_score"] = calls_df["compliance"].apply(lambda x: compliance_score(x)["score"])
    calls_df["is_fcr"] = calls_df["resolution"].apply(is_fcr)
    
    agent_stats = []
    
    for agent_id in calls_df["agent_id"].unique():
        agent_calls = calls_df[calls_df["agent_id"] == agent_id]
        
        if len(agent_calls) == 0:
            continue
        
        aes_values = agent_calls["aes"].tolist()
        aci_result = aci(aes_values)
        
        agent_name = agent_calls.iloc[0]["agent_name"]
        team = agent_calls.iloc[0]["team"]
        
        agent_stats.append({
            "agent_id": agent_id,
            "agent_name": agent_name,
            "team": team,
            "aes_avg": round(agent_calls["aes"].mean(), 1),
            "aci": aci_result["aci"],
            "stability": aci_result["stability"],
            "fcr_rate": round(100 * agent_calls["is_fcr"].sum() / len(agent_calls), 1),
            "comp_avg": round(agent_calls["comp_score"].mean(), 1),
            "aht_avg": round(agent_calls["duration_sec"].mean(), 1),
            "call_count": len(agent_calls)
        })
    
    return pd.DataFrame(agent_stats)


# ============================================================================
# BENCHMARKS & COMPARISONS
# ============================================================================

def compare_to_benchmark(value: float, benchmark: float, higher_is_better: bool = True) -> str:
    """
    Porovná hodnotu s benchmarkom.
    
    Returns:
        "Above" | "On Target" | "Below"
    """
    threshold = 0.05  # 5% tolerance
    
    if abs(value - benchmark) / benchmark <= threshold:
        return "On Target"
    
    if higher_is_better:
        return "Above" if value > benchmark else "Below"
    else:
        return "Below" if value > benchmark else "Above"


# ============================================================================
# SENTIMENT ANALYSIS - NEW FOR UI V2
# ============================================================================

def bucket_sentiment(value: float) -> str:
    """
    Bucketuje sentiment hodnotu do 3 kategórií.
    
    Args:
        value: Sentiment (-1 až +1)
        
    Returns:
        "Neg" | "Neutral" | "Pos"
    """
    if value < -0.2:
        return "Neg"
    elif value <= 0.2:
        return "Neutral"
    else:
        return "Pos"


def compute_sentiment_buckets(calls_df: pd.DataFrame) -> pd.DataFrame:
    """
    Vypočíta sentiment transition matrix (Start → End buckets).
    
    Args:
        calls_df: DataFrame s sentiment_start a sentiment_end
        
    Returns:
        DataFrame s: start_bucket, end_bucket, count, pct
    """
    if len(calls_df) == 0:
        return pd.DataFrame(columns=["start_bucket", "end_bucket", "count", "pct"])
    
    # Bucket sentiments
    calls_df = calls_df.copy()
    calls_df["start_bucket"] = calls_df["sentiment_start"].apply(bucket_sentiment)
    calls_df["end_bucket"] = calls_df["sentiment_end"].apply(bucket_sentiment)
    
    # Count transitions
    transitions = calls_df.groupby(["start_bucket", "end_bucket"]).size().reset_index(name="count")
    
    # Calculate percentages
    total = len(calls_df)
    transitions["pct"] = round(100 * transitions["count"] / total, 1)
    
    return transitions


def compute_sentiment_improvement_kpis(calls_df: pd.DataFrame) -> Dict:
    """
    Vypočíta KPI pre sentiment improvement/deterioration.
    
    Args:
        calls_df: DataFrame s sentiment_start a sentiment_end
        
    Returns:
        Dict s: pct_improving, pct_stable, pct_deteriorating
    """
    if len(calls_df) == 0:
        return {"pct_improving": 0.0, "pct_stable": 0.0, "pct_deteriorating": 0.0}
    
    # Calculate deltas
    deltas = calls_df["sentiment_end"] - calls_df["sentiment_start"]
    
    improving = (deltas > 0.1).sum()
    deteriorating = (deltas < -0.1).sum()
    stable = len(deltas) - improving - deteriorating
    
    total = len(calls_df)
    
    return {
        "pct_improving": round(100 * improving / total, 1),
        "pct_stable": round(100 * stable / total, 1),
        "pct_deteriorating": round(100 * deteriorating / total, 1),
        "count_improving": improving,
        "count_stable": stable,
        "count_deteriorating": deteriorating
    }


# ============================================================================
# QUALITY BREAKDOWN - NEW FOR UI V2
# ============================================================================

def compute_quality_components_daily(calls_df: pd.DataFrame) -> pd.DataFrame:
    """
    Vypočíta denné priemery 4 QA binárnych komponentov + AES.
    
    Args:
        calls_df: DataFrame s quality dict a AES
        
    Returns:
        DataFrame s: date, active_listening_pct, empathy_pct, solution_pct, professional_pct, aes_avg
    """
    if len(calls_df) == 0:
        return pd.DataFrame(columns=["date", "active_listening_pct", "empathy_pct", "solution_pct", "professional_pct", "aes_avg"])
    
    # Ensure AES is calculated
    if "aes" not in calls_df.columns:
        calls_df = calls_df.copy()
        calls_df["aes"] = calls_df.apply(calculate_aes_for_call, axis=1)
    
    # Extract quality components
    calls_df = calls_df.copy()
    calls_df["date"] = pd.to_datetime(calls_df["timestamp"]).dt.date
    calls_df["active_listening"] = calls_df["quality"].apply(lambda x: 1 if x.get("active_listening", False) else 0)
    calls_df["empathy_shown"] = calls_df["quality"].apply(lambda x: 1 if x.get("empathy_shown", False) else 0)
    calls_df["solution_offered"] = calls_df["quality"].apply(lambda x: 1 if x.get("solution_offered", False) else 0)
    calls_df["professional_tone"] = calls_df["quality"].apply(lambda x: 1 if x.get("professional_tone", False) else 0)
    
    # Group by date
    daily = calls_df.groupby("date").agg({
        "active_listening": "mean",
        "empathy_shown": "mean",
        "solution_offered": "mean",
        "professional_tone": "mean",
        "aes": "mean"
    }).reset_index()
    
    # Convert to percentages
    daily["active_listening_pct"] = round(daily["active_listening"] * 100, 1)
    daily["empathy_pct"] = round(daily["empathy_shown"] * 100, 1)
    daily["solution_pct"] = round(daily["solution_offered"] * 100, 1)
    daily["professional_pct"] = round(daily["professional_tone"] * 100, 1)
    daily["aes_avg"] = round(daily["aes"], 1)
    
    # Keep only needed columns
    daily = daily[["date", "active_listening_pct", "empathy_pct", "solution_pct", "professional_pct", "aes_avg"]]
    
    # Last 7 days
    daily = daily.sort_values("date").tail(7)
    
    return daily


def get_compliance_top_failures(calls_df: pd.DataFrame, top_n: int = 2) -> List[Tuple[str, int]]:
    """
    Zistí top N najčastejšie chýbajúce compliance položky.
    
    Args:
        calls_df: DataFrame s compliance dict
        top_n: Počet top položiek
        
    Returns:
        List of (field_name, fail_count) tuples
    """
    if len(calls_df) == 0:
        return []
    
    # Count failures for each boolean field
    failure_counts = {}
    
    for _, row in calls_df.iterrows():
        comp = row["compliance"]
        for key, value in comp.items():
            if isinstance(value, bool) and not value:
                failure_counts[key] = failure_counts.get(key, 0) + 1
    
    # Sort by count descending
    sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_failures[:top_n]
