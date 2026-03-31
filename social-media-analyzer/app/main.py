from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_auth, routes_users, routes_sources, routes_posts, routes_analysis, routes_reports, routes_dashboard
from app.models import (  # noqa: F401 - import models to register them with SQLAlchemy metadata
    Role, User, Platform, SourceConfig, Post, PostKeyword, PostEntity,
    Comment, PostAnalysis, Keyword, Entity, SyncJob, Alert, AuditLog,
)

app = FastAPI(title="Social Media Post Collection & Analysis System", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(routes_auth.router)
app.include_router(routes_users.router)
app.include_router(routes_sources.router)
app.include_router(routes_posts.router)
app.include_router(routes_analysis.router)
app.include_router(routes_reports.router)
app.include_router(routes_dashboard.router)

@app.on_event("startup")
def startup_event():
    try:
        from app.core.database import create_tables
        create_tables()
        _seed_initial_data()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Startup init failed (may be OK in test env): {e}")

def _seed_initial_data():
    from app.core.database import SessionLocal
    from app.models.role import Role
    from app.models.platform import Platform
    from app.models.user import User
    from app.core.security import get_password_hash
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            db.add_all([Role(id=1, name="admin", description="Administrator"),
                        Role(id=2, name="analyst", description="Analyst"),
                        Role(id=3, name="viewer", description="Viewer")])
            db.commit()
        if db.query(Platform).count() == 0:
            db.add_all([Platform(id=1, name="facebook", base_api_url="https://graph.facebook.com"),
                        Platform(id=2, name="youtube", base_api_url="https://www.googleapis.com/youtube/v3"),
                        Platform(id=3, name="twitter", base_api_url="https://api.twitter.com/2"),
                        Platform(id=4, name="reddit", base_api_url="https://oauth.reddit.com")])
            db.commit()
        if db.query(User).count() == 0:
            db.add(User(full_name="Admin User", email="admin@example.com",
                        password_hash=get_password_hash("admin123"), role_id=1))
            db.commit()
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}
