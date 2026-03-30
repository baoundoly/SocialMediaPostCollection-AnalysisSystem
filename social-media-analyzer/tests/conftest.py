import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.models.role import Role
from app.models.platform import Platform
from app.models.user import User
from app.core.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try: yield db
    finally: db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        if db.query(Role).count() == 0:
            db.add_all([Role(id=1, name="admin", description="Administrator"),
                        Role(id=2, name="analyst", description="Analyst"),
                        Role(id=3, name="viewer", description="Viewer")])
            db.commit()
        if db.query(Platform).count() == 0:
            db.add_all([Platform(id=1, name="facebook", base_api_url="https://graph.facebook.com"),
                        Platform(id=2, name="youtube", base_api_url="https://www.googleapis.com"),
                        Platform(id=3, name="twitter", base_api_url="https://api.twitter.com"),
                        Platform(id=4, name="reddit", base_api_url="https://oauth.reddit.com")])
            db.commit()
        if db.query(User).filter(User.email == "admin@test.com").count() == 0:
            db.add(User(full_name="Admin Test", email="admin@test.com",
                        password_hash=get_password_hash("testpass123"), role_id=1))
            db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try: yield db
    finally: db.close()

@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def admin_token(client):
    response = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "testpass123"})
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="session")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
