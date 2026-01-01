import streamlit as st

from ui.api_client import ApiClient, ApiError, get_api_base_url
from ui.helpers import show_api_error
from ui.state import init_state

init_state()
st.title("Login / Signup")

api = ApiClient(get_api_base_url())

tab1, tab2 = st.tabs(["Login", "Signup"])

with tab1:
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", type="primary"):
        try:
            with st.spinner("Logging in..."):
                data = api.login(email=email, password=password)
            st.session_state["token"] = data["access_token"]
            st.session_state["role"] = data.get("role")
            st.session_state["email"] = email
            st.success(f"Logged in as {email} ({st.session_state['role']})")
        except ApiError as err:
            show_api_error(err)

with tab2:
    email2 = st.text_input("Email", key="signup_email")
    password2 = st.text_input(
        "Password (min 8 chars)", type="password", key="signup_password"
    )
    if st.button("Signup", type="primary"):
        if not email2.strip() or not password2 or len(password2) < 8:
            st.error("Valid email and password (min 8 chars) are required.")
        else:
            try:
                with st.spinner("Creating account..."):
                    api.signup(email=email2, password=password2)
                st.success("Signup successful. Now login.")
            except ApiError as err:
                show_api_error(err)
