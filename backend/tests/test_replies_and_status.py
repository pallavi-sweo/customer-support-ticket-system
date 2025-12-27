def _signup(client, email, password="password123"):
    return client.post("/auth/signup", json={"email": email, "password": password})


def _login(client, email, password="password123"):
    return client.post(
        "/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]


def _create_ticket(client, token, i=1):
    r = client.post(
        "/tickets",
        headers={"Authorization": f"Bearer {token}"},
        json={"subject": f"Sub {i}", "description": "desc " * 5, "priority": "MEDIUM"},
    )
    assert r.status_code == 201
    return r.json()


def test_user_can_reply_to_own_ticket_and_list_thread(client):
    _signup(client, "u1@example.com")
    token = _login(client, "u1@example.com")

    ticket = _create_ticket(client, token, 1)

    r = client.post(
        f"/tickets/{ticket['id']}/replies",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Hello support"},
    )
    assert r.status_code == 201
    reply = r.json()
    assert reply["ticket_id"] == ticket["id"]

    r2 = client.get(
        f"/tickets/{ticket['id']}/replies",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    thread = r2.json()
    assert len(thread) == 1
    assert thread[0]["message"] == "Hello support"


def test_user_cannot_reply_to_others_ticket(client):
    _signup(client, "u1@example.com")
    _signup(client, "u2@example.com")
    t1 = _login(client, "u1@example.com")
    t2 = _login(client, "u2@example.com")

    ticket = _create_ticket(client, t1, 1)

    r = client.post(
        f"/tickets/{ticket['id']}/replies",
        headers={"Authorization": f"Bearer {t2}"},
        json={"message": "I should not be able to reply"},
    )
    assert r.status_code == 403


def test_admin_can_update_status_with_valid_transitions(client, db_session):
    # Create admin via signup then manually elevate role is not supported.
    # For tests we call signup then directly login, and assume role=USER.
    # So, we simulate admin by setting bootstrap env in real app, but in tests we need a way.
    # Easiest: create admin using /auth/signup by temporarily allowing role, or insert directly via DB.
    # We'll insert directly via DB here using SQLite test DB override.

    from sqlalchemy import select
    from app.core.security import hash_password
    from app.models.user import User
    from app.db import session as session_module

    # Access the override DB session generator by calling it once
    existing = db_session.scalar(select(User).where(User.email == "admin@example.com"))
    if not existing:
        admin = User(
            email="admin@example.com",
            password_hash=hash_password("admin12345"),
            role="ADMIN",
        )
        db_session.add(admin)
        db_session.commit()

    # Login as admin (login expects JSON in your Day1 setup)
    admin_token = client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "admin12345"}
    ).json()["access_token"]

    _signup(client, "u1@example.com")
    user_token = _login(client, "u1@example.com")
    ticket = _create_ticket(client, user_token, 1)

    # OPEN -> IN_PROGRESS
    r = client.put(
        f"/admin/tickets/{ticket['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "IN_PROGRESS"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"

    # IN_PROGRESS -> RESOLVED
    r2 = client.put(
        f"/admin/tickets/{ticket['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "RESOLVED"

    # RESOLVED -> CLOSED
    r3 = client.put(
        f"/admin/tickets/{ticket['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "CLOSED"},
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "CLOSED"


def test_invalid_transition_returns_400(client, db_session):
    from app.core.security import hash_password
    from app.models.user import User
    from sqlalchemy import select

    existing = db_session.scalar(select(User).where(User.email == "admin2@example.com"))
    if not existing:
        admin = User(
            email="admin2@example.com",
            password_hash=hash_password("admin12345"),
            role="ADMIN",
        )
        db_session.add(admin)
        db_session.commit()

    admin_token = client.post(
        "/auth/login", json={"email": "admin2@example.com", "password": "admin12345"}
    ).json()["access_token"]

    _signup(client, "u1@example.com")
    user_token = _login(client, "u1@example.com")
    ticket = _create_ticket(client, user_token, 1)

    # OPEN -> RESOLVED is invalid by our rules
    r = client.put(
        f"/admin/tickets/{ticket['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert r.status_code == 400


def test_non_admin_cannot_update_status(client):
    _signup(client, "u1@example.com")
    token = _login(client, "u1@example.com")
    ticket = _create_ticket(client, token, 1)

    r = client.put(
        f"/admin/tickets/{ticket['id']}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "IN_PROGRESS"},
    )
    assert r.status_code == 403
