import streamlit as st


def init_state() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("role", None)
    st.session_state.setdefault("email", None)
    st.session_state.setdefault("selected_ticket_id", None)


def is_logged_in() -> bool:
    return bool(st.session_state.get("token"))


def logout() -> None:
    st.session_state["token"] = None
    st.session_state["role"] = None
    st.session_state["email"] = None
    st.session_state["selected_ticket_id"] = None
