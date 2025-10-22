"""
CC Analytics - Synthetic Data Generation Module
Generuje realistické volania s STT transkriptmi a AutoQA výstupmi
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Literal
import random


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

CZECH_PHRASES = [
    "Dobrý den", "Jak vám mohu pomoci?", "Rozumím vašemu problému",
    "Moment prosím", "Podívám se na to", "Mám tady vaše údaje",
    "Děkuji za pochopení", "Je to vyřešeno", "Můžu vám ještě s něčím pomoci?",
    "Nashledanou", "Omlouvám se za komplikace", "Zkontrolujte prosím",
    "Máte nějaké další dotazy?", "Rád vám pomohu", "Nechte mi chvíli",
    "Ano, to je správně", "Bohužel to není možné", "Zkusíme to vyřešit",
]

SLOVAK_PHRASES = [
    "Dobrý deň", "Ako vám môžem pomôcť?", "Rozumiem vášmu problému",
    "Moment prosím", "Pozriem sa na to", "Mám tu vaše údaje",
    "Ďakujem za pochopenie", "Je to vyriešené", "Môžem vám ešte s niečím pomôcť?",
    "Dovidenia", "Ospravedlňujem sa za komplikácie", "Skontrolujte prosím",
    "Máte nejaké ďalšie otázky?", "Rád vám pomôžem", "Nechajte mi chvíľu",
]

ENGLISH_PHRASES = [
    "Good day", "How can I help you?", "I understand your issue",
    "One moment please", "Let me check that", "I have your information here",
    "Thank you for your patience", "It's resolved", "Can I help with anything else?",
    "Goodbye", "I apologize for the inconvenience", "Please verify",
    "Do you have any other questions?", "I'm happy to help", "Give me a moment",
]

CUSTOMER_PHRASES_CS = [
    "Volám kvůli faktúře", "Nemůžu se přihlásit", "To nefunguje",
    "Chtěl bych se zeptat", "Kdy to bude opraveno?", "Nerozumím tomu",
    "Děkuji", "To je výborné", "Konečně", "Je to složité",
    "Můžete mi vysvětlit?", "Co mám dělat?", "Potřebuji pomoc",
]

CUSTOMER_PHRASES_SK = [
    "Volám kvôli faktúre", "Nemôžem sa prihlásiť", "To nefunguje",
    "Chcel by som sa opýtať", "Kedy to bude opravené?", "Nerozumiem tomu",
    "Ďakujem", "To je výborné", "Konečne", "Je to zložité",
]

CUSTOMER_PHRASES_EN = [
    "I'm calling about my bill", "I can't log in", "It's not working",
    "I'd like to ask", "When will this be fixed?", "I don't understand",
    "Thank you", "That's great", "Finally", "This is complicated",
]

TOPICS = {
    "billing": {"complexity": 2, "avg_duration": 240, "sentiment_start": -0.3, "benchmark_aht": 4.2},
    "technical": {"complexity": 4, "avg_duration": 480, "sentiment_start": -0.5, "benchmark_aht": 8.5},
    "product_info": {"complexity": 2, "avg_duration": 180, "sentiment_start": 0.2, "benchmark_aht": 3.1},
    "complaint": {"complexity": 3, "avg_duration": 420, "sentiment_start": -0.6, "benchmark_aht": 7.0},
    "account": {"complexity": 2, "avg_duration": 210, "sentiment_start": -0.1, "benchmark_aht": 3.8},
    "order": {"complexity": 3, "avg_duration": 270, "sentiment_start": 0.1, "benchmark_aht": 4.5},
}

SALES_PRODUCTS = ["Premium Plan", "Extended Warranty", "Add-on Service", "Upgrade Package", "Bundle Deal"]

TEAMS = ["Sales", "Support", "Tech", "Retention"]


# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def generate_agents(n_agents: int, seed: int) -> pd.DataFrame:
    """Generuje DataFrame agentov"""
    np.random.seed(seed)
    random.seed(seed)
    
    first_names_cs = ["Jan", "Petra", "Martin", "Kateřina", "Tomáš", "Jana", "Lukáš", "Markéta"]
    last_names_cs = ["Novák", "Svobodová", "Dvořák", "Černá", "Procházka", "Kučerová"]
    
    agents = []
    for i in range(n_agents):
        agent_id = f"AG{1000+i}"
        first = random.choice(first_names_cs)
        last = random.choice(last_names_cs)
        agent_name = f"{first} {last}"
        team = random.choice(TEAMS)
        agents.append({
            "agent_id": agent_id,
            "agent_name": agent_name,
            "team": team,
        })
    
    return pd.DataFrame(agents)


def generate_transcript_segments(
    duration_sec: float,
    language: str,
    topic: str,
    simulate_interruptions: bool = False
) -> List[Dict]:
    """Generuje transkript segmenty pre jeden hovor"""
    
    if language == "cs":
        agent_phrases = CZECH_PHRASES
        customer_phrases = CUSTOMER_PHRASES_CS
    elif language == "sk":
        agent_phrases = SLOVAK_PHRASES
        customer_phrases = CUSTOMER_PHRASES_SK
    else:
        agent_phrases = ENGLISH_PHRASES
        customer_phrases = CUSTOMER_PHRASES_EN
    
    segments = []
    current_time = 0.0
    speaker = "AGENT"  # začína agent
    
    # Počet segmentov závisí od dĺžky
    n_segments = int(duration_sec / 15) + random.randint(2, 6)
    
    for i in range(n_segments):
        if current_time >= duration_sec:
            break
        
        # Alternovanie speakerov
        speaker = "CUSTOMER" if speaker == "AGENT" else "AGENT"
        
        # Vyber frázu
        if speaker == "AGENT":
            text = random.choice(agent_phrases)
        else:
            text = random.choice(customer_phrases)
        
        word_count = len(text.split())
        # Priemerná dĺžka segmentu 3-8 sekúnd
        segment_duration = random.uniform(3, 8)
        
        start_time = current_time
        end_time = min(current_time + segment_duration, duration_sec)
        
        # Simulácia interrupcie (prekrytie)
        if simulate_interruptions and random.random() < 0.05:  # 5% šanca
            # Posunieme začiatok späť
            overlap = random.uniform(0.2, 0.8)
            start_time = max(0, start_time - overlap)
        
        # Calculate WPM (Words Per Minute) for this segment
        duration_minutes = segment_duration / 60
        wpm = int(word_count / duration_minutes) if duration_minutes > 0 else 0
        
        # Add realistic variance to WPM
        if speaker == "AGENT":
            base_wpm = 145  # Average agent WPM
        else:
            base_wpm = 138  # Average customer WPM
        
        # Vary WPM by ±20% from base
        wpm = int(base_wpm + random.uniform(-0.2 * base_wpm, 0.2 * base_wpm))
        
        segments.append({
            "speaker": speaker,
            "text": text,
            "start_time": round(start_time, 2),
            "end_time": round(end_time, 2),
            "word_count": word_count,
            "wpm": wpm,  # ✅ REAL WPM calculated from segment
        })
        
        # Pauza medzi segmentami (0.5-2 sekundy)
        current_time = end_time + random.uniform(0.5, 2)
    
    return segments


def detect_silences(segments: List[Dict], duration_sec: float) -> Tuple[List[Dict], float]:
    """Detekuje ticho medzi segmentami"""
    silences = []
    
    sorted_segs = sorted(segments, key=lambda x: x["start_time"])
    
    for i in range(len(sorted_segs) - 1):
        gap_start = sorted_segs[i]["end_time"]
        gap_end = sorted_segs[i + 1]["start_time"]
        gap_duration = gap_end - gap_start
        
        if gap_duration > 3:  # pause threshold
            silence_type = "hold" if gap_duration > 10 else "pause"
            silences.append({
                "start": round(gap_start, 2),
                "end": round(gap_end, 2),
                "duration": round(gap_duration, 2),
                "type": silence_type,
            })
    
    total_silence = sum(s["duration"] for s in silences)
    silence_ratio = round(total_silence / duration_sec, 3) if duration_sec > 0 else 0.0
    
    return silences, silence_ratio


def detect_interruptions(segments: List[Dict]) -> List[Dict]:
    """Detekuje prerušenia (overlapping segments)"""
    interruptions = []
    sorted_segs = sorted(segments, key=lambda x: x["start_time"])
    
    for i in range(len(sorted_segs) - 1):
        current = sorted_segs[i]
        next_seg = sorted_segs[i + 1]
        
        # Overlap = next začína pred koncom current
        if next_seg["start_time"] < current["end_time"]:
            interruptions.append({
                "time": round(next_seg["start_time"], 2),
                "interrupter": next_seg["speaker"],
                "interrupted": current["speaker"],
            })
    
    return interruptions


def generate_sales_opportunity(topic: str) -> Dict:
    """
    Generuje sales opportunity (len pre Sales team!).
    
    Returns:
        Dict s type, success, value, product alebo None
    """
    # 70% šanca že bola opportunity
    if random.random() > 0.7:
        return None
    
    # Typ opportunity
    opp_types = ['upsell', 'cross_sell', 'closing']
    opp_type = random.choice(opp_types)
    
    # Success rate závisí od typu
    success_rates = {
        'upsell': 0.35,
        'cross_sell': 0.42,
        'closing': 0.61,
    }
    success = random.random() < success_rates[opp_type]
    
    # Hodnota opportunity (EUR)
    value_ranges = {
        'upsell': (50, 200),
        'cross_sell': (30, 150),
        'closing': (100, 500),
    }
    value = random.uniform(*value_ranges[opp_type])
    
    # Produkt
    product = random.choice(SALES_PRODUCTS)
    
    return {
        'type': opp_type,
        'success': success,
        'value': round(value, 2),
        'product': product
    }


def generate_autoqa_compliance(topic: str, language: str) -> Dict:
    """Syntetické AutoQA compliance polia"""
    # Default: väčšina prešla
    compliance = {
        "greeting_proper": random.random() > 0.05,
        "identification": random.random() > 0.08,
        "customer_verification": random.random() > 0.1,
        "data_protection_mentioned": random.random() > 0.12,
        "call_recording_notice": random.random() > 0.15,
        "clear_communication": random.random() > 0.03,
        "no_misleading_info": random.random() > 0.02,
        "proper_closing": random.random() > 0.1,
        "opt_out_offered": random.random() > 0.2,
    }
    
    critical_violations = []
    if not compliance["data_protection_mentioned"] and random.random() < 0.5:
        critical_violations.append("gdpr_missing")
    if not compliance["customer_verification"] and random.random() < 0.3:
        critical_violations.append("id_not_verified")
    
    compliance["critical_violations"] = critical_violations
    return compliance


def generate_autoqa_resolution(topic: str) -> Dict:
    """Syntetické AutoQA resolution polia"""
    complexity = TOPICS[topic]["complexity"]
    
    # Vyššia komplexita → nižšia šanca na full resolution
    full_prob = 0.85 - (complexity * 0.1)
    
    if random.random() < full_prob:
        resolution_achieved = "full"
        customer_satisfied = random.random() > 0.1
        callback_needed = False
    elif random.random() < 0.7:
        resolution_achieved = "partial"
        customer_satisfied = random.random() > 0.5
        callback_needed = random.random() < 0.4
    else:
        resolution_achieved = "none"
        customer_satisfied = False
        callback_needed = random.random() < 0.6
    
    escalated = random.random() < (0.05 + complexity * 0.02)
    escalation_reasons = ["authority", "knowledge", "customer_request", "none"]
    escalation_reason = random.choice(escalation_reasons[:3]) if escalated else "none"
    
    return {
        "issue_identified": True,
        "issue_category": topic,
        "resolution_achieved": resolution_achieved,
        "customer_satisfied": customer_satisfied,
        "callback_needed": callback_needed,
        "escalated": escalated,
        "escalation_reason": escalation_reason,
    }


def generate_autoqa_quality(topic: str, resolution: Dict) -> Dict:
    """Syntetické AutoQA quality polia"""
    
    # Kvalita koreluje s resolution
    base_prob = 0.85 if resolution["resolution_achieved"] == "full" else 0.6
    
    quality = {
        "active_listening": random.random() < base_prob,
        "empathy_shown": random.random() < base_prob - 0.1,
        "solution_offered": random.random() < base_prob,
        "professional_tone": random.random() < base_prob + 0.1,
        "customer_name_used": random.random() < 0.5,
    }
    
    script_options = ["good", "partial", "poor"]
    weights = [0.7, 0.25, 0.05] if base_prob > 0.7 else [0.4, 0.4, 0.2]
    quality["script_adherence"] = random.choices(script_options, weights=weights)[0]
    quality["call_control"] = random.choices(script_options, weights=weights)[0]
    
    positive_moments = []
    negative_moments = []
    
    if quality["empathy_shown"]:
        positive_moments.append("Excellent empathy demonstrated")
    if quality["solution_offered"]:
        positive_moments.append("Clear solution provided")
    
    if not quality["active_listening"]:
        negative_moments.append("Missed customer cues")
    if quality["script_adherence"] == "poor":
        negative_moments.append("Script not followed")
    
    quality["positive_moments"] = positive_moments
    quality["negative_moments"] = negative_moments
    
    return quality


def generate_autoqa_topic(topic: str, language: str) -> Dict:
    """Syntetické AutoQA topic polia"""
    
    sub_topics_map = {
        "billing": ["invoice", "payment", "charges"],
        "technical": ["connectivity", "device", "software"],
        "product_info": ["features", "pricing", "availability"],
        "complaint": ["service", "quality", "delay"],
        "account": ["login", "settings", "profile"],
        "order": ["status", "delivery", "cancellation"],
    }
    
    intents = ["get_information", "resolve_problem", "make_complaint", "request_service"]
    intent_weights = {
        "billing": [0.3, 0.5, 0.15, 0.05],
        "technical": [0.2, 0.7, 0.05, 0.05],
        "product_info": [0.8, 0.1, 0.05, 0.05],
        "complaint": [0.1, 0.3, 0.6, 0.0],
        "account": [0.4, 0.4, 0.1, 0.1],
        "order": [0.5, 0.2, 0.1, 0.2],
    }
    
    return {
        "primary_topic": topic,
        "sub_topics": random.sample(sub_topics_map[topic], k=random.randint(1, 2)),
        "customer_intent": random.choices(intents, weights=intent_weights[topic])[0],
        "topic_complexity": TOPICS[topic]["complexity"],
        "keywords": [topic, language],
    }


def generate_sentiment_journey(topic: str, resolution: Dict) -> Tuple[float, float, float]:
    """Generuje sentiment journey (start, middle, end)"""
    
    start = TOPICS[topic]["sentiment_start"] + random.uniform(-0.2, 0.2)
    start = max(-1.0, min(1.0, start))
    
    # Middle: mierne zlepšenie
    middle = start + random.uniform(0.1, 0.3)
    middle = max(-1.0, min(1.0, middle))
    
    # End: závisí od resolution
    if resolution["resolution_achieved"] == "full":
        end = random.uniform(0.5, 0.9)
    elif resolution["resolution_achieved"] == "partial":
        end = random.uniform(0.0, 0.5)
    else:
        end = random.uniform(-0.6, 0.1)
    
    end = max(-1.0, min(1.0, end))
    
    return round(start, 3), round(middle, 3), round(end, 3)


def generate_dataset(
    n_calls: int = 200,
    n_agents: int = 12,
    seed: int = 42,
    simulate_interruptions: bool = False
) -> Tuple[pd.DataFrame, Dict, pd.DataFrame]:
    """
    Hlavná funkcia na generovanie datasetu.
    
    Returns:
        calls_df: DataFrame s hovormi
        transcripts: Dict[call_id] -> List[segments]
        agents_df: DataFrame s agentmi
    """
    np.random.seed(seed)
    random.seed(seed)
    
    agents_df = generate_agents(n_agents, seed)
    
    calls = []
    transcripts = {}
    
    # Časový rozsah: posledných 30 dní
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for i in range(n_calls):
        call_id = f"CALL-{10000+i}"
        
        # Random timestamp
        random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
        timestamp = start_date + timedelta(seconds=random_seconds)
        
        # Direction
        direction = random.choices(["INBOUND", "OUTBOUND"], weights=[0.8, 0.2])[0]
        
        # Language: 70% cs/sk, 30% en
        language = random.choices(["cs", "sk", "en"], weights=[0.4, 0.3, 0.3])[0]
        
        # Agent
        agent = agents_df.sample(1).iloc[0]
        agent_id = agent["agent_id"]
        agent_name = agent["agent_name"]
        team = agent["team"]
        
        # Topic
        topic = random.choice(list(TOPICS.keys()))
        
        # Duration: podľa topicu + variancia
        base_duration = TOPICS[topic]["avg_duration"]
        duration_sec = max(60, random.gauss(base_duration, base_duration * 0.3))
        duration_sec = round(duration_sec, 1)
        
        # Generate transcript
        segments = generate_transcript_segments(duration_sec, language, topic, simulate_interruptions)
        transcripts[call_id] = segments
        
        # Calculate speaking times
        agent_segments = [s for s in segments if s["speaker"] == "AGENT"]
        customer_segments = [s for s in segments if s["speaker"] == "CUSTOMER"]
        
        agent_talk_sec = sum(s["end_time"] - s["start_time"] for s in agent_segments)
        customer_talk_sec = sum(s["end_time"] - s["start_time"] for s in customer_segments)
        
        turns = len(segments)
        
        # Silence detection
        silence_periods, silence_ratio = detect_silences(segments, duration_sec)
        
        # Interruption detection
        interruptions = detect_interruptions(segments) if simulate_interruptions else []
        interrupt_count = len(interruptions)
        
        # AutoQA outputs
        compliance = generate_autoqa_compliance(topic, language)
        resolution = generate_autoqa_resolution(topic)
        quality = generate_autoqa_quality(topic, resolution)
        topic_data = generate_autoqa_topic(topic, language)
        sentiment_start, sentiment_middle, sentiment_end = generate_sentiment_journey(topic, resolution)
        
        # ✅ Sales Opportunity (LEN pre Sales team!)
        sales_opportunity = None
        if team == "Sales":
            sales_opportunity = generate_sales_opportunity(topic)
        
        # ✅ AutoQA Score (separate from quality_score)
        # Score 0-100 based on compliance + quality
        compliance_score = sum(1 for v in compliance.values() if isinstance(v, bool) and v) / 9 * 100
        quality_score_autoqa = quality["quality_score"]  # Already 0-100
        autoqa_score = round((compliance_score * 0.6 + quality_score_autoqa * 0.4), 1)
        
        # ✅ Benchmark AHT for comparison
        benchmark_aht = TOPICS[topic]["benchmark_aht"]
        
        call_record = {
            "call_id": call_id,
            "timestamp": timestamp,
            "direction": direction,
            "language": language,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "team": team,
            "duration_sec": duration_sec,
            "agent_talk_sec": round(agent_talk_sec, 1),
            "customer_talk_sec": round(customer_talk_sec, 1),
            "turns": turns,
            "silence_ratio": silence_ratio,
            "interrupt_count": interrupt_count,
            "sentiment_start": sentiment_start,
            "sentiment_middle": sentiment_middle,
            "sentiment_end": sentiment_end,
            # Store ako JSON/dict columns
            "compliance": compliance,
            "resolution": resolution,
            "quality": quality,
            "topic_data": topic_data,
            # ✅ NEW FIELDS for redesign
            "sales_opportunity": sales_opportunity,  # None if not Sales team
            "autoqa_score": autoqa_score,  # 0-100 (separate metric)
            "benchmark_aht": benchmark_aht,  # Minutes for topic comparison
        }
        
        calls.append(call_record)
    
    calls_df = pd.DataFrame(calls)
    
    return calls_df, transcripts, agents_df


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_transcript_for_call(call_id: str, transcripts: Dict) -> List[Dict]:
    """Získa transkript pre daný call_id"""
    return transcripts.get(call_id, [])


def calculate_speaking_rate(segments: List[Dict], speaker: str) -> float:
    """Vypočíta WPM (words per minute) pre daného speakera"""
    speaker_segments = [s for s in segments if s["speaker"] == speaker]
    
    if not speaker_segments:
        return 0.0
    
    total_words = sum(s["word_count"] for s in speaker_segments)
    total_time_sec = sum(s["end_time"] - s["start_time"] for s in speaker_segments)
    
    if total_time_sec == 0:
        return 0.0
    
    wpm = (total_words / total_time_sec) * 60
    return round(wpm, 1)
