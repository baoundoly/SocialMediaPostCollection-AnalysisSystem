def test_register(client):
    response = client.post("/api/auth/register", json={"full_name": "Test User", "email": "testregister@test.com", "password": "password123", "role_id": 3})
    assert response.status_code == 200
    assert response.json()["email"] == "testregister@test.com"

def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={"full_name": "Dup User", "email": "dup@test.com", "password": "password123"})
    response = client.post("/api/auth/register", json={"full_name": "Dup User2", "email": "dup@test.com", "password": "password456"})
    assert response.status_code == 400

def test_login_success(client):
    response = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "testpass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_get_me(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"

def test_get_me_no_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 403

def test_admin_access_users(client, auth_headers):
    response = client.get("/api/users", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_viewer_cannot_access_users(client):
    client.post("/api/auth/register", json={"full_name": "Viewer", "email": "viewer@test.com", "password": "viewerpass", "role_id": 3})
    login_resp = client.post("/api/auth/login", json={"email": "viewer@test.com", "password": "viewerpass"})
    token = login_resp.json()["access_token"]
    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
