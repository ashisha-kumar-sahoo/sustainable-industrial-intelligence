"""Header-level UI: theme switch, login screen (hero + admin login / create-account forms) and the page header.
Moved from app.py: set_mode, picker (-> theme_switch), public() (-> render_login) and HERO (title text already replaced as app.py did).
Authentication logic itself stays in services/auth_service.py and is only called here, exactly as before."""
import streamlit as st
from services import auth_service as auth
from styles import LOGIN_CSS

LOGIN_HERO = ('<div class="hero"><div class="scene"><div class="cube"><div class="face f1">🏭</div><div class="face f2">⚡</div><div class="face f3">💧</div><div class="face f4">🌿</div><div class="face f5">⚙️</div><div class="face f6">🚨</div></div></div>'
        '<h1>SUSTAINABLE INDUSTRIAL INTELLIGENCE</h1><p>AI-powered monitoring &amp; decision support for industrial estates</p></div>')


def page_header(title): st.header(title)


def set_mode(where):
    """Apply the selected theme before the next Streamlit render."""
    st.session_state.light_mode = not st.session_state[f"theme_toggle_{where}"]


def theme_switch(where, dark):
    key = f"theme_toggle_{where}"
    if key not in st.session_state:
        st.session_state[key] = dark
    st.toggle("Theme", key=key, on_change=set_mode, args=(where,), help="ON = Dark, OFF = Light")

def render_login(dark):
    st.markdown(LOGIN_CSS, unsafe_allow_html=True); theme_switch("login", dark); st.markdown(LOGIN_HERO, unsafe_allow_html=True); _, mid, _ = st.columns([1, 1.5, 1]); tl, tr = mid.tabs(["🔐 Login", "📝 Create Account"])
    with tl, st.form("login"):
        st.subheader("Welcome Back"); i = st.text_input("Admin ID / Email"); p = st.text_input("Password", type="password")
        if st.form_submit_button("LOGIN", use_container_width=True):
            u = auth.login(i, p)
            if u: st.session_state.user = u; st.rerun()
            else: st.error("Invalid user ID/email or password.")
    with tr, st.form("reg"):
        st.subheader("Create Account")
        if st.session_state.get("registered"): st.success("Admin account created successfully. Continue to Login.")
        f = dict(full_name=st.text_input("Full Name"), admin_id=st.text_input("User ID / Username"), email=st.text_input("Email"), org=st.text_input("Organization / Facility"), phone=st.text_input("Phone Number"), role=st.selectbox("Role", ["OPERATIONS", "SUSTAINABILITY", "ADMIN"]), password=st.text_input("Password", type="password"), confirm=st.text_input("Confirm Password", type="password"), terms=st.checkbox("I agree to the terms and conditions."))
        if st.form_submit_button("CREATE ADMIN ACCOUNT", use_container_width=True):
            e = auth.register(f)
            if e: st.error(e)
            else: st.session_state.registered = True; st.rerun()
