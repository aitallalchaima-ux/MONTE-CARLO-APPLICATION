# -*- coding: utf-8 -*-
"""
DUROC Monte-Carlo LAB  -  version 3
Analyse probabiliste du taux de chute de fruits - Zone de prépack (DUROC Agadir)

Installation :  pip install streamlit numpy pandas matplotlib plotly openpyxl
Lancement    :  python -m streamlit run duroc_monte_carlo_v3.py
"""
import io
import os
import time
import inspect
import itertools
import textwrap
from datetime import datetime
from types import SimpleNamespace

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# Thème sombre : écrit .streamlit/config.toml s'il n'existe pas
# (pris en compte au prochain démarrage de Streamlit)
# ----------------------------------------------------------------------
THEME_TOML = """[theme]
base = "dark"
primaryColor = "#22d3ee"
backgroundColor = "#0b1220"
secondaryBackgroundColor = "#111a2e"
textColor = "#e6edf7"
"""
try:
    _d = os.path.join(os.getcwd(), ".streamlit")
    _p = os.path.join(_d, "config.toml")
    if not os.path.exists(_p):
        os.makedirs(_d, exist_ok=True)
        with open(_p, "w", encoding="utf-8") as _f:
            _f.write(THEME_TOML)
except Exception:
    pass

st.set_page_config(page_title="DUROC Monte-Carlo LAB", page_icon="🍅", layout="wide")

# ======================================================================
# STYLE (CSS)
# ======================================================================
CSS = """
<style>
.stApp {background: radial-gradient(1200px 600px at 10% -10%, #12234a 0%, #0b1220 55%) fixed;}
header[data-testid="stHeader"] {background: transparent;}
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 1.2rem; max-width: 1550px;}
section[data-testid="stSidebar"] {background: linear-gradient(180deg,#0a1630 0%,#08101f 100%);
  border-right: 1px solid rgba(148,163,184,.15);}
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp span, .stApp div[data-testid="stMarkdownContainer"] {color: #e6edf7;}
.brand {display:flex; align-items:center; gap:10px; padding:6px 4px 14px 4px;}
.brand .logo {background:linear-gradient(135deg,#ef4444,#f59e0b); width:38px; height:38px;
  border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px;}
.brand .bt {font-weight:800; font-size:17px; letter-spacing:.3px; line-height:1.1;}
.brand .bs {font-size:11px; color:#94a3b8;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {padding:9px 12px; border-radius:10px;
  margin-bottom:3px; border:1px solid transparent; transition:all .15s;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {background:rgba(34,211,238,.10);}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
  background:linear-gradient(90deg,rgba(34,211,238,.28),rgba(59,130,246,.12));
  border-color:rgba(34,211,238,.55);}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {display:none;}
.hero {display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:10px;
  margin-bottom:14px; padding-bottom:12px; border-bottom:1px solid rgba(148,163,184,.15);}
.hero h1 {margin:0; font-size:30px; font-weight:800;
  background:linear-gradient(90deg,#22d3ee,#3b82f6 60%,#a78bfa); -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;}
.hero .sub {color:#94a3b8; font-size:14px; margin-top:2px;}
.chips {display:flex; gap:8px; flex-wrap:wrap;}
.chip {background:rgba(148,163,184,.12); border:1px solid rgba(148,163,184,.25); border-radius:999px;
  padding:4px 12px; font-size:12px; color:#cbd5e1;}
.chip.live {border-color:rgba(34,197,94,.6); color:#86efac;}
.chip.live:before {content:""; display:inline-block; width:8px; height:8px; border-radius:50%;
  background:#22c55e; margin-right:6px; animation:pulse 1.6s infinite;}
@keyframes pulse {0%{box-shadow:0 0 0 0 rgba(34,197,94,.7);} 70%{box-shadow:0 0 0 9px rgba(34,197,94,0);}
  100%{box-shadow:0 0 0 0 rgba(34,197,94,0);}}
.kgrid {display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin:6px 0 16px 0;}
.kpi {background:linear-gradient(160deg,rgba(30,41,70,.85),rgba(15,23,42,.85)); border:1px solid rgba(148,163,184,.18);
  border-left:4px solid var(--c); border-radius:14px; padding:14px 16px; box-shadow:0 6px 24px rgba(0,0,0,.25);
  transition:transform .15s;}
.kpi:hover {transform:translateY(-3px);}
.kpi .kl {font-size:12px; color:#94a3b8; text-transform:uppercase; letter-spacing:.6px;}
.kpi .kv {font-size:30px; font-weight:800; color:var(--c); line-height:1.15; margin-top:4px;}
.kpi .ks {font-size:12px; color:#94a3b8; margin-top:2px;}
.panel {background:rgba(15,23,42,.65); border:1px solid rgba(148,163,184,.16); border-radius:16px; padding:14px 18px;}
.sect {font-size:19px; font-weight:700; margin:18px 0 6px 0;}
.sect small {color:#94a3b8; font-weight:400; font-size:13px; margin-left:8px;}
.note {background:rgba(34,211,238,.08); border:1px solid rgba(34,211,238,.35); border-radius:12px;
  padding:10px 14px; font-size:14px; margin:8px 0;}
.warn {background:rgba(245,158,11,.10); border:1px solid rgba(245,158,11,.45); border-radius:12px;
  padding:10px 14px; font-size:14px; margin:8px 0;}
.lgrid {display:grid; grid-template-columns:repeat(auto-fill,minmax(175px,1fr)); gap:12px; margin:8px 0 14px 0;}
.lcard {background:rgba(15,23,42,.75); border:1px solid var(--c); border-radius:14px; padding:12px 14px;
  box-shadow:0 0 14px color-mix(in srgb, var(--c) 25%, transparent);}
.lcard .lh {display:flex; justify-content:space-between; font-weight:700; font-size:15px;}
.lcard .dot {width:10px; height:10px; border-radius:50%; background:var(--c); animation:pulse 1.8s infinite;}
.lcard .lv {font-size:26px; font-weight:800; color:var(--c); margin-top:4px;}
.lcard .ls {font-size:11.5px; color:#94a3b8; min-height:30px;}
.lcard .bar {height:6px; background:rgba(148,163,184,.2); border-radius:6px; margin-top:6px; overflow:hidden;}
.lcard .bar i {display:block; height:100%; background:var(--c); border-radius:6px;}
.flow {display:flex; align-items:stretch; gap:6px; flex-wrap:wrap; padding:14px; border:2px dashed rgba(239,68,68,.55);
  border-radius:18px; background:rgba(239,68,68,.04); position:relative; margin-top:18px;}
.flow .zt {position:absolute; top:-12px; left:20px; background:#0b1220; padding:0 10px; font-size:12px;
  color:#fca5a5; font-weight:700; letter-spacing:.6px;}
.node {flex:1; min-width:120px; background:rgba(30,41,70,.9); border:1px solid rgba(148,163,184,.25);
  border-radius:14px; padding:10px; text-align:center;}
.node .ni {font-size:24px;} .node .nt {font-weight:700; font-size:13px; margin:2px 0 6px 0;}
.badge {display:block; font-size:11px; border-radius:8px; padding:3px 6px; margin-top:4px; font-weight:600;}
.arrow {align-self:center; font-size:22px; color:#22d3ee; animation:slide 1.4s infinite;}
@keyframes slide {0%{transform:translateX(-3px); opacity:.4;} 50%{transform:translateX(3px); opacity:1;}
  100%{transform:translateX(-3px); opacity:.4;}}
div[data-testid="stExpander"] {border:1px solid rgba(148,163,184,.18); border-radius:12px;
  background:rgba(15,23,42,.5);}
.stButton > button, .stDownloadButton > button {border-radius:10px; border:1px solid rgba(34,211,238,.5);
  background:linear-gradient(90deg,rgba(34,211,238,.18),rgba(59,130,246,.18)); color:#e6edf7; font-weight:600;}
.stButton > button:hover, .stDownloadButton > button:hover {border-color:#22d3ee; box-shadow:0 0 14px rgba(34,211,238,.4);}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ======================================================================
# CONSTANTES MÉTIER
# ======================================================================
REF = {"taux": 13.24, "cible": 5.0, "rend_moy": 1337, "rend_sd": 429, "arret": 3.6}
MODELES = ["Multiplicatif (pertes successives)", "Additif (somme des pertes)"]
LOIS = ["Triangulaire", "Uniforme", "PERT (Beta)", "Normale tronquée", "Binomiale"]
DEPS = ["Indépendance", "Dépendance positive (ρ commun)", "Personnalisée (matrice)"]
CALIBS = ["Calibré sur 13,24 %", "Hypothèses (libre)"]
STATUTS = ["Hypothèse", "Estimation d'expert", "Mesure terrain"]
PAGES = ["🏠 Dashboard", "📘 Méthodologie", "🏭 Données industrielles", "⚙️ Modèle probabiliste",
         "🎲 Simulation Monte-Carlo", "📊 Analyse des résultats", "📈 Convergence LGN & TCL",
         "🔧 Scénarios d'amélioration", "🎯 Optimisation", "🧪 Monte-Carlo LAB", "📄 Rapports"]

CAUSES = [
    dict(name="Désynchronisation des convoyeurs", short="Convoyeurs", lo=2.5, mo=4.5, hi=6.5,
         action="Synchronisation des convoyeurs", cost=2000, eff=60),
    dict(name="Mauvais alignement du poste de coupe", short="Poste de coupe", lo=1.5, mo=3.0, hi=4.5,
         action="Réglage du poste de coupe", cost=1000, eff=70),
    dict(name="Pertes au transfert remplisseur → moule", short="Transfert", lo=0.8, mo=2.0, hi=3.5,
         action="Solidarisation du transfert", cost=3000, eff=80),
    dict(name="Absence de cadre (table d'ajustement)", short="Table pesage", lo=0.4, mo=1.2, hi=2.2,
         action="Cadre de retenue", cost=1500, eff=90),
    dict(name="Autres causes non identifiées", short="Autres", lo=1.0, mo=2.5, hi=4.0,
         action="Aucune action identifiée", cost=0, eff=0),
]
K = len(CAUSES)

# Lignes : valeurs ESTIMÉES d'après l'ordre des graphiques de la charte (à remplacer par les vraies)
LINES0 = [("PP4", 1050, 3.0), ("PP5", 1150, 3.0), ("PP6", 1500, 2.5), ("PP6A", 1550, 2.5),
          ("PP7", 1200, 2.2), ("PP8", 1250, 4.5), ("PP9", 1300, 6.5), ("PP10", 1400, 4.3),
          ("PP11", 1750, 2.8), ("PP12", 2150, 3.4), ("PP13", 1950, 2.6), ("PP14", 900, 6.0),
          ("PP15", 800, 7.5), ("PP16", 700, 4.0)]
SACHET = {"PP9", "PP14", "PP15"}

_cnt = itertools.count()
PLOT_KW = {"width": "stretch"} if "width" in inspect.signature(st.plotly_chart).parameters \
    else {"use_container_width": True}
DF_KW = {"width": "stretch"} if "width" in inspect.signature(st.dataframe).parameters \
    else {"use_container_width": True}


# ======================================================================
# ÉTAT PAR DÉFAUT (persistant entre les pages)
# ======================================================================
def default_lines():
    rows = []
    for nom, rend, arret in LINES0:
        mult = float(np.clip(1 + 0.25 * (REF["rend_moy"] - rend) / REF["rend_sd"] + 0.05 * (arret - REF["arret"]),
                             0.7, 1.6))
        rows.append({"Ligne": nom, "Conditionnement": "Sachet" if nom in SACHET else "n.d.",
                     "Rendement (kg/h)": float(rend), "Arrêt moyen (min)": float(arret),
                     "Multiplicateur de chute": round(mult, 2), "Statut": "Hypothèse"})
    return pd.DataFrame(rows)


def init_state():
    S = st.session_state
    base = {"p_n": 50000, "p_seed": 42, "p_cible": 5.0, "p_modele": MODELES[0], "p_calib": CALIBS[0],
            "p_scope": "Zone prépack (14 lignes)", "p_shift": "Les deux shifts", "p_sh1": 0.95, "p_sh2": 1.05,
            "p_heures": 16, "p_jours": 250, "p_poids": 15.0, "p_prix": 6.0, "p_revalo": 1.0,
            "p_dep": DEPS[0], "p_rho": 0.30, "p_alpha": 10, "p_thr": 80}
    for k_, v in base.items():
        S.setdefault(k_, v)
    for i, c in enumerate(CAUSES):
        S.setdefault(f"p_c{i}_law", "Triangulaire")
        S.setdefault(f"p_c{i}_lo", float(c["lo"]))
        S.setdefault(f"p_c{i}_mo", float(c["mo"]))
        S.setdefault(f"p_c{i}_hi", float(c["hi"]))
        S.setdefault(f"p_c{i}_N", 2000)
        S.setdefault(f"p_c{i}_stat", "Hypothèse")
        S.setdefault(f"p_cost{i}", int(c["cost"]))
        S.setdefault(f"p_eff{i}", int(c["eff"]))
        S.setdefault(f"p_red_{i}", 0)
    defaults_rho = {(0, 1): 0.3, (0, 2): 0.4, (1, 2): 0.2}
    for i in range(K):
        for j in range(i + 1, K):
            S.setdefault(f"p_r{i}_{j}", defaults_rho.get((i, j), 0.0))
    if "lines_df" not in S:
        S["lines_df"] = default_lines()
    # protège les widgets des pages non affichées
    for key in [k_ for k_ in S.keys() if str(k_).startswith("p_")]:
        S[key] = S[key]


init_state()


# ======================================================================
# OUTILS GÉNÉRAUX
# ======================================================================
def fr(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",")


def plot(fig):
    st.plotly_chart(fig, key=f"pl{next(_cnt)}", **PLOT_KW)


def show_df(df):
    st.dataframe(df, hide_index=True, **DF_KW)


def style(fig, h=360, title=None):
    kw = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
              height=h, margin=dict(l=10, r=10, t=46 if title else 14, b=10), font=dict(color="#cbd5e1"),
              legend=dict(orientation="h", y=1.14, x=0), hovermode="x unified")
    if title:
        kw["title"] = dict(text=title, font=dict(size=15))
    fig.update_layout(**kw)
    fig.update_xaxes(gridcolor="rgba(148,163,184,.15)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.15)")
    return fig


def kpi(label, value, sub="", color="#22d3ee"):
    return (f'<div class="kpi" style="--c:{color}"><div class="kl">{label}</div>'
            f'<div class="kv">{value}</div><div class="ks">{sub}</div></div>')


def kpi_row(items):
    st.markdown('<div class="kgrid">' + "".join(items) + "</div>", unsafe_allow_html=True)


def sect(title, sub=""):
    s = f"<small>{sub}</small>" if sub else ""
    st.markdown(f'<div class="sect">{title}{s}</div>', unsafe_allow_html=True)


def note(text, warn=False):
    st.markdown(f'<div class="{"warn" if warn else "note"}">{text}</div>', unsafe_allow_html=True)


def status(m, cible):
    if m <= cible * 1.5:
        return "Maîtrisé", "#22c55e"
    if m <= cible * 2.5:
        return "Vigilance", "#f59e0b"
    return "Critique", "#ef4444"


def hist_bars(T, bins, lo, hi):
    counts, edges = np.histogram(T, bins=bins, range=(lo, hi))
    return (edges[:-1] + edges[1:]) / 2, counts / len(T) * 100, edges[1] - edges[0]


def stats_of(T, cible):
    s = pd.Series(T)
    return {"Espérance E(T) (%)": T.mean(), "Variance (pts²)": T.var(ddof=1), "Écart-type (pts)": T.std(ddof=1),
            "Asymétrie": s.skew(), "Aplatissement": s.kurt(), "Médiane (%)": np.median(T),
            "Percentile 5 % (%)": np.percentile(T, 5), "Percentile 95 % (%)": np.percentile(T, 95),
            f"P(T ≤ {cible:g} %)": (T <= cible).mean() * 100}


def ic_mean(T):
    return 1.96 * T.std(ddof=1) / np.sqrt(len(T))


# ======================================================================
# MOTEUR MONTE-CARLO
# ======================================================================
def sample_marginal(law, lo, mo, hi, N, size, rng):
    """Tire des pertes (en %) selon la loi choisie."""
    if law == "Triangulaire":
        return rng.triangular(lo, mo, hi, size)
    if law == "Uniforme":
        return rng.uniform(lo, hi, size)
    if law == "PERT (Beta)":
        a = 1 + 4 * (mo - lo) / (hi - lo)
        b = 1 + 4 * (hi - mo) / (hi - lo)
        return lo + (hi - lo) * rng.beta(a, b, size)
    if law == "Normale tronquée":
        return np.clip(rng.normal(mo, (hi - lo) / 6, size), lo, hi)
    return rng.binomial(int(N), mo / 100.0, size) / float(N) * 100.0     # Binomiale


def make_corr(mode, rho, pairs):
    C = np.eye(K)
    if mode.startswith("Dépendance positive"):
        C = np.full((K, K), rho)
        np.fill_diagonal(C, 1.0)
    elif mode.startswith("Personnalisée"):
        for (i, j), v in pairs.items():
            C[i, j] = C[j, i] = v
    w, V = np.linalg.eigh(C)                      # rend la matrice définie positive
    C = (V * np.clip(w, 1e-6, None)) @ V.T
    d = np.sqrt(np.diag(C))
    C = C / np.outer(d, d)
    return tuple(map(tuple, np.round(C, 6)))


def combine(P, modele):
    if modele == MODELES[0]:
        return 1.0 - np.prod(1.0 - P, axis=-1)
    return np.minimum(P.sum(axis=-1), 1.0)


@st.cache_resource(show_spinner=False, max_entries=5)
def simulate_base(spec, corr, n, seed):
    """Pertes par cause (fraction), avec dépendance par copule gaussienne."""
    rng = np.random.default_rng(seed)
    X = np.column_stack([sample_marginal(*s[:4], s[4], n, rng) for s in spec]) / 100.0
    C = np.array(corr)
    if not np.allclose(C, np.eye(K), atol=1e-5):
        L = np.linalg.cholesky(C)
        Z = rng.standard_normal((n, K)) @ L.T
        out = np.empty_like(X)
        for j in range(K):
            ranks = np.empty(n, dtype=np.int64)
            ranks[np.argsort(Z[:, j])] = np.arange(n)
            out[:, j] = np.sort(X[:, j])[ranks]
        X = out
    return X


@st.cache_data(show_spinner=False, max_entries=20)
def calibrate(spec, corr, n, seed, modele, mults, weights, target):
    P = simulate_base(spec, corr, n, seed)[:15000]
    w = np.array(weights, float)
    w = w / w.sum()
    mu = np.array(mults, float)

    def f(k_):
        return sum(wi * combine(np.clip(P * k_ * m, 0, 0.999), modele).mean() for wi, m in zip(w, mu)) * 100

    lo, hi = 0.01, 6.0
    if f(hi) < target:
        return hi
    for _ in range(28):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < target else (lo, mid)
    return (lo + hi) / 2


@st.cache_data(show_spinner=False, max_entries=20)
def per_line(spec, corr, n, seed, modele, k_, mults, shift_mult, red, cible):
    P = simulate_base(spec, corr, n, seed)[:8000]
    out = []
    for m in mults:
        Pc = np.clip(P * k_ * m * shift_mult, 0, 0.999)
        Tc = combine(Pc, modele) * 100
        Ta = combine(Pc * (1 - np.array(red)), modele) * 100
        out.append((Tc.mean(), (Tc <= cible).mean() * 100, Ta.mean(), (Ta <= cible).mean() * 100,
                    np.percentile(Tc, 95)))
    return out


@st.cache_data(show_spinner=False, max_entries=20)
def means_rep(spec, sc, modele, m, seed, R=1000):
    rng = np.random.default_rng(seed)
    cols = [sample_marginal(*s[:4], s[4], (R, m), rng) for s in spec]
    P = np.clip(np.stack(cols, axis=-1) / 100.0 * sc, 0, 0.999)
    return (combine(P, modele) * 100).mean(axis=1)


def build_ctx():
    S = st.session_state
    c = SimpleNamespace()
    c.n, c.seed, c.cible, c.modele = int(S["p_n"]), int(S["p_seed"]), float(S["p_cible"]), S["p_modele"]
    spec, bad = [], False
    for i in range(K):
        lo, mo, hi = S[f"p_c{i}_lo"], S[f"p_c{i}_mo"], S[f"p_c{i}_hi"]
        lo2, hi2 = min(lo, mo, hi), max(lo, mo, hi)
        if hi2 - lo2 < 0.01:
            hi2 = lo2 + 0.01
        if (lo, mo, hi) != (lo2, min(max(mo, lo2), hi2), hi2):
            bad = True
        spec.append((S[f"p_c{i}_law"], float(lo2), float(min(max(mo, lo2), hi2)), float(hi2),
                     int(S[f"p_c{i}_N"])))
    c.spec, c.invalid = tuple(spec), bad
    pairs = {(i, j): S[f"p_r{i}_{j}"] for i in range(K) for j in range(i + 1, K)}
    c.corr = make_corr(S["p_dep"], S["p_rho"], pairs)
    lines = S["lines_df"]
    c.lines = lines
    c.mults = tuple(float(x) for x in lines["Multiplicateur de chute"])
    c.weights = tuple(float(x) for x in lines["Rendement (kg/h)"])
    c.P_base = simulate_base(c.spec, c.corr, c.n, c.seed)
    c.calibrated = S["p_calib"] == CALIBS[0]
    c.k = float(calibrate(c.spec, c.corr, c.n, c.seed, c.modele, c.mults, c.weights, REF["taux"])) \
        if c.calibrated else 1.0
    c.scope, c.shift = S["p_scope"], S["p_shift"]
    c.shift_mult = {"Les deux shifts": 1.0, "Shift 1": float(S["p_sh1"]), "Shift 2": float(S["p_sh2"])}[c.shift]
    w = np.array(c.weights) / np.sum(c.weights)
    if c.scope.startswith("Zone"):
        rng = np.random.default_rng(c.seed + 7)
        idx = rng.choice(len(lines), size=c.n, p=w)
        mult = np.array(c.mults)[idx]
        c.kg_h = float(np.sum(c.weights))
        c.arret = float(lines["Arrêt moyen (min)"].mean())
    else:
        row = lines[lines["Ligne"] == c.scope].iloc[0]
        mult = np.full(c.n, float(row["Multiplicateur de chute"]))
        c.kg_h = float(row["Rendement (kg/h)"])
        c.arret = float(row["Arrêt moyen (min)"])
    c.scale = c.k * mult * c.shift_mult
    c.P_cur = np.clip(c.P_base * c.scale[:, None], 0, 0.999)
    c.T_cur = combine(c.P_cur, c.modele) * 100
    c.T_nocal = (combine(np.clip(c.P_base * (mult * c.shift_mult)[:, None], 0, 0.999), c.modele) * 100).mean()
    c.red = tuple(S[f"p_red_{i}"] / 100.0 for i in range(K))
    c.P_after = c.P_cur * (1 - np.array(c.red))
    c.T_after = combine(c.P_after, c.modele) * 100
    c.heures, c.jours, c.poids = S["p_heures"], S["p_jours"], S["p_poids"]
    c.prix, c.revalo = S["p_prix"], S["p_revalo"]
    c.kg_jour = c.kg_h * c.heures
    c.fruits_jour = c.kg_jour * 1000.0 / c.poids
    c.kg_an = c.kg_jour * c.jours
    return c


# ======================================================================
# OPTIMISATION (recherche exhaustive)
# ======================================================================
def run_optim(c, thr):
    S = st.session_state
    eff = np.array([S[f"p_eff{i}"] for i in range(K)]) / 100.0
    cost = np.array([S[f"p_cost{i}"] for i in range(K)], float)
    active = [i for i in range(K) if eff[i] > 0]
    m = min(c.n, 30000)
    rows = []
    for mask in range(2 ** len(active)):
        x = np.zeros(K)
        for b, i in enumerate(active):
            if (mask >> b) & 1:
                x[i] = 1
        T = combine(c.P_cur[:m] * (1 - eff * x), c.modele) * 100
        names = [CAUSES[i]["short"] for i in active if x[i] == 1]
        rows.append({"Combinaison d'actions": " + ".join(names) if names else "Aucune action",
                     "Nb actions": int(x.sum()), "Coût (DH)": float((cost * x).sum()),
                     "Taux moyen (%)": T.mean(), f"P(T ≤ {c.cible:g} %) en %": (T <= c.cible).mean() * 100})
    df = pd.DataFrame(rows)
    pc = f"P(T ≤ {c.cible:g} %) en %"
    feas = df[df[pc] >= thr].sort_values(["Coût (DH)", pc], ascending=[True, False])
    best = feas.iloc[0] if len(feas) else df.sort_values(pc, ascending=False).iloc[0]
    return df.sort_values(["Coût (DH)", pc], ascending=[True, False]), best, len(feas) > 0


# ======================================================================
# COMPOSANTS D'INTERFACE
# ======================================================================
def hero(title, sub, c):
    chips = [f'<span class="chip live">LIVE</span>',
             f'<span class="chip">{c.scope}</span>', f'<span class="chip">{c.shift}</span>',
             f'<span class="chip">n = {fr(c.n, 0)}</span>', f'<span class="chip">graine {c.seed}</span>',
             f'<span class="chip">{"Calibré k=" + fr(c.k, 3) if c.calibrated else "Mode hypothèses"}</span>']
    st.markdown(f'<div class="hero"><div><h1>{title}</h1><div class="sub">{sub}</div></div>'
                f'<div class="chips">{"".join(chips)}</div></div>', unsafe_allow_html=True)
    if c.invalid:
        note("Certains paramètres (Min ≤ Mode ≤ Max) étaient incohérents et ont été corrigés automatiquement "
             "pour la simulation. Corrigez-les dans « Modèle probabiliste ».", warn=True)


def flow_html(c, P):
    means = P.mean(axis=0) * 100

    def badge(i):
        r = means[i] / c.cible
        col = "#ef4444" if r >= 0.7 else ("#f59e0b" if r >= 0.35 else "#22c55e")
        return (f'<span class="badge" style="background:{col}22; border:1px solid {col}; color:{col}">'
                f'{CAUSES[i]["short"]} : {fr(means[i], 1)} %</span>')

    nodes = [("📥", "Réception", []), ("🔍", "Triage", []), ("⬆️", "Élévateur", []),
             ("➡️", "Convoyeur", [0]), ("🎛️", "Trieuse", []), ("📦", "Conditionnement", [1, 2, 3, 4]),
             ("🏷️", "Étiqueteuse", [])]
    parts = []
    for k_, (ico, name, ids) in enumerate(nodes):
        parts.append(f'<div class="node"><div class="ni">{ico}</div><div class="nt">{name}</div>'
                     f'{"".join(badge(i) for i in ids)}</div>')
        if k_ < len(nodes) - 1:
            parts.append('<div class="arrow">➜</div>')
    return ('<div class="flow"><span class="zt">ZONE CRITIQUE : DU TRIAGE À L\'ÉTIQUETAGE</span>'
            + "".join(parts) + "</div>")


# ======================================================================
# PAGES
# ======================================================================
def page_dashboard(c):
    hero("Dashboard de pilotage", "Taux de chute de fruits : situation simulée et objectif DMAIC (13,24 % → 5 %)", c)
    view = st.radio("Vue", ["Situation actuelle", "Après scénario"], horizontal=True, key="dash_view",
                    label_visibility="collapsed")
    after = view == "Après scénario"
    T, P = (c.T_after, c.P_after) if after else (c.T_cur, c.P_cur)
    mean, p = T.mean(), (T <= c.cible).mean() * 100
    col_m = status(mean, c.cible)[1]
    means_c = P.mean(axis=0) * 100
    top = CAUSES[int(np.argmax(means_c))]["short"]
    perdus_j = mean / 100 * c.fruits_jour
    gain = (c.T_cur.mean() - c.T_after.mean()) / 100 * c.kg_an * (c.prix - c.revalo)
    kpi_row([
        kpi("Taux de chute moyen", f"{fr(mean)} %", f"Objectif {c.cible:g} % · observé {REF['taux']} %", col_m),
        kpi(f"P(T ≤ {c.cible:g} %)", f"{fr(p, 1)} %", "Probabilité d'atteindre l'objectif",
            "#22c55e" if p >= 80 else ("#f59e0b" if p >= 50 else "#ef4444")),
        kpi("Fruits perdus / jour", fr(perdus_j, 0), f"sur {fr(c.fruits_jour, 0)} fruits entrants", "#a78bfa"),
        kpi("Matière perdue / an", f"{fr(mean / 100 * c.kg_an / 1000, 0)} t", f"{fr(c.kg_an / 1000, 0)} t traitées",
            "#f59e0b"),
        kpi("Gain annuel du scénario", f"{fr(gain, 0)} DH", "net de revalorisation", "#22d3ee"),
        kpi("Cause prioritaire", top, f"{fr(means_c.max(), 1)} % de perte moyenne", "#ef4444")])

    g1, g2, g3 = st.columns([1, 1.4, 1])
    with g1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=p, number={"suffix": " %", "font": {"size": 38}},
            title={"text": f"P(T ≤ {c.cible:g} %)"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#22d3ee"},
                   "steps": [{"range": [0, 50], "color": "rgba(239,68,68,.35)"},
                             {"range": [50, 80], "color": "rgba(245,158,11,.35)"},
                             {"range": [80, 100], "color": "rgba(34,197,94,.35)"}],
                   "threshold": {"line": {"color": "white", "width": 3}, "thickness": .8, "value": 80}}))
        plot(style(fig, 320))
    with g2:
        lo, hi = min(c.T_cur.min(), c.T_after.min()), max(c.T_cur.max(), c.T_after.max())
        fig = go.Figure()
        for TT, name, colr in [(c.T_cur, "Avant", "#ef4444"), (c.T_after, "Après scénario", "#22c55e")]:
            x, y, w = hist_bars(TT, 60, lo, hi)
            fig.add_bar(x=x, y=y, width=w, name=name, marker_color=colr, opacity=0.6)
        fig.add_vline(x=c.cible, line_dash="dash", line_color="white", annotation_text="Cible")
        fig.update_layout(barmode="overlay")
        fig.update_xaxes(title="Taux de chute (%)")
        fig.update_yaxes(title="% des simulations")
        plot(style(fig, 320))
    with g3:
        fig = go.Figure(go.Pie(labels=[x["short"] for x in CAUSES], values=means_c, hole=.62,
                               marker=dict(colors=["#ef4444", "#f59e0b", "#a78bfa", "#22d3ee", "#64748b"]),
                               textinfo="percent"))
        fig.update_layout(showlegend=True)
        plot(style(fig, 320, "Répartition des pertes"))

    sect("Flux de production", "pertes moyennes par poste")
    st.markdown(flow_html(c, P), unsafe_allow_html=True)

    sect("État des lignes PP4 → PP16", "statut selon l'écart à la cible")
    res = per_line(c.spec, c.corr, c.n, c.seed, c.modele, c.k, c.mults, c.shift_mult, c.red, c.cible)
    cards = []
    for (nom, *_), r in zip(c.lines.itertuples(index=False), res):
        m_, p_ = (r[2], r[3]) if after else (r[0], r[1])
        lab, col = status(m_, c.cible)
        cards.append(f'<div class="lcard" style="--c:{col}"><div class="lh"><span>{nom}</span><span class="dot">'
                     f'</span></div><div class="lv">{fr(m_, 1)} %</div><div class="ls">{lab} · P(≤{c.cible:g} %) = '
                     f'{fr(p_, 0)} %</div><div class="bar"><i style="width:{min(m_ / 20 * 100, 100)}%"></i></div></div>')
    st.markdown('<div class="lgrid">' + "".join(cards) + "</div>", unsafe_allow_html=True)
    vals = [(r[2] if after else r[0]) for r in res]
    order = np.argsort(vals)[::-1]
    fig = go.Figure(go.Bar(x=[c.lines["Ligne"].iloc[i] for i in order], y=[vals[i] for i in order],
                           marker_color=[status(vals[i], c.cible)[1] for i in order]))
    fig.add_hline(y=c.cible, line_dash="dash", line_color="white", annotation_text="Cible")
    fig.update_yaxes(title="Taux moyen (%)")
    plot(style(fig, 300, "Classement des lignes (taux de chute moyen simulé)"))


def page_method(c):
    hero("Méthodologie", "Pourquoi et comment : du problème industriel à la simulation", c)
    cc = st.columns(4)
    for col, (l, v) in zip(cc, [("Taux actuel", "13,24 %"), ("Cible", "5 %"), ("Gain visé", "8,24 pts"),
                                ("Réduction relative", "≈ 62 %")]):
        col.metric(l, v)
    sect("1. Le problème industriel")
    st.markdown("Dans la zone de prépack, les fruits passent par **Triage → Élévateur → Convoyeur → Trieuse → "
                "Conditionnement → Étiqueteuse**. Quatre risques principaux sont identifiés : désynchronisation "
                "des convoyeurs, mauvais alignement du poste de coupe, pertes au transfert remplisseur → moule, "
                "absence de cadre sur la table d'ajustement.")
    sect("2. Pourquoi Monte-Carlo ?")
    st.markdown("Le taux de chute **varie** (jours, lignes, réglages, opérateurs) et la part de chaque cause est "
                "mal connue. Monte-Carlo simule des milliers de journées fictives : à chaque tirage, une perte est "
                "choisie au hasard pour chaque cause, puis le taux global est calculé. On obtient une **distribution** "
                "et pas un seul chiffre, donc des probabilités, par exemple P(T ≤ 5 %).")
    sect("3. Les notions du cours")
    st.markdown("**Loi des grands nombres** : la moyenne simulée converge vers l'espérance.")
    st.latex(r"\overline{X}_n=\frac1n\sum_{i=1}^{n}X_i \xrightarrow[n\to\infty]{} E(X)")
    st.markdown("**Théorème central limite** : la moyenne est approximativement normale, d'où l'intervalle de confiance.")
    st.latex(r"\frac{\overline{X}_n-E(X)}{\sigma/\sqrt n}\xrightarrow{\mathcal L}\mathcal N(0,1)\qquad "
             r"IC_{95\%}=\overline X_n\pm1{,}96\,\frac{s}{\sqrt n}")
    st.markdown("**Modèle de combinaison** (pertes successives, pas de double comptage) :")
    st.latex(r"T=1-\prod_{i=1}^{5}(1-p_i)")
    st.markdown("**Dépendance** entre causes : copule gaussienne de matrice de corrélation $R$. "
                "**Calibration** : on multiplie les pertes par un facteur $k$ pour retrouver le taux observé de 13,24 %.")
    sect("4. Objectif industriel et objectif mathématique")
    note("<b>Objectif industriel</b> : réduire réellement le taux de chute de 13,24 % à 5 %.<br>"
         "<b>Objectif de l'application</b> : étudier la variabilité du taux, estimer des probabilités, "
         "hiérarchiser les causes, comparer des scénarios et rechercher la combinaison d'actions la moins coûteuse "
         "qui atteint l'objectif. Elle ne prouve pas que le taux réel sera de 5 %.")
    sect("5. Honnêteté sur les données")
    note("La charte donne le taux global (13,24 %), les rendements et les arrêts, mais <b>pas la répartition par "
         "cause</b> ni les valeurs numériques exactes par ligne. Les paramètres de cause, les valeurs par ligne, "
         "les multiplicateurs, les coûts et l'efficacité des actions sont des <b>hypothèses</b> (champ « Statut ») "
         "à remplacer par les mesures de l'étape Mesurer.", warn=True)

    sect("6. Simulation à la main", "5 tirages pour comprendre le calcul")
    if "hand_seed" not in st.session_state:
        st.session_state.hand_seed = 1
    st.button("🎲 Nouveau tirage", on_click=lambda: st.session_state.update(hand_seed=st.session_state.hand_seed + 1))
    rng = np.random.default_rng(st.session_state.hand_seed)
    H = np.column_stack([sample_marginal(*s[:4], s[4], 5, rng) for s in c.spec]) / 100
    H = np.clip(H * c.k, 0, 0.999)
    Th = combine(H, c.modele) * 100
    df = pd.DataFrame(H * 100, columns=[x["short"] for x in CAUSES]).round(2)
    df["Taux global T (%)"] = Th.round(2)
    df.insert(0, "Simulation", [f"#{i + 1}" for i in range(5)])
    show_df(df)
    if c.modele == MODELES[0]:
        st.latex(r"T=1-" + "".join(f"(1-{p:.4f})" for p in H[0]) + rf"={Th[0] / 100:.4f}={Th[0]:.2f}\,\%")
    else:
        st.latex(r"T=" + "+".join(f"{p:.4f}" for p in H[0]) + rf"={Th[0]:.2f}\,\%")
    st.caption(f"Moyenne de ces 5 simulations : {fr(Th.mean())} % ; avec {fr(c.n, 0)} simulations : "
               f"{fr(c.T_cur.mean())} %. Relancez plusieurs fois : c'est la loi des grands nombres.")


def page_data(c):
    hero("Données industrielles", "Périmètre, shifts, production et paramètres par ligne", c)
    S = st.session_state
    a, b = st.columns(2)
    with a:
        sect("Périmètre et shift")
        st.selectbox("Périmètre de l'étude", ["Zone prépack (14 lignes)"] + list(c.lines["Ligne"]), key="p_scope")
        st.selectbox("Shift analysé", ["Les deux shifts", "Shift 1", "Shift 2"], key="p_shift")
        s1, s2 = st.columns(2)
        s1.number_input("Multiplicateur Shift 1", 0.5, 2.0, step=0.01, key="p_sh1",
                        help="Hypothèse illustrative : à remplacer par l'écart observé entre shifts.")
        s2.number_input("Multiplicateur Shift 2", 0.5, 2.0, step=0.01, key="p_sh2")
    with b:
        sect("Production et économie")
        p1, p2, p3 = st.columns(3)
        p1.number_input("Heures / jour", 1, 24, key="p_heures")
        p2.number_input("Jours / an", 1, 365, key="p_jours")
        p3.number_input("Poids moyen d'un fruit (g)", 1.0, 200.0, step=1.0, key="p_poids")
        q1, q2 = st.columns(2)
        q1.number_input("Valeur de la matière (DH/kg)", 0.0, 100.0, step=0.5, key="p_prix")
        q2.number_input("Valeur de revalorisation des fruits tombés (DH/kg)", 0.0, 100.0, step=0.5, key="p_revalo",
                        help="Un fruit tombé peut être revendu déclassé : la perte nette est (prix − revalorisation).")

    sect("Paramètres par ligne", "valeurs ESTIMÉES d'après l'ordre des graphiques de la charte : à remplacer")
    note("Le <b>multiplicateur de chute</b> traduit l'hypothèse que les lignes à faible rendement et arrêts longs "
         "perdent plus de fruits (corrélation <i>apparente</i> dans la charte, à confirmer à l'étape Mesurer). "
         "Formule par défaut : 1 + 0,25·(1337 − rendement)/429 + 0,05·(arrêt − 3,6).")

    def apply_edit():
        state = st.session_state["lines_editor"]
        df = st.session_state["lines_df"].copy()
        for r, ch in state.get("edited_rows", {}).items():
            for col, v in ch.items():
                df.iloc[int(r), df.columns.get_loc(col)] = v
        st.session_state["lines_df"] = df

    st.data_editor(
        S["lines_df"], key="lines_editor", hide_index=True, on_change=apply_edit,
        disabled=["Ligne", "Conditionnement"],
        column_config={
            "Rendement (kg/h)": st.column_config.NumberColumn(min_value=100.0, max_value=5000.0, step=10.0),
            "Arrêt moyen (min)": st.column_config.NumberColumn(min_value=0.0, max_value=30.0, step=0.1),
            "Multiplicateur de chute": st.column_config.NumberColumn(min_value=0.3, max_value=3.0, step=0.01),
            "Statut": st.column_config.SelectboxColumn(options=STATUTS)})
    if st.button("↺ Réinitialiser les lignes"):
        st.session_state["lines_df"] = default_lines()
        st.rerun()

    L = c.lines
    kpi_row([kpi("Rendement moyen (14 lignes)", f"{fr(L['Rendement (kg/h)'].mean(), 0)} kg/h",
                 f"charte : ≈ {REF['rend_moy']} kg/h", "#22d3ee"),
             kpi("Écart-type du rendement", f"{fr(L['Rendement (kg/h)'].std(), 0)} kg/h",
                 f"charte : {REF['rend_sd']} kg/h", "#a78bfa"),
             kpi("Arrêt moyen", f"{fr(L['Arrêt moyen (min)'].mean(), 1)} min", f"charte : ≈ {REF['arret']} min",
                 "#f59e0b"),
             kpi("Fruits entrants / jour", fr(c.fruits_jour, 0), f"{fr(c.kg_jour / 1000, 1)} t · {c.scope}", "#22c55e")])
    g1, g2 = st.columns(2)
    with g1:
        d = L.sort_values("Rendement (kg/h)")
        fig = go.Figure(go.Bar(x=d["Ligne"], y=d["Rendement (kg/h)"], marker_color="#22d3ee"))
        fig.add_hline(y=REF["rend_moy"], line_dash="dash", line_color="white", annotation_text="Moyenne charte")
        plot(style(fig, 320, "Rendement par ligne (kg/h)"))
    with g2:
        fig = go.Figure(go.Scatter(x=L["Rendement (kg/h)"], y=L["Arrêt moyen (min)"], mode="markers+text",
                                   text=L["Ligne"], textposition="top center",
                                   marker=dict(size=L["Multiplicateur de chute"] * 22, color=L["Multiplicateur de chute"],
                                               colorscale="Turbo", showscale=True,
                                               colorbar=dict(title="Mult."))))
        fig.update_xaxes(title="Rendement (kg/h)")
        fig.update_yaxes(title="Arrêt moyen (min)")
        plot(style(fig, 320, "Rendement vs arrêts (taille = multiplicateur de chute)"))


def page_model(c):
    hero("Modèle probabiliste", "Lois de probabilité, dépendance entre causes et calibration", c)
    S = st.session_state
    a, b = st.columns(2)
    with a:
        sect("Calibration")
        st.radio("Mode", CALIBS, key="p_calib", horizontal=True)
        st.radio("Combinaison des causes", MODELES, key="p_modele")
        if c.calibrated:
            note(f"<b>Mode calibré</b> : les pertes sont multipliées par k = <b>{fr(c.k, 3)}</b> pour que le taux moyen "
                 f"de la zone soit {REF['taux']} %. Sans calibration, le modèle donnerait {fr(c.T_nocal)} %. "
                 "Attention : le 13,24 % est alors <i>imposé</i>, ce n'est pas une prédiction du modèle.")
        else:
            note(f"<b>Mode hypothèses</b> : le taux moyen simulé ({fr(c.T_cur.mean())} %) provient librement des "
                 f"paramètres saisis (observé : {REF['taux']} %).", warn=True)
    with b:
        sect("Dépendance entre causes")
        st.radio("Structure", DEPS, key="p_dep")
        if S["p_dep"].startswith("Dépendance positive"):
            st.slider("Corrélation commune ρ", 0.0, 0.9, step=0.05, key="p_rho")
        elif S["p_dep"].startswith("Personnalisée"):
            cols = st.columns(5)
            n_ = 0
            for i in range(K):
                for j in range(i + 1, K):
                    cols[n_ % 5].slider(f"{CAUSES[i]['short'][:7]}–{CAUSES[j]['short'][:7]}", -0.9, 0.9, step=0.05,
                                        key=f"p_r{i}_{j}")
                    n_ += 1
        st.caption("Copule gaussienne : les marges (lois) restent identiques, seule la liaison change. "
                   "Les corrélations doivent être justifiées par des observations ou l'avis d'experts.")

    sect("Lois et paramètres des causes", "perte en % des fruits traités")
    for i, cs in enumerate(CAUSES):
        with st.expander(f"{i + 1}. {cs['name']}", expanded=(i == 0)):
            r = st.columns([1.3, 1, 1, 1, 1, 1.2])
            r[0].selectbox("Loi", LOIS, key=f"p_c{i}_law")
            r[1].number_input("Min (%)", 0.0, 50.0, step=0.1, key=f"p_c{i}_lo")
            r[2].number_input("Mode (%)", 0.0, 50.0, step=0.1, key=f"p_c{i}_mo")
            r[3].number_input("Max (%)", 0.0, 50.0, step=0.1, key=f"p_c{i}_hi")
            r[4].number_input("N fruits (binomiale)", 100, 100000, step=100, key=f"p_c{i}_N")
            r[5].selectbox("Statut de la donnée", STATUTS, key=f"p_c{i}_stat")
    if c.invalid:
        note("Il faut Min ≤ Mode ≤ Max (et Max > Min) pour chaque cause : correction automatique appliquée.", warn=True)

    g1, g2 = st.columns([1.4, 1])
    with g1:
        rng = np.random.default_rng(c.seed + 99)
        fig = go.Figure()
        colors = ["#ef4444", "#f59e0b", "#a78bfa", "#22d3ee", "#64748b"]
        for i, s in enumerate(c.spec):
            x = sample_marginal(*s[:4], s[4], 20000, rng)
            xs, ys, _ = hist_bars(x, 45, 0, max(sp[3] for sp in c.spec) * 1.1)
            fig.add_scatter(x=xs, y=ys, mode="lines", name=CAUSES[i]["short"], line=dict(color=colors[i], width=2.5),
                            fill="tozeroy", fillcolor=colors[i] + "33")
        fig.update_xaxes(title="Perte de la cause (%)")
        fig.update_yaxes(title="% des tirages")
        plot(style(fig, 330, "Distribution de chaque cause (avant calibration)"))
    with g2:
        Cm = np.array(c.corr)
        names = [x["short"] for x in CAUSES]
        fig = go.Figure(go.Heatmap(z=Cm, x=names, y=names, zmin=-1, zmax=1, colorscale="RdBu_r", text=np.round(Cm, 2),
                                   texttemplate="%{text}"))
        fig.update_yaxes(autorange="reversed")
        plot(style(fig, 330, "Matrice de corrélation utilisée"))


def page_sim(c):
    hero("Simulation Monte-Carlo", "Tirages aléatoires, distribution du taux de chute et risques extrêmes", c)
    T = c.T_cur
    kpi_row([kpi("Moyenne", f"{fr(T.mean())} %", "taux de chute simulé", "#22d3ee"),
             kpi("Médiane", f"{fr(np.median(T))} %", f"écart-type {fr(T.std(ddof=1))} pts", "#3b82f6"),
             kpi("Minimum simulé", f"{fr(T.min())} %", "meilleur scénario", "#22c55e"),
             kpi("Maximum simulé", f"{fr(T.max())} %", "pire scénario", "#ef4444"),
             kpi("Percentile 95 %", f"{fr(np.percentile(T, 95))} %", "scénario défavorable", "#f59e0b")])
    x, y, w = hist_bars(T, 70, T.min(), T.max())
    fig = go.Figure(go.Bar(x=x, y=y, width=w, marker_color="#3b82f6", opacity=0.85, name="Simulations"))
    fig.add_vline(x=T.mean(), line_color="#22d3ee", annotation_text="Moyenne")
    fig.add_vline(x=c.cible, line_dash="dash", line_color="#22c55e", annotation_text="Cible")
    fig.add_vline(x=np.percentile(T, 95), line_dash="dot", line_color="#f59e0b", annotation_text="P95")
    fig.update_xaxes(title="Taux de chute (%)")
    fig.update_yaxes(title="% des simulations")
    plot(style(fig, 360, "Distribution du taux de chute"))

    sect("Analyse des risques extrêmes")
    thr = st.slider("Seuil personnalisé (%)", 1.0, 30.0, 12.0, 0.5, key="sim_thr")
    kpi_row([kpi(f"P(T > {c.cible:g} %)", f"{fr((T > c.cible).mean() * 100, 1)} %", "dépasse la cible", "#f59e0b"),
             kpi("P(T > 10 %)", f"{fr((T > 10).mean() * 100, 1)} %", "niveau préoccupant", "#f97316"),
             kpi("P(T > 15 %)", f"{fr((T > 15).mean() * 100, 1)} %", "niveau critique", "#ef4444"),
             kpi(f"P(T > {thr:g} %)", f"{fr((T > thr).mean() * 100, 1)} %", "seuil personnalisé", "#a78bfa")])

    sect("Comparaison Shift 1 / Shift 2", "multiplicateurs définis dans « Données industrielles »")
    S = st.session_state
    base_scale = c.scale / c.shift_mult
    fig = go.Figure()
    rows = []
    for nom, mult, colr in [("Shift 1", S["p_sh1"], "#22d3ee"), ("Shift 2", S["p_sh2"], "#f59e0b")]:
        Ts = combine(np.clip(c.P_base * (base_scale * mult)[:, None], 0, 0.999), c.modele) * 100
        xs, ys, ww = hist_bars(Ts, 60, T.min() * 0.7, T.max() * 1.3)
        fig.add_bar(x=xs, y=ys, width=ww, name=nom, marker_color=colr, opacity=0.6)
        rows.append({"Shift": nom, "Moyenne (%)": round(Ts.mean(), 2), "Écart-type": round(Ts.std(ddof=1), 2),
                     f"P(T ≤ {c.cible:g} %)": round((Ts <= c.cible).mean() * 100, 1)})
    fig.update_layout(barmode="overlay")
    fig.add_vline(x=c.cible, line_dash="dash", line_color="white")
    plot(style(fig, 300))
    show_df(pd.DataFrame(rows))

    sect("Voir la simulation se construire", "illustration dynamique de la loi des grands nombres")
    if st.button("▶ Lancer l'animation"):
        ph = st.empty()
        frames = np.unique(np.logspace(2, np.log10(c.n), 22).astype(int))
        ymax = hist_bars(T, 50, T.min(), T.max())[1].max() * 1.7
        for f in frames:
            xs, ys, ww = hist_bars(T[:f], 50, T.min(), T.max())
            fg = go.Figure(go.Bar(x=xs, y=ys, width=ww, marker_color="#22d3ee"))
            fg.add_vline(x=T[:f].mean(), line_color="#f59e0b")
            fg.update_yaxes(range=[0, ymax], title="% des simulations")
            fg.update_xaxes(title="Taux de chute (%)")
            style(fg, 300, f"n = {fr(f, 0)} simulations · moyenne = {fr(T[:f].mean(), 3)} %")
            ph.plotly_chart(fg, key=f"anim{f}", **PLOT_KW)
            time.sleep(0.12)


def bootstrap_ci(T, q, B=200, size=10000, seed=1):
    rng = np.random.default_rng(seed)
    sub = T[:size]
    qs = [np.percentile(rng.choice(sub, len(sub), replace=True), q) for _ in range(B)]
    return np.percentile(qs, [2.5, 97.5])


def page_results(c):
    hero("Analyse des résultats", "Statistiques, intervalles de confiance, sensibilité et comparaison des lignes", c)
    t1, t2, t3, t4 = st.tabs(["Statistiques", "Fonction de répartition", "Sensibilité", "Par ligne"])
    T = c.T_cur
    with t1:
        d = pd.DataFrame({"Avant": stats_of(T, c.cible), "Après scénario": stats_of(c.T_after, c.cible)}).round(3)
        st.dataframe(d, **DF_KW)
        hw = ic_mean(T)
        p = (T <= c.cible).mean()
        hp = 1.96 * np.sqrt(p * (1 - p) / len(T))
        b = bootstrap_ci(T, 95)
        kpi_row([kpi("IC 95 % de E(T)", f"[{fr(T.mean() - hw, 3)} ; {fr(T.mean() + hw, 3)}]", "TCL : x̄ ± 1,96·s/√n", "#22d3ee"),
                 kpi(f"IC 95 % de P(T ≤ {c.cible:g} %)",
                     f"[{fr(max(p - hp, 0) * 100, 2)} ; {fr(min(p + hp, 1) * 100, 2)}] %", "p̂ ± 1,96·√(p̂(1−p̂)/n)", "#22c55e"),
                 kpi("IC 95 % du percentile 95 % (bootstrap)", f"[{fr(b[0], 2)} ; {fr(b[1], 2)}] %",
                     "200 rééchantillonnages", "#f59e0b")])
    with t2:
        qs = np.linspace(0, 1, 800)
        fig = go.Figure()
        fig.add_scatter(x=np.quantile(c.T_cur, qs), y=qs * 100, name="Avant", line=dict(color="#ef4444", width=3))
        fig.add_scatter(x=np.quantile(c.T_after, qs), y=qs * 100, name="Après scénario", line=dict(color="#22c55e", width=3))
        fig.add_vline(x=c.cible, line_dash="dash", line_color="white", annotation_text="Cible")
        fig.update_xaxes(title="Taux de chute (%)")
        fig.update_yaxes(title="P(T ≤ x) en %")
        plot(style(fig, 380, "Fonction de répartition empirique"))
        st.caption("La hauteur de la courbe à l'abscisse de la cible est la probabilité d'atteindre l'objectif.")
    with t3:
        ranks = pd.Series(T).rank().to_numpy()
        rho = [np.corrcoef(pd.Series(c.P_cur[:, i]).rank().to_numpy(), ranks)[0, 1] for i in range(K)]
        test = st.slider("Réduction testée sur une cause à la fois (%)", 10, 100, 50, 10, key="sens_test")
        gains = []
        for i in range(K):
            Pt = c.P_cur.copy()
            Pt[:, i] *= 1 - test / 100
            gains.append(T.mean() - (combine(Pt, c.modele) * 100).mean())
        names = [x["short"] for x in CAUSES]
        g1, g2 = st.columns(2)
        with g1:
            o = np.argsort(rho)
            plot(style(go.Figure(go.Bar(x=[rho[i] for i in o], y=[names[i] for i in o], orientation="h",
                                        marker_color="#3b82f6")), 320, "Corrélation de Spearman avec T"))
        with g2:
            o = np.argsort(gains)
            plot(style(go.Figure(go.Bar(x=[gains[i] for i in o], y=[names[i] for i in o], orientation="h",
                                        marker_color="#22c55e")), 320, f"Gain en traitant une cause (−{test} %)"))
        note(f"Cause à traiter en premier selon ce modèle : <b>{names[int(np.argmax(gains))]}</b>. "
             "Ce classement dépend des paramètres saisis.")
    with t4:
        res = per_line(c.spec, c.corr, c.n, c.seed, c.modele, c.k, c.mults, c.shift_mult, c.red, c.cible)
        df = pd.DataFrame({"Ligne": c.lines["Ligne"], "Taux moyen (%)": [r[0] for r in res],
                           f"P(T ≤ {c.cible:g} %) en %": [r[1] for r in res],
                           "P95 (%)": [r[4] for r in res],
                           "Taux moyen après scénario (%)": [r[2] for r in res],
                           "Fruits perdus / jour": [r[0] / 100 * c.lines["Rendement (kg/h)"].iloc[i] * c.heures * 1000 / c.poids
                                                    for i, r in enumerate(res)]}).round(2)
        show_df(df.sort_values("Taux moyen (%)", ascending=False))


def page_conv(c):
    hero("Convergence : LGN et TCL", "Pourquoi la méthode fonctionne, et avec quelle précision", c)
    T, n = c.T_cur, c.n
    sect("A. Loi des grands nombres")
    idx = np.unique(np.logspace(2, np.log10(n), 250).astype(int))
    cs, cs2 = np.cumsum(T), np.cumsum(T ** 2)
    mr = cs[idx - 1] / idx
    vr = np.maximum((cs2[idx - 1] / idx - mr ** 2) * idx / (idx - 1), 0)
    hw = 1.96 * np.sqrt(vr / idx)
    fig = go.Figure()
    fig.add_scatter(x=idx, y=mr + hw, line=dict(width=0), showlegend=False)
    fig.add_scatter(x=idx, y=mr - hw, fill="tonexty", fillcolor="rgba(34,211,238,.2)", line=dict(width=0), name="IC 95 %")
    fig.add_scatter(x=idx, y=mr, name="Moyenne cumulée", line=dict(color="#22d3ee", width=3))
    fig.add_hline(y=T.mean(), line_dash="dash", line_color="white")
    fig.update_xaxes(type="log", title="Nombre de simulations n")
    fig.update_yaxes(title="Taux moyen (%)")
    plot(style(fig, 360, "La moyenne simulée se stabilise quand n augmente"))
    cps = [x for x in [100, 500, 1000, 5000, 10000, 50000, 100000, 500000] if x <= n]
    df = pd.DataFrame({"n": cps, "Moyenne estimée (%)": [T[:x].mean() for x in cps],
                       "Erreur standard σ/√n": [T[:x].std(ddof=1) / np.sqrt(x) for x in cps],
                       "Demi-largeur IC 95 %": [ic_mean(T[:x]) for x in cps]}).round(4)
    show_df(df)
    st.caption("L'erreur standard décroît en 1/√n : pour être 10 fois plus précis, il faut 100 fois plus de simulations.")

    sect("B. Théorème central limite")
    m = st.select_slider("Taille m de chaque expérience", [5, 30, 100, 500], value=30, key="tcl_m")
    means = means_rep(c.spec, float(c.scale.mean()), c.modele, m, c.seed + 1)
    g1, g2 = st.columns(2)
    with g1:
        x, y, w = hist_bars(T, 60, T.min(), T.max())
        plot(style(go.Figure(go.Bar(x=x, y=y, width=w, marker_color="#ef4444")), 320, "Une simulation : T (asymétrique)"))
    with g2:
        x, y, w = hist_bars(means, 35, means.min(), means.max())
        fig = go.Figure(go.Bar(x=x, y=y, width=w, marker_color="#3b82f6", opacity=0.8, name="Moyennes simulées"))
        s_th = T.std(ddof=1) / np.sqrt(m)
        xs = np.linspace(means.min(), means.max(), 200)
        dens = np.exp(-(xs - T.mean()) ** 2 / (2 * s_th ** 2)) / (s_th * np.sqrt(2 * np.pi)) * w * 100
        fig.add_scatter(x=xs, y=dens, name="Loi normale théorique", line=dict(color="white", width=2))
        plot(style(fig, 320, f"1000 moyennes de {m} simulations"))
    st.caption("Même si T n'est pas normal, la distribution de ses moyennes épouse la loi normale : c'est le TCL.")

    sect("C. Combien de simulations ?")
    eps = st.number_input("Précision souhaitée sur le taux moyen (± points)", 0.001, 5.0, 0.05, 0.01, format="%.3f",
                          key="eps")
    n_req = int(np.ceil((1.96 * T.std(ddof=1) / eps) ** 2))
    st.latex(r"n\ge\left(\frac{1{,}96\,\sigma}{\varepsilon}\right)^2")
    note(f"Pour ± {eps} point à 95 % de confiance : <b>{fr(n_req, 0)} simulations</b> (vous en utilisez {fr(n, 0)}).")


def page_scen(c):
    hero("Scénarios d'amélioration", "Effet des actions correctives sur le taux de chute, la probabilité et l'économie", c)
    S = st.session_state

    def preset(vals):
        for i, v in enumerate(vals):
            st.session_state[f"p_red_{i}"] = v

    b = st.columns(3)
    b[0].button("Aucune action", on_click=preset, args=([0] * K,))
    b[1].button("Scénario modéré", on_click=preset, args=([30, 40, 50, 60, 0],))
    b[2].button("Scénario ambitieux", on_click=preset, args=([60, 70, 80, 90, 0],))
    cols = st.columns(2)
    for i, cs in enumerate(CAUSES):
        cols[i % 2].slider(f"{cs['name']} · {cs['action']}", 0, 100, step=5, key=f"p_red_{i}", format="%d %%")
    note("Les réductions sont des <b>hypothèses de scénario</b>. Les situations « avant » et « après » utilisent les mêmes "
         "tirages aléatoires : l'écart vient uniquement des actions.")
    Tb, Ta = c.T_cur, c.T_after
    pb, pa = (Tb <= c.cible).mean() * 100, (Ta <= c.cible).mean() * 100
    kpi_row([kpi("Taux moyen avant", f"{fr(Tb.mean())} %", "", "#ef4444"),
             kpi("Taux moyen après", f"{fr(Ta.mean())} %", f"{fr(Ta.mean() - Tb.mean())} pts", "#22c55e"),
             kpi(f"P(T ≤ {c.cible:g} %) avant", f"{fr(pb, 1)} %", "", "#f59e0b"),
             kpi(f"P(T ≤ {c.cible:g} %) après", f"{fr(pa, 1)} %", f"{fr(pa - pb, 1)} pts",
                 "#22c55e" if pa >= 80 else "#f59e0b")])
    if pa >= 80:
        note(f"L'objectif est atteint dans {fr(pa, 0)} % des simulations : atteignable sous les hypothèses du modèle.")
    elif pa >= 50:
        note(f"Objectif atteint dans {fr(pa, 0)} % des simulations : plausible mais non garanti.", warn=True)
    else:
        note(f"Objectif atteint dans seulement {fr(pa, 0)} % des simulations : scénario insuffisant.", warn=True)

    g1, g2 = st.columns(2)
    with g1:
        lo, hi = min(Tb.min(), Ta.min()), max(Tb.max(), Ta.max())
        fig = go.Figure()
        for TT, nm, colr in [(Tb, "Avant", "#ef4444"), (Ta, "Après", "#22c55e")]:
            x, y, w = hist_bars(TT, 60, lo, hi)
            fig.add_bar(x=x, y=y, width=w, name=nm, marker_color=colr, opacity=0.6)
        fig.update_layout(barmode="overlay")
        fig.add_vline(x=c.cible, line_dash="dash", line_color="white")
        plot(style(fig, 330, "Distributions avant / après"))
    with g2:
        rs = np.linspace(0, 1, 21)
        pr = [(combine(c.P_cur * (1 - r), c.modele) * 100 <= c.cible).mean() * 100 for r in rs]
        fig = go.Figure(go.Scatter(x=rs * 100, y=pr, mode="lines+markers", line=dict(color="#22d3ee", width=3)))
        fig.add_hline(y=80, line_dash="dot", line_color="#22c55e", annotation_text="80 %")
        fig.update_xaxes(title="Réduction uniforme de toutes les causes (%)")
        fig.update_yaxes(title=f"P(T ≤ {c.cible:g} %)")
        plot(style(fig, 330, "Quelle réduction globale viser ?"))

    sect("Impact économique", "perte, matière sauvée et gain réellement récupérable")
    sauve_kg = (Tb.mean() - Ta.mean()) / 100 * c.kg_an
    kpi_row([kpi("Matière perdue avant", f"{fr(Tb.mean() / 100 * c.kg_an / 1000, 0)} t/an", "", "#ef4444"),
             kpi("Matière perdue après", f"{fr(Ta.mean() / 100 * c.kg_an / 1000, 0)} t/an", "", "#f59e0b"),
             kpi("Matière sauvée", f"{fr(sauve_kg / 1000, 0)} t/an", "", "#22c55e"),
             kpi("Valeur brute sauvée", f"{fr(sauve_kg * c.prix, 0)} DH/an", f"à {c.prix} DH/kg", "#22d3ee"),
             kpi("Gain net récupérable", f"{fr(sauve_kg * (c.prix - c.revalo), 0)} DH/an",
                 f"déduction revalorisation {c.revalo} DH/kg", "#a78bfa")])

    sect("Lien avec le rendement et les arrêts", "hypothèse explicite, pas une proportionnalité automatique")
    alpha = st.slider("Part des arrêts attribuable aux chutes de fruits (%)", 0, 50, key="p_alpha")
    red_rel = (Tb.mean() - Ta.mean()) / Tb.mean()
    arret_ap = c.arret * (1 - alpha / 100 * red_rel)
    kpi_row([kpi("Rendement utile avant", f"{fr(c.kg_h * (1 - Tb.mean() / 100), 0)} kg/h", "débit × (1 − T)", "#ef4444"),
             kpi("Rendement utile après", f"{fr(c.kg_h * (1 - Ta.mean() / 100), 0)} kg/h", "débit × (1 − T)", "#22c55e"),
             kpi("Arrêt moyen avant", f"{fr(c.arret, 2)} min", "", "#f59e0b"),
             kpi("Arrêt moyen après", f"{fr(arret_ap, 2)} min", f"si {alpha} % des arrêts liés aux chutes", "#22d3ee")])


def page_optim(c):
    hero("Optimisation des actions correctives", "Combinaison la moins coûteuse qui atteint l'objectif", c)
    S = st.session_state
    st.latex(r"\min\; C=\sum_i c_i x_i\quad\text{sous}\quad P(T\le T_{cible})\ge p_{min},\quad x_i\in\{0,1\}")
    st.caption("Résolution par recherche exhaustive de toutes les combinaisons (2^k cas) : chaque combinaison est évaluée "
               "par Monte-Carlo sur les mêmes tirages. Coûts et efficacités sont des hypothèses à confirmer.")
    hd = st.columns([2, 1, 1])
    hd[0].markdown("**Action**")
    hd[1].markdown("**Coût (DH)**")
    hd[2].markdown("**Réduction si réalisée (%)**")
    for i, cs in enumerate(CAUSES):
        r = st.columns([2, 1, 1])
        r[0].markdown(f"{cs['short']} — {cs['action']}")
        r[1].number_input("c", 0, 1000000, step=100, key=f"p_cost{i}", label_visibility="collapsed")
        r[2].number_input("e", 0, 100, step=5, key=f"p_eff{i}", label_visibility="collapsed")
    thr = st.slider("Probabilité minimale exigée P(T ≤ cible) (%)", 50, 99, key="p_thr")
    df, best, ok = run_optim(c, thr)
    pc = f"P(T ≤ {c.cible:g} %) en %"
    combo = best["Combinaison d'actions"]
    if ok:
        note(f"<b>Combinaison optimale</b> : {combo} — coût {fr(best['Coût (DH)'], 0)} DH, "
             f"P(T ≤ {c.cible:g} %) = {fr(best[pc], 1)} %.")
    else:
        note(f"Aucune combinaison n'atteint {thr} %. La meilleure probabilité est {fr(best[pc], 1)} % avec : "
             f"{combo}. Renforcez les actions ou revoyez l'objectif.", warn=True)
    gain_net = (c.T_cur.mean() - best["Taux moyen (%)"]) / 100 * c.kg_an * (c.prix - c.revalo)
    pay = best["Coût (DH)"] / gain_net * 12 if gain_net > 0 else float("nan")
    kpi_row([kpi("Coût de la solution", f"{fr(best['Coût (DH)'], 0)} DH", "", "#22d3ee"),
             kpi("Taux moyen obtenu", f"{fr(best['Taux moyen (%)'])} %", f"avant : {fr(c.T_cur.mean())} %", "#22c55e"),
             kpi("Gain net annuel", f"{fr(gain_net, 0)} DH", "", "#a78bfa"),
             kpi("Retour sur investissement", f"{fr(pay, 1)} mois" if pay == pay else "n.d.", "coût / gain mensuel", "#f59e0b")])
    fig = go.Figure(go.Scatter(x=df["Coût (DH)"], y=df[pc], mode="markers+text", text=df["Nb actions"].astype(str),
                               textposition="top center",
                               marker=dict(size=14, color=df[pc], colorscale="Turbo", showscale=True,
                                           colorbar=dict(title="P %")),
                               hovertext=df["Combinaison d'actions"]))
    fig.add_hline(y=thr, line_dash="dash", line_color="white", annotation_text=f"Seuil {thr} %")
    fig.add_scatter(x=[best["Coût (DH)"]], y=[best[pc]], mode="markers", name="Optimum",
                    marker=dict(size=24, color="rgba(0,0,0,0)", line=dict(color="#22c55e", width=3)))
    fig.update_xaxes(title="Coût total (DH)")
    fig.update_yaxes(title=pc)
    plot(style(fig, 380, "Compromis coût / probabilité (chaque point = une combinaison)"))
    show_df(df.round(2))
    return df, best


def page_lab(c):
    hero("Monte-Carlo LAB", "Comparez deux lois de probabilité sur une même cause et observez l'effet sur le résultat", c)
    S = st.session_state
    names = [x["name"] for x in CAUSES]
    i = names.index(st.selectbox("Cause à expérimenter", names, key="lab_cause"))
    a, b = st.columns(2)
    la = a.selectbox("Loi A", LOIS, index=0, key="lab_a")
    lb = b.selectbox("Loi B", LOIS, index=1, key="lab_b")
    s0 = c.spec[i]
    q = st.columns(3)
    lo = q[0].number_input("Min (%)", 0.0, 50.0, s0[1], 0.1, key=f"lab_lo{i}")
    mo = q[1].number_input("Mode (%)", 0.0, 50.0, s0[2], 0.1, key=f"lab_mo{i}")
    hi = q[2].number_input("Max (%)", 0.0, 50.0, s0[3], 0.1, key=f"lab_hi{i}")
    lo, hi = min(lo, mo, hi), max(lo, mo, hi)
    if hi - lo < 0.01:
        hi = lo + 0.01
    mo = min(max(mo, lo), hi)
    m = min(c.n, 50000)
    out = {}
    for nm, law in [("A", la), ("B", lb)]:
        rng = np.random.default_rng(c.seed + 5)
        x = sample_marginal(law, lo, mo, hi, s0[4], m, rng) / 100.0
        P = c.P_base[:m].copy()
        P[:, i] = x
        P = np.clip(P * c.scale[:m, None], 0, 0.999)
        out[nm] = (x * 100, combine(P, c.modele) * 100, law)
    g1, g2 = st.columns(2)
    for col, idx_, ttl in [(g1, 0, "Perte de la cause (%)"), (g2, 1, "Taux de chute global T (%)")]:
        with col:
            lo_, hi_ = min(out["A"][idx_].min(), out["B"][idx_].min()), max(out["A"][idx_].max(), out["B"][idx_].max())
            fig = go.Figure()
            for nm, colr in [("A", "#22d3ee"), ("B", "#f59e0b")]:
                x, y, w = hist_bars(out[nm][idx_], 50, lo_, hi_)
                fig.add_bar(x=x, y=y, width=w, name=f"Loi {nm} : {out[nm][2]}", marker_color=colr, opacity=0.6)
            fig.update_layout(barmode="overlay")
            if idx_ == 1:
                fig.add_vline(x=c.cible, line_dash="dash", line_color="white")
            fig.update_xaxes(title=ttl)
            plot(style(fig, 340))
    rows = []
    for nm in ["A", "B"]:
        Tl = out[nm][1]
        rows.append({"Loi": f"{nm} : {out[nm][2]}", "Moyenne T (%)": Tl.mean(), "Variance T": Tl.var(ddof=1),
                     "Écart-type T": Tl.std(ddof=1), f"P(T ≤ {c.cible:g} %) en %": (Tl <= c.cible).mean() * 100,
                     "P(T > 10 %) en %": (Tl > 10).mean() * 100})
    show_df(pd.DataFrame(rows).round(3))
    d = rows[1]["Moyenne T (%)"] - rows[0]["Moyenne T (%)"]
    note(f"Passer de la loi A à la loi B change le taux moyen de {fr(d, 3)} point et la probabilité d'atteindre la cible "
         f"de {fr(rows[1][f'P(T ≤ {c.cible:g} %) en %'] - rows[0][f'P(T ≤ {c.cible:g} %) en %'], 2)} points : "
         "les hypothèses probabilistes influencent les conclusions. (La dépendance n'est pas appliquée à la cause testée.)")


def interpretation(c, best):
    T, Ta = c.T_cur, c.T_after
    p, pa = (T <= c.cible).mean() * 100, (Ta <= c.cible).mean() * 100
    means = c.P_cur.mean(axis=0) * 100
    top = CAUSES[int(np.argmax(means))]["name"]
    lines = [
        f"Périmètre : {c.scope} ; shift : {c.shift} ; {fr(c.n, 0)} simulations (graine {c.seed}).",
        f"Mode : {'calibré sur le taux observé (k = ' + fr(c.k, 3) + ')' if c.calibrated else 'hypothèses libres'} ; "
        f"combinaison : {c.modele}.",
        f"Situation actuelle : taux de chute moyen {fr(T.mean())} % (écart-type {fr(T.std(ddof=1))} pts), "
        f"percentile 95 % = {fr(np.percentile(T, 95))} %. Probabilité d'atteindre {c.cible:g} % : {fr(p, 1)} %.",
        f"Cause la plus contributrice : {top} ({fr(means.max(), 1)} % de perte moyenne).",
        f"Après scénario : taux moyen {fr(Ta.mean())} %, probabilité d'atteindre la cible {fr(pa, 1)} %.",
        f"Combinaison d'actions la moins coûteuse (seuil {st.session_state['p_thr']} %) : "
        f"{best["Combinaison d'actions"]} pour {fr(best['Coût (DH)'], 0)} DH.",
        "Limites : les paramètres des causes, les multiplicateurs par ligne, les coûts et les efficacités sont des "
        "hypothèses ; les conclusions sont conditionnelles au modèle et doivent être validées par les mesures de l'étape Mesurer."]
    return lines


def make_pdf(c, best):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.08, 0.95, "Rapport de simulation Monte-Carlo", fontsize=20, weight="bold", color="#0b3b5c")
        fig.text(0.08, 0.925, f"DUROC Agadir – Zone de prépack – {datetime.now():%d/%m/%Y}", fontsize=10, color="gray")
        y = 0.88
        for ln in interpretation(c, best):
            for part in textwrap.wrap(ln, 95):
                fig.text(0.08, y, part, fontsize=10)
                y -= 0.022
            y -= 0.012
        pdf.savefig(fig)
        plt.close(fig)
        fig, axs = plt.subplots(3, 1, figsize=(8.27, 11.69))
        lo, hi = min(c.T_cur.min(), c.T_after.min()), max(c.T_cur.max(), c.T_after.max())
        axs[0].hist(c.T_cur, 60, range=(lo, hi), alpha=.6, color="#c0392b", label="Avant")
        axs[0].hist(c.T_after, 60, range=(lo, hi), alpha=.6, color="#27ae60", label="Après")
        axs[0].axvline(c.cible, color="k", ls="--")
        axs[0].set_title("Distribution du taux de chute (%)")
        axs[0].legend()
        idx = np.unique(np.logspace(2, np.log10(c.n), 200).astype(int))
        axs[1].plot(idx, np.cumsum(c.T_cur)[idx - 1] / idx)
        axs[1].set_xscale("log")
        axs[1].set_title("Convergence de la moyenne (loi des grands nombres)")
        axs[2].barh([x["short"] for x in CAUSES], c.P_cur.mean(axis=0) * 100, color="#2980b9")
        axs[2].set_title("Perte moyenne par cause (%)")
        fig.tight_layout(pad=3)
        pdf.savefig(fig)
        plt.close(fig)
    return buf.getvalue()


def make_excel(c, df_opt):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        pd.DataFrame([{"Cause": CAUSES[i]["name"], "Loi": s[0], "Min (%)": s[1], "Mode (%)": s[2], "Max (%)": s[3],
                       "Statut": st.session_state[f"p_c{i}_stat"]} for i, s in enumerate(c.spec)]).to_excel(xw, sheet_name="Paramètres", index=False)
        c.lines.to_excel(xw, sheet_name="Lignes", index=False)
        pd.DataFrame({"Avant": stats_of(c.T_cur, c.cible), "Après": stats_of(c.T_after, c.cible)}).to_excel(xw, sheet_name="Résultats")
        df_opt.to_excel(xw, sheet_name="Optimisation", index=False)
        pd.DataFrame({"taux_avant_%": c.T_cur[:20000], "taux_apres_%": c.T_after[:20000]}).to_excel(xw, sheet_name="Simulations (20000)", index=False)
    return buf.getvalue()


def page_report(c, df_opt, best):
    hero("Rapports et exportation", "Interprétation automatique, PDF, Excel et CSV", c)
    sect("Interprétation automatique")
    for ln in interpretation(c, best):
        st.markdown(f"- {ln}")
    sect("Téléchargements")
    d1, d2, d3 = st.columns(3)
    try:
        d1.download_button("📄 Rapport PDF", make_pdf(c, best), "rapport_monte_carlo_duroc.pdf", "application/pdf")
    except Exception as e:
        d1.warning(f"PDF indisponible : {e}")
    try:
        d2.download_button("📊 Classeur Excel", make_excel(c, df_opt), "monte_carlo_duroc.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        d2.warning("Excel indisponible : installez openpyxl (pip install openpyxl).")
    d3.download_button("⬇ Simulations (CSV)", pd.DataFrame({"taux_avant_%": c.T_cur, "taux_apres_%": c.T_after}).to_csv(
        index=False), "simulations.csv", "text/csv")


# ======================================================================
# NAVIGATION ET EXÉCUTION
# ======================================================================
with st.sidebar:
    st.markdown('<div class="brand"><div class="logo">🍅</div><div><div class="bt">DUROC · MC LAB</div>'
                '<div class="bs">Monte-Carlo · Prépack · Agadir</div></div></div>', unsafe_allow_html=True)
    page = st.radio("Navigation", PAGES, label_visibility="collapsed", key="nav")
    st.markdown("---")
    st.markdown("**Paramètres globaux**")
    st.select_slider("Nombre de simulations n", [1000, 5000, 10000, 50000, 100000, 200000, 500000], key="p_n")
    st.number_input("Graine aléatoire", 0, 10 ** 6, step=1, key="p_seed")
    st.number_input("Taux cible (%)", 0.5, 30.0, step=0.5, key="p_cible")
    st.caption(f"{datetime.now():%d/%m/%Y} · DMAIC : Définir → Mesurer → Analyser → Innover → Contrôler")

ctx = build_ctx()

if page == PAGES[0]:
    page_dashboard(ctx)
elif page == PAGES[1]:
    page_method(ctx)
elif page == PAGES[2]:
    page_data(ctx)
elif page == PAGES[3]:
    page_model(ctx)
elif page == PAGES[4]:
    page_sim(ctx)
elif page == PAGES[5]:
    page_results(ctx)
elif page == PAGES[6]:
    page_conv(ctx)
elif page == PAGES[7]:
    page_scen(ctx)
elif page == PAGES[8]:
    page_optim(ctx)
elif page == PAGES[9]:
    page_lab(ctx)
else:
    _df, _best, _ok = run_optim(ctx, st.session_state["p_thr"])
    page_report(ctx, _df, _best)