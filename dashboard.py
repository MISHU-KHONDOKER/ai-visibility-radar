"""
dashboard.py
------------
HEIDSTAR Sales & Marketing Agent - professional control dashboard.
"""

import streamlit as st
import subprocess
import sys
import os

# Page config must come first (before other st. calls)
st.set_page_config(page_title="HEIDSTAR AI Agent", page_icon="🔬", layout="wide",
                   initial_sidebar_state="expanded")

# Paths
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_THIS_DIR, "src")

# Allow importing helper modules from src/
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
from usage_summary import summarize as _usage_summarize
from run_summary import group_into_runs as _group_runs

# ============================================================
#  LOGIN GATE
# ============================================================
import configparser

def get_dashboard_password():
    """Read the dashboard password from the gitignored config file."""
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(_THIS_DIR, "config", "config.ini"), encoding="utf-8")
    try:
        return cfg.get("dashboard", "password")
    except Exception:
        return None

def check_login():
    """Show a polished animated login screen. Returns True only if correct."""
    if st.session_state.get("authenticated", False):
        return True

    # Full styling for an attractive login screen
    st.markdown("""
    <style>
                /* Cost breakdown table */
.cost-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    animation: fadeIn 0.6s ease;
}
.cost-table thead th {
    background: linear-gradient(135deg, #2a5298, #2c7fb8);
    color: #ffffff !important;
    padding: 14px 18px;
    font-size: 14px;
    font-weight: 700;
    text-align: left;
}
.cost-table tbody td {
    background: rgba(255,255,255,0.04);
    color: #d6f3ff !important;
    padding: 13px 18px;
    font-size: 14px;
    border-bottom: 1px solid rgba(120,170,255,0.12);
}
.cost-table tbody tr:hover td {
    background: rgba(109,213,237,0.12);
}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    .stApp {
        background: radial-gradient(circle at 30% 10%, #1e3a5f 0%, #0c1524 55%, #050a14 100%);
        font-family: 'Inter', sans-serif;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* Login card */
    .login-card {
        background: linear-gradient(145deg, rgba(30,60,114,0.45), rgba(15,30,55,0.55));
        border: 1px solid rgba(120,180,255,0.25);
        border-radius: 24px;
        padding: 44px 40px 30px 40px;
        box-shadow: 0 24px 60px rgba(0,0,0,0.55);
        animation: rise 0.8s cubic-bezier(0.16,1,0.3,1);
        backdrop-filter: blur(8px);
        text-align: center;
    }
    .login-icon {
        font-size: 56px; display: block; margin-bottom: 6px;
        animation: float 3s ease-in-out infinite;
    }
    .login-title {
        color: #ffffff !important; font-size: 30px; font-weight: 800;
        letter-spacing: -0.5px; margin: 0;
    }
    .login-sub {
        color: #9fc0e0 !important; font-size: 15px; margin-top: 8px; margin-bottom: 6px;
    }

    /* Make the password label readable */
    .stTextInput label { color: #cfe2f5 !important; font-weight: 600 !important; }
    /* Password input box */
    .stTextInput input {
        background-color: rgba(255,255,255,0.95) !important;
        color: #0a1322 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(120,180,255,0.4) !important;
        padding: 12px !important;
    }

    /* Login button */
    .stButton > button {
        background: linear-gradient(135deg, #2a5298 0%, #6dd5ed 100%) !important;
        color: #ffffff !important; font-weight: 700 !important; font-size: 16px !important;
        border: none !important; border-radius: 12px !important; padding: 14px !important;
        box-shadow: 0 8px 22px rgba(44,127,184,0.5) !important;
        transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    }
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 16px 34px rgba(109,213,237,0.6) !important;
        background: linear-gradient(135deg, #6dd5ed 0%, #a78bfa 100%) !important;
        color: #0a1322 !important;
    }

    @keyframes rise { from {opacity:0; transform:translateY(30px);} to {opacity:1; transform:translateY(0);} }
    @keyframes float { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-10px);} }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
          <span class="login-icon">🔬</span>
          <p class="login-title">HEIDSTAR AI Agent</p>
          <p class="login-sub">Sales &amp; Marketing Intelligence Engine</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        pw = st.text_input("🔑 Password", type="password")
        if st.button("🔓  Log in", use_container_width=True):
            correct = get_dashboard_password()
            if correct and pw == correct:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
    return False


# Stop here and show login if not authenticated.
if not check_login():
    st.stop()
# ============================================================
#  STYLING
# ============================================================
st.markdown("""
<style>
            /* AI Brain - premium hero button */
.brain-section {
    background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(44,127,184,0.18));
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 20px;
    padding: 26px 30px;
    margin: 10px 0 6px 0;
    box-shadow: 0 12px 34px rgba(80,40,160,0.3);
    animation: fadeUp 0.8s ease;
    position: relative;
    overflow: hidden;
}
.brain-section::before {
    content: "";
    position: absolute; top: -40%; right: -5%;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(167,139,250,0.35) 0%, transparent 70%);
    animation: float 5s ease-in-out infinite;
}
.brain-title { font-size: 23px; font-weight: 800; color: #ffffff; margin: 0; }
.brain-desc { color: #c9b8f0; font-size: 14px; margin-top: 6px; }

/* Make the brain button itself special (purple gradient, glowing) */
div[data-testid="column"] .stButton > button[kind="primary"],
.brain-btn button {
    background: linear-gradient(135deg, #7c3aed 0%, #6dd5ed 100%) !important;
    font-size: 17px !important;
    font-weight: 800 !important;
    padding: 20px !important;
    box-shadow: 0 10px 30px rgba(124,58,237,0.55) !important;
    animation: glowPulse 2.5s infinite !important;
}
@keyframes glowPulse {
    0%,100% { box-shadow: 0 10px 30px rgba(124,58,237,0.45); }
    50% { box-shadow: 0 14px 42px rgba(109,213,237,0.7); }
}
            
        
            
            /* Sales Advisor - premium section (teal/green accent) */
.sales-section {
    background: linear-gradient(135deg, rgba(16,185,129,0.16), rgba(44,127,184,0.16));
    border: 1px solid rgba(52,211,153,0.35);
    border-radius: 20px;
    padding: 26px 30px;
    margin: 10px 0 6px 0;
    box-shadow: 0 12px 34px rgba(16,120,90,0.3);
    animation: fadeUp 0.8s ease;
    position: relative;
    overflow: hidden;
}
.sales-section::before {
    content: "";
    position: absolute; top: -40%; right: -5%;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(52,211,153,0.3) 0%, transparent 70%);
    animation: float 5s ease-in-out infinite;
}
.sales-title { font-size: 23px; font-weight: 800; color: #ffffff; margin: 0; }
.sales-desc { color: #a7e8d0; font-size: 14px; margin-top: 6px; }

.sales-btn button {
    background: linear-gradient(135deg, #10b981 0%, #6dd5ed 100%) !important;
    font-size: 17px !important;
    font-weight: 800 !important;
    padding: 20px !important;
    box-shadow: 0 10px 30px rgba(16,185,129,0.55) !important;
    animation: glowPulseGreen 2.5s infinite !important;
}
@keyframes glowPulseGreen {
    0%,100% { box-shadow: 0 10px 30px rgba(16,185,129,0.45); }
    50% { box-shadow: 0 14px 42px rgba(109,213,237,0.7); }
}
            
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

/* App background */
.stApp {
    background: radial-gradient(circle at 20% 0%, #1a2a45 0%, #0c1524 45%, #070d18 100%);
    font-family: 'Inter', sans-serif;
}
.stApp, .stApp p, .stApp label, .stApp span, .stApp div { color: #e6edf5; }

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101d33 0%, #0a1322 100%);
    border-right: 1px solid rgba(120,170,255,0.12);
}
[data-testid="stSidebar"] * { color: #cdd9ec !important; }

/* Hero */
.hero {
    background: linear-gradient(110deg, #1e3c72 0%, #2a5298 55%, #2c7fb8 100%);
    border-radius: 22px;
    padding: 38px 44px;
    margin-bottom: 10px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.45);
    border: 1px solid rgba(255,255,255,0.10);
    animation: slideDown 0.7s cubic-bezier(0.16,1,0.3,1);
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: ""; position: absolute; top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(120,210,255,0.25) 0%, transparent 70%);
    animation: float 6s ease-in-out infinite;
}
.hero h1 { color: #fff; font-size: 40px; font-weight: 800; margin: 0; letter-spacing: -1px; }
.hero p { color: #cfe6ff; font-size: 17px; margin-top: 10px; font-weight: 400; }
.live-dot {
    display: inline-block; width: 9px; height: 9px; background: #4ade80;
    border-radius: 50%; margin-right: 7px; box-shadow: 0 0 10px #4ade80;
    animation: pulse 1.5s infinite;
}
            

/* Daily Cost cards */
.day-wrap { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 6px; }
.day-card {
    flex: 1 1 180px;
    background: linear-gradient(150deg, rgba(30,60,114,0.4), rgba(15,30,55,0.4));
    border: 1px solid rgba(120,170,255,0.18);
    border-top: 3px solid #6dd5ed;
    border-radius: 14px;
    padding: 18px 20px;
    transition: all 0.25s ease;
    animation: fadeUp 0.6s ease backwards;
}
.day-card:hover { transform: translateY(-5px);
    box-shadow: 0 12px 28px rgba(44,127,184,0.35); border-top-color: #a78bfa; }
.day-date { font-size: 15px; font-weight: 700; color: #ffffff; margin-bottom: 12px; }
.day-stats { display: flex; justify-content: space-between; gap: 12px; }
.day-stat { display: flex; flex-direction: column; }
.day-val { font-size: 18px; font-weight: 800;
    background: linear-gradient(135deg,#6dd5ed,#a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.day-lbl { font-size: 10.5px; color: #8da3bd; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 2px; }
.day-avg {
    display: flex; gap: 26px; justify-content: flex-end; align-items: center;
    margin-top: 14px; padding: 14px 24px;
    background: linear-gradient(100deg, rgba(16,185,129,0.15), rgba(44,127,184,0.15));
    border: 1px solid rgba(52,211,153,0.3); border-radius: 12px;
    font-size: 13px; color: #c9d6e8; font-weight: 600;
}
.day-avg-cost { color: #34d399; font-weight: 800; font-size: 15px; }
            
                        

/* Metric cards */
.metric-card {
    background: linear-gradient(145deg, rgba(40,82,152,0.35), rgba(20,40,75,0.35));
    border: 1px solid rgba(120,170,255,0.22);
    border-radius: 16px; padding: 22px 16px; text-align: center;
    box-shadow: 0 8px 22px rgba(0,0,0,0.3);
    animation: fadeUp 0.8s ease backwards;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.metric-card:hover { transform: translateY(-5px); box-shadow: 0 14px 30px rgba(44,127,184,0.4); }
.metric-card .num { font-size: 34px; font-weight: 800;
    background: linear-gradient(135deg,#6dd5ed,#a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-card .lbl { font-size: 12.5px; color: #9fb3cc; margin-top: 6px; letter-spacing: 0.3px; text-transform: uppercase; }

/* Section heading */
.section-label { font-size: 24px; font-weight: 700; color: #ffffff;
    margin: 26px 0 2px 0; animation: fadeIn 0.9s ease; }
.section-sub { color: #8da3bd; font-size: 14px; margin-bottom: 16px; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2a5298 0%, #2c7fb8 100%);
    color: #ffffff !important; font-weight: 600; font-size: 15px;
    border: 1px solid rgba(140,200,255,0.25); border-radius: 14px;
    padding: 18px 12px; width: 100%;
    box-shadow: 0 8px 20px rgba(20,50,100,0.45);
    transition: all 0.28s cubic-bezier(0.34,1.56,0.64,1);
}
.stButton > button:hover {
    transform: translateY(-5px);
    background: linear-gradient(135deg, #6dd5ed 0%, #a78bfa 100%);
    color: #0a1322 !important;
    box-shadow: 0 16px 34px rgba(109,213,237,0.55);
    border-color: rgba(167,139,250,0.6);
}
.stButton > button:active { transform: translateY(-1px) scale(0.98); }

/* Output blocks - readable */
.stCode, pre {
    border-radius: 14px !important;
    border: 1px solid rgba(120,210,255,0.3) !important;
    background-color: #0a1420 !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
    animation: fadeIn 0.6s ease;
}
.stCode div, .stCode span, .stCode code, pre, pre span, code {
    color: #d6f3ff !important; background-color: transparent !important;
    font-family: 'Consolas','Monaco',monospace !important; font-size: 13.5px !important;
}

/* Spinner text */
.stSpinner > div { color: #6dd5ed !important; }

/* Animations */
@keyframes slideDown { from {opacity:0; transform:translateY(-25px);} to {opacity:1; transform:translateY(0);} }
@keyframes fadeUp { from {opacity:0; transform:translateY(22px);} to {opacity:1; transform:translateY(0);} }
@keyframes fadeIn { from {opacity:0;} to {opacity:1;} }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
@keyframes float { 0%,100%{transform:translateY(0);} 50%{transform:translateY(20px);} }
.metric-card:nth-child(1){animation-delay:0.05s;} 
            
            /* Engine Run History - "mission log" aesthetic */
.run-log-wrap { display: flex; flex-direction: column; gap: 12px; margin-top: 6px; }
.run-log {
    display: grid;
    grid-template-columns: 1.3fr 2.4fr 1.3fr;
    align-items: center;
    gap: 18px;
    background: linear-gradient(100deg, rgba(20,40,70,0.5), rgba(12,22,40,0.5));
    border: 1px solid rgba(120,170,255,0.16);
    border-left: 3px solid #6dd5ed;
    border-radius: 14px;
    padding: 16px 22px;
    transition: all 0.25s ease;
    animation: fadeUp 0.5s ease backwards;
}
.run-log:hover { transform: translateX(4px); border-left-color: #a78bfa;
    box-shadow: 0 8px 24px rgba(80,40,160,0.25); }
.run-log-big { border-left: 3px solid #a78bfa;
    background: linear-gradient(100deg, rgba(40,30,80,0.5), rgba(20,30,55,0.5)); }
.rl-no { font-size: 16px; font-weight: 800; color: #ffffff; }
.rl-time { font-size: 12.5px; color: #9fb3cc; margin-top: 2px; }
.rl-badge-big { display:inline-block; margin-top:7px; font-size:10px; font-weight:700;
    letter-spacing:0.5px; color:#0a1322; background:#a78bfa; padding:2px 9px; border-radius:20px; }
.rl-badge-small { display:inline-block; margin-top:7px; font-size:10px; font-weight:700;
    letter-spacing:0.5px; color:#9fb3cc; background:rgba(255,255,255,0.08); padding:2px 9px; border-radius:20px; }
.rl-stats { display: flex; justify-content: space-around; gap: 10px; }
.rl-stat { text-align: center; }
.rl-val { font-size: 17px; font-weight: 800;
    background: linear-gradient(135deg,#6dd5ed,#a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.rl-lbl { font-size: 10.5px; color: #8da3bd; text-transform: uppercase; letter-spacing: 0.4px; }
.rl-models { font-size: 11.5px; color: #7f93ab; text-align: right; }
.run-total {
    display: flex; gap: 26px; justify-content: flex-end; align-items: center;
    margin-top: 14px; padding: 14px 24px;
    background: linear-gradient(100deg, rgba(124,58,237,0.18), rgba(44,127,184,0.18));
    border: 1px solid rgba(167,139,250,0.3); border-radius: 12px;
    font-size: 13px; color: #c9d6e8; font-weight: 600;
}
.run-total-cost { color: #6dd5ed; font-weight: 800; font-size: 15px; }
            
</style>
""", unsafe_allow_html=True)


def run_tool(script_name):
    script_path = os.path.join(_SRC_DIR, script_name)
    try:
        result = subprocess.run(
            [sys.executable, script_path], cwd=_SRC_DIR,
            capture_output=True, text=True, encoding="utf-8", timeout=10000,
        )
        out = result.stdout
        if result.stderr:
            out += "\n[errors]\n" + result.stderr
        return out or "(no output)"
    except Exception as e:
        return f"Error running {script_name}: {e}"


# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🔬 HEIDSTAR")
    st.markdown("**AI Agent Control**")
    st.markdown("---")
    st.markdown("**Phase 1**")
    st.markdown("✅ Visibility Measurement")
    st.markdown("✅ Competitor Intelligence")
    st.markdown("✅ Customer Finding")
    st.markdown("---")
    st.markdown("**Engines**")
    st.markdown("🟢 DeepSeek — model memory")
    st.markdown("🟢 Qwen — web reality")
    st.markdown("---")
    #st.caption("China-first GEO/AEO engine")


# ============================================================
#  HERO
# ============================================================
st.markdown("""
<div class="hero">
  <h1>🔬 HEIDSTAR Sales &amp; Marketing Agent</h1>
  <p><span class="live-dot"></span>AI Visibility &amp; Intelligence Engine &nbsp;•&nbsp; Live Control Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
#  METRICS
# ============================================================
m1, m2, m3, m4 = st.columns(4)
m1.markdown('<div class="metric-card"><div class="num">2</div><div class="lbl">AI Engines Monitored</div></div>', unsafe_allow_html=True)
m2.markdown('<div class="metric-card"><div class="num">19</div><div class="lbl">Buyer Questions</div></div>', unsafe_allow_html=True)
m3.markdown('<div class="metric-card"><div class="num">165+</div><div class="lbl">Competitors Tracked</div></div>', unsafe_allow_html=True)
m4.markdown('<div class="metric-card"><div class="num">84</div><div class="lbl">Customer Leads</div></div>', unsafe_allow_html=True)

# ============================================================
#  INTELLIGENCE VIEWS
# ============================================================
st.markdown('<div class="section-label">📊 Intelligence Views</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Instant insights from existing data — free to view anytime.</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    b_score = st.button("📈  Visibility Scorecard")
    b_comp = st.button("🏢  Competitor Tracking")
with c2:
    b_oem = st.button("🎯  OEM / ODM Lane")
    b_cat = st.button("📋  Category Breakdown")
with c3:
    b_new = st.button("🆕  New Entrants")
    b_cust = st.button("👥  Customer Candidates")


def show(title, script):
    st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)
    with st.spinner("Running the engine..."):
        st.code(run_tool(script))

if b_score: show("📈 Visibility Scorecard", "heidstar_scorecard.py")
if b_comp:  show("🏢 Competitor Tracking", "track_competitors.py")
if b_oem:   show("🎯 OEM / ODM Lane", "oem_odm_view.py")
if b_cat:   show("📋 Category Breakdown", "category_breakdown.py")
if b_new:   show("🆕 New Entrants", "find_new_entrants.py")
if b_cust:  show("👥 Customer Candidates", "show_candidates.py")

# ============================================================
#  AI BRAIN - strategic summary & recommendations (premium)
# ============================================================
st.markdown("""
<div class="brain-section">
  <p class="brain-title">🧠 AI Strategy Brain</p>
  <p class="brain-desc">The agent reads all findings and generates an executive summary plus
  data-driven recommendations to improve HEIDSTAR's visibility. AI proposes — you decide.</p>
</div>
""", unsafe_allow_html=True)

brain_col1, brain_col2, brain_col3 = st.columns([1, 1.2, 1])
with brain_col2:
    st.markdown('<div class="brain-btn">', unsafe_allow_html=True)
    brain_clicked = st.button("✨  Generate Strategy & Recommendations  ✨", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if brain_clicked:
    st.markdown('<div class="section-label">🧠 Strategic Analysis & Recommendations</div>', unsafe_allow_html=True)
    st.caption("AI reasoning over the engine's real findings. These are recommendations for human review, not auto-executed actions.")
    with st.spinner("🧠 The brain is analyzing all findings and forming strategy..."):
        st.code(run_tool("agent_brain.py"))

# ============================================================
#  SALES STRATEGY ADVISOR (premium - CEO instruction #2)
# ============================================================
st.markdown("""
<div class="sales-section">
  <p class="sales-title">🎯 Sales Strategy Advisor</p>
  <p class="sales-desc">Generates per-segment sales strategy, competitive positioning, and legitimate
  channels to reach each customer type — based on the engine's real findings.</p>
</div>
""", unsafe_allow_html=True)

sales_col1, sales_col2, sales_col3 = st.columns([1, 1.2, 1])
with sales_col2:
    st.markdown('<div class="sales-btn">', unsafe_allow_html=True)
    sales_clicked = st.button("🎯  Generate Sales Strategy & Channels  🎯", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if sales_clicked:
    st.markdown('<div class="section-label">🎯 Sales Strategy & Channels</div>', unsafe_allow_html=True)
    st.warning("⚠️ These are AI-generated suggestions for the sales team to VALIDATE. "
               "Specific tactics, prices, or claims are ideas to verify — not confirmed HEIDSTAR commitments. "
               "Real personal contacts require the company CRM or proper data sources, not AI.")
    with st.spinner("🎯 Forming sales strategy and channel routing..."):
        st.code(run_tool("sales_advisor.py"))        

# ============================================================
#  LIVE-RUN CONTROLS (expensive - make real API calls)
# ============================================================
st.markdown('<div class="section-label">⚡ Live Engine Runs</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">These make REAL API calls (use quota). A confirmation is required before each run.</div>', unsafe_allow_html=True)

# Initialise confirmation flags in session memory.
for key in ["confirm_wide", "confirm_measure", "confirm_proc"]:
    if key not in st.session_state:
        st.session_state[key] = False

lc1, lc2, lc3 = st.columns(3)

# ---- Wide Customer Search ----
with lc1:
    if st.button("🌐  Run Wide Customer Search"):
        st.session_state.confirm_wide = True
    if st.session_state.confirm_wide:
        st.warning("This runs ~40 live searches and uses API quota.")
        cc1, cc2 = st.columns(2)
        if cc1.button("✅ Confirm", key="cw_yes"):
            st.session_state.confirm_wide = False
            show("🌐 Wide Customer Search (live)", "find_customers_wide.py")
        if cc2.button("✖ Cancel", key="cw_no"):
            st.session_state.confirm_wide = False

# ---- Procurement Search ----
with lc2:
    if st.button("📑  Run Procurement Search"):
        st.session_state.confirm_proc = True
    if st.session_state.confirm_proc:
        st.warning("This runs live procurement searches (~6 API calls).")
        pc1, pc2 = st.columns(2)
        if pc1.button("✅ Confirm", key="cp_yes"):
            st.session_state.confirm_proc = False
            show("📑 Procurement Search (live)", "find_procurement.py")
        if pc2.button("✖ Cancel", key="cp_no"):
            st.session_state.confirm_proc = False

# ---- Full Measurement ----
with lc3:
    if st.button("📡  Run Full Measurement"):
        st.session_state.confirm_measure = True
    if st.session_state.confirm_measure:
        st.warning("HEAVY: ~150 API calls, several minutes.")
        mc1, mc2 = st.columns(2)
        if mc1.button("✅ Confirm", key="cm_yes"):
            st.session_state.confirm_measure = False
            show("📡 Full Measurement (live)", "run_measurement.py")
        if mc2.button("✖ Cancel", key="cm_no"):
            st.session_state.confirm_measure = False

st.write("")

# ============================================================
#  API CONSUMPTION & COST
# ============================================================
st.markdown('<div class="section-label">💰 API Consumption & Cost</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Live token usage and estimated cost (at standard rates). Free quota currently covers actual charges.</div>', unsafe_allow_html=True)

_usage = _usage_summarize()
_tot = _usage["totals"]

# Headline metric cards
uc1, uc2, uc3, uc4 = st.columns(4)
uc1.markdown(f'<div class="metric-card"><div class="num">{_tot["calls"]:,}</div><div class="lbl">Total API Calls</div></div>', unsafe_allow_html=True)
uc2.markdown(f'<div class="metric-card"><div class="num">{_tot["tokens"]:,}</div><div class="lbl">Total Tokens</div></div>', unsafe_allow_html=True)
uc3.markdown(f'<div class="metric-card"><div class="num">¥{_tot["cost"]:.6f}</div><div class="lbl">Est. Cost (RMB)</div></div>', unsafe_allow_html=True)
uc4.markdown(f'<div class="metric-card"><div class="num">{len(_usage["by_model"])}</div><div class="lbl">Models Used</div></div>', unsafe_allow_html=True)

st.write("")

if _tot["calls"] > 0:
    import pandas as pd
    import plotly.graph_objects as go

     # Fixed colors per model - consistent across ALL charts
    MODEL_COLORS = {
        "qwen-plus": "#6dd5ed",      # light green/cyan
        "deepseek-chat": "#a78bfa",  # purple
    }
    def color_for(model):
        return MODEL_COLORS.get(model, "#8da3bd")  # grey fallback for others

    # Shared dark-theme styling for charts
    def style_fig(fig, height=340):
        fig.update_layout(
            height=height,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.03)",
            font=dict(color="#cfe2f5", family="Inter"),
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        )
        return fig

    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("**🔹 Tokens by Model**")
        models = list(_usage["by_model"].keys())
        tokens = [_usage["by_model"][m]["tokens"] for m in models]
        fig = go.Figure(go.Bar(
            x=models, y=tokens,
            marker=dict(
                color=[color_for(m) for m in models],
                line=dict(color="rgba(255,255,255,0.25)", width=1.5),
            ),
            text=tokens, textposition="outside",
            textfont=dict(color="#e6edf5", size=14),
        ))
        style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.markdown("**🔹 Estimated Cost Over Time (¥)**")
        dates = sorted(_usage["by_date"].keys())
        costs = [_usage["by_date"][d]["cost"] for d in dates]
        fig2 = go.Figure(go.Scatter(
            x=dates, y=costs, mode="lines+markers",
            line=dict(color="#a78bfa", width=3, shape="spline"),
            marker=dict(size=10, color="#6dd5ed", line=dict(color="#a78bfa", width=2)),
            fill="tozeroy", fillcolor="rgba(167,139,250,0.15)",
        ))
        style_fig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # Cost by model (a second bar, more useful than just tokens)
    st.markdown("**🔹 Estimated Cost by Model (¥)**")
    cost_models = list(_usage["by_model"].keys())
    cost_vals = [_usage["by_model"][m]["cost"] for m in cost_models]
    fig3 = go.Figure(go.Bar(
        x=cost_vals, y=cost_models, orientation="h",
        marker=dict(color=[color_for(m) for m in cost_models],
                    line=dict(color="rgba(255,255,255,0.2)", width=1)),
        text=[f"¥{c:.6f}" for c in cost_vals], textposition="outside",
        textfont=dict(color="#e6edf5"),
    ))
    style_fig(fig3, height=240)
    st.plotly_chart(fig3, use_container_width=True)

    # Detailed table
    # Detailed table - dark themed
    st.markdown("**🔹 Detailed Breakdown**")
    rows_html = ""
    for m, d in _usage["by_model"].items():
        rows_html += f"""
        <tr>
          <td>{m}</td>
          <td style="text-align:right">{d['calls']:,}</td>
          <td style="text-align:right">{d['tokens']:,}</td>
          <td style="text-align:right">¥{d['cost']:.6f}</td>
        </tr>"""
    st.markdown(f"""
    <table class="cost-table">
      <thead>
        <tr>
          <th>Model</th>
          <th style="text-align:right">Calls</th>
          <th style="text-align:right">Tokens</th>
          <th style="text-align:right">Est. Cost (¥)</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
else:
    st.info("No usage logged yet. Run the engine (any live button) and usage will appear here.")


# ============================================================
#  DAILY COST VIEW (professional - CEO requested)
# ============================================================
st.markdown('<div class="section-label">📅 Daily Cost Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Total tokens and estimated cost per day — the daily spend at a glance.</div>', unsafe_allow_html=True)

_by_date = _usage.get("by_date", {})
if _by_date:
    # Build daily cards, newest day first
    day_cards = ""
    sorted_days = sorted(_by_date.keys(), reverse=True)
    for day in sorted_days:
        v = _by_date[day]
        day_cards += f"""
        <div class="day-card">
          <div class="day-date">{day}</div>
          <div class="day-stats">
            <div class="day-stat"><span class="day-val">¥{v['cost']:.6f}</span><span class="day-lbl">cost</span></div>
            <div class="day-stat"><span class="day-val">{v['tokens']:,}</span><span class="day-lbl">tokens</span></div>
          </div>
        </div>"""
    st.markdown(f'<div class="day-wrap">{day_cards}</div>', unsafe_allow_html=True)

    # Average per day
    n_days = len(sorted_days)
    avg_cost = sum(v["cost"] for v in _by_date.values()) / n_days
    avg_tokens = sum(v["tokens"] for v in _by_date.values()) / n_days
    st.markdown(f"""
    <div class="day-avg">
      <span>📈 {n_days} active day(s)</span>
      <span>avg/day: {avg_tokens:,.0f} tokens</span>
      <span class="day-avg-cost">avg ¥{avg_cost:.6f}/day</span>
    </div>""", unsafe_allow_html=True)
else:
    st.info("No daily data yet.")


# ============================================================
#  PER-RUN HISTORY (distinct "mission log" aesthetic)
# ============================================================
st.markdown('<div class="section-label">🛰️ Engine Run History</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Each engine run grouped by time — with its own cost, tokens, and duration.</div>', unsafe_allow_html=True)

_runs = _group_runs()
if _runs:
    # newest first
    run_cards = ""
    for idx, run in enumerate(reversed(_runs)):
        run_no = len(_runs) - idx
        dur = (run["end"] - run["start"]).total_seconds() / 60.0
        models = " · ".join(f"{m} ×{n}" for m, n in run["models"].items())
        is_big = run["calls"] >= 20  # highlight full runs
        badge = "FULL RUN" if is_big else "quick"
        badge_class = "rl-badge-big" if is_big else "rl-badge-small"
        run_cards += f"""
        <div class="run-log {'run-log-big' if is_big else ''}">
          <div class="rl-left">
            <div class="rl-no">RUN #{run_no}</div>
            <div class="rl-time">{run['start'].strftime('%b %d, %Y · %H:%M')}</div>
            <span class="{badge_class}">{badge}</span>
          </div>
          <div class="rl-stats">
            <div class="rl-stat"><div class="rl-val">¥{run['cost']:.6f}</div><div class="rl-lbl">cost</div></div>
            <div class="rl-stat"><div class="rl-val">{run['tokens']:,}</div><div class="rl-lbl">tokens</div></div>
            <div class="rl-stat"><div class="rl-val">{run['calls']}</div><div class="rl-lbl">calls</div></div>
            <div class="rl-stat"><div class="rl-val">{dur:.0f}m</div><div class="rl-lbl">duration</div></div>
          </div>
          <div class="rl-models">{models}</div>
        </div>"""
    st.markdown(f'<div class="run-log-wrap">{run_cards}</div>', unsafe_allow_html=True)

    # grand total strip
    tot_cost = sum(r["cost"] for r in _runs)
    tot_tokens = sum(r["tokens"] for r in _runs)
    tot_calls = sum(r["calls"] for r in _runs)
    st.markdown(f"""
    <div class="run-total">
      <span>📊 {len(_runs)} runs</span>
      <span>{tot_calls} calls</span>
      <span>{tot_tokens:,} tokens</span>
      <span class="run-total-cost">¥{tot_cost:.6f} total</span>
    </div>""", unsafe_allow_html=True)
else:
    st.info("No runs logged yet.")

st.markdown('<div class="section-sub">HEIDSTAR AI Agent • Phase 1: Visibility & Intelligence • All systems live.</div>', unsafe_allow_html=True)