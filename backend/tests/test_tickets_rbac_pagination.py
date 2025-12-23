def _signup(client, email, password="password123"):
    return client.post("/auth/signup", json={"email": email, "password": password})


def _login(client, email, password="password123"):
    return client.post("/auth/login", json={"email": email, "password": password}).json()[
        "access_token"
    ]


def test_user_can_create_and_list_own_tickets(client):
    _signup(client, "u1@example.com")
    token = _login(client, "u1@example.com")

    # Create 3 tickets
    for i in range(3):
        r = client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {token}"},
            json={"subject": f"Subject {i}", "description": "desc " * 5, "priority": "LOW"},
        )
        assert r.status_code == 201

    r = client.get("/tickets?page=1&page_size=10", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()

    assert set(body.keys()) == {"items", "page", "page_size", "total"}
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_user_cannot_access_others_ticket(client):
    _signup(client, "u1@example.com")
    _signup(client, "u2@example.com")
    t1 = _login(client, "u1@example.com")
    t2 = _login(client, "u2@example.com")

    created = client.post(
        "/tickets",
        headers={"Authorization": f"Bearer {t1}"},
        json={"subject": "A subject", "description": "desc " * 5, "priority": "MEDIUM"},
    ).json()

    r = client.get(f"/tickets/{created['id']}", headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 403


def test_pagination_works(client):
    _signup(client, "u1@example.com")
    token = _login(client, "u1@example.com")

    for i in range(15):
        client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {token}"},
            json={"subject": f"S{i}", "description": "desc " * 5, "priority": "HIGH"},
        )

    r = client.get("/tickets?page=1&page_size=10", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 15
    assert len(body["items"]) == 10

    r2 = client.get("/tickets?page=2&page_size=10", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    body2 = r2.json()
    assert len(body2["items"]) == 5
