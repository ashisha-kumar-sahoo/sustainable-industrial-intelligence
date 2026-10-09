"""Header widgets, theme controls, and the account login/registration form."""

import streamlit as st

from services import auth_service as auth
from styles import LOGIN_CSS

LOGIN_HERO = (
    '<div class="hero"><div class="scene"><div class="cube">'
    '<div class="face f1">🏭</div><div class="face f2">⚡</div>'
    '<div class="face f3">💧</div><div class="face f4">🌿</div>'
    '<div class="face f5">⚙️</div><div class="face f6">🚨</div>'
    '</div></div><h1>SUSTAINABLE INDUSTRIAL INTELLIGENCE</h1>'
    '<p>AI-powered monitoring &amp; decision support for industrial estates</p></div>'
)


def page_header(title: str) -> None:
    """Render a consistent page title."""
    st.header(title)


def set_mode(where: str) -> None:
    """Save the theme choice before Streamlit reruns the page."""
    st.session_state.light_mode = not st.session_state[f"theme_toggle_{where}"]


def theme_switch(where: str, dark: bool) -> None:
    """Render a theme toggle with a stable key for each location."""
    key = f"theme_toggle_{where}"
    if key not in st.session_state:
        st.session_state[key] = dark

    st.toggle(
        "Theme",
        key=key,
        on_change=set_mode,
        args=(where,),
        help="ON = Dark, OFF = Light",
    )


def render_login(dark: bool) -> None:
    """Render login and first-account/public-account registration forms."""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    theme_switch("login", dark)
    st.markdown(LOGIN_HERO, unsafe_allow_html=True)

    _left_column, middle_column, _right_column = st.columns([1, 1.5, 1])
    login_tab, registration_tab = middle_column.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    with login_tab, st.form("login"):
        st.subheader("Welcome Back")
        identifier = st.text_input("Admin ID / Email")
        password = st.text_input("Password", type="password")

        if st.form_submit_button("LOGIN", use_container_width=True):
            user = auth.login(identifier, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid user ID/email or password.")

    with registration_tab, st.form("reg"):
        st.subheader("Create Account")
        if st.session_state.get("registered"):
            st.success("Account created successfully. Continue to Login.")

        role_options = auth.available_registration_roles()
        form_data = {
            "full_name": st.text_input("Full Name"),
            "admin_id": st.text_input("User ID / Username"),
            "email": st.text_input("Email"),
            "org": st.text_input("Organization / Facility"),
            "phone": st.text_input("Phone Number"),
            "role": st.selectbox("Role", role_options),
            "password": st.text_input("Password", type="password"),
            "confirm": st.text_input("Confirm Password", type="password"),
            "terms": st.checkbox("I agree to the terms and conditions."),
        }

        if st.form_submit_button("CREATE ACCOUNT", use_container_width=True):
            error_message = auth.register(form_data)
            if error_message:
                st.error(error_message)
            else:
                st.session_state.registered = True
                st.rerun()
