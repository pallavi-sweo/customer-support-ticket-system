import streamlit as st

from ui.api_client import ApiClient, ApiError, get_api_base_url
from ui.helpers import require_login, show_api_error
from ui.state import init_state

init_state()
st.title("Ticket Detail")

require_login()

api = ApiClient(get_api_base_url(), token=st.session_state["token"])

# ----------------------------
# Ticket selection
# ----------------------------
ticket_id = st.session_state.get("selected_ticket_id")
ticket_id_input = st.number_input(
    "Ticket ID", min_value=1, value=int(ticket_id or 1), step=1
)

col_a, col_b = st.columns([1, 3])
if col_a.button("Load Ticket"):
    st.session_state["selected_ticket_id"] = int(ticket_id_input)
    # reset replies paging when switching tickets
    st.session_state["replies_page"] = 1
    st.rerun()

if col_b.button("Clear Selection"):
    st.session_state.pop("selected_ticket_id", None)
    st.session_state.pop("replies_page", None)
    st.session_state.pop("replies_page_size", None)
    st.rerun()

ticket_id = st.session_state.get("selected_ticket_id")
if not ticket_id:
    st.info(
        "Select a ticket from Ticket List first, or enter Ticket ID above and click Load."
    )
    st.stop()

# ----------------------------
# Load ticket
# ----------------------------
try:
    with st.spinner("Loading ticket..."):
        ticket = api.get_ticket(ticket_id=int(ticket_id))
except ApiError as err:
    show_api_error(err)
    st.stop()

st.subheader(f"Ticket #{ticket['id']}: {ticket['subject']}")
st.write(
    f"**Status:** {ticket['status']} | "
    f"**Priority:** {ticket['priority']} | "
    f"**User ID:** {ticket['user_id']}"
)
st.write("**Description:**")
st.write(ticket["description"])

# ----------------------------
# Admin status update
# ----------------------------
if st.session_state.get("role") == "ADMIN":
    st.markdown("---")
    st.subheader("Admin: Update Status")

    status_options = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
    current_status = ticket.get("status")
    default_index = (
        status_options.index(current_status) if current_status in status_options else 0
    )

    new_status = st.selectbox("New Status", status_options, index=default_index)

    if st.button("Update Status", type="primary"):
        try:
            with st.spinner("Updating status..."):
                res = api.update_status(ticket_id=int(ticket_id), status=new_status)
            st.success(f"Updated status to {res['status']}")
            st.rerun()
        except ApiError as err:
            show_api_error(err)

# ----------------------------
# Replies (supports new envelope: {items, total, page, page_size})
# ----------------------------
st.markdown("---")
st.subheader("Replies")

# Defaults for reply pagination state
st.session_state.setdefault("replies_page", 1)
st.session_state.setdefault("replies_page_size", 20)

rcols = st.columns([1, 1, 2])
replies_page = rcols[0].number_input(
    "Replies Page",
    min_value=1,
    value=int(st.session_state["replies_page"]),
    step=1,
)
replies_page_size = rcols[1].selectbox(
    "Replies Page Size",
    [10, 20, 50, 100],
    index=[10, 20, 50, 100].index(int(st.session_state["replies_page_size"])),
)
refresh = rcols[2].button("Refresh Replies")

# persist
st.session_state["replies_page"] = int(replies_page)
st.session_state["replies_page_size"] = int(replies_page_size)

try:
    with st.spinner("Loading replies..."):
        # Works with updated api_client that accepts page/page_size,
        # and also works if api_client ignores extra params (but your new client should accept them).
        replies_data = api.list_replies(
            ticket_id=int(ticket_id),
            page=int(st.session_state["replies_page"]),
            page_size=int(st.session_state["replies_page_size"]),
        )
except TypeError:
    # Backward compatibility: if api_client.list_replies(ticket_id) only accepts ticket_id
    try:
        with st.spinner("Loading replies..."):
            replies_data = api.list_replies(ticket_id=int(ticket_id))
    except ApiError as err:
        show_api_error(err)
        st.stop()
except ApiError as err:
    show_api_error(err)
    st.stop()

# Normalize response:
# - NEW backend: dict with "items"
# - OLD backend: list
if isinstance(replies_data, dict):
    items = replies_data.get("items", [])
    total = replies_data.get("total", len(items))
else:
    items = replies_data
    total = len(items)

st.caption(f"Total replies: {total}")

if not items:
    st.info("No replies yet.")
else:
    for r in items:
        with st.container(border=True):
            created_at = r.get("created_at", "")
            st.caption(
                f"Reply #{r['id']} | Author: {r['author_id']} | At: {created_at}"
            )
            st.write(r["message"])

# Simple Prev/Next
nav_cols = st.columns([1, 1, 3])
prev_disabled = st.session_state["replies_page"] <= 1
next_disabled = isinstance(replies_data, dict) and (
    st.session_state["replies_page"] * st.session_state["replies_page_size"] >= total
)

if nav_cols[0].button("⬅ Prev", disabled=prev_disabled):
    st.session_state["replies_page"] -= 1
    st.rerun()

if nav_cols[1].button("Next ➡", disabled=next_disabled):
    st.session_state["replies_page"] += 1
    st.rerun()

# ----------------------------
# Add reply
# ----------------------------
st.markdown("### Add Reply")
msg = st.text_area("Message", height=120)

send_disabled = not msg.strip()
if st.button("Send Reply", type="primary", disabled=send_disabled):
    try:
        with st.spinner("Posting reply..."):
            api.create_reply(ticket_id=int(ticket_id), message=msg.strip())
        st.success("Reply posted.")
        # After posting, jump to last page (optional). Here we just refresh from page 1.
        st.rerun()
    except ApiError as err:
        show_api_error(err)
