import streamlit as st

from ui.api_client import ApiError
from ui.state import is_logged_in


def require_login() -> None:
    if not is_logged_in():
        st.warning("Please login first (go to Login/Signup page).")
        st.stop()


def show_api_error(err: ApiError) -> None:
    st.error(f"API Error ({err.status_code}): {err.message}")
    # Optional: details expander
    with st.expander("Details"):
        st.write(err.details)
