"""Global CSS and theme styling for the Streamlit dashboard.

The theme toggle stores its state in ``st.session_state["light_mode"]``.
``apply_styles`` injects the same styles on the login and dashboard pages.
"""
import re as _re
import streamlit as st


def css(dark):
    dark_variables = (
        "--bg1:#050b1a;--bg2:#0d2552;--card:rgba(255,255,255,.07);"
        "--t:#e2e8f0;--m:#94a3b8;--a:#38bdf8;"
        "--b:rgba(255,255,255,.14);--inp:rgba(255,255,255,.08);"
        "--sh:rgba(0,0,0,.55)"
    )
    light_variables = (
        "--bg1:#e6f0ff;--bg2:#ffffff;--card:rgba(255,255,255,.8);"
        "--t:#0f172a;--m:#475569;--a:#0369a1;"
        "--b:rgba(15,23,42,.14);--inp:#ffffff;--sh:rgba(30,64,120,.25)"
    )
    variables = dark_variables if dark else light_variables
    return "<style>:root{" + variables + "}" + """
.stApp{background:linear-gradient(-45deg,var(--bg1),var(--bg2),var(--bg1));
background-size:300% 300%;
animation:bg 18s ease infinite;
color:var(--t)}
@keyframes bg{0%{background-position:0 50%}50%{background-position:100% 50%}100%{background-position:0 50%}}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:var(--card);backdrop-filter:blur(14px);border-right:1px solid var(--b)}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp li,[data-testid="stMarkdownContainer"]{color:var(--t)}
.stTextInput input,div[data-baseweb="select"]>div{background:var(--inp)!important;
color:var(--t)!important;
border-radius:12px}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{border-radius:12px;
border:0;
background:linear-gradient(135deg,#0ea5e9,#6366f1);
box-shadow:0 10px 24px rgba(14,165,233,.4);
transition:.25s}
.stButton p,.stFormSubmitButton p,.stDownloadButton p{color:#fff!important;font-weight:600}
.stButton>button:hover,
.stFormSubmitButton>button:hover,
.stDownloadButton>button:hover{transform:translateY(-3px) scale(1.03)}
[data-testid="stForm"]{border:1px solid var(--b);
border-radius:22px;
padding:24px;
background:var(--card);
backdrop-filter:blur(16px);
transition:transform .3s ease;
box-shadow:18px 24px 50px var(--sh),inset 0 1px 0 rgba(255,255,255,.2)}
[data-testid="stForm"]:active{transform:scale(1.03)}[data-testid="stForm"]:focus-within{transform:scale(1.015)}
.scene{perspective:900px;height:170px;display:flex;justify-content:center;align-items:center;margin-top:10px}
.cube{width:90px;height:90px;position:relative;transform-style:preserve-3d;animation:spin 14s linear infinite}
.face{position:absolute;
width:90px;
height:90px;
display:flex;
align-items:center;
justify-content:center;
font-size:34px;
border:1px solid var(--a);
background:rgba(56,189,248,.18);
box-shadow:0 0 22px rgba(56,189,248,.35)}
.f1{transform:translateZ(45px)}
.f2{transform:rotateY(180deg) translateZ(45px)}
.f3{transform:rotateY(90deg) translateZ(45px)}
.f4{transform:rotateY(-90deg) translateZ(45px)}
.f5{transform:rotateX(90deg) translateZ(45px)}
.f6{transform:rotateX(-90deg) translateZ(45px)}
@keyframes spin{from{transform:rotateX(-22deg) rotateY(0)}to{transform:rotateX(-22deg) rotateY(360deg)}}
.hero{text-align:center}
.hero h1{font-size:2.2rem;
letter-spacing:.5px;
text-shadow:0 6px 18px var(--sh)}
.hero p{color:var(--m)!important}
.kg{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px;margin:8px 0 18px}
.kpi{background:var(--card);
border:1px solid var(--b);
border-radius:18px;
padding:16px;
backdrop-filter:blur(12px);
box-shadow:8px 12px 28px var(--sh);
transition:.3s;
transform:perspective(700px) rotateX(3deg)}
.kpi:hover{transform:perspective(700px) rotateX(8deg) translateY(-8px) scale(1.03)}
.kpi small{color:var(--m)}.kpi b{display:block;font-size:1.65rem;margin:4px 0}.kpi i{font-style:normal;font-size:.8rem}
.s-normal{border-bottom:4px solid #34d399}
.s-warning{border-bottom:4px solid #facc15}
.s-critical{border-bottom:4px solid #ef4444}
.s-info{border-bottom:4px solid #38bdf8}
.s-resolved{border-bottom:4px solid #94a3b8}
.alert{background:var(--card);
border:1px solid var(--b);
border-left:6px solid;
border-radius:14px;
padding:14px 18px;
margin:10px 0;
box-shadow:6px 10px 22px var(--sh);
transition:.3s}
.alert:hover{transform:translateX(6px) translateY(-3px)}
.alert.critical{border-left-color:#ef4444}
.alert.warning{border-left-color:#fb923c}
.alert.info{border-left-color:#38bdf8}
.alert.resolved{border-left-color:#94a3b8}
.alert small,.alert i{color:var(--m)}
""" + ("" if dark else '[data-testid="stDataFrame"]{filter:invert(1) hue-rotate(180deg)}') + "</style>"
def _min(css_text):
    """Remove CSS comments and source newlines before injecting styles."""
    without_comments = _re.sub(r"/\*.*?\*/", "", css_text, flags=_re.S)
    return _re.sub(r"\s*\n\s*", "", without_comments)
def ui_css(dark):
    """Add the neon-glass sidebar and navigation styles for the current theme."""
    dark_variables = (
        "--nb:rgba(0,240,255,.34);--nbh:#00f0ff;--ng:rgba(0,240,255,.45);"
        "--glass:rgba(8,22,52,.55);--glass2:rgba(0,240,255,.15);"
        "--sw:rgba(0,240,255,.2)"
    )
    light_variables = (
        "--nb:rgba(2,132,199,.40);--nbh:#0284c7;--ng:rgba(2,132,199,.35);"
        "--glass:rgba(255,255,255,.72);--glass2:rgba(2,132,199,.14);"
        "--sw:rgba(2,132,199,.16)"
    )
    variables = dark_variables if dark else light_variables
    return _min("<style>:root{" + variables + "}" + """
/* ---- sidebar: compact top, tidy spacing ---- */
[data-testid="stSidebarHeader"]{height:2.2rem!important;
min-height:0!important;
padding:.4rem .8rem 0!important;
margin:0!important}
[data-testid="stSidebarUserContent"]{padding-top:.2rem!important;padding-bottom:1.2rem!important}
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"]{gap:.7rem}
.sb-brand{display:flex;align-items:center;gap:10px}
.sb-logo{flex:0 0 auto;
width:40px;
height:40px;
display:flex;
align-items:center;
justify-content:center;
font-size:22px;
border-radius:12px;
border:1px solid var(--nb);
background:var(--glass);
box-shadow:0 0 14px var(--sw)}
.sb-title{font-weight:800;font-size:1.02rem;line-height:1.2;color:var(--t)}
.sb-user{margin:8px 0 0;font-size:.9rem;font-weight:600;color:var(--m)}
.sb-sec{font-size:.72rem;
font-weight:700;
letter-spacing:.14em;
text-transform:uppercase;
color:var(--m);
margin:2px 0 -2px}
.sb-sep{height:1px;margin:4px 0 2px;background:linear-gradient(90deg,transparent,var(--nb),transparent)}
/* filters: same neon-glass language */
[data-testid="stSidebar"] div[data-baseweb="select"]>div,
[data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"]{
border:1px solid var(--nb)!important;
border-radius:10px!important}
/* ---- theme switch: single compact ON/OFF control ---- */
[class*="st-key-tsw_"]{padding:0!important;margin:0!important}
[class*="st-key-tsw_"] label{color:var(--t)!important;font-weight:700!important;font-size:.85rem!important}
[class*="st-key-tsw_"] [data-testid="stToggle"]{padding-top:0!important}
.st-key-sidebar_logout button{min-height:2rem!important;height:2rem!important;padding:.2rem .7rem!important}
.block-container,[data-testid="stMainBlockContainer"]{padding-top:2.2rem!important}
/* ---- sidebar navigation buttons ---- */
section[data-testid="stSidebar"] .st-key-nav{gap:.4rem!important}
.st-key-nav .stButton>button{min-height:2.4rem;
padding:.35rem .85rem;
justify-content:flex-start;
text-align:left;
border-radius:10px;
border:1px solid var(--nb);
background:var(--glass);
backdrop-filter:blur(10px);
box-shadow:none;
transform:none;
transition:all .22s ease}
.st-key-nav .stButton>button p{color:var(--t)!important;font-weight:600;font-size:.92rem;text-align:left;margin:0}
.st-key-nav .stButton>button:hover{transform:translateX(3px);
border-color:var(--nbh);
filter:brightness(1.15);
box-shadow:0 0 12px var(--ng)}
.st-key-nav .stButton>button[kind="primary"],.st-key-nav [data-testid="stBaseButton-primary"]{background:var(--glass2);
border:1.5px solid var(--nbh);
box-shadow:0 0 14px var(--ng),inset 0 0 12px var(--sw)}
.st-key-nav .stButton>button[kind="primary"] p,.st-key-nav [data-testid="stBaseButton-primary"] p{font-weight:800}
""" + "</style>")

LOGIN_CSS = _min("""<style>
.block-container,[data-testid="stMainBlockContainer"]{padding-top:1.2rem!important;padding-bottom:2rem!important}
.hero{margin-top:-2.4rem;pointer-events:none}
.st-key-tsw_login{align-self:flex-start!important;margin:0 auto .4rem 0!important;justify-self:flex-start!important}
[data-testid="stLayoutWrapper"]:has(>.st-key-tsw_login),
[data-testid="stElementContainer"]:has(>.st-key-tsw_login){
display:flex!important;
justify-content:flex-start!important;
width:100%!important}
.scene{height:130px!important;margin-top:0!important}
.hero h1{font-size:clamp(1.5rem,2.6vw,2.2rem)!important;margin:0!important;padding:.2rem 0 .3rem!important}
.hero p{margin-bottom:.4rem!important}
</style>""")


def neon_css(dark):
    """Animated neon form border + KPI hover glow (was the NEON string in app.py; needs the current theme)."""
    surface_color = "#0b1a38" if dark else "#ffffff"
    css_rules = (
        "<style>:root{--sol:COLOR_PLACEHOLDER}"
        """@property --ang{syntax:'<angle>';inherits:false;initial-value:0deg}
[data-testid="stForm"]{border:2px solid transparent!important;
background:linear-gradient(var(--sol),var(--sol)) padding-box,
conic-gradient(from var(--ang),#00f0ff,#ff00e5,#a3ff12,#00f0ff) border-box!important;
animation:rot 5s linear infinite;
box-shadow:0 0 18px #00f0ff88,0 0 46px #ff00e555,18px 24px 50px var(--sh)}
@keyframes rot{to{--ang:360deg}}.kpi:hover{box-shadow:0 0 22px #00f0ff88}</style>"""
    )
    return css_rules.replace("COLOR_PLACEHOLDER", surface_color)


NAV = """<style>
[data-testid="stRadio"] [role="radiogroup"]{gap:8px}
[data-testid="stRadio"] label[data-baseweb="radio"]{flex:1 1 auto;
margin:0;
padding:10px 14px;
border-radius:12px;
border:1px solid var(--b);
background:var(--card);
transition:all .25s ease;
cursor:pointer}
[data-testid="stRadio"] label[data-baseweb="radio"]>div:first-child{display:none}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover{transform:translateX(4px);
border-color:#00f0ff;
box-shadow:0 0 14px #00f0ff66}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked){
background:linear-gradient(135deg,#0ea5e9,#6366f1);
border-color:transparent;
box-shadow:0 8px 20px rgba(14,165,233,.45)}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p{color:#fff!important;font-weight:700}
.fg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;max-width:1000px;margin:26px auto}
.feat{background:var(--card);
color:var(--t);
border:1.5px solid #00f0ff99;
border-radius:14px;
padding:16px 8px;
text-align:center;
font-weight:600;
cursor:pointer;
outline:none;
box-shadow:0 0 12px #00f0ff44;
transition:transform .3s cubic-bezier(.2,.8,.2,1),box-shadow .3s}
.feat:hover,.feat:focus,.feat:active{transform:scale(1.1) translateY(-6px);
box-shadow:0 0 26px #00f0ffaa,0 14px 30px var(--sh)}
</style>"""


def apply_styles(dark):
    """Inject the shared theme, neon accents, navigation, and sidebar styles."""
    primary_styles = css(dark) + neon_css(dark) + NAV
    sidebar_styles = ui_css(dark)
    st.markdown(primary_styles, unsafe_allow_html=True)
    st.markdown(sidebar_styles, unsafe_allow_html=True)
