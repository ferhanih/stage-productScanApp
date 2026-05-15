import time
import streamlit as st
import requests
import re
import streamlit.components.v1 as components
import math

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

st.set_page_config(page_title="ProductScan", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")


# ── HTTP SESSION ──────────────────────────────────────────────
def _make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.4, status_forcelist={429, 500, 502, 503, 504},
                  allowed_methods={"GET"}, raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {"User-Agent": "ProductScan/1.0 (contact: opensource@productscan.app)", "Accept": "application/json"})
    return session


_HTTP = _make_session()


# ── PALETTE ──────────────────────────────────────────────────
def get_palette(score):

    match score:
        case _ if score >= 80:
            return {"bg": "#DFF0E8", "card": "#EEF7F2", "accent": "#16A34A", "accent2": "#15803D",
                    "text": "#0F1A14", "sub": "#5A7A6A", "bar_bg": "#C8DFCF", "medal": "🥇", "label": "Eccellente",
                    "score_fg": "#16A34A", "score_bg": "#D8EEE2", "score_border": "#9ECDB0",
                    "pill_bg": "#C4E8D2", "pill_fg": "#14532D",
                    "glow": "rgba(22,163,74,0.16)"}
        case _ if score >= 60:
            return {"bg": "#DFF5EE", "card": "#EEF9F4", "accent": "#0D9E6A", "accent2": "#0A8A5C",
                    "text": "#0A1F16", "sub": "#4A7A62", "bar_bg": "#C0E5D4", "medal": "🥈", "label": "Buono",
                    "score_fg": "#0D9E6A", "score_bg": "#D5F0E5", "score_border": "#8ED4B8",
                    "pill_bg": "#C0E8D4", "pill_fg": "#0A4D30",
                    "glow": "rgba(13,158,106,0.16)"}
        case _ if score >= 40:
            return {"bg": "#EDE4D2", "card": "#F7F0E4", "accent": "#D97706", "accent2": "#B45309",
                    "text": "#1A1200", "sub": "#706050", "bar_bg": "#E0D0B0", "medal": "🥉", "label": "Nella media",
                    "score_fg": "#D97706", "score_bg": "#F0E2C8", "score_border": "#DEC070",
                    "pill_bg": "#E8D4A0", "pill_fg": "#78350F",
                    "glow": "rgba(217,119,6,0.16)"}
        case _ if score >= 20:
            return {"bg": "#EDE0D4", "card": "#F7EEE4", "accent": "#EA580C", "accent2": "#C2410C",
                    "text": "#1A0800", "sub": "#706050", "bar_bg": "#E0CCBA", "medal": "🔶", "label": "Scarso",
                    "score_fg": "#EA580C", "score_bg": "#F0DECE", "score_border": "#E8A870",
                    "pill_bg": "#E8CEAC", "pill_fg": "#7C2D12",
                    "glow": "rgba(234,88,12,0.15)"}
        case _:
            return {"bg": "#EEDADC", "card": "#F7ECEE", "accent": "#DC2626", "accent2": "#B91C1C",
                    "text": "#1A0008", "sub": "#706068", "bar_bg": "#E0C4C8", "medal": "⚠️", "label": "Molto scarso",
                    "score_fg": "#DC2626", "score_bg": "#F0D8DC", "score_border": "#E89CA8",
                    "pill_bg": "#E8C8CE", "pill_fg": "#7F1D1D",
                    "glow": "rgba(220,38,38,0.14)"}



# ── CSS ──────────────────────────────────────────────────────
def render_css(p):
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

:root {{
  --bg: {p['bg']};
  --card: {p['card']};
  --accent: {p['accent']};
  --accent2: {p['accent2']};
  --text: {p['text']};
  --sub: {p['sub']};
  --bar-bg: {p['bar_bg']};
  --sc-fg: {p['score_fg']};
  --sc-bg: {p['score_bg']};
  --sc-bdr: {p['score_border']};
  --pl-bg: {p['pill_bg']};
  --pl-fg: {p['pill_fg']};
  --glow: {p['glow']};
  --r: 16px;
  --r-sm: 10px;
  --r-xs: 7px;
  --bdr: 1px solid rgba(0,0,0,0.06);
  --sh-xs: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
  --sh-sm: 0 4px 16px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
  --sh-md: 0 8px 32px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
  --font: 'DM Sans', sans-serif;
  --mono: 'DM Mono', monospace;
}}

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, .stApp {{
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.6s ease;
}}

/* Hide Streamlit chrome */
.stApp > header, #MainMenu, footer,
[data-testid="stToolbar"], [data-testid="stHeader"],
[data-testid="stDecoration"], .stDeployButton {{ display: none !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}

/* Layout */
.block-container {{
  padding: 0 !important;
  max-width: 480px !important;
  margin: 0 auto !important;
}}
[data-testid="stTextInput"] label {{ display: none !important; }}
[data-testid="stMarkdownContainer"] p {{
  color: var(--text) !important;
  margin: 0 !important;
}}
div[data-testid="stVerticalBlock"] {{ gap: 0; background: var(--card) !important; }}
.element-container {{ margin: 0 !important; }}

/* Search button */
button[data-testid="stBaseButton-secondary"] {{
  width: 100%;
  margin: 9px;
}}

/* ── INPUT ── */
[data-testid="stTextInput"] input {{
  background: var(--card) !important;
  border: var(--bdr) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.95rem !important;
  font-weight: 400 !important;
  padding: 14px 16px !important;
  box-shadow: var(--sh-xs) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
  outline: none !important;
  height: 50px !important;
}}
[data-testid="stTextInput"] input:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--glow), var(--sh-xs) !important;
}}
[data-testid="stTextInput"] input::placeholder {{
  color: var(--sub) !important;
  opacity: 0.55;
  font-size: 0.9rem !important;
}}

/* ── BUTTON ── */
.stButton > button {{
  background: var(--accent) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--r-sm) !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  width: 100% !important;
  height: 50px !important;
  letter-spacing: -0.01em !important;
  transition: background 0.18s, box-shadow 0.18s, transform 0.12s !important;
  box-shadow: 0 2px 8px var(--glow) !important;
  cursor: pointer !important;
}}
.stButton > button:hover {{
  background: var(--accent2) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px var(--glow) !important;
}}
.stButton > button:active {{
  transform: translateY(0) !important;
  box-shadow: 0 1px 4px var(--glow) !important;
}}
[data-testid="stSpinner"] > div {{ border-top-color: var(--accent) !important; }}

/* ── HEADER ── */
.ps-header {{
  background: rgba(255,255,255,0.92);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  padding: 14px 20px 16px 20px;
  border-bottom: var(--bdr);
  display: flex; 
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  margin-bottom: 20px;
}}
.ps-logo {{
  font-family: var(--font);
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.04em;
  display: flex;
  align-items: center;
  gap: 6px;
}}
.ps-logo span {{ color: var(--accent); }}
.ps-logo-icon {{
  width: 28px;
  height: 28px;
  background: var(--accent);
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}}
.ps-tag {{
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--sub);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: var(--pl-bg);
  color: var(--pl-fg);
  padding: 3px 9px;
  border-radius: 20px;
  font-weight: 500;
}}

/* ── SEARCH AREA ── */
.search-wrap {{
  background: var(--card);
  padding: 12px 16px 12px;
  border-bottom: var(--bdr);
  margin-top: 0;          /* ← était 10px */
}}
.search-wrap [data-testid="stColumn"],
.search-wrap [data-testid="stColumn"] > div,
.search-wrap [data-testid="stHorizontalBlock"] {{
  background: var(--card) !important;  /* ← était var(--bg) */
}}

/* Supprime la règle scanner-wrap iframe */
.scanner-wrap {{
  background: var(--card);
  padding: 12px 16px;
  border-bottom: var(--bdr);
}}

/* Supprime le gap Streamlit entre les éléments */
div[data-testid="stVerticalBlock"] {{
  gap: 0 !important;        /* ← ajoute !important */
  background: var(--card) !important;
}}
.element-container {{
  margin: 0 !important;
  padding: 0 !important;    /* ← ajoute padding 0 */
}}

/* Supprime les backgrounds parasites des colonnes Streamlit */
[data-testid="stColumn"] {{
  background: var(--card) !important;
  padding: 0 !important;
}}
[data-testid="stHorizontalBlock"] {{
  background: var(--card) !important;
  gap: 8px !important;
  padding: 0 !important;
}}


/* ── HERO ── */
.hero {{
  background: var(--card);
  padding: 20px 20px 16px;
  border-bottom: var(--bdr);
}}
.hero-top {{
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 16px;
}}
.hero-img {{
  width: 80px;
  height: 80px;
  border-radius: 14px;
  object-fit: contain;
  background: var(--bg);
  border: var(--bdr);
  flex-shrink: 0;
  box-shadow: var(--sh-sm);
}}
.hero-img-ph {{
  width: 72px;
  height: 72px;
  border-radius: 14px;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  flex-shrink: 0;
  border: var(--bdr);
}}
.hero-meta {{
  flex: 1;
  min-width: 0;
  padding-top: 2px;
}}
.hero-name {{
  font-family: var(--font);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
  letter-spacing: -0.025em;
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.hero-brand {{
  font-family: var(--font);
  font-size: 0.78rem;
  color: var(--sub);
  font-weight: 400;
  margin-bottom: 10px;
  letter-spacing: -0.01em;
}}

/* ── SCORE CARD ── */
.score-card {{
  background: var(--sc-bg);
  border: 1px solid var(--sc-bdr);
  border-radius: var(--r);
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px var(--glow);
}}
.score-ring {{
  position: relative;
  width: 68px;
  height: 68px;
  flex-shrink: 0;
}}
.score-ring svg {{
  position: absolute;
  top: 0;
  left: 0;
}}
.score-ring-inner {{
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}}
.score-num {{
  font-family: var(--font);
  font-size: 1.55rem;
  font-weight: 800;
  color: var(--sc-fg);
  line-height: 1;
  letter-spacing: -0.05em;
}}
.score-den {{
  font-family: var(--mono);
  font-size: 0.42rem;
  color: var(--sub);
  letter-spacing: 0.04em;
  margin-top: 1px;
  opacity: 0.7;
}}
.score-body {{ flex: 1; }}
.score-medal {{
  font-size: 1.1rem;
  line-height: 1;
  margin-bottom: 3px;
}}
.score-label {{
  font-family: var(--font);
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
}}
.score-meta {{
  font-family: var(--mono);
  font-size: 0.56rem;
  color: var(--sub);
  margin-top: 5px;
  line-height: 1.7;
  letter-spacing: 0.01em;
  opacity: 0.8;
}}
.score-track {{
  height: 3px;
  background: color-mix(in srgb, var(--sc-fg) 14%, transparent);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 14px;
}}
.score-fill {{
  height: 100%;
  border-radius: 2px;
  background: var(--sc-fg);
  transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* ── NUTRISCORE ── */
.ns-row {{
  display: flex;
  gap: 4px;
  margin-top: 8px;
}}
.ns-l {{
  padding: 4px 9px;
  border-radius: 6px;
  font-family: var(--font);
  font-size: 0.72rem;
  font-weight: 700;
  color: #fff;
  opacity: 0.18;
  transition: opacity 0.3s, transform 0.25s;
  letter-spacing: 0.02em;
}}
.ns-l.active {{
  opacity: 1;
  transform: scale(1.08);
}}
.nsa-c {{ background: #16A34A; }}
.nsb-c {{ background: #84CC16; }}
.nsc-c {{ background: #EAB308; color: #333; }}
.nsd-c {{ background: #F97316; }}
.nse-c {{ background: #EF4444; }}

/* ── NOVA ── */
.nova-row {{
  display: flex;
  gap: 6px;
  margin-top: 7px;
  align-items: center;
}}
.nova-dot {{
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font);
  font-weight: 700;
  font-size: 0.72rem;
  color: #fff;
  opacity: 0.14;
  transition: opacity 0.3s, transform 0.25s;
}}
.nova-dot.active {{
  opacity: 1;
  transform: scale(1.1);
}}
.n1c {{ background: #16A34A; }}
.n2c {{ background: #84CC16; }}
.n3c {{ background: #EAB308; color: #333; }}
.n4c {{ background: #EF4444; }}

/* ── SECTIONS ── */
/* Collapse any Streamlit-injected gap between scanner and first product block */
.element-container:has(.scanner-wrap) + .element-container {{
  margin-top: 0 !important;
}}
.element-container:has(.scanner-wrap) + .element-container .hero {{
  margin-top: 0 !important;
}}
.bc-input{{
margin-bottom: 10px;
  border-bottom: var(--bdr);

}}

.section {{
  background: var(--card);
  margin-top: 6px;
  padding: 18px 20px;
  border-bottom: var(--bdr);
}}
.section-hd {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}}
.section-title {{
  font-family: var(--font);
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--sub);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}}
.section-badge {{
  font-family: var(--mono);
  font-size: 0.54rem;
  padding: 3px 9px;
  border-radius: 20px;
  background: var(--pl-bg);
  color: var(--pl-fg);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  font-weight: 500;
}}
.section-sub {{
  font-family: var(--font);
  font-size: 0.72rem;
  color: var(--sub);
  margin-bottom: 14px;
  margin-top: -8px;
  font-weight: 400;
  opacity: 0.75;
}}
.divider {{
  height: 1px;
  background: var(--bar-bg);
  margin: 13px 0;
  opacity: 0.6;
}}

/* ── FACTOR ROWS ── */
.factor {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 0;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}}
.factor:last-child {{ border-bottom: none; }}
.factor-icon {{
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}}
.fi-green {{ background: #F0FDF4; }}
.fi-orange {{ background: #FFFBEB; }}
.fi-red {{ background: #FFF1F2; }}
.factor-text {{ flex: 1; min-width: 0; }}
.factor-name {{
  font-family: var(--font);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.01em;
}}
.factor-desc {{
  font-family: var(--font);
  font-size: 0.7rem;
  color: var(--sub);
  margin-top: 2px;
  letter-spacing: -0.01em;
}}
.dot {{
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}}
.dot-g {{ background: #16A34A; }}
.dot-o {{ background: #D97706; }}
.dot-r {{ background: #DC2626; }}

/* ── ADDITIVI ── */
.additivi-section {{
  background: #FFFDF5;
  border: 1px solid #F5E4A8;
  border-radius: var(--r-sm);
  padding: 14px 16px;
}}
.additivi-title {{
  font-family: var(--font);
  font-size: 0.72rem;
  font-weight: 700;
  color: #92400E;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.additive-pill {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid #F5E4A8;
  border-radius: 20px;
  padding: 5px 11px;
  margin: 2px 2px;
  font-family: var(--mono);
  font-size: 0.64rem;
  color: #78350F;
  font-weight: 500;
}}
.additive-risk {{
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}}
.risk-low {{ background: #D97706; }}
.risk-med {{ background: #DC2626; }}
.risk-high {{ background: #7F1D1D; }}

/* ── NF BARS ── */
.nf-row {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}}
.nf-row:last-child {{ border-bottom: none; }}
.nf-name {{
  font-family: var(--font);
  font-size: 0.79rem;
  color: var(--text);
  width: 128px;
  flex-shrink: 0;
  font-weight: 500;
  letter-spacing: -0.01em;
}}
.nf-bar-bg {{
  flex: 1;
  height: 4px;
  background: var(--bar-bg);
  border-radius: 3px;
  overflow: hidden;
}}
.nf-bar {{
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}}
.nf-val {{
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--sub);
  width: 44px;
  text-align: right;
  flex-shrink: 0;
  font-weight: 500;
}}

/* ── INGREDIENTI ── */
.ing-text {{
  font-family: var(--font);
  font-size: 0.82rem;
  line-height: 1.9;
  color: var(--text);
  font-weight: 400;
  letter-spacing: -0.01em;
}}
.ia {{
  color: #DC2626;
  font-weight: 700;
  text-transform: uppercase;
  background: #FFF1F2;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.75rem;
}}
.ing-missing {{
  background: var(--bg);
  border-radius: var(--r-sm);
  padding: 16px;
  font-family: var(--font);
  font-size: 0.8rem;
  color: var(--sub);
  text-align: center;
  border: var(--bdr);
}}
.atags {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}}
.atag {{
  font-family: var(--font);
  font-size: 0.68rem;
  padding: 4px 10px;
  background: #FFF1F2;
  border: 1px solid #FECDD3;
  color: #9F1239;
  border-radius: 20px;
  font-weight: 500;
  letter-spacing: -0.01em;
}}

/* ── CHART ── */
.chart-wrap {{
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 4px 0 14px;
  flex-wrap: wrap;
}}
.chart-legend {{
  font-family: var(--font);
  font-size: 0.78rem;
  line-height: 2.1;
  color: var(--text);
  font-weight: 400;
  letter-spacing: -0.01em;
}}

/* ── KCAL ROW ── */
.kcal-row {{
  display: flex;
  align-items: baseline;
  gap: 7px;
  margin-top: 14px;
  padding: 10px 14px;
  background: var(--bg);
  border-radius: var(--r-sm);
  border: var(--bdr);
}}
.kcal-label {{
  font-family: var(--font);
  font-size: 0.74rem;
  color: var(--sub);
  letter-spacing: -0.01em;
}}
.kcal-val {{
  font-family: var(--font);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.04em;
}}
.kcal-unit {{
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--sub);
}}

/* ── FSA INFO ── */
.fsa-info {{
  font-family: var(--mono);
  font-size: 0.56rem;
  color: var(--sub);
  margin-top: 14px;
  padding: 10px 12px;
  background: var(--bg);
  border-radius: var(--r-sm);
  line-height: 1.8;
  border: var(--bdr);
  letter-spacing: 0.01em;
  opacity: 0.7;
}}

/* ── ALT CARDS ── */
.alt-card {{
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 13px 0;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}}
.alt-card:last-child {{ border-bottom: none; }}
.alt-info {{
  flex: 1;
  min-width: 0;
}}
.alt-name {{
  font-family: var(--font);
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.02em;
}}
.alt-brand {{
  font-family: var(--font);
  font-size: 0.7rem;
  color: var(--sub);
  margin-top: 2px;
  letter-spacing: -0.01em;
}}
.alt-link {{
  font-family: var(--font);
  font-size: 0.72rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  border: 1.5px solid var(--accent);
  border-radius: var(--r-xs);
  padding: 7px 12px;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
  letter-spacing: -0.01em;
}}
.alt-link:hover {{
  background: var(--accent);
  color: #fff;
}}

/* ── MISC ── */
.src-badge {{
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--accent);
  background: var(--pl-bg);
  border-radius: 20px;
  padding: 3px 10px;
  margin-bottom: 8px;
  letter-spacing: 0.04em;
  font-weight: 500;
}}
.ps-err {{
  background: var(--card);
  border: 1px solid #FECDD3;
  border-radius: var(--r);
  padding: 14px 18px;
  font-family: var(--font);
  font-size: 0.85rem;
  color: #9F1239;
  margin: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: var(--sh-xs);
  letter-spacing: -0.01em;
}}
.scanner-wrap {{
  background: var(--card);
  padding: 30px 16px 14px;
  margin-top: 0;
  border-bottom: none;
}}

#alternativesSection {{
    padding-bottom: 100px;
    margin-bottom: 0;
}}

.ps-footer {{
    background: var(--card);
  padding: 10px 16px calc(10px + env(safe-area-inset-bottom));
  border-top: var(--bdr);
  display: flex;
  align-items: center;
  justify-content: space-around;
  width: 100%;
  position: fixed;
  bottom: 0;
  left: 0;
  z-index: 100;
}}
.ps-footer-btn {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  flex: 1;
  padding: 6px 4px;
  border-radius: 9px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: var(--mono);
  font-size: 0.54rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--sub);
  transition: background 0.15s;
}}
.ps-footer-btn:hover {{
  background: rgba(0,0,0,0.05);
}}
.ps-footer-btn.active {{
  color: var(--accent);
  background: var(--glow);
}}
.ps-footer-btn svg {{
  width: 18px;
  height: 18px;
}}

#product-presentation {{
 padding-top: 30px
}}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 480px) {{
  .block-container {{ max-width: 100% !important; }}
  .hero {{ padding: 16px 16px 14px; }}
  .section {{ padding: 16px 16px; }}
  .ps-footer {{ padding: 16px 16px; }}
  .search-wrap {{ padding: 12px 14px 10px; }}
  .nf-name {{ width: 95px !important; font-size: 0.74rem !important; }}
  .score-num {{ font-size: 1.35rem !important; }}
  .hero-name {{ font-size: 0.96rem !important; }}
  .score-ring {{ width: 62px !important; height: 62px !important; }}
  .hero-img, .hero-img-ph {{ width: 66px !important; height: 66px !important; }}
  .factor-icon {{ width: 32px !important; height: 32px !important; }}
  .ps-header {{ padding: 12px 16px; }}
}}

@media (max-width: 360px) {{
  .hero-name {{ font-size: 0.88rem !important; }}
  .score-num {{ font-size: 1.2rem !important; }}
  .section-title {{ font-size: 0.64rem !important; }}
  .factor-name {{ font-size: 0.82rem !important; }}
}}

</style>
<script>
(function() {{
  function fixIframes() {{
    document.querySelectorAll('iframe').forEach(function(f) {{
      if (!f.getAttribute('allow') || !f.getAttribute('allow').includes('camera'))
        f.setAttribute('allow', 'camera;microphone');
    }});
  }}
  fixIframes();
  new MutationObserver(fixIframes).observe(document.body, {{childList: true, subtree: true}});
}})();
</script>
"""


# ── FSA NUTRIENT PROFILING MODEL ─────────────────────────────
ADDITIVI_DB = {
    "en:e102": ("Tartrazina", "Colorante azoico, possibile iperattività nei bambini", "high"),
    "en:e110": ("Sunset Yellow", "Colorante azoico, vietato in alcuni paesi", "high"),
    "en:e122": ("Carmoisina", "Colorante azoico, possibile iperattività", "high"),
    "en:e124": ("Ponceau 4R", "Colorante azoico, vietato negli USA", "high"),
    "en:e129": ("Rosso Allura", "Colorante azoico", "med"),
    "en:e171": ("Biossido di Titanio", "Classificato possibile cancerogeno EFSA 2021", "high"),
    "en:e211": ("Benzoato di Sodio", "Conservante, possibile iperattività in combo con coloranti", "med"),
    "en:e220": ("Anidride Solforosa", "Conservante, può causare reazioni nei sensibili", "med"),
    "en:e250": ("Nitrito di Sodio", "Conservante carni, potenzialmente cancerogeno (IARC)", "high"),
    "en:e251": ("Nitrato di Sodio", "Conservante carni, convertibile in nitriti", "high"),
    "en:e320": ("BHA", "Conservante antiossidante, possibile cancerogeno", "high"),
    "en:e321": ("BHT", "Conservante antiossidante, controverso", "med"),
    "en:e951": ("Aspartame", "Dolcificante, controverso (rivalutazione EFSA 2023)", "med"),
    "en:e950": ("Acesulfame K", "Dolcificante intensivo", "low"),
    "en:e955": ("Sucralosio", "Dolcificante clorurato", "low"),
    "en:e471": ("Mono/Digliceridi", "Emulsionante, possibile impatto microbioma", "low"),
    "en:e472e": ("DATEM", "Emulsionante", "low"),
    "en:e476": ("Poliricinoleato", "Emulsionante", "low"),
    "en:e481": ("Stearoil Lattilato Na", "Emulsionante", "low"),
    "en:e621": ("Glutammato Monosodico", "Esaltatore di sapidità", "low"),
    "en:e627": ("Guanilato Disodico", "Esaltatore di sapidità", "low"),
    "en:e407": ("Carragenina", "Addensante, possibile infiammazione intestinale", "med"),
    "en:e412": ("Gomma di Guar", "Addensante, generalmente sicuro", "low"),
    "en:e415": ("Gomma Xantana", "Addensante, generalmente sicuro", "low"),
    "en:e433": ("Polisorbato 80", "Emulsionante, impatto microbioma (studi su topi)", "med"),
}


def compute_fsa_score(p):
    nutriments = p.get("nutriments", {})
    pos_factors, neg_factors = [], []
    kj = nutriments.get("energy_100g") or (nutriments.get("energy-kcal_100g", 0) * 4.184)
    a_en = a_en_calculator(kj)
    sug = nutriments.get("sugars_100g") or 0
    a_sug = a_sug_calculator(sug)
    sat = nutriments.get("saturated-fat_100g") or 0
    a_sat = a_sat_calculator(sat)
    salt = nutriments.get("salt_100g") or 0
    sodium = salt * 400
    a_sod = sodium_calculator(sodium)
    score_a = a_en + a_sug + a_sat + a_sod
    fiber = nutriments.get("fiber_100g") or 0
    c_fib = fiber_calculator(fiber)
    prot = nutriments.get("proteins_100g") or 0
    c_pro = prot_calculator(prot)
    fvn = nutriments.get("fruits-vegetables-nuts-estimate-from-ingredients_100g") or nutriments.get("fruits-vegetables-nuts_100g") or 0
    c_fvn = fvn_calculator(fvn)
    score_c = c_fib + c_pro + c_fvn
    fsa_raw = score_a - score_c
    score_100 = round(max(0, min(100, (40 - fsa_raw) / 55 * 100)))
    nova = p.get("nova_group")
    nova_malus = {1: 0, 2: 0, 3: -5, 4: -15}
    if nova and nova in nova_malus:
        score_100 = max(0, score_100 + nova_malus[nova])
    kcal = nutriments.get("energy-kcal_100g") or (kj / 4.184 if kj else None)
    if c_fib >= 3:
        pos_factors.append(("🌾", "Fibre", f"Eccellente: {fiber:.1f}g/100g", "dot-g"))
    elif c_fib >= 1:
        pos_factors.append(("🌾", "Fibre", f"Presente: {fiber:.1f}g/100g", "dot-g"))
    if c_pro >= 3:
        pos_factors.append(("💪", "Proteine", f"Ottima quantità: {prot:.1f}g/100g", "dot-g"))
    elif c_pro >= 1:
        pos_factors.append(("💪", "Proteine", f"Buona quantità: {prot:.1f}g/100g", "dot-g"))
    if c_fvn >= 2:
        pos_factors.append(("🍎", "Frutta/Verdura", f"Alta presenza: {fvn:.0f}%", "dot-g"))
    elif c_fvn == 1:
        pos_factors.append(("🍎", "Frutta/Verdura", f"Presente: {fvn:.0f}%", "dot-g"))
    if a_sod == 0:
        pos_factors.append(("🧂", "Sale", f"Senza sale: {salt:.2f}g/100g", "dot-g"))
    elif a_sod <= 1:
        pos_factors.append(("🧂", "Sale", f"Basso: {salt:.2f}g/100g", "dot-g"))
    if a_sat <= 1: pos_factors.append(("💧", "Grassi saturi", f"Bassi: {sat:.1f}g/100g", "dot-g"))
    if nova and nova <= 2: pos_factors.append(
        ("🌿", "Alimento non trasformato", f"NOVA {nova} — bassa trasformazione", "dot-g"))
    if a_sug >= 5:
        neg_factors.append(("🍬", "Zuccheri", f"Elevati: {sug:.1f}g/100g", "dot-r"))
    elif a_sug >= 2:
        neg_factors.append(("🍬", "Zuccheri", f"Moderati: {sug:.1f}g/100g", "dot-o"))
    if a_sat >= 5:
        neg_factors.append(("🧈", "Grassi saturi", f"Elevati: {sat:.1f}g/100g", "dot-r"))
    elif a_sat >= 3:
        neg_factors.append(("🧈", "Grassi saturi", f"Moderati: {sat:.1f}g/100g", "dot-o"))
    if a_sod >= 5:
        neg_factors.append(("🧂", "Sale", f"Elevato: {salt:.2f}g/100g", "dot-r"))
    elif a_sod >= 3:
        neg_factors.append(("🧂", "Sale", f"Moderato: {salt:.2f}g/100g", "dot-o"))
    if kcal and kcal > 450: neg_factors.append(("🔥", "Energia", f"{int(kcal)} kcal/100g", "dot-o"))
    if nova and nova == 4:
        neg_factors.append(("🏭", "Ultra-trasformato", "NOVA 4 — alto grado di trasformazione", "dot-r"))
    elif nova and nova == 3:
        neg_factors.append(("🏭", "Trasformato", "NOVA 3 — alimento trasformato", "dot-o"))
    return score_100, pos_factors, neg_factors, {
        "a": score_a, "c": score_c, "fsa": fsa_raw,
        "nova": nova, "fiber": fiber, "prot": prot, "sugar": sug,
        "sat": sat, "salt": salt, "kcal": kcal, "fvn": fvn,
    }

# ── FSA CALCULATORS ────────────────────────────────────────────────
def a_en_calculator(kj: int) -> int:
    return min(10, int(kj / 335))

    # if kj <= 335:
    #     a_en = 0
    # elif kj <= 670:
    #     a_en = 1
    # elif kj <= 1005:
    #     a_en = 2
    # elif kj <= 1340:
    #     a_en = 3
    # elif kj <= 1675:
    #     a_en = 4
    # elif kj <= 2010:
    #     a_en = 5
    # elif kj <= 2345:
    #     a_en = 6
    # elif kj <= 2680:
    #     a_en = 7
    # elif kj <= 3015:
    #     a_en = 8
    # elif kj <= 3350:
    #     a_en = 9
    # else:
    #     a_en = 10
    # return a_en


def a_sug_calculator(sug: int) -> int:
    return min(10, int(sug / 4.5))

    # if sug <= 4.5:
    #     a_sug = 0
    # elif sug <= 9:
    #     a_sug = 1
    # elif sug <= 13.5:
    #     a_sug = 2
    # elif sug <= 18:
    #     a_sug = 3
    # elif sug <= 22.5:
    #     a_sug = 4
    # elif sug <= 27:
    #     a_sug = 5
    # elif sug <= 31:
    #     a_sug = 6
    # elif sug <= 36:
    #     a_sug = 7
    # elif sug <= 40:
    #     a_sug = 8
    # elif sug <= 45:
    #     a_sug = 9
    # else:
    #     a_sug = 10
    # return a_sug


def a_sat_calculator(sat: int ) -> int:
    return max(0, min(10, int(sat) - 1))

    if sat <= 1:
        a_sat = 0
    elif sat <= 2:
        a_sat = 1
    elif sat <= 3:
        a_sat = 2
    elif sat <= 4:
        a_sat = 3
    elif sat <= 5:
        a_sat = 4
    elif sat <= 6:
        a_sat = 5
    elif sat <= 7:
        a_sat = 6
    elif sat <= 8:
        a_sat = 7
    elif sat <= 9:
        a_sat = 8
    elif sat <= 10:
        a_sat = 9
    else:
        a_sat = 10
    return a_sat


def fvn_calculator(fvn: int) -> int:
    if fvn <= 40:
        c_fvn = 0
    elif fvn <= 60:
        c_fvn = 1
    elif fvn <= 80:
        c_fvn = 2
    else:
        c_fvn = 5
    return c_fvn


def prot_calculator(prot: int) -> int:
    return min(5, int(prot / 1.6) - 1)

    if prot <= 1.6:
        c_pro = 0
    elif prot <= 3.2:
        c_pro = 1
    elif prot <= 4.8:
        c_pro = 2
    elif prot <= 6.4:
        c_pro = 3
    elif prot <= 8.0:
        c_pro = 4
    else:
        c_pro = 5
    return c_pro


def fiber_calculator(fiber: int) -> int:
    return next((i for i, t in enumerate([0.9, 1.9, 2.8, 3.7, 4.7]) if fiber <= t), 5)
    # if fiber <= 0.9:
    #     c_fib = 0
    # elif fiber <= 1.9:
    #     c_fib = 1
    # elif fiber <= 2.8:
    #     c_fib = 2
    # elif fiber <= 3.7:
    #     c_fib = 3
    # elif fiber <= 4.7:
    #     c_fib = 4
    # else:
    #     c_fib = 5
    # return c_fib


def sodium_calculator(sodium: int) -> int:
    return min(10, int(sodium / 90))

    if sodium <= 90:
        a_sod = 0
    elif sodium <= 180:
        a_sod = 1
    elif sodium <= 270:
        a_sod = 2
    elif sodium <= 360:
        a_sod = 3
    elif sodium <= 450:
        a_sod = 4
    elif sodium <= 540:
        a_sod = 5
    elif sodium <= 630:
        a_sod = 6
    elif sodium <= 720:
        a_sod = 7
    elif sodium <= 810:
        a_sod = 8
    elif sodium <= 900:
        a_sod = 9
    else:
        a_sod = 10
    return a_sod


# ── ADDITIVI ────────────────────────────────────────────────
def render_additivi(p):
    tags = p.get("additives_tags") or []
    if not tags:
        return ('<div class="additivi-section" style="background:#F0FDF4;border-color:#BBF7D0;">'
                '<div class="additivi-title" style="color:#14532D;">✓ Nessun additivo rilevato</div>'
                '<div style="font-family:\'DM Sans\',sans-serif;font-size:.78rem;color:#16A34A;line-height:1.6;font-weight:400;">'
                'Ottimo: nessun additivo presente nel database.</div>'
                '</div>')
    pills = ""
    for tag in tags:
        tag_clean = tag.lower().replace("_", " ")
        if tag_clean in ADDITIVI_DB:
            name, desc, risk = ADDITIVI_DB[tag_clean]
            risk_cls = f"risk-{risk}"
            code = tag.replace("en:", "").upper()
            pills += f'<div class="additive-pill"><div class="additive-risk {risk_cls}"></div>{code} — {name}</div>'
        else:
            code = tag.replace("en:", "").upper()
            pills += f'<div class="additive-pill"><div class="additive-risk risk-low"></div>{code}</div>'
    risk_legend = '<div style="font-family:\'DM Mono\',monospace;font-size:.54rem;color:#92400E;margin-top:10px;letter-spacing:.02em;opacity:.75;">● Alto &nbsp;● Moderato &nbsp;● Basso rischio</div>'
    return f'<div class="additivi-section"><div class="additivi-title">⚗ Additivi ({len(tags)})</div>{pills}{risk_legend}</div>'


# ── DATA SOURCES ─────────────────────────────────────────────
_OFF_FIELDS = ",".join([
    "product_name", "product_name_it", "product_name_en", "product_name_fr",
    "brands", "categories_tags", "ingredients_text", "ingredients_text_it",
    "ingredients_text_en", "ingredients_text_fr", "ingredients",
    "allergens_tags", "additives_tags", "nova_group",
    "nutriscore_grade", "nutriments",
    "image_url", "image_front_url", "code",
])

DBS = [
    ("food", "Open Food Facts", "https://world.openfoodfacts.org"),
    ("beauty", "Open Beauty Facts", "https://world.openbeautyfacts.org"),
    ("generic", "Open Products Facts", "https://world.openproductsfacts.org"),
]


@st.cache_data(ttl=604800, show_spinner=False)
def _fetch_off_single(barcode: str, base: str) -> dict | None:
    url = f"{base}/api/v2/product/{barcode}"
    try:
        r = _HTTP.get(url, params={"fields": _OFF_FIELDS}, timeout=(4, 10))
        r.raise_for_status()
        data = r.json()
        if data.get("status") == 1 and data.get("product"):
            return data["product"]
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException:
        pass
    return None

def fetch_off(barcode: str, placeholder) -> tuple[dict | None, str | None, str | None]:
    for db_id, db_name, base in DBS:
        placeholder.markdown(f'<div class="src-badge">→ {db_name}</div>', unsafe_allow_html=True)
        product = _fetch_off_single(barcode, base)
        if product:
            return product, db_id, db_name
    return None, None, None


def fetch_upc(barcode: str, placeholder) -> tuple[dict | None, str | None, str | None]:
    placeholder.markdown('<div class="src-badge">→ UPCitemdb</div>', unsafe_allow_html=True)
    url = "https://api.upcitemdb.com/prod/trial/lookup"
    try:
        r = _HTTP.get(url, params={"upc": barcode}, timeout=(4, 10))
        if r.status_code == 429:
            return None, None, None
        r.raise_for_status()
        items = r.json().get("items") or []
        if not items:
            return None, None, None
        item = items[0]
        product = {
            "product_name": item.get("title", ""),
            "brands": item.get("brand", ""),
            "categories": item.get("category", ""),
            "ingredients_text": item.get("ingredients", ""),
            "image_url": (item.get("images") or [""])[0],
        }
        return product, "generic", "UPCitemdb"
    except requests.exceptions.RequestException:
        return None, None, None


def search(barcode: str, placeholder) -> tuple[dict | None, str | None, str | None]:
    product, db_id, source = fetch_off(barcode, placeholder)
    if product:
        return product, db_id, source
    return fetch_upc(barcode, placeholder)


def normalize_query_value(v):
    if isinstance(v, list):
        return str(v[0]).strip() if v else ""
    return str(v).strip() if v is not None else ""


# ── SUGGESTIONS ──────────────────────────────────────────────
_SEARCH_FIELDS = "product_name,brands,nutriscore_grade,nova_group,nutriments,additives_tags,categories_tags,code"
@st.cache_data(ttl=604800, show_spinner=False)
def get_suggestions(cats: tuple, current_score, current_ns: str = ""):
    """
    Cerca alternative migliori per un alimento.
    Strategia:
      1) Categorie da più specifica a più generale (top 5)
      2) Fallback Nutri-Score: filtro nutrition_grades=a sulla categoria più generale
      3) Soglia di miglioramento adattiva (≥+3 inizialmente, scende a +1 nel fallback)
    """
    # `reversed`: OFF ordina dal più generale al più specifico → invertiamo
    candidates = [c for c in reversed(cats) if c.startswith("en:") and len(c) > 5]
    if not candidates:
        return ("no_cat", str(cats[:3]))

    fields = ("product_name,brands,nutriscore_grade,nova_group,nutriments,"
              "additives_tags,categories_tags,code,image_url")
    last_err = ("no_cat", "")

    # ── Step 1: ricerca per categoria, soglia +3 ──
    for cat in candidates[:5]:
        try:
            r = _HTTP.get(
                "https://world.openfoodfacts.org/api/v2/search",
                params={
                    "categories_tags": cat,
                    "sort_by": "unique_scans_n",
                    "page_size": 30,
                    "fields": _SEARCH_FIELDS,
                },
                timeout=(4, 12),
            )
            if r.status_code != 200:
                last_err = ("http_err", str(r.status_code)); continue
            prods = r.json().get("products", [])
            if not prods:
                last_err = ("empty", cat); continue
            results = []
            for prod in prods:
                if not prod.get("product_name"): continue
                s, _, _, _ = compute_fsa_score(prod)
                if s > current_score + 3:
                    results.append((s, prod))
            results.sort(key=lambda x: -x[0])
            if results:
                return results[:4]
            last_err = ("none_better", f"score={current_score}")
        except Exception as ex:
            last_err = ("exception", str(ex)[:80]); continue

    # ── Step 2: fallback Nutri-Score=a sulla categoria più generale ──
    # Senza questo, prodotti molto specifici (es. "biscotti al cioccolato senza glutine")
    # spesso non hanno alternative migliori entro la categoria stretta.
    #current_ns = (p.get("nutriscore_grade") or "").lower()
    if current_ns in "cdez" or current_score < 50:
        broad_cats = candidates[-3:]  # top categorie più generali
        for cat in broad_cats:
            try:
                r = _HTTP.get(
                    "https://world.openfoodfacts.org/api/v2/search",
                    params={
                        "categories_tags": cat,
                        "nutrition_grades_tags": "a",
                        "sort_by": "unique_scans_n",
                        "page_size": 20,
                        "fields": _SEARCH_FIELDS,
                    },
                    timeout=(4, 12),
                )
                if r.status_code != 200: continue
                prods = r.json().get("products", [])
                if not prods: continue
                results = []
                for prod in prods:
                    if not prod.get("product_name"): continue
                    s, _, _, _ = compute_fsa_score(prod)
                    if s > current_score + 1:  # soglia ridotta nel fallback
                        results.append((s, prod))
                results.sort(key=lambda x: -x[0])
                if results:
                    return results[:4]
            except Exception as ex:
                last_err = ("exception", str(ex)[:80]); continue

    return last_err

@st.cache_data(ttl=604800, show_spinner=False)
def get_suggestions_old(cats: tuple, current_score: int):
    global last_err
    candidates = [c for c in reversed(cats) if c.startswith("en:") and len(c) > 5]
    if not candidates:
        return ("no_cat", str(cats[:3]))

    for cat in candidates[:3]:
        try:
            r = _HTTP.get(
                "https://world.openfoodfacts.org/api/v2/search",
                params={
                    "categories_tags": cat,
                    "sort_by": "unique_scans_n",
                    "page_size": 30,
                    "fields": _SEARCH_FIELDS,
                },
                timeout=(4, 12),
            )
            if r.status_code != 200:
                last_err = ("http_err", str(r.status_code))
                continue

            prods = (r.json()).get("products") or []
            prods = [p for p in prods if p.get("nutriscore_grade", "") in ("a", "b", "c", "d")]
            if not prods:
                last_err = ("empty", cat)
                continue
            results = []
            for prod in prods:
                if not prod.get("product_name"): continue
                s, _, _, _ = compute_fsa_score(prod)
                if s > current_score + 3:
                    results.append((s, prod))
                if len(results) >= 4: break
            results.sort(key=lambda x: -x[0])
            if results:
                return results[:4]
            last_err = ("none_better", f"score={current_score}")
        except requests.exceptions.Timeout:
            last_err = ("exception", "timeout")
        except Exception as ex:
            last_err = ("exception", str(ex)[:80])
    return last_err


# ── HELPERS ──────────────────────────────────────────────────
def e(s): return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nutriscore_html(ns):
    letters, colors = ["A", "B", "C", "D", "E"], ["nsa-c", "nsb-c", "nsc-c", "nsd-c", "nse-c"]
    html = '<div class="ns-row">'
    for l, c in zip(letters, colors):
        html += f'<div class="ns-l {c}{"  active" if l.lower() == ns else ""}">{l}</div>'
    return html + "</div>"


def nova_html(nova):
    html = '<div class="nova-row">'
    for i, c in enumerate(["n1c", "n2c", "n3c", "n4c"], 1):
        html += f'<div class="nova-dot {c}{"  active" if nova == i else ""}">{i}</div>'
    return html + "</div>"


def macro_svg(fat, carbs, prot):
    tot = fat * 9 + carbs * 4 + prot * 4
    if tot == 0: return ""
    pf = fat * 9 / tot * 100;
    pc = carbs * 4 / tot * 100;
    pp = prot * 4 / tot * 100

    def sl(s, en, col):
        if en - s >= 100: en -= 0.01
        a = math.radians(s / 100 * 360 - 90);
        b = math.radians(en / 100 * 360 - 90)
        r = 52;
        cx = 60;
        cy = 60
        x1, y1 = cx + r * math.cos(a), cy + r * math.sin(a)
        x2, y2 = cx + r * math.cos(b), cy + r * math.sin(b)
        return f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {1 if en - s > 50 else 0},1 {x2:.1f},{y2:.1f} Z" fill="{col}"/>'

    svg = (f'<svg width="108" height="108" viewBox="0 0 120 120">'
           f'{sl(0, pf, "#DC2626")}{sl(pf, pf + pc, "#D97706")}{sl(pf + pc, pf + pc + pp, "#16A34A")}'
           f'<circle cx="60" cy="60" r="30" fill="var(--bg)"/>'
           f'<text x="60" y="57" text-anchor="middle" font-family="DM Sans" font-size="10" font-weight="700" fill="var(--text)">{int(tot)}</text>'
           f'<text x="60" y="69" text-anchor="middle" font-family="DM Mono" font-size="7" fill="var(--sub)">kcal</text>'
           f'</svg>')
    leg = (f'<div class="chart-legend">'
           f'<span style="color:#DC2626">●</span> Grassi {fat:.1f}g ({pf:.0f}%)<br>'
           f'<span style="color:#D97706">●</span> Carb {carbs:.1f}g ({pc:.0f}%)<br>'
           f'<span style="color:#16A34A">●</span> Prot {prot:.1f}g ({pp:.0f}%)</div>')
    return f'<div class="chart-wrap">{svg}{leg}</div>'


def ha(txt):
    for a in ['LATTE', 'GLUTINE', 'FRUMENTO', 'GRANO', 'UOVA', 'SOIA', 'ARACHIDI', 'NOCI',
              'MANDORLE', 'NOCCIOLE', 'SESAMO', 'SENAPE', 'SEDANO', 'LUPINI', 'CROSTACEI', 'PESCE', 'SOLFITI']:
        txt = re.sub(f'\\b{a}\\b', f'<span class="ia">{a}</span>', txt, flags=re.IGNORECASE)
    return txt


def nf_bar(name, val, mx, unit, color):
    pct = min(100, (val / mx) * 100) if val else 0
    vs = f"{val:.1f}{unit}" if val is not None else "—"
    return (f'<div class="nf-row"><div class="nf-name">{name}</div>'
            f'<div class="nf-bar-bg"><div class="nf-bar" style="width:{pct}%;background:{color};"></div></div>'
            f'<div class="nf-val">{vs}</div></div>')


def factor_row(icon, name, desc, dot):
    fi = {"dot-g": "fi-green", "dot-o": "fi-orange", "dot-r": "fi-red"}.get(dot, "fi-orange")
    return (f'<div class="factor"><div class="factor-icon {fi}">{icon}</div>'
            f'<div class="factor-text"><div class="factor-name">{name}</div>'
            f'<div class="factor-desc">{desc}</div></div>'
            f'<div class="dot {dot}"></div></div>')


def bar_color(v, low, high):
    if v is None: return "var(--bar-bg)"
    return "#16A34A" if v <= low else "#D97706" if v <= high else "#DC2626"


# ── SCANNER ──────────────────────────────────────────────────
def scanner_html(pal):
    return f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=DM+Mono:wght@400;500&display=swap');
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: {pal['card']}; font-family: 'DM Sans', sans-serif; overflow: hidden;}}
#wrap {{ padding: 0; margin: 6px; }}
#btn {{
  width: 100%; padding: 14px;
  background: {pal['accent']}; border: none;
  font-size: 0.9rem; 
  border-radius: 10px;
  box-shadow: 0 2px 10px {pal['glow']};
  transition: opacity .15s, transform .12s;
}}
#btn:active {{ opacity: .85; transform: scale(.99); }}
#stop {{
  width: 100%; padding: 14px;
  background: transparent; color: {pal['accent']};
  border: 1.5px solid {pal['accent']}; font-size: 0.9rem; font-weight: 600;
  cursor: pointer; border-radius: 10px; display: none;
  letter-spacing: -0.01em;
}}
#vp {{ width: 100%; border-radius: 10px; overflow: hidden; background: #000; margin-top: 10px; }}
#vp video {{ width: 100% !important; display: block; }}
#vp canvas.drawingBuffer {{ display: none !important; }}
#msg {{
  font-size: 0.66rem; color: {pal['sub']}; padding: 7px 0 0; text-align: center;
  font-family: 'DM Mono', monospace; letter-spacing: 0.03em; opacity: .75;
}}
#found {{
  display: none; margin-top: 9px; padding: 14px;
  background: {pal['score_bg']}; border-radius: 10px; text-align: center;
  border: 1px solid {pal['score_border']};
}}
#found-code {{
  font-size: 0.9rem; color: {pal['text']}; font-weight: 700;
  margin-bottom: 11px; font-family: 'DM Mono', monospace; letter-spacing: 0.06em;
}}
#found-btn {{
  display: inline-block; padding: 10px 22px;
  background: {pal['accent']}; color: #fff; border: none;
  font-size: 0.83rem; font-weight: 600; cursor: pointer;
  border-radius: 8px; text-decoration: none; letter-spacing: -0.01em;
}}
</style>
<div id="wrap">
  <button id="btn" onclick="go()">Scan Barcode</button>
  <button id="stop" onclick="halt()">⏹ Ferma</button>
  <div id="vp"></div>
  <div id="msg"></div>
  <div id="found">
    <div id="found-code"></div>
    <a id="found-btn" href="#" target="_top">Cerca Prodotto →</a>
  </div>
</div>
<script>
var running=false,done=false;

function resize(){{
  var h = document.getElementById('wrap').scrollHeight;
  window.parent.postMessage({{type:'streamlit:setFrameHeight', height: h + 4}}, '*');
}}

// Send height on load and after any DOM change
window.addEventListener('load', function(){{ setTimeout(resize, 50); }});
new MutationObserver(resize).observe(document.getElementById('wrap'), {{subtree:true, childList:true, attributes:true}});

function go(){{
  done=false;
  document.getElementById('btn').style.display='none';
  document.getElementById('stop').style.display='block';
  document.getElementById('found').style.display='none';
  document.getElementById('msg').textContent='Inizializzazione fotocamera...';
  resize();
  Quagga.init({{
    inputStream:{{type:"LiveStream",target:document.getElementById('vp'),
      constraints:{{facingMode:"environment",width:{{ideal:1280}},height:{{ideal:720}}}}}},
    decoder:{{readers:["ean_reader","ean_8_reader","upc_reader","upc_e_reader","code_128_reader"]}},
    locate:true,numOfWorkers:2,frequency:10
  }},function(err){{
    if(err){{document.getElementById('msg').textContent='Errore: '+err;halt();return;}}
    Quagga.start();running=true;
    document.getElementById('msg').textContent='Inquadra il barcode...';
    setTimeout(resize, 300);
  }});
  Quagga.onDetected(function(r){{
    if(done)return;done=true;
    var code=r.codeResult.code;
    halt();
    document.getElementById('msg').textContent='✓ Rilevato';
    document.getElementById('found-code').textContent=code;
    var target=window.top.location.pathname+'?barcode='+encodeURIComponent(code);
    document.getElementById('found-btn').href=target;
    document.getElementById('found').style.display='block';
    resize();
    setTimeout(function(){{window.top.location.href=target;}},250);
  }});
}}
function halt(){{
  if(running){{try{{Quagga.stop();}}catch(e){{}}running=false;}}
  document.getElementById('btn').style.display='block';
  document.getElementById('stop').style.display='none';
  document.getElementById('vp').innerHTML='';
  resize();
}}
</script>"""


# ── RENDER FOOD ───────────────────────────────────────────────
def render_food(p, score, pos, neg, details, pal):
    n = p.get("nutriments", {})
    name = e(p.get("product_name") or p.get("product_name_it") or p.get("product_name_en") or "Prodotto")
    brand = e(p.get("brands", ""))
    img = p.get("image_url") or p.get("image_front_url") or ""
    ns = (p.get("nutriscore_grade") or "").lower()
    nova = p.get("nova_group")
    label = pal['label'];
    medal = pal['medal']
    sc_fg = pal['score_fg']

    img_html = (f'<img class="hero-img" src="{img}" onerror="this.style.display=\'none\'">'
                if img else '<div class="hero-img-ph">📦</div>')

    # SVG ring
    circ = 2 * math.pi * 27
    dash = circ * score / 100
    ring_svg = (f'<svg width="68" height="68" viewBox="0 0 68 68" style="transform:rotate(-90deg)">'
                f'<circle cx="34" cy="34" r="27" fill="none" stroke="color-mix(in srgb,{sc_fg} 14%,transparent)" stroke-width="5"/>'
                f'<circle cx="34" cy="34" r="27" fill="none" stroke="{sc_fg}" stroke-width="5"'
                f' stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-linecap="round"/>'
                f'</svg>')

    st.markdown(
        f'<div class="hero" id="product-presentation">'
        f'<div class="hero-top">{img_html}'
        f'<div class="hero-meta">'
        f'<div class="hero-name">{name}</div>'
        f'<div class="hero-brand">{brand}</div>'
        f'{nutriscore_html(ns)}'
        f'</div></div>'
        f'<div class="score-card">'
        f'  <div class="score-ring">'
        f'    {ring_svg}'
        f'    <div class="score-ring-inner">'
        f'      <div class="score-num">{score}</div>'
        f'      <div class="score-den">/100</div>'
        f'    </div>'
        f'  </div>'
        f'  <div class="score-body">'
        f'    <div class="score-medal">{medal}</div>'
        f'    <div class="score-label">{label}</div>'
        f'    <div class="score-meta">FSA Nutrient Profiling Model<br>'
        f'NOVA: {nova or "N/D"} · Nutri-Score: {ns.upper() if ns else "N/D"}</div>'
        f'  </div>'
        f'</div>'
        f'<div class="score-track"><div class="score-fill" style="width:{score}%;"></div></div>'
        f'</div>', unsafe_allow_html=True)

    if pos:
        rows = "".join([factor_row(ic, nm, dc, dt) for ic, nm, dc, dt in pos])
        st.markdown(
            f'<div class="section"><div class="section-hd"><div class="section-title">Positivo</div><div class="section-badge">per 100g</div></div>{rows}</div>',
            unsafe_allow_html=True)

    if neg:
        rows = "".join([factor_row(ic, nm, dc, dt) for ic, nm, dc, dt in neg])
        st.markdown(
            f'<div class="section"><div class="section-hd"><div class="section-title">Negativo</div><div class="section-badge">per 100g</div></div>{rows}</div>',
            unsafe_allow_html=True)

    add_html = render_additivi(p)
    st.markdown(f'<div class="section">{add_html}</div>', unsafe_allow_html=True)

    ing = (p.get("ingredients_text") or p.get("ingredients_text_it") or
           p.get("ingredients_text_en") or p.get("ingredients_text_fr") or "").strip()
    if not ing and p.get("ingredients"):
        try:
            ing = ", ".join([i.get("text", "") for i in p["ingredients"] if i.get("text")])
        except:
            pass
    allergens = [t.replace("en:", "").replace("-", " ") for t in (p.get("allergens_tags") or [])]
    atags_html = "".join([f'<span class="atag">{a}</span>' for a in allergens])
    ih = (f'<div class="ing-text">{ha(e(ing))}</div>' if ing
          else f'<div class="ing-missing">Ingredienti non disponibili.<br>'
               f'<a href="https://world.openfoodfacts.org/product/{e(p.get("code", ""))}" target="_blank" style="color:{pal["accent"]};">Contribuisci su openfoodfacts.org →</a></div>')
    if atags_html:
        ih += f'<div class="atags">{atags_html}</div>'
    st.markdown(
        f'<div class="section"><div class="section-hd"><div class="section-title">Ingredienti</div></div>{ih}</div>',
        unsafe_allow_html=True)

    fat = n.get("fat_100g");
    sat = n.get("saturated-fat_100g")
    carbs = n.get("carbohydrates_100g");
    sugar = n.get("sugars_100g")
    fiber = n.get("fiber_100g");
    prot = n.get("proteins_100g")
    salt = n.get("salt_100g");
    kcal_v = details.get("kcal")

    nf = (nf_bar("Grassi", fat, 30, "g", bar_color(fat, 3, 17.5)) +
          nf_bar("↳ Grassi saturi", sat, 10, "g", bar_color(sat, 1.5, 5)) +
          nf_bar("Carboidrati", carbs, 80, "g", bar_color(carbs, 20, 60)) +
          nf_bar("↳ Zuccheri", sugar, 40, "g", bar_color(sugar, 5, 22.5)) +
          nf_bar("Fibre", fiber, 10, "g", "#16A34A" if fiber and fiber >= 3 else "#D97706") +
          nf_bar("Proteine", prot, 30, "g", "#16A34A" if prot and prot >= 8 else "#D97706") +
          nf_bar("Sale", salt, 3, "g", bar_color(salt, 0.3, 1.5)))

    chart = macro_svg(fat or 0, carbs or 0, prot or 0)
    kcal_s = (f'<div class="kcal-row">'
              f'<span class="kcal-label">Energia per 100g</span>'
              f'<span class="kcal-val">{int(kcal_v)}</span>'
              f'<span class="kcal-unit">kcal</span>'
              f'</div>' if kcal_v else "")
    nova_s = (f'<div class="divider"></div>'
              f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.73rem;font-weight:700;'
              f'margin-bottom:7px;color:var(--text);text-transform:uppercase;letter-spacing:.06em;">'
              f'Trasformazione NOVA</div>'
              f'{nova_html(nova)}'
              f'<div style="font-family:\'DM Mono\',monospace;font-size:.54rem;color:var(--sub);'
              f'margin-top:6px;letter-spacing:.03em;opacity:.7;">Monteiro et al. 2019 — PAHO/WHO</div>')
    fsa_info = (f'<div class="fsa-info">'
                f'Score FSA grezzo: A={details["a"]} C={details["c"]} → {details["fsa"]} → normalizzato {score}/100 · '
                f'Rayner M et al. FSA 2005 — OMS Nutrient Profiling</div>')
    st.markdown(
        f'<div class="section">'
        f'<div class="section-hd"><div class="section-title">Valori Nutrizionali</div>'
        f'<div class="section-badge">per 100g</div></div>'
        f'{chart}{nf}{kcal_s}{nova_s}{fsa_info}'
        f'</div>', unsafe_allow_html=True)


def render_alternatives(suggestions, pal):
    sub = pal["sub"]
    if isinstance(suggestions, tuple):
        err_type, err_msg = suggestions
        msgs = {
            "no_cat": "Categoria prodotto non rilevata nel database.",
            "http_err": f"Errore connessione OFF (HTTP {err_msg}).",
            "empty": f"Nessun prodotto trovato per la categoria: {err_msg}.",
            "none_better": f"Non esistono alternative con score migliore ({err_msg}).",
            "exception": f"Errore di rete: {err_msg}.",
        }
        msg = msgs.get(err_type, f"{err_type}: {err_msg}")
        st.markdown(
            f'<div class="section" id=alternativesSection><div class="section-hd"><div class="section-title">Alternative Migliori</div></div>'
            f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.76rem;color:{sub};padding:4px 0 8px;letter-spacing:-0.01em;">{msg}</div></div>',
            unsafe_allow_html=True)
        return
    if not suggestions:
        return
    html = (f'<div class="section">'
            f'<div class="section-hd"><div class="section-title">Alternative Migliori</div></div>'
            f'<div class="section-sub">Prodotti simili con score FSA superiore</div>')
    for s, prod in suggestions:
        # Grade A (>=75) and B (>=60) both use green; C (>=45) amber; below red
        if s >= 60:
            bc = "#16A34A"
        elif s >= 45:
            bc = "#D97706"
        else:
            bc = "#DC2626"
        name = e((prod.get("product_name") or "")[:45])
        brand = e((prod.get("brands") or "")[:28])
        code = prod.get("code", "")
        ns2 = (prod.get("nutriscore_grade") or "").lower()
        ns_txt = f'Nutri-Score {ns2.upper()}' if ns2 and ns2 in "abcde" else ""
        circle_s = (f"width:46px;height:46px;border-radius:50%;flex-shrink:0;"
                    f"background:#fff;display:flex;align-items:center;justify-content:center;"
                    f"border:2px solid {bc};box-shadow:0 2px 8px rgba(0,0,0,.06);"
                    f"font-family:'DM Sans',sans-serif;font-size:.86rem;font-weight:800;"
                    f"color:{bc};letter-spacing:-.04em;")
        html += (f'<div class="alt-card">'
                 f'<div style="{circle_s}">{s}</div>'
                 f'<div class="alt-info">'
                 f'<div class="alt-name">{name}</div>'
                 f'<div class="alt-brand">{brand}{(" · " + ns_txt) if ns_txt else ""}</div>'
                 f'</div>'
                 f'<a class="alt-link" href="?barcode={code}" target="_top"">Analizza →</a>'
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
    img_html = (f'<img class="hero-img" src="{img}" onerror="this.style.display=\'none\'">'
                if img else '<div class="hero-img-ph">📦</div>')
    st.markdown(
        f'<div class="hero">'
        f'<div class="hero-top">{img_html}'
        f'<div class="hero-meta"><div class="hero-name">{name}</div>'
        f'<div class="hero-brand">{brand}</div></div></div>'
        f'<div class="section-sub" style="margin:0;">Fonte dati: {source_txt}</div>'
        f'</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section"><div class="section-hd"><div class="section-title">Caratterizzazione Base</div></div>'
        f'<div class="divider"></div>'
        f'<div class="ing-text"><strong>Categoria:</strong> {categories}</div>'
        f'<div class="ing-text" style="margin-top:8px;"><strong>Ingredienti:</strong> {ing}</div>'
        f'<div class="section-sub" style="margin-top:12px;margin-bottom:0;">Dati nutrizionali non disponibili nella fonte corrente.</div>'
        f'</div>', unsafe_allow_html=True)


# ── MAIN ──────────────────────────────────────────────────────
def main():
    params = st.query_params
    barcode = normalize_query_value(params.get("barcode", ""))
    tab = normalize_query_value(params.get("tab", "")) or "search"

    # ── 1. CSS par défaut en premier (palette neutre) ──
    pal = get_palette(45)
    st.markdown(render_css(pal), unsafe_allow_html=True)

    # ── 2. Header fixe ──
    st.markdown(
        f'<div class="ps-header">'
        f'<div style="display:flex;align-items:center;gap:9px;">'
        f'<div class="ps-logo">Product<span>Scan</span></div>'
        f'</div>'
        f'<div class="ps-tag">Nutri</div>'
        f'</div>', unsafe_allow_html=True)

    # ── 3. Fetch produit (si barcode dans URL) ──
    product = None; did = None; source = None
    score = 45; pos = []; neg = []; details = {}

    if barcode:
        pre_ph = st.empty()
        with st.spinner(""):
            product, did, source = search(barcode, pre_ph)
        pre_ph.empty()
        if product:
            if did == "food":
                score, pos, neg, details = compute_fsa_score(product)
            else:
                score, pos, neg, details = 50, [], [], {}
            # ── 4. Re-injecter le CSS avec la bonne palette ──
            pal = get_palette(score)
            st.markdown(render_css(pal), unsafe_allow_html=True)

    # ── 5. Contenu selon le tab ──
    if tab == "scan":
        st.markdown('<div class="scanner-wrap">', unsafe_allow_html=True)
        components.html(scanner_html(pal), height=90, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    elif tab == "search":
        st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
        ci, cb = st.columns([4, 1])
        with ci:
            st.markdown('<div class="bc-input">', unsafe_allow_html=True)
            bc_input = st.text_input("bc", value=barcode,
                                     placeholder="Codice EAN-13 / UPC",
                                     label_visibility="collapsed")
            st.markdown('</div', unsafe_allow_html=True)
        with cb:
            clicked = st.button("Search", key="btn_search")
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked and bc_input.strip() and bc_input.strip() != barcode:
            st.query_params.update({"barcode": bc_input.strip()})
            st.rerun()

    # ── 6. Affichage produit ──
    if product:
        if did == "food":
            render_food(product, score, pos, neg, details, pal)
            with st.spinner("Ricerca alternative…"):
                sugg = get_suggestions(
                    tuple(product.get("categories_tags") or []),
                    score,
                    (product.get("nutriscore_grade") or "").lower()
                )
            render_alternatives(sugg, pal)
        elif did == "beauty":
            st.markdown(
                f'<div class="section"><div class="section-hd">'
                f'<div class="section-title">{e(product.get("product_name", ""))}'
                f'</div></div></div>',
                unsafe_allow_html=True)
        elif did == "generic":
            render_generic(product, source, pal)

    elif barcode and not product:
        st.markdown(
            f'<div class="ps-err">⚠ Prodotto non trovato: <strong>{e(barcode)}</strong></div>',
            unsafe_allow_html=True)

    # ── 7. Bottom nav (toujours en dernier) ──
    bc_param = f"&barcode={barcode}" if barcode else ""
    st.markdown(
        f'<div class="ps-footer">'

        f'<a href="?tab=search" target="_top" '
        f'class="ps-footer-btn {"active" if tab == "search" else ""}">'
        f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
        f'<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'
        f'<span>Search</span></a>'

        f'<a href="?tab=history" target="_top" '
        f'class="ps-footer-btn {"active" if tab == "history" else ""}">'
        f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
        f'<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>'
        f'<rect x="9" y="3" width="6" height="4" rx="1"/></svg>'
        f'<span>History</span></a>'

        f'<a href="?tab=scan" target="_top" '
        f'class="ps-footer-btn {"active" if tab == "scan" else ""}">'
        f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
        f'<path d="M23 7 16 12 23 17V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>'
        f'<span>Scan</span></a>'

        f'</div>',
        unsafe_allow_html=True)


if __name__ == "__main__":
    main()
