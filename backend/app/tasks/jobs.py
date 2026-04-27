from backend.app.core.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.services.aggregate import aggregate_profiles
from backend.app.services.alerting import process_profiles_to_alerts_and_bans
from backend.app.models.audit import AuditLog


@celery_app.task
def run_aggregation_and_alerts():
    db = SessionLocal()
    try:
        profs = aggregate_profiles(db, window_minutes=60)
        process_profiles_to_alerts_and_bans(db)

        db.add(AuditLog(actor="system", action="jobs.aggregate", detail={"profiles_updated": len(profs)}))
        db.commit()

        return {"ok": True, "profiles_updated": len(profs)}
    finally:
        db.close()