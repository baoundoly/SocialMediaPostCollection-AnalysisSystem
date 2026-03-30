from app.models.post import Post
from datetime import datetime

def test_get_posts_empty(client, auth_headers):
    response = client.get("/api/posts", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_filter_posts(client, auth_headers, db):
    post = Post(platform_id=1, external_post_id="test-ext-id-001", author_name="Test Author",
                content="This is a test post about technology", posted_at=datetime.utcnow(), likes_count=100)
    db.add(post); db.commit()
    response = client.get("/api/posts/filter?keyword=technology", headers=auth_headers)
    assert response.status_code == 200
    assert any("technology" in (p.get("content") or "").lower() for p in response.json())

def test_get_post_by_id(client, auth_headers, db):
    post = Post(platform_id=1, external_post_id="test-ext-id-002", author_name="Author Two",
                content="Another test post content", posted_at=datetime.utcnow(), likes_count=50)
    db.add(post); db.commit(); db.refresh(post)
    response = client.get(f"/api/posts/{post.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == post.id

def test_get_post_not_found(client, auth_headers):
    response = client.get("/api/posts/999999", headers=auth_headers)
    assert response.status_code == 404

def test_collect_jobs(client, auth_headers):
    response = client.get("/api/collect/jobs", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
