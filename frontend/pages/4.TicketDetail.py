import streamlit as st

from ui.api_client import ApiClient, ApiError, get_api_base_url
from ui.helpers import require_login, show_api_error
from ui.state import init_state

init_state()
st.title("Ticket Detail")

require_login()

api = ApiClient(get_api_base_url(), token=st.session_state["token"])

ticket_id = st.session_state.get("selected_ticket_id")
ticket_id_input = st.number_input(
    "Ticket ID", min_value=1, value=int(ticket_id or 1), step=1
)
if st.button("Load Ticket"):
    st.session_state["selected_ticket_id"] = int(ticket_id_input)
    st.rerun()

ticket_id = st.session_state.get("selected_ticket_id")
if not ticket_id:
    st.info(
        "Select a ticket from Ticket List first, or enter Ticket ID above and click Load."
    )
    st.stop()

# Load ticket
try:
    with st.spinner("Loading ticket..."):
        ticket = api.get_ticket(ticket_id=int(ticket_id))
except ApiError as err:
    show_api_error(err)
    st.stop()

st.subheader(f"Ticket #{ticket['id']}: {ticket['subject']}")
st.write(
    f"**Status:** {ticket['status']} | **Priority:** {ticket['priority']} | **User ID:** {ticket['user_id']}"
)
st.write("**Description:**")
st.write(ticket["description"])

# Admin status update
if st.session_state.get("role") == "ADMIN":
    st.markdown("---")
    st.subheader("Admin: Update Status")
    new_status = st.selectbox(
        "New Status", ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"], index=0
    )
    if st.button("Update Status", type="primary"):
        try:
            with st.spinner("Updating status..."):
                res = api.update_status(ticket_id=int(ticket_id), status=new_status)
            st.success(f"Updated status to {res['status']}")
            st.rerun()
        except ApiError as err:
            show_api_error(err)

# Replies section
st.markdown("---")
st.subheader("Replies")

try:
    with st.spinner("Loading replies..."):
        replies = api.list_replies(ticket_id=int(ticket_id))
except ApiError as err:
    show_api_error(err)
    st.stop()

if not replies:
    st.info("No replies yet.")
else:
    for r in replies:
        with st.container(border=True):
            st.write(f"**Reply #{r['id']}** | Author: {r['author_id']}")
            st.write(r["message"])

st.markdown("### Add Reply")
msg = st.text_area("Message", height=120)
if st.button("Send Reply", type="primary"):
    try:
        with st.spinner("Posting reply..."):
            api.create_reply(ticket_id=int(ticket_id), message=msg)
        st.success("Reply posted.")
        st.rerun()
    except ApiError as err:
        show_api_error(err)
