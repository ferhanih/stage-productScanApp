"""
test_perf.py — Profiling ciblé pour ProductScan
Usage:
    python -m cProfile -o results.prof test_perf.py
    snakeviz results.prof
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Imports depuis ton app ──────────────────────────────────
# Remplace "app" par le vrai nom de ton fichier .py si différent
from app import (
    get_palette,
    compute_fsa_score,
    render_additivi,
    get_suggestions,
    render_food,
    render_alternatives,
    render_generic,
    render_css,
    scanner_html,
    fetch_off,
    fetch_upc,
    search,
    nutriscore_html,
    nova_html,
    macro_svg,
    ha,
    nf_bar,
    factor_row,
    bar_color,
    normalize_query_value,
)

import time

# ── Produit mock (évite les vraies requêtes réseau) ──────────
# Structure identique à ce que retourne Open Food Facts
MOCK_PRODUCT = {
    "product_name": "Nutella",
    "brands": "Ferrero",
    "code": "3017620422003",
    "nova_group": 4,
    "nutriscore_grade": "e",
    "categories_tags": ["en:spreads", "en:sweet-spreads", "en:hazelnut-spreads"],
    "additives_tags": ["en:e322", "en:e476"],
    "allergens_tags": ["en:milk", "en:nuts"],
    "image_url": "https://images.openfoodfacts.org/images/products/301/762/042/2003/front_fr.jpg",
    "ingredients_text": "Zucchero, olio di palma, NOCCIOLE 13%, cacao magro 7.4%, LATTE scremato in polvere 6.6%, LATTOSIO, siero di LATTE, lecitina di SOIA, vanillina.",
    "nutriments": {
        "energy_100g": 2252,
        "energy-kcal_100g": 539,
        "fat_100g": 30.9,
        "saturated-fat_100g": 10.6,
        "carbohydrates_100g": 57.5,
        "sugars_100g": 56.3,
        "fiber_100g": 3.0,
        "proteins_100g": 6.3,
        "salt_100g": 0.107,
        "fruits-vegetables-nuts-estimate-from-ingredients_100g": 13,
    }
}

MOCK_PRODUCT_HEALTHY = {
    "product_name": "Fiocchi d'avena",
    "brands": "Bio Natura",
    "code": "1234567890123",
    "nova_group": 1,
    "nutriscore_grade": "a",
    "categories_tags": ["en:cereals", "en:oats"],
    "additives_tags": [],
    "allergens_tags": ["en:gluten"],
    "image_url": "",
    "ingredients_text": "Fiocchi d'avena integrali 100%.",
    "nutriments": {
        "energy_100g": 1560,
        "energy-kcal_100g": 373,
        "fat_100g": 7.0,
        "saturated-fat_100g": 1.3,
        "carbohydrates_100g": 60.0,
        "sugars_100g": 1.1,
        "fiber_100g": 9.4,
        "proteins_100g": 13.5,
        "salt_100g": 0.01,
        "fruits-vegetables-nuts-estimate-from-ingredients_100g": 0,
    }
}


# ── Section 1 : Fonctions de scoring ────────────────────────
print("\n[1/6] compute_fsa_score (×1000)")
t0 = time.perf_counter()
for _ in range(1000):
    score, pos, neg, details = compute_fsa_score(MOCK_PRODUCT)
    compute_fsa_score(MOCK_PRODUCT_HEALTHY)
print(f"    → {(time.perf_counter()-t0)*1000:.2f} ms total | score Nutella={score}")


# ── Section 2 : Palette et CSS ──────────────────────────────
print("\n[2/6] get_palette + render_css (×500)")
t0 = time.perf_counter()
for _ in range(500):
    pal = get_palette(score)
    css = render_css(pal)
print(f"    → {(time.perf_counter()-t0)*1000:.2f} ms total | CSS len={len(css)}")


# ── Section 3 : Rendu HTML (helpers) ────────────────────────
print("\n[3/6] Helpers HTML (×500 chaque)")
t0 = time.perf_counter()
for _ in range(500):
    nutriscore_html("e")
    nova_html(4)
    ha(MOCK_PRODUCT["ingredients_text"])
    render_additivi(MOCK_PRODUCT)
    render_additivi(MOCK_PRODUCT_HEALTHY)  # cas sans additifs
    macro_svg(30.9, 57.5, 6.3)
    nf_bar("Grassi", 30.9, 30, "g", "#e53935")
    factor_row("🍬", "Zuccheri", "Elevati: 56.3g/100g", "dot-r")
    bar_color(10.6, 1.5, 5)
    scanner_html(pal)
print(f"    → {(time.perf_counter()-t0)*1000:.2f} ms total")


# ── Section 4 : normalize_query_value ───────────────────────
print("\n[4/6] normalize_query_value (×10000)")
t0 = time.perf_counter()
for _ in range(10000):
    normalize_query_value("3017620422003")
    normalize_query_value(["3017620422003"])
    normalize_query_value(None)
print(f"    → {(time.perf_counter()-t0)*1000:.2f} ms total")


# ── Section 5 : Appels réseau réels ─────────────────────────
# (décommente pour tester les vraies requêtes API)
# Ces fonctions sont probablement le vrai goulot d'étranglement !
print("\n[5/6] Appels réseau (OFF + UPCitemdb) — ACTIFS")
import streamlit as st  # nécessaire pour fetch_off/fetch_upc (utilisent st.markdown)

class FakePlaceholder:
    def markdown(self, *a, **kw): pass

ph = FakePlaceholder()

t0 = time.perf_counter()
p, did, src = search("3017620422003", ph)  # Nutella — produit très populaire
elapsed = (time.perf_counter()-t0)*1000
print(f"    → search('3017620422003') : {elapsed:.0f} ms | trouvé={p is not None} via {src}")

t0 = time.perf_counter()
p2, did2, src2 = search("5000112548167", ph)  # Kit Kat
elapsed2 = (time.perf_counter()-t0)*1000
print(f"    → search('5000112548167') : {elapsed2:.0f} ms | trouvé={p2 is not None} via {src2}")


# ── Section 6 : get_suggestions ─────────────────────────────
print("\n[6/6] get_suggestions (requête réseau OFF)")
t0 = time.perf_counter()
sugg = get_suggestions(MOCK_PRODUCT, score)
elapsed = (time.perf_counter()-t0)*1000
print(f"    → get_suggestions : {elapsed:.0f} ms | résultat={type(sugg).__name__}, nb={len(sugg) if isinstance(sugg,list) else sugg}")


print("\n✅ Profiling terminé.")
print("   Lance maintenant : snakeviz results.prof")