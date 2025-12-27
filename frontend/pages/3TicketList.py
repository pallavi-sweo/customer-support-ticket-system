import streamlit as st

from ui.api_client import ApiClient, ApiError, get_api_base_url
from ui.helpers import require_login, show_api_error
from ui.state import init_state

init_state()
st.title("Ticket List")

require_login()

api = ApiClient(get_api_base_url(), token=st.session_state["token"])

with st.sidebar:
    st.subheader("Filters")
    status = st.selectbox(
        "Status", ["", "OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"], index=0
    )
    priority = st.selectbox("Priority", ["", "LOW", "MEDIUM", "HIGH"], index=0)
    created_from = st.text_input(
        "Created From (ISO)", placeholder="2025-01-01T00:00:00"
    )
    created_to = st.text_input("Created To (ISO)", placeholder="2025-12-31T23:59:59")

    st.subheader("Pagination")
    page = st.number_input("Page", min_value=1, value=1, step=1)
    page_size = st.selectbox("Page Size", [5, 10, 20, 50], index=1)

try:
    with st.spinner("Loading tickets..."):
        data = api.list_tickets(
            page=int(page),
            page_size=int(page_size),
            status=status or None,
            priority=priority or None,
            created_from=created_from or None,
            created_to=created_to or None,
        )
except ApiError as err:
    show_api_error(err)
    st.stop()

st.caption(
    f"Logged in as: {st.session_state.get('email')} ({st.session_state.get('role')})"
)
st.write(f"Total tickets: {data['total']}")

items = data["items"]
if not items:
    st.info("No tickets found for the given filters.")
    st.stop()

for t in items:
    with st.container(border=True):
        cols = st.columns([2, 2, 2, 2, 1])
        cols[0].markdown(f"**ID:** {t['id']}")
        cols[1].markdown(f"**Status:** {t['status']}")
        cols[2].markdown(f"**Priority:** {t['priority']}")
        cols[3].markdown(f"**Subject:** {t['subject']}")
        if cols[4].button("Open", key=f"open_{t['id']}"):
            st.session_state["selected_ticket_id"] = t["id"]
            st.success(f"Selected ticket {t['id']} — open Ticket Detail page.")
