from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(255), nullable=False)
    entity_type = Column(String(50))  # PERSON, ORG, LOCATION
