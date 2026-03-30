def test_dashboard_overview(client, auth_headers):
    response = client.get("/api/dashboard/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_posts" in data and "platform_breakdown" in data

def test_dashboard_sentiment(client, auth_headers):
    response = client.get("/api/dashboard/sentiment?days=7", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_dashboard_keywords(client, auth_headers):
    response = client.get("/api/dashboard/keywords?top_n=10", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_dashboard_top_posts(client, auth_headers):
    response = client.get("/api/dashboard/top-posts?limit=5", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_daily_report(client, auth_headers):
    response = client.get("/api/reports/daily", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_posts" in data and "sentiments" in data

def test_weekly_report(client, auth_headers):
    response = client.get("/api/reports/weekly", headers=auth_headers)
    assert response.status_code == 200
    assert "total_posts" in response.json()

def test_export_csv(client, auth_headers):
    response = client.get("/api/reports/export/csv", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
