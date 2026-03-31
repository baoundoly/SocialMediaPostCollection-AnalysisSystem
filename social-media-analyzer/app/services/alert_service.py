from sqlalchemy.orm import Session
from app.models.alert import Alert
from typing import List

class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, alert_type, message, severity="info", reference_id=None):
        alert = Alert(alert_type=alert_type, message=message, severity=severity, reference_id=reference_id)
        self.db.add(alert); self.db.commit(); self.db.refresh(alert)
        return alert

    def get_unread_alerts(self):
        return self.db.query(Alert).filter(Alert.is_read == False).order_by(Alert.created_at.desc()).all()

    def mark_read(self, alert_id):
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert: return False
        alert.is_read = True; self.db.commit()
        return True
