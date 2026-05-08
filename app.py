import streamlit as st
import requests
import re
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="ProductScan", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")

# ── PALETTE ORO→BRONZO ──────────────────────────────────────
def get_palette(score):
    """Restituisce colori dashboard in funzione dello score."""
    if score >= 80:   # ORO
        return {"bg":"#FFFBF0","card":"#FFF8E1","accent":"#FFB300","accent2":"#FF8F00",
                "text":"#4E3B00","sub":"#8D6E00","bar_bg":"#FFE082","medal":"🥇","label":"Eccellente"}
    elif score >= 60: # ARGENTO DORATO
        return {"bg":"#F9F6EE","card":"#F5F0E0","accent":"#C9A84C","accent2":"#A67C2E",
                "text":"#3D2F00","sub":"#7A6030","bar_bg":"#E8D9A0","medal":"🥈","label":"Buono"}
    elif score >= 40: # BRONZO
        return {"bg":"#F7F0E6","card":"#F0E6D3","accent":"#CD7F32","accent2":"#A0522D",
                "text":"#3B1F00","sub":"#7A4C20","bar_bg":"#DEB887","medal":"🥉","label":"Nella media"}
    elif score >= 20: # RAME SCURO
        return {"bg":"#F5EDE0","card":"#EDE0CC","accent":"#B87333","accent2":"#8B5A2B",
                "text":"#3A1500","sub":"#7A3D1A","bar_bg":"#D4A07A","medal":"🔶","label":"Scarso"}
    else:             # OSSIDATO
        return {"bg":"#F0E8D8","card":"#E8D8C0","accent":"#8B6914","accent2":"#6B4F10",
                "text":"#2C1A00","sub":"#6B4A10","bar_bg":"#C4A060","medal":"⚠️","label":"Molto scarso"}

def render_css(p):
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{{
  --bg:{p['bg']};--card:{p['card']};--accent:{p['accent']};--accent2:{p['accent2']};
  --text:{p['text']};--sub:{p['sub']};--bar-bg:{p['bar_bg']};
}}
html,body,.stApp{{background:var(--bg)!important;color:var(--text)!important;transition:background 0.6s;}}
.stApp>header{{display:none!important;}}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stHeader"],[data-testid="stDecoration"],.stDeployButton{{display:none!important;}}
section[data-testid="stSidebar"]{{display:none!important;}}
.block-container{{padding:0!important;max-width:560px!important;margin:0 auto!important;}}
[data-testid="stTextInput"] label{{display:none!important;}}
[data-testid="stTextInput"] input{{background:var(--card)!important;border:1.5px solid var(--bar-bg)!important;border-radius:12px!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;font-size:1rem!important;padding:14px 18px!important;box-shadow:none!important;transition:all 0.3s;}}
[data-testid="stTextInput"] input:focus{{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(205,127,50,0.2)!important;}}
[data-testid="stTextInput"] input::placeholder{{color:var(--sub)!important;opacity:0.6;}}
.stButton>button{{background:var(--accent)!important;color:#fff!important;border:none!important;border-radius:12px!important;font-family:'DM Sans',sans-serif!important;font-weight:700!important;font-size:1rem!important;padding:14px 22px!important;width:100%!important;transition:all 0.2s!important;box-shadow:0 2px 8px rgba(0,0,0,0.15)!important;}}
.stButton>button:hover{{background:var(--accent2)!important;transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,0.2)!important;}}
[data-testid="stSpinner"]>div{{border-top-color:var(--accent)!important;}}
[data-testid="stMarkdownContainer"] p{{color:var(--text)!important;margin:0!important;}}
div[data-testid="stVerticalBlock"]{{gap:0!important;}}
.element-container{{margin-bottom:0!important;}}

.ps-header{{background:var(--card);padding:16px 20px;border-bottom:1px solid var(--bar-bg);
  display:flex;align-items:center;gap:10px;}}
.ps-logo{{font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:var(--text);}}
.ps-logo-accent{{color:var(--accent);}}
.search-wrap{{background:var(--card);padding:12px 16px;border-bottom:1px solid var(--bar-bg);}}

/* HERO */
.hero{{background:var(--card);padding:20px 16px 16px;border-bottom:2px solid var(--bar-bg);}}
.hero-top{{display:flex;align-items:flex-start;gap:16px;margin-bottom:16px;}}
.hero-img{{width:88px;height:88px;border-radius:14px;object-fit:contain;background:var(--bg);
  border:2px solid var(--bar-bg);flex-shrink:0;}}
.hero-img-ph{{width:88px;height:88px;border-radius:14px;background:var(--bg);display:flex;
  align-items:center;justify-content:center;font-size:2rem;flex-shrink:0;border:2px solid var(--bar-bg);}}
.hero-name{{font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;color:var(--text);line-height:1.3;margin-bottom:2px;}}
.hero-brand{{font-family:'DM Sans',sans-serif;font-size:0.82rem;color:var(--sub);margin-bottom:10px;}}

/* SCORE — argentato perlato, bordo colorato per score */
.score-block{{
  background:linear-gradient(145deg,#F5F5FA,#EAEAF2,#DCDCE8)!important;
  border-radius:16px!important;padding:18px 20px!important;
  display:flex!important;align-items:center!important;gap:20px!important;
  border:4px solid #4CAF50!important;
  box-shadow:0 2px 20px rgba(0,0,0,0.12),inset 0 1px 0 rgba(255,255,255,0.9)!important;}}
.score-circle{{
  width:72px!important;height:72px!important;border-radius:50%!important;
  background:linear-gradient(145deg,#FFFFFF,#EEEEF6)!important;
  display:flex!important;flex-direction:column!important;align-items:center!important;
  justify-content:center!important;flex-shrink:0!important;
  border:2px solid rgba(0,0,0,0.08)!important;
  box-shadow:0 2px 8px rgba(0,0,0,0.08),inset 0 1px 2px rgba(255,255,255,1)!important;}}
.score-n{{font-family:'Syne',sans-serif!important;font-size:1.8rem!important;font-weight:800!important;color:#1a1a2e!important;line-height:1!important;}}
.score-d{{font-family:'DM Mono',monospace!important;font-size:0.5rem!important;color:#888!important;}}
.score-info{{flex:1!important;}}
.score-medal{{font-size:1.6rem!important;line-height:1!important;}}
.score-label{{font-family:'Syne',sans-serif!important;font-size:1.15rem!important;font-weight:700!important;color:#1a1a2e!important;}}
.score-algo{{font-family:'DM Mono',monospace!important;font-size:0.62rem!important;color:#666!important;margin-top:3px!important;line-height:1.5!important;}}
.score-bar-wrap{{margin-top:10px!important;}}
.score-bar-bg{{height:6px!important;background:rgba(0,0,0,0.08)!important;border-radius:3px!important;overflow:hidden!important;}}
.score-bar-fill{{height:100%!important;border-radius:3px!important;transition:width 0.8s!important;}}

/* SECTIONS */
.section{{background:var(--card);margin-top:8px;padding:18px 16px;}}
.section-header{{display:flex;align-items:center;gap:8px;margin-bottom:4px;}}
.section-title{{font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:var(--text);}}
.section-badge{{font-family:'DM Mono',monospace;font-size:0.6rem;padding:2px 8px;border-radius:20px;
  background:var(--bar-bg);color:var(--text);text-transform:uppercase;letter-spacing:0.05em;}}
.section-sub{{font-family:'DM Sans',sans-serif;font-size:0.72rem;color:var(--sub);margin-bottom:14px;margin-top:2px;}}
.divider{{height:1px;background:var(--bar-bg);margin:10px 0;}}

/* FACTOR ROWS */
.factor{{display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--bar-bg);}}
.factor:last-child{{border-bottom:none;}}
.factor-icon{{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;}}
.factor-text{{flex:1;}}
.factor-name{{font-family:'DM Sans',sans-serif;font-size:0.92rem;font-weight:500;color:var(--text);}}
.factor-desc{{font-family:'DM Sans',sans-serif;font-size:0.72rem;color:var(--sub);margin-top:1px;}}
.factor-val{{font-family:'DM Mono',monospace;font-size:0.82rem;color:var(--sub);margin-right:6px;}}
.dot{{width:11px;height:11px;border-radius:50%;flex-shrink:0;}}
.dot-g{{background:#4CAF50;}}.dot-o{{background:#FF9800;}}.dot-r{{background:#e53935;}}

/* ADDITIVI */
.additivi-section{{background:linear-gradient(135deg,rgba(255,152,0,0.1),rgba(255,87,34,0.08));
  border:1.5px solid rgba(255,152,0,0.3);border-radius:14px;padding:14px 16px;margin:8px 0;}}
.additivi-title{{font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;color:#E65100;margin-bottom:10px;}}
.additive-pill{{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid rgba(255,152,0,0.4);
  border-radius:20px;padding:5px 12px;margin:3px;font-family:'DM Mono',monospace;font-size:0.72rem;color:#BF360C;}}
.additive-risk{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
.risk-low{{background:#FF9800;}}.risk-med{{background:#F44336;}}.risk-high{{background:#B71C1C;}}

/* NF BARS */
.nf-row{{display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--bar-bg);}}
.nf-row:last-child{{border-bottom:none;}}
.nf-name{{font-family:'DM Sans',sans-serif;font-size:0.88rem;color:var(--text);width:125px;flex-shrink:0;}}
.nf-bar-bg{{flex:1;height:7px;background:var(--bar-bg);border-radius:4px;overflow:hidden;}}
.nf-bar{{height:100%;border-radius:4px;}}
.nf-val{{font-family:'DM Mono',monospace;font-size:0.75rem;color:var(--sub);width:46px;text-align:right;flex-shrink:0;}}

/* INGREDIENTI */
.ing-text{{font-family:'DM Sans',sans-serif;font-size:0.85rem;line-height:1.9;color:var(--text);}}
.ia{{color:#e53935;font-weight:700;text-transform:uppercase;}}
.ing-missing{{background:var(--bg);border-radius:10px;padding:14px;font-family:'DM Sans',sans-serif;font-size:0.85rem;color:var(--sub);text-align:center;}}
.atags{{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;}}
.atag{{font-family:'DM Sans',sans-serif;font-size:0.72rem;padding:4px 10px;
  background:rgba(229,57,53,0.1);border:1px solid rgba(229,57,53,0.3);color:#c62828;border-radius:20px;}}

/* CHART */
.chart-wrap{{display:flex;align-items:center;gap:20px;padding:8px 0 14px;flex-wrap:wrap;}}
.chart-legend{{font-family:'DM Sans',sans-serif;font-size:0.8rem;line-height:2.1;color:var(--text);}}

/* NUTRISCORE */
.ns-row{{display:flex;gap:4px;margin-top:6px;}}
.ns-l{{padding:5px 10px;border-radius:6px;font-family:'Syne',sans-serif;font-size:0.82rem;
  font-weight:700;color:#fff;opacity:0.25;transition:opacity 0.3s;}}
.ns-l.active{{opacity:1;}}
.nsa-c{{background:#038141;}}.nsb-c{{background:#85bb2f;}}.nsc-c{{background:#fecb02;color:#333;}}
.nsd-c{{background:#ee8100;}}.nse-c{{background:#e63312;}}

/* NOVA */
.nova-row{{display:flex;gap:6px;margin-top:6px;align-items:center;}}
.nova-dot{{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-family:'Syne',sans-serif;font-weight:700;font-size:0.8rem;
  color:#fff;opacity:0.2;transition:opacity 0.3s;}}
.nova-dot.active{{opacity:1;}}
.n1c{{background:#038141;}}.n2c{{background:#85bb2f;}}.n3c{{background:#fecb02;color:#333;}}.n4c{{background:#e63312;}}

/* ALTERNATIVES */
.alt-card{{display:flex;align-items:center;gap:12px;padding:13px 0;border-bottom:1px solid var(--bar-bg);}}
.alt-card:last-child{{border-bottom:none;}}
.alt-score{{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:1rem;font-weight:800;flex-shrink:0;
  background:linear-gradient(145deg,#F5F5FA,#DCDCE8)!important;
  color:#1a1a2e!important;
  border:3px solid #4CAF50;
  box-shadow:0 2px 8px rgba(0,0,0,0.1),inset 0 1px 2px rgba(255,255,255,0.9);}}
.alt-info{{flex:1;}}
.alt-name{{font-family:'DM Sans',sans-serif;font-size:0.88rem;font-weight:600;color:var(--text);}}
.alt-brand{{font-family:'DM Sans',sans-serif;font-size:0.72rem;color:var(--sub);}}
.alt-link{{font-family:'DM Sans',sans-serif;font-size:0.78rem;color:var(--accent);
  text-decoration:none;font-weight:700;border:1.5px solid var(--accent);border-radius:8px;padding:5px 10px;}}

/* MISC */
.ps-footer{{background:var(--card);margin-top:8px;padding:14px;text-align:center;
  font-family:'DM Mono',monospace;font-size:0.68rem;color:var(--sub);border-top:1px solid var(--bar-bg);}}
.src-badge{{display:inline-block;font-family:'DM Mono',monospace;font-size:0.7rem;color:var(--accent);
  background:var(--bar-bg);border-radius:20px;padding:3px 10px;margin-bottom:8px;}}
.ps-err{{background:var(--card);border:1.5px solid var(--bar-bg);border-radius:12px;padding:16px;
  font-family:'DM Sans',sans-serif;font-size:0.9rem;color:var(--text);margin:10px 16px;}}

@media(max-width:540px){{
  .nf-name{{width:90px!important;}}
  .score-n{{font-size:1.5rem!important;}}
}}
</style>
<script>
function fixIframes(){{
  document.querySelectorAll('iframe').forEach(function(f){{
    if(!f.getAttribute('allow')||!f.getAttribute('allow').includes('camera'))
      f.setAttribute('allow','camera;microphone');
  }});
}}
fixIframes();
new MutationObserver(fixIframes).observe(document.body,{{childList:true,subtree:true}});
</script>
"""

# ── FSA NUTRIENT PROFILING MODEL (scientifico) ──────────────
# Fonte: Rayner M et al. (2005) Food Standards Agency UK
# Validato OMS, usato da Nutri-Score come base
# Punteggio A (negativo): energia, zuccheri, grassi saturi, sodio
# Punteggio C (positivo): fibre, proteine, frutta/verdura/noci
# Score finale = A - C, normalizzato 0-100 (invertito: alto = buono)
# Moltiplicatore NOVA: Monteiro et al. PAHO 2019

ADDITIVI_DB = {
    # Coloranti
    "en:e102":("Tartrazina","Colorante azoico, possibile iperattività nei bambini","high"),
    "en:e110":("Sunset Yellow","Colorante azoico, vietato in alcuni paesi","high"),
    "en:e122":("Carmoisina","Colorante azoico, possibile iperattività","high"),
    "en:e124":("Ponceau 4R","Colorante azoico, vietato negli USA","high"),
    "en:e129":("Rosso Allura","Colorante azoico","med"),
    "en:e171":("Biossido di Titanio","Classificato possibile cancerogeno EFSA 2021","high"),
    # Conservanti
    "en:e211":("Benzoato di Sodio","Conservante, possibile iperattività in combo con coloranti","med"),
    "en:e220":("Anidride Solforosa","Conservante, può causare reazioni nei sensibili","med"),
    "en:e250":("Nitrito di Sodio","Conservante carni, potenzialmente cancerogeno (IARC)","high"),
    "en:e251":("Nitrato di Sodio","Conservante carni, convertibile in nitriti","high"),
    "en:e320":("BHA","Conservante antiossidante, possibile cancerogeno","high"),
    "en:e321":("BHT","Conservante antiossidante, controverso","med"),
    # Dolcificanti
    "en:e951":("Aspartame","Dolcificante, controverso (rivalutazione EFSA 2023)","med"),
    "en:e950":("Acesulfame K","Dolcificante intensivo","low"),
    "en:e955":("Sucralosio","Dolcificante clorurato","low"),
    # Emulsionanti
    "en:e471":("Mono/Digliceridi","Emulsionante, possibile impatto microbioma","low"),
    "en:e472e":("DATEM","Emulsionante","low"),
    "en:e476":("Poliricinoleato","Emulsionante","low"),
    "en:e481":("Stearoil Lattilato Na","Emulsionante","low"),
    # Esaltatori
    "en:e621":("Glutammato Monosodico","Esaltatore di sapidità","low"),
    "en:e627":("Guanilato Disodico","Esaltatore di sapidità","low"),
    # Addensanti
    "en:e407":("Carragenina","Addensante, possibile infiammazione intestinale","med"),
    "en:e412":("Gomma di Guar","Addensante, generalmente sicuro","low"),
    "en:e415":("Gomma Xantana","Addensante, generalmente sicuro","low"),
    "en:e433":("Polisorbato 80","Emulsionante, impatto microbioma (studi su topi)","med"),
}

def compute_fsa_score(p):
    """
    FSA Nutrient Profiling Model normalizzato 0-100.
    Score A (0-10): energia, zuccheri totali, grassi saturi, sodio
    Score C (0-15): fibre, proteine, % frutta/verdura/noci
    NOVA malus: ultratrasformati penalizzati
    FSA score grezzo = A - C (più basso = più sano)
    Normalizzato: score_100 = round((15 - clamped(fsa,-5,15)) / 20 * 100)
    """
    n = p.get("nutriments", {})
    pos_factors, neg_factors = [], []

    # ── SCORE A (negativo, 0-10 per categoria) ──
    # Energia (kJ per 100g)
    kj = n.get("energy_100g") or (n.get("energy-kcal_100g",0)*4.184)
    if kj <= 335: a_en = 0
    elif kj <= 670: a_en = 1
    elif kj <= 1005: a_en = 2
    elif kj <= 1340: a_en = 3
    elif kj <= 1675: a_en = 4
    elif kj <= 2010: a_en = 5
    elif kj <= 2345: a_en = 6
    elif kj <= 2680: a_en = 7
    elif kj <= 3015: a_en = 8
    elif kj <= 3350: a_en = 9
    else: a_en = 10

    # Zuccheri totali (g/100g)
    sug = n.get("sugars_100g") or 0
    if sug <= 4.5: a_sug = 0
    elif sug <= 9: a_sug = 1
    elif sug <= 13.5: a_sug = 2
    elif sug <= 18: a_sug = 3
    elif sug <= 22.5: a_sug = 4
    elif sug <= 27: a_sug = 5
    elif sug <= 31: a_sug = 6
    elif sug <= 36: a_sug = 7
    elif sug <= 40: a_sug = 8
    elif sug <= 45: a_sug = 9
    else: a_sug = 10

    # Grassi saturi (g/100g)
    sat = n.get("saturated-fat_100g") or 0
    if sat <= 1: a_sat = 0
    elif sat <= 2: a_sat = 1
    elif sat <= 3: a_sat = 2
    elif sat <= 4: a_sat = 3
    elif sat <= 5: a_sat = 4
    elif sat <= 6: a_sat = 5
    elif sat <= 7: a_sat = 6
    elif sat <= 8: a_sat = 7
    elif sat <= 9: a_sat = 8
    elif sat <= 10: a_sat = 9
    else: a_sat = 10

    # Sodio (mg/100g — sale*400)
    salt = n.get("salt_100g") or 0
    sodium = salt * 400
    if sodium <= 90: a_sod = 0
    elif sodium <= 180: a_sod = 1
    elif sodium <= 270: a_sod = 2
    elif sodium <= 360: a_sod = 3
    elif sodium <= 450: a_sod = 4
    elif sodium <= 540: a_sod = 5
    elif sodium <= 630: a_sod = 6
    elif sodium <= 720: a_sod = 7
    elif sodium <= 810: a_sod = 8
    elif sodium <= 900: a_sod = 9
    else: a_sod = 10

    score_a = a_en + a_sug + a_sat + a_sod  # 0-40

    # ── SCORE C (positivo, 0-5 per categoria) ──
    # Fibre (g/100g) — AOAC method
    fiber = n.get("fiber_100g") or 0
    if fiber <= 0.9: c_fib = 0
    elif fiber <= 1.9: c_fib = 1
    elif fiber <= 2.8: c_fib = 2
    elif fiber <= 3.7: c_fib = 3
    elif fiber <= 4.7: c_fib = 4
    else: c_fib = 5

    # Proteine (g/100g)
    prot = n.get("proteins_100g") or 0
    if prot <= 1.6: c_pro = 0
    elif prot <= 3.2: c_pro = 1
    elif prot <= 4.8: c_pro = 2
    elif prot <= 6.4: c_pro = 3
    elif prot <= 8.0: c_pro = 4
    else: c_pro = 5

    # Frutta/verdura/noci (%)
    fvn = n.get("fruits-vegetables-nuts-estimate-from-ingredients_100g") or \
          n.get("fruits-vegetables-nuts_100g") or 0
    if fvn <= 40: c_fvn = 0
    elif fvn <= 60: c_fvn = 1
    elif fvn <= 80: c_fvn = 2
    else: c_fvn = 5

    score_c = c_fib + c_pro + c_fvn  # 0-15

    # ── FSA RAW ──
    fsa_raw = score_a - score_c  # da -15 a +40

    # Normalizza: -15 = 100 (ottimo), +40 = 0 (pessimo)
    score_100 = round(max(0, min(100, (40 - fsa_raw) / 55 * 100)))

    # ── MALUS NOVA (Monteiro et al. 2019) ──
    nova = p.get("nova_group")
    nova_malus = {1:0, 2:0, 3:-5, 4:-15}
    if nova and nova in nova_malus:
        score_100 = max(0, score_100 + nova_malus[nova])

    # ── FATTORI POSITIVI E NEGATIVI ──
    kcal = n.get("energy-kcal_100g") or (kj/4.184 if kj else None)

    # Positivi
    if c_fib >= 3: pos_factors.append(("🌾","Fibre",f"Eccellente: {fiber:.1f}g/100g","dot-g"))
    elif c_fib >= 1: pos_factors.append(("🌾","Fibre",f"Presente: {fiber:.1f}g/100g","dot-g"))
    if c_pro >= 3: pos_factors.append(("💪","Proteine",f"Ottima quantità: {prot:.1f}g/100g","dot-g"))
    elif c_pro >= 1: pos_factors.append(("💪","Proteine",f"Buona quantità: {prot:.1f}g/100g","dot-g"))
    if c_fvn >= 2: pos_factors.append(("🍎","Frutta/Verdura",f"Alta presenza: {fvn:.0f}%","dot-g"))
    elif c_fvn == 1: pos_factors.append(("🍎","Frutta/Verdura",f"Presente: {fvn:.0f}%","dot-g"))
    if a_sod == 0: pos_factors.append(("🧂","Sale",f"Senza sale: {salt:.2f}g/100g","dot-g"))
    elif a_sod <= 1: pos_factors.append(("🧂","Sale",f"Basso: {salt:.2f}g/100g","dot-g"))
    if a_sat <= 1: pos_factors.append(("💧","Grassi saturi",f"Bassi: {sat:.1f}g/100g","dot-g"))
    if nova and nova <= 2: pos_factors.append(("🌿","Alimento non trasformato",f"NOVA {nova} — bassa trasformazione","dot-g"))

    # Negativi
    if a_sug >= 5: neg_factors.append(("🍬","Zuccheri",f"Elevati: {sug:.1f}g/100g","dot-r"))
    elif a_sug >= 2: neg_factors.append(("🍬","Zuccheri",f"Moderati: {sug:.1f}g/100g","dot-o"))
    if a_sat >= 5: neg_factors.append(("🧈","Grassi saturi",f"Elevati: {sat:.1f}g/100g","dot-r"))
    elif a_sat >= 3: neg_factors.append(("🧈","Grassi saturi",f"Moderati: {sat:.1f}g/100g","dot-o"))
    if a_sod >= 5: neg_factors.append(("🧂","Sale",f"Elevato: {salt:.2f}g/100g","dot-r"))
    elif a_sod >= 3: neg_factors.append(("🧂","Sale",f"Moderato: {salt:.2f}g/100g","dot-o"))
    if kcal and kcal > 450: neg_factors.append(("🔥","Energia",f"{int(kcal)} kcal/100g","dot-o"))
    if nova and nova == 4: neg_factors.append(("🏭","Ultra-trasformato",f"NOVA 4 — alto grado di trasformazione","dot-r"))
    elif nova and nova == 3: neg_factors.append(("🏭","Trasformato",f"NOVA 3 — alimento trasformato","dot-o"))

    return score_100, pos_factors, neg_factors, {"a":score_a,"c":score_c,"fsa":fsa_raw,
           "nova":nova,"fiber":fiber,"prot":prot,"sugar":sug,"sat":sat,"salt":salt,
           "kcal":kcal,"fvn":fvn}

# ── ADDITIVI ────────────────────────────────────────────────
def render_additivi(p):
    tags = p.get("additives_tags") or []
    if not tags:
        return ('<div class="additivi-section" style="background:linear-gradient(135deg,rgba(76,175,80,0.1),rgba(139,195,74,0.08));border-color:rgba(76,175,80,0.4);">'
                '<div class="additivi-title" style="color:#2E7D32;">✅ Additivi — Nessuno rilevato</div>'
                '<div style="font-family:DM Sans,sans-serif;font-size:0.82rem;color:#388E3C;line-height:1.6;">Ottimo: nessun additivo presente nel database. Prodotto con ingredienti naturali.</div>'
                '</div>')
    pills = ""
    for tag in tags:
        tag_clean = tag.lower().replace("_"," ")
        if tag_clean in ADDITIVI_DB:
            name, desc, risk = ADDITIVI_DB[tag_clean]
            risk_cls = f"risk-{risk}"
            code = tag.replace("en:","").upper()
            pills += f'<div class="additive-pill"><div class="additive-risk {risk_cls}"></div>{code} — {name}</div>'
        else:
            code = tag.replace("en:","").upper()
            pills += f'<div class="additive-pill"><div class="additive-risk risk-low"></div>{code}</div>'
    risk_legend = '<div style="font-family:DM Mono,monospace;font-size:0.62rem;color:#E65100;margin-top:10px;">🔴 Alto rischio &nbsp;🟠 Moderato &nbsp;🟡 Basso rischio</div>'
    return f'<div class="additivi-section"><div class="additivi-title">⚗️ Additivi ({len(tags)})</div>{pills}{risk_legend}</div>'

# ── DB ────────────────────────────────────────────────────────
DBS=[("food","Open Food Facts","https://world.openfoodfacts.org"),
     ("beauty","Open Beauty Facts","https://world.openbeautyfacts.org"),
     ("generic","Open Products Facts","https://world.openproductsfacts.org")]

def fetch_off(bc,ph):
    for did,dn,base in DBS:
        ph.markdown(f'<div class="src-badge">→ {dn}</div>',unsafe_allow_html=True)
        try:
            r=requests.get(f"{base}/api/v0/product/{bc}.json",timeout=8,headers={"User-Agent":"ProductScan/0.5"})
            if r.status_code==200:
                d=r.json()
                if d.get("status")==1: return d["product"],did,dn
        except: pass
    return None,None,None

def fetch_upc(bc,ph):
    ph.markdown('<div class="src-badge">→ UPCitemdb</div>',unsafe_allow_html=True)
    try:
        r=requests.get(f"https://api.upcitemdb.com/prod/trial/lookup?upc={bc}",timeout=8,headers={"User-Agent":"ProductScan/0.5"})
        if r.status_code==200:
            items=r.json().get("items",[])
            if items:
                i=items[0]
                return {"product_name":i.get("title",""),"brands":i.get("brand",""),"categories":i.get("category",""),"ingredients_text":i.get("ingredients",""),"image_url":(i.get("images")or[""])[0]}, "generic","UPCitemdb"
    except: pass
    return None,None,None

def search(bc,ph):
    p,d,s=fetch_off(bc,ph)
    if p: return p,d,s
    p,d,s=fetch_upc(bc,ph)
    if p: return p,d,s
    return None,None,None

def normalize_query_value(v):
    if isinstance(v, list):
        return str(v[0]).strip() if v else ""
    return str(v).strip() if v is not None else ""

def get_suggestions(p, current_score):
    cats = p.get("categories_tags") or []
    candidates = [c for c in reversed(cats) if c.startswith("en:") and len(c) > 5]
    if not candidates:
        return ("no_cat", str(cats[:3]))
    last_err = ("no_cat", "")
    for cat in candidates[:3]:
        try:
            r = requests.get(
                "https://world.openfoodfacts.org/cgi/search.pl",
                params={
                    "action":"process",
                    "tagtype_0":"categories","tag_contains_0":"contains","tag_0":cat,
                    "sort_by":"unique_scans_n","page_size":"30",
                    "fields":"product_name,brands,nutriscore_grade,nova_group,nutriments,additives_tags,categories_tags,code",
                    "json":"1"
                },
                timeout=25,
                headers={"User-Agent":"ProductScan/0.5"}
            )
            if r.status_code != 200:
                last_err = ("http_err", str(r.status_code)); continue
            prods = r.json().get("products", [])
            if not prods:
                last_err = ("empty", cat); continue
            results = []
            for prod in prods:
                if not prod.get("product_name"): continue
                s,_,_,_ = compute_fsa_score(prod)
                if s > current_score + 3:
                    results.append((s, prod))
            results.sort(key=lambda x: -x[0])
            if results:
                return results[:4]
            last_err = ("none_better", f"score={current_score}")
        except Exception as ex:
            last_err = ("exception", str(ex)[:80]); continue
    return last_err

# ── HELPERS ──────────────────────────────────────────────────
def e(s): return str(s or"").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def nutriscore_html(ns):
    letters,colors=["A","B","C","D","E"],["nsa-c","nsb-c","nsc-c","nsd-c","nse-c"]
    html='<div class="ns-row">'
    for l,c in zip(letters,colors):
        html+=f'<div class="ns-l {c}{"  active" if l.lower()==ns else ""}">{l}</div>'
    return html+"</div>"

def nova_html(nova):
    html='<div class="nova-row">'
    for i,c in enumerate(["n1c","n2c","n3c","n4c"],1):
        html+=f'<div class="nova-dot {c}{"  active" if nova==i else ""}">{i}</div>'
    return html+"</div>"

def macro_svg(fat, carbs, prot):
    tot=fat*9+carbs*4+prot*4
    if tot==0: return ""
    pf=fat*9/tot*100; pc=carbs*4/tot*100; pp=prot*4/tot*100
    def sl(s,en,col):
        if en-s>=100: en-=0.01
        a=math.radians(s/100*360-90); b=math.radians(en/100*360-90)
        r=52; cx=60; cy=60
        x1,y1=cx+r*math.cos(a),cy+r*math.sin(a); x2,y2=cx+r*math.cos(b),cy+r*math.sin(b)
        return f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {1 if en-s>50 else 0},1 {x2:.1f},{y2:.1f} Z" fill="{col}"/>'
    svg=(f'<svg width="120" height="120" viewBox="0 0 120 120">'
         f'{sl(0,pf,"#e53935")}{sl(pf,pf+pc,"#FF9800")}{sl(pf+pc,pf+pc+pp,"#4CAF50")}'
         f'<circle cx="60" cy="60" r="30" fill="var(--bg)"/>'
         f'<text x="60" y="56" text-anchor="middle" font-family="Syne" font-size="11" font-weight="700" fill="var(--text)">{int(tot)}</text>'
         f'<text x="60" y="69" text-anchor="middle" font-family="DM Sans" font-size="8" fill="var(--sub)">kcal</text>'
         f'</svg>')
    leg=(f'<div class="chart-legend">'
         f'<span style="color:#e53935">●</span> Grassi {fat:.1f}g ({pf:.0f}%)<br>'
         f'<span style="color:#FF9800">●</span> Carb {carbs:.1f}g ({pc:.0f}%)<br>'
         f'<span style="color:#4CAF50">●</span> Prot {prot:.1f}g ({pp:.0f}%)</div>')
    return f'<div class="chart-wrap">{svg}{leg}</div>'

def ha(txt):
    for a in['LATTE','GLUTINE','FRUMENTO','GRANO','UOVA','SOIA','ARACHIDI','NOCI','MANDORLE','NOCCIOLE','SESAMO','SENAPE','SEDANO','LUPINI','CROSTACEI','PESCE','SOLFITI']:
        txt=re.sub(f'\\b{a}\\b',f'<span class="ia">{a}</span>',txt,flags=re.IGNORECASE)
    return txt

def nf_bar(name,val,mx,unit,color):
    pct=min(100,(val/mx)*100) if val else 0
    vs=f"{val:.1f}{unit}" if val is not None else "—"
    return (f'<div class="nf-row"><div class="nf-name">{name}</div>'
            f'<div class="nf-bar-bg"><div class="nf-bar" style="width:{pct}%;background:{color};"></div></div>'
            f'<div class="nf-val">{vs}</div></div>')

def factor_row(icon,name,desc,dot):
    fi={"dot-g":"fi-green","dot-o":"fi-orange","dot-r":"fi-red"}.get(dot,"fi-orange")
    return (f'<div class="factor"><div class="factor-icon {fi}">{icon}</div>'
            f'<div class="factor-text"><div class="factor-name">{name}</div>'
            f'<div class="factor-desc">{desc}</div></div>'
            f'<div class="dot {dot}"></div></div>')

def bar_color(v,low,high):
    if v is None: return "var(--bar-bg)"
    return "#4CAF50" if v<=low else "#FF9800" if v<=high else "#e53935"

# ── SCANNER ──────────────────────────────────────────────────
def scanner_html(pal):
    return f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:{pal['card']};font-family:'DM Sans',sans-serif;padding:0;}}
#btn{{width:100%;padding:14px;background:{pal['accent']};color:#fff;border:none;
  font-size:0.95rem;font-weight:700;cursor:pointer;border-radius:12px;margin-bottom:8px;
  box-shadow:0 2px 8px rgba(0,0,0,0.2);letter-spacing:0.02em;}}
#btn:active{{opacity:0.85;}}
#stop{{width:100%;padding:14px;background:{pal['card']};color:{pal['accent']};
  border:2px solid {pal['accent']};font-size:0.95rem;font-weight:700;
  cursor:pointer;border-radius:12px;margin-bottom:8px;display:none;}}
#vp{{width:100%;border-radius:12px;overflow:hidden;background:#000;}}
#vp video{{width:100%!important;display:block;}}
#vp canvas.drawingBuffer{{display:none!important;}}
#msg{{font-size:0.78rem;color:{pal['sub']};padding:8px 2px;text-align:center;}}
#found{{display:none;margin-top:8px;padding:14px;background:{pal['bar_bg']};
  border-radius:12px;text-align:center;}}
#found-code{{font-size:1rem;color:{pal['text']};font-weight:700;margin-bottom:10px;font-family:DM Mono,monospace;}}
#found-btn{{display:inline-block;padding:12px 28px;background:{pal['accent']};color:#fff;
  border:none;font-size:0.9rem;font-weight:700;cursor:pointer;border-radius:10px;
  text-decoration:none;letter-spacing:0.02em;}}
</style>
<button id="btn" onclick="go()">📷 Scan</button>
<button id="stop" onclick="halt()">⏹ Ferma</button>
<div id="vp"></div>
<div id="msg">Premi Scan per avviare la fotocamera</div>
<div id="found">
  <div id="found-code"></div>
  <a id="found-btn" href="#" target="_top">🔍 Cerca Prodotto</a>
</div>
<script>
var running=false,done=false;
function go(){{
  done=false;
  document.getElementById('btn').style.display='none';
  document.getElementById('stop').style.display='block';
  document.getElementById('found').style.display='none';
  document.getElementById('msg').textContent='Inizializzazione fotocamera...';
  Quagga.init({{
    inputStream:{{type:"LiveStream",target:document.getElementById('vp'),
      constraints:{{facingMode:"environment",width:{{ideal:1280}},height:{{ideal:720}}}}}},
    decoder:{{readers:["ean_reader","ean_8_reader","upc_reader","upc_e_reader","code_128_reader"]}},
    locate:true,numOfWorkers:2,frequency:10
  }},function(err){{
    if(err){{document.getElementById('msg').textContent='Errore: '+err;halt();return;}}
    Quagga.start();running=true;
    document.getElementById('msg').textContent='Inquadra il barcode...';
  }});
  Quagga.onDetected(function(r){{
    if(done)return;done=true;
    var code=r.codeResult.code;
    halt();
    document.getElementById('msg').textContent='✓ Rilevato';
    document.getElementById('found-code').textContent=code;
    var target = window.top.location.pathname + '?barcode=' + encodeURIComponent(code);
    document.getElementById('found-btn').href=target;
    document.getElementById('found').style.display='block';
    setTimeout(function(){{ window.top.location.href = target; }}, 250);
  }});
}}
function halt(){{
  if(running){{try{{Quagga.stop();}}catch(e){{}}running=false;}}
  document.getElementById('btn').style.display='block';
  document.getElementById('stop').style.display='none';
}}
</script>"""

# ── RENDER FOOD ───────────────────────────────────────────────
def render_food(p, score, pos, neg, details, pal):
    n=p.get("nutriments",{})
    name=e(p.get("product_name") or p.get("product_name_it") or p.get("product_name_en") or "Prodotto")
    brand=e(p.get("brands",""))
    img=p.get("image_url") or p.get("image_front_url") or ""
    ns=(p.get("nutriscore_grade") or "").lower()
    nova=p.get("nova_group")
    col=pal['accent']; label=pal['label']; medal=pal['medal']

    img_html=(f'<img class="hero-img" src="{img}" onerror="this.style.display=\'none\'">'
              if img else '<div class="hero-img-ph">📦</div>')
    if score >= 75:   border_col="#4CAF50"; shadow_col="rgba(76,175,80,0.35)"
    elif score >= 50: border_col="#8BC34A"; shadow_col="rgba(139,195,74,0.35)"
    elif score >= 30: border_col="#FF9800"; shadow_col="rgba(255,152,0,0.35)"
    else:             border_col="#e53935"; shadow_col="rgba(229,57,53,0.35)"

    # Stili 100% inline — non dipendono dal CSS globale
    sb_style = (f"background:linear-gradient(145deg,#F5F5FA,#EAEAF2,#DCDCE8);"
                f"border-radius:16px;padding:18px 20px;"
                f"display:flex;align-items:center;gap:20px;"
                f"border:4px solid {border_col};"
                f"box-shadow:0 3px 20px {shadow_col},inset 0 1px 0 rgba(255,255,255,0.9);"
                f"margin-top:14px;")
    circle_style = ("width:72px;height:72px;border-radius:50%;flex-shrink:0;"
                    "background:linear-gradient(145deg,#FFFFFF,#EEEEF6);"
                    "display:flex;flex-direction:column;align-items:center;justify-content:center;"
                    "border:2px solid rgba(0,0,0,0.08);"
                    "box-shadow:0 2px 8px rgba(0,0,0,0.1),inset 0 1px 2px rgba(255,255,255,1);")
    num_style  = "font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#1a1a2e;line-height:1;"
    den_style  = "font-family:'DM Mono',monospace;font-size:0.48rem;color:#888;"
    lbl_style  = "font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:700;color:#1a1a2e;"
    alg_style  = "font-family:'DM Mono',monospace;font-size:0.6rem;color:#666;margin-top:4px;line-height:1.5;"
    bar_bg_s   = "height:6px;background:rgba(0,0,0,0.08);border-radius:3px;overflow:hidden;margin-top:10px;"
    bar_fill_s = f"height:100%;width:{score}%;background:{border_col};border-radius:3px;"

    st.markdown(
        f'<div class="hero">'
        f'<div class="hero-top">{img_html}'
        f'<div class="hero-info"><div class="hero-name">{name}</div>'
        f'<div class="hero-brand">{brand}</div>'
        f'{nutriscore_html(ns)}</div></div>'
        f'<div style="{sb_style}">'
        f'  <div style="{circle_style}"><div style="{num_style}">{score}</div><div style="{den_style}">/100</div></div>'
        f'  <div style="flex:1;">'
        f'    <div style="font-size:1.5rem;line-height:1;">{medal}</div>'
        f'    <div style="{lbl_style}">{label}</div>'
        f'    <div style="{alg_style}">FSA Nutrient Profiling Model<br>NOVA: {nova or "N/D"} · Nutri-Score: {ns.upper() if ns else "N/D"}</div>'
        f'  </div>'
        f'</div>'
        f'<div style="{bar_bg_s}"><div style="{bar_fill_s}"></div></div>'
        f'</div>', unsafe_allow_html=True)

    # POSITIVI
    if pos:
        rows="".join([factor_row(ic,nm,dc,dt) for ic,nm,dc,dt in pos])
        st.markdown(f'<div class="section"><div class="section-header"><div class="section-title">Positivo</div><div class="section-badge">per 100g</div></div>{rows}</div>', unsafe_allow_html=True)

    # NEGATIVI
    if neg:
        rows="".join([factor_row(ic,nm,dc,dt) for ic,nm,dc,dt in neg])
        st.markdown(f'<div class="section"><div class="section-header"><div class="section-title">Negativo</div><div class="section-badge">per 100g</div></div>{rows}</div>', unsafe_allow_html=True)

    # ADDITIVI — sempre visibile
    add_html = render_additivi(p)
    st.markdown(f'<div class="section">{add_html}</div>', unsafe_allow_html=True)

    # INGREDIENTI
    ing=(p.get("ingredients_text") or p.get("ingredients_text_it") or
         p.get("ingredients_text_en") or p.get("ingredients_text_fr") or "").strip()
    if not ing and p.get("ingredients"):
        try: ing=", ".join([i.get("text","") for i in p["ingredients"] if i.get("text")])
        except: pass
    allergens=[t.replace("en:","").replace("-"," ") for t in (p.get("allergens_tags") or [])]
    atags_html="".join([f'<span class="atag">{a}</span>' for a in allergens])
    ih=f'<div class="ing-text">{ha(e(ing))}</div>' if ing else f'<div class="ing-missing">Ingredienti non disponibili.<br><a href="https://world.openfoodfacts.org/product/{e(p.get("code",""))}" target="_blank" style="color:{pal["accent"]};">Contribuisci su openfoodfacts.org</a></div>'
    if atags_html: ih+=f'<div class="atags">{atags_html}</div>'
    st.markdown(f'<div class="section"><div class="section-title">Ingredienti</div><div class="divider"></div>{ih}</div>', unsafe_allow_html=True)

    # VALORI NUTRIZIONALI
    fat=n.get("fat_100g"); sat=n.get("saturated-fat_100g")
    carbs=n.get("carbohydrates_100g"); sugar=n.get("sugars_100g")
    fiber=n.get("fiber_100g"); prot=n.get("proteins_100g"); salt=n.get("salt_100g")
    kcal_v=details.get("kcal")
    nf=(nf_bar("Grassi",fat,30,"g",bar_color(fat,3,17.5))+
        nf_bar("↳ Grassi saturi",sat,10,"g",bar_color(sat,1.5,5))+
        nf_bar("Carboidrati",carbs,80,"g",bar_color(carbs,20,60))+
        nf_bar("↳ Zuccheri",sugar,40,"g",bar_color(sugar,5,22.5))+
        nf_bar("Fibre",fiber,10,"g","#4CAF50" if fiber and fiber>=3 else "#FF9800")+
        nf_bar("Proteine",prot,30,"g","#4CAF50" if prot and prot>=8 else "#FF9800")+
        nf_bar("Sale",salt,3,"g",bar_color(salt,0.3,1.5)))
    chart=macro_svg(fat or 0, carbs or 0, prot or 0)
    kcal_s=f'<div style="font-family:DM Sans,sans-serif;font-size:0.8rem;color:var(--sub);margin-top:14px;">Energia per 100g: <strong style="color:var(--text);font-size:1rem;">{int(kcal_v)} kcal</strong></div>' if kcal_v else ""
    nova_s=f'<div class="divider"></div><div style="font-family:DM Sans,sans-serif;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Grado di trasformazione (NOVA)</div>{nova_html(nova)}<div style="font-family:DM Mono,monospace;font-size:0.65rem;color:var(--sub);margin-top:4px;">Monteiro et al. 2019 — PAHO/WHO</div>'
    fsa_info=f'<div style="font-family:DM Mono,monospace;font-size:0.62rem;color:var(--sub);margin-top:14px;padding:10px;background:var(--bg);border-radius:8px;">Score FSA grezzo: A={details["a"]} C={details["c"]} → {details["fsa"]} → normalizzato {score}/100<br>Rayner M et al. FSA 2005 — OMS Nutrient Profiling</div>'
    st.markdown(f'<div class="section"><div class="section-title">Valori Nutrizionali</div><div class="section-sub">per 100g</div>{chart}{nf}{kcal_s}{nova_s}{fsa_info}</div>', unsafe_allow_html=True)

def render_alternatives(suggestions, pal):
    acc = pal["accent"]
    sub = pal["sub"]
    bg  = pal["bar_bg"]

    # Errore diagnostico
    if isinstance(suggestions, tuple):
        err_type, err_msg = suggestions
        msgs = {
            "no_cat":     "Categoria prodotto non rilevata nel database.",
            "http_err":   f"Errore connessione OFF (HTTP {err_msg}).",
            "empty":      f"Nessun prodotto trovato per la categoria: {err_msg}.",
            "none_better":f"Non esistono alternative con score migliore ({err_msg}).",
            "exception":  f"Errore di rete: {err_msg}.",
        }
        msg = msgs.get(err_type, f"{err_type}: {err_msg}")
        st.markdown(
            f'<div class="section"><div class="section-title">Alternative Migliori</div>'+
            f'<div style="font-family:DM Sans,sans-serif;font-size:0.82rem;color:{sub};padding:12px 0;">{msg}</div></div>',
            unsafe_allow_html=True)
        return

    if not suggestions:
        return

    html = (f'<div class="section">'+
            f'<div class="section-title">Alternative Migliori</div>'+
            f'<div class="section-sub">Prodotti simili con score FSA superiore</div>')
    for s, prod in suggestions:
        if s >= 75:   bc="#4CAF50"
        elif s >= 50: bc="#8BC34A"
        elif s >= 30: bc="#FF9800"
        else:         bc="#e53935"
        name  = e((prod.get("product_name") or "")[:45])
        brand = e((prod.get("brands") or "")[:25])
        code  = prod.get("code","")
        ns2   = (prod.get("nutriscore_grade") or "").lower()
        ns_txt = f'Nutri-Score {ns2.upper()}' if ns2 and ns2 in "abcde" else ""
        circle_s = (f"width:50px;height:50px;border-radius:50%;flex-shrink:0;"
                    f"background:linear-gradient(145deg,#FFFFFF,#EEEEF6);"
                    f"display:flex;align-items:center;justify-content:center;"
                    f"border:3px solid {bc};"
                    f"box-shadow:0 2px 8px rgba(0,0,0,0.1),inset 0 1px 2px rgba(255,255,255,1);"
                    f"font-family:'Syne',sans-serif;font-size:1rem;font-weight:800;color:#1a1a2e;")
        html += (f'<div class="alt-card">'+
                 f'<div style="{circle_s}">{s}</div>'+
                 f'<div class="alt-info">'+
                 f'<div class="alt-name">{name}</div>'+
                 f'<div class="alt-brand">{brand}{(" · "+ns_txt) if ns_txt else ""}</div>'+
                 f'</div>'+
                 f'<a class="alt-link" href="?barcode={code}">Analizza →</a>'+
                 f'</div>')
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_generic(p, source, pal):
    name = e(p.get("product_name") or p.get("title") or "Prodotto")
    brand = e(p.get("brands") or p.get("brand") or "Marca non disponibile")
    img = p.get("image_url") or ""
    categories = e(p.get("categories") or "Categoria non disponibile")
    ing = e((p.get("ingredients_text") or "").strip()) or "Ingredienti non disponibili"
    source_txt = e(source or "Fonte esterna")

    img_html = (
        f'<img class="hero-img" src="{img}" onerror="this.style.display=\'none\'">'
        if img else '<div class="hero-img-ph">📦</div>'
    )
    st.markdown(
        f'<div class="hero">'
        f'<div class="hero-top">{img_html}'
        f'<div class="hero-info"><div class="hero-name">{name}</div>'
        f'<div class="hero-brand">{brand}</div></div></div>'
        f'<div class="section-sub">Fonte dati: {source_txt}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="section"><div class="section-title">Caratterizzazione Base</div>'
        f'<div class="divider"></div>'
        f'<div class="ing-text"><strong>Categoria:</strong> {categories}</div>'
        f'<div class="ing-text" style="margin-top:8px;"><strong>Ingredienti:</strong> {ing}</div>'
        f'<div class="section-sub" style="margin-top:12px;">Dati nutrizionali non disponibili nella fonte corrente, quindi non posso calcolare lo score FSA in modo affidabile.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── MAIN ──────────────────────────────────────────────────────
def main():
    params = st.query_params
    chip = normalize_query_value(params.get("barcode",""))

    # ── Pre-calcola score e palette PRIMA di iniettare CSS ──
    default_pal = get_palette(45)
    product = None; did = None; source = None
    score = 45; pal = default_pal
    pre_ph = st.empty()

    if chip:
        with st.spinner(""):
            product, did, source = search(chip, pre_ph)
        pre_ph.empty()
        if product:
            if did == "food":
                score, pos, neg, details = compute_fsa_score(product)
            else:
                score, pos, neg, details = 50, [], [], {}
            pal = get_palette(score)

    # Inietta CSS UNA SOLA VOLTA con palette corretta
    st.markdown(render_css(pal), unsafe_allow_html=True)

    st.markdown(f'<div class="ps-header"><div class="ps-logo">Product<span class="ps-logo-accent">Scan</span></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
    ci, cb = st.columns([4,1])
    with ci: bc_input = st.text_input("bc", value=chip, placeholder="EAN-13 / UPC", label_visibility="collapsed")
    with cb: clicked = st.button("→")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding:14px 16px;background:var(--card);margin-top:8px;">', unsafe_allow_html=True)
    components.html(scanner_html(pal), height=380, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # Ricerca manuale (bottone)
    if clicked and bc_input.strip() and bc_input.strip() != chip:
        ph2 = st.empty()
        with st.spinner(""):
            product, did, source = search(bc_input.strip(), ph2)
        ph2.empty()
        if product:
            if did == "food":
                score, pos, neg, details = compute_fsa_score(product)
            else:
                score, pos, neg, details = 50, [], [], {}

    if not product and chip:
        st.markdown(f'<div class="ps-err">⚠ Prodotto non trovato: <strong>{e(chip)}</strong></div>', unsafe_allow_html=True)
    elif product:
        if did == "food":
            render_food(product, score, pos, neg, details, pal)
            with st.spinner("Ricerca alternative…"):
                sugg = get_suggestions(product, score)
            render_alternatives(sugg, pal)
        elif did == "beauty":
            st.markdown(f'<div class="section"><div class="section-title">{e(product.get("product_name",""))}</div></div>', unsafe_allow_html=True)
        elif did == "generic":
            render_generic(product, source, pal)

    st.markdown('<div class="ps-footer">FSA Nutrient Profiling Model · Open Food Facts (CC BY-SA)</div>', unsafe_allow_html=True)

if __name__=="__main__":
    main()
