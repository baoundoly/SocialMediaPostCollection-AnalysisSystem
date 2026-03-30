from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.source import SourceConfigCreate, SourceConfigUpdate, SourceConfigOut
from app.models.source_config import SourceConfig
from app.core.security import encrypt_value
from app.api.deps import get_current_user, require_analyst
from app.models.user import User

router = APIRouter(prefix="/api/sources", tags=["sources"])

@router.get("", response_model=List[SourceConfigOut])
def list_sources(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(SourceConfig).all()

@router.post("", response_model=SourceConfigOut)
def create_source(payload: SourceConfigCreate, db: Session = Depends(get_db), _: User = Depends(require_analyst)):
    sc = SourceConfig(
        platform_id=payload.platform_id,
        source_type=payload.source_type,
        keyword=payload.keyword,
        account_name=payload.account_name,
        page_name=payload.page_name,
        api_key_encrypted=encrypt_value(payload.api_key) if payload.api_key else None,
        access_token_encrypted=encrypt_value(payload.access_token) if payload.access_token else None,
    )
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc

@router.put("/{source_id}", response_model=SourceConfigOut)
def update_source(source_id: int, payload: SourceConfigUpdate, db: Session = Depends(get_db), _: User = Depends(require_analyst)):
    sc = db.query(SourceConfig).filter(SourceConfig.id == source_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Source not found")
    data = payload.model_dump(exclude_none=True)
    if "api_key" in data:
        sc.api_key_encrypted = encrypt_value(data.pop("api_key"))
    if "access_token" in data:
        sc.access_token_encrypted = encrypt_value(data.pop("access_token"))
    for field, value in data.items():
        setattr(sc, field, value)
    db.commit()
    db.refresh(sc)
    return sc

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db), _: User = Depends(require_analyst)):
    sc = db.query(SourceConfig).filter(SourceConfig.id == source_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(sc)
    db.commit()
    return {"detail": "Source deleted"}
