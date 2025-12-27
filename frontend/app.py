import streamlit as st

from ui.state import init_state, is_logged_in, logout

st.set_page_config(page_title="Ticket System", layout="wide")

init_state()

st.title("Customer Support Ticket System")

col1, col2 = st.columns([3, 1])
with col1:
    st.caption(
        "Streamlit frontend for FastAPI ticket workflow (RBAC + lifecycle + replies)."
    )
with col2:
    if is_logged_in():
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

st.info(
    "Use the Pages sidebar to navigate: \nLogin/Signup → Create Ticket → Ticket List → Ticket Detail → Admin Dashboard."
)
