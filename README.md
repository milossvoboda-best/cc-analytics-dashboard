# CC Analytics - Streamlit Demo

**Contact Center Analytics Dashboard** s podporou STT transkriptov a AutoQA analýzy.

## 🚀 Quick Start

### 1. Vytvorenie virtuálneho prostredia

```bash
python -m venv .venv
```

### 2. Aktivácia virtuálneho prostredia

**Windows:**
```bash
.venv\Scripts\activate
```

**Unix/Mac:**
```bash
source .venv/bin/activate
```

### 3. Inštalácia závislostí

```bash
pip install -r requirements.txt
```

### 4. Spustenie aplikácie

```bash
streamlit run app.py
```

Aplikácia sa otvorí v prehliadači na adrese `http://localhost:8501`

---

## 📊 Features

### 10 Hlavných Widgetov

1. **Agent Effectiveness Score (AES)** - Komplexná metrika výkonnosti agenta
2. **Customer Sentiment Journey** - Analýza vývoja sentimentu počas hovoru
3. **First Contact Resolution (FCR)** - Percento vyriešených hovorov na prvý kontakt
4. **Compliance Risk Score** - Monitorovanie dodržiavania pravidiel
5. **Topic Resolution Efficiency (TRE)** - Efektivita riešenia podľa tém
6. **Agent Consistency Index (ACI)** - Index konzistentnosti výkonu agenta
7. **Escalation Prevention Rate (EPR)** - Miera prevencie eskalácií
8. **Average Handle Time (AHT)** - Priemerná dĺžka hovoru
9. **Call Volume by Topic** - Distribúcia hovorov podľa tém
10. **Quality Trends** - 7-dňový trend kvality

### Ďalšie Funkcie

- **Interactive Timeline** - Vizualizácia hovoru s transkriptmi, tichom, sentimentom
- **Interruption Detection** - Detekcia prerušení v konverzácii (voliteľné)
- **Multi-language Support** - Čeština, slovenčina, angličtina
- **Advanced Filtering** - Filtrovanie podľa tímu, agenta, témy, jazyka, smeru
- **Agent Performance Analysis** - Detailná analýza výkonu jednotlivých agentov
- **Call Detail View** - Kompletný detail každého hovoru

---

## 🏗️ Architektúra

### Súborová štruktúra

```
cc_analytics_demo/
├── app.py                   # Hlavná Streamlit aplikácia
├── data_generation.py       # Generovanie syntetických dát
├── metrics.py               # Výpočty metrík a KPI
├── ui_components.py         # UI komponenty a vizualizácie
├── styles.css               # Custom CSS štýly
├── requirements.txt         # Python závislosti
└── README.md               # Tento súbor
```

### Technológie

- **Streamlit** - Web framework
- **Pandas** - Dátová analýza
- **NumPy** - Numerické výpočty
- **Plotly** - Interaktívne grafy
- **Python 3.8+** - Runtime

---

## 📈 Metriky & Výpočty

### Agent Effectiveness Score (AES)

Vážený priemer 4 komponentov:

- **Sentiment** (25%): Zlepšenie sentimentu zákazníka
- **Compliance** (30%): Dodržiavanie pravidiel
- **Resolution** (30%): Úspešnosť vyriešenia problému
- **Quality** (15%): Kvalita komunikácie

**Vzorec:**
```
AES = 0.25 × Sentiment + 0.30 × Compliance + 0.30 × Resolution + 0.15 × Quality
```

### Agent Consistency Index (ACI)

Meria stabilitu výkonu agenta pomocou invertovaného koeficientu variácie:

```
ACI = 100 - (100 × CV)
kde CV = StdDev(AES) / Mean(AES)
```

- **85-100**: Very Stable
- **70-84**: Stable
- **50-69**: Unstable
- **0-49**: Highly Unstable

### Compliance Risk Score

Hodnotenie rizika na základe:

- **Critical Fields** (5 bodov každé): GDPR, verifikácia, zavádzajúce info
- **Weighted Fields**: Nahrávanie (3b), uzavretie (2b), privítanie (1b)
- **Critical Violations**: +7 bodov

**Risk Levels:**
- 0-4: Low
- 5-14: Medium
- 15+: High

### First Contact Resolution (FCR)

```
FCR = True keď:
  - resolution_achieved == "full"
  - callback_needed == False
  - escalated == False
```

---

## 🎛️ Konfigurácia

### Dataset Parameters

V bočnom paneli (sidebar) v sekcii "Dataset Configuration":

- **Number of calls**: 10-1000 (default: 200)
- **Number of agents**: 1-50 (default: 12)
- **Random seed**: 0-9999 (default: 42)
- **Simulate interruptions**: Zapne detekciu prerušení v konverzácii

### Filtre

- **Date Range**: Časový rozsah hovorov
- **Team**: Filtrovanie podľa tímu
- **Agent**: Filtrovanie podľa konkrétneho agenta
- **Topic**: Téma hovoru (billing, technical, complaint, atď.)
- **Direction**: INBOUND / OUTBOUND
- **Language**: cs / sk / en

---

## 🧪 Syntetické Dáta

Všetky dáta sú generované offline, bez volania externých API.

### Dátový Model

**Call Record:**
- Základné info: ID, timestamp, direction, language, duration
- Agent info: ID, name, team
- STT transkript: Segmenty s textom, časom, speakerom
- Ticho: Detekované pauzy a hold periody
- Prerušenia: Overlapping segments (voliteľné)

**AutoQA Výstupy (syntetické):**
- **Compliance**: 9 boolean polí + critical violations
- **Resolution**: Status, kategória, eskalácia
- **Quality**: Active listening, empathy, profesionalita
- **Topic**: Primárna téma, sub-témy, intent, komplexita
- **Sentiment**: Start, middle, end hodnoty (-1 až +1)

### Realistické Distribúcie

- **AHT**: 3-18 minút, heavy tail pre complaint/technical
- **Silence ratio**: Vyšší pri technical issues
- **Sentiment start**: Nižší pri complaint, vyšší pri product_info
- **FCR**: 70-85% podľa témy
- **Compliance**: 2-5% kritických zlyhaní

---

## 🔮 Budúce Rozšírenia (TODO)

### API Integrácie

- [ ] ElevenLabs STT adapter
- [ ] Daktela/Coworkers AutoQA API
- [ ] Real-time data streaming

### Pokročilé Funkcie

- [ ] Akustický sentiment (tone, pace, energy)
- [ ] Unsupervised topic discovery
- [ ] Real-time alerty a notifikácie
- [ ] Export reportov (PDF, Excel)
- [ ] Team benchmarking
- [ ] Predictive analytics

### UI Vylepšenia

- [ ] Dark mode
- [ ] Vlastné témy
- [ ] Mobilná optimalizácia
- [ ] Multi-user dashboard

---

## 📝 Poznámky

### Výkonnosť

- Dataset je cachovaný pomocou `@st.cache_data`
- Zmena filtrov neprerátava celý dataset
- Optimalizované pre 200-500 hovorov

### Limitácie

- Syntetické dáta (nie reálne hovory)
- Žiadne LLM výpočty v runtime
- Timeline zobrazuje max 50 segmentov

### Best Practices

- Pre produkčné použitie pripojte reálne API
- Implementujte autentifikáciu
- Použite databázu namiesto in-memory dát
- Pridajte logging a monitoring

---

## 🐛 Troubleshooting

### Streamlit sa nespustí

```bash
# Overte inštaláciu
pip list | grep streamlit

# Reinstalujte
pip install --upgrade streamlit
```

### Import errors

```bash
# Overte všetky závislosti
pip install -r requirements.txt --upgrade
```

### Prázdny dashboard

- Skontrolujte filtre v sidebar
- Resetujte dataset (Regenerate Dataset)
- Overte date range

---

## 👥 Autori

CC Analytics Team

## 📄 Licencia

Internal use only

---

## 📞 Kontakt

Pre otázky a podporu kontaktujte development tím.
