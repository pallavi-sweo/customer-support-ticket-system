import streamlit as st

from ui.api_client import ApiClient, ApiError, get_api_base_url
from ui.helpers import require_login, show_api_error
from ui.state import init_state

init_state()
st.title("Create Ticket")

require_login()

if st.session_state.get("role") != "USER":
    st.warning("Only customers (USER role) can create tickets.")
    st.stop()

api = ApiClient(get_api_base_url(), token=st.session_state["token"])

subject = st.text_input("Subject (5–200 chars)")
description = st.text_area("Description (10–5000 chars)", height=150)
priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], index=1)

if st.button("Create Ticket", type="primary"):
    try:
        with st.spinner("Creating ticket..."):
            t = api.create_ticket(
                subject=subject, description=description, priority=priority
            )
        st.success(f"Ticket created: ID {t['id']}")
        st.session_state["selected_ticket_id"] = t["id"]
        st.info("Go to Ticket Detail page to add replies.")
    except ApiError as err:
        show_api_error(err)
