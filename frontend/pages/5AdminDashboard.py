import streamlit as st

from ui.api_client import ApiClient, ApiError, get_api_base_url
from ui.helpers import require_login, show_api_error
from ui.state import init_state

init_state()
st.title("Admin Dashboard")

require_login()

if st.session_state.get("role") != "ADMIN":
    st.warning("Admin access required.")
    st.stop()

api = ApiClient(get_api_base_url(), token=st.session_state["token"])

with st.sidebar:
    st.subheader("Filters")
    status = st.selectbox(
        "Status", ["", "OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"], index=0
    )
    priority = st.selectbox("Priority", ["", "LOW", "MEDIUM", "HIGH"], index=0)
    page = st.number_input("Page", min_value=1, value=1, step=1)
    page_size = st.selectbox("Page Size", [5, 10, 20, 50], index=1)

try:
    with st.spinner("Loading all tickets..."):
        data = api.list_tickets(
            page=int(page),
            page_size=int(page_size),
            status=status or None,
            priority=priority or None,
        )
except ApiError as err:
    show_api_error(err)
    st.stop()

st.write(f"Total: {data['total']}")
items = data["items"]
if not items:
    st.info("No tickets.")
    st.stop()

for t in items:
    with st.container(border=True):
        cols = st.columns([1, 2, 2, 3, 2])
        cols[0].write(f"#{t['id']}")
        cols[1].write(f"Status: {t['status']}")
        cols[2].write(f"Priority: {t['priority']}")
        cols[3].write(t["subject"])

        new_status = cols[4].selectbox(
            "Update",
            ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
            index=(
                ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"].index(t["status"])
                if t["status"] in ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
                else 0
            ),
            key=f"status_{t['id']}",
        )
        if cols[4].button("Apply", key=f"apply_{t['id']}"):
            try:
                with st.spinner("Updating..."):
                    api.update_status(ticket_id=t["id"], status=new_status)
                st.success(f"Ticket {t['id']} updated.")
                st.rerun()
            except ApiError as err:
                show_api_error(err)
