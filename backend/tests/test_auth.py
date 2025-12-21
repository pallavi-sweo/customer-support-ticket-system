def test_signup_and_login_success(client):
    r = client.post("/auth/signup", json={"email": "u1@example.com", "password": "password123"})
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "u1@example.com"
    assert body["role"] == "USER"

    r = client.post("/auth/login", json={"email": "u1@example.com", "password": "password123"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["role"] == "USER"


def test_signup_duplicate_email(client):
    client.post("/auth/signup", json={"email": "u2@example.com", "password": "password123"})
    r = client.post("/auth/signup", json={"email": "u2@example.com", "password": "password123"})
    assert r.status_code == 409


def test_login_invalid_credentials(client):
    client.post("/auth/signup", json={"email": "u3@example.com", "password": "password123"})
    r = client.post("/auth/login", json={"email": "u3@example.com", "password": "wrongpass123"})
    assert r.status_code == 401
