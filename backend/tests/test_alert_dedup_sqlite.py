from datetime import datetime, timezone, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.services.alerting import upsert_dedup_alert


def test_upsert_dedup_alert_sqlite_window():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        a1 = upsert_dedup_alert(
            db=db,
            src_ip="1.2.3.4",
            fingerprint="fp1",
            alert_type="attacker.high_risk",
            level="high",
            title="High risk",
            evidence={"k": 1},
            window_minutes=10,
        )
        assert a1.hit_count == 1

        a2 = upsert_dedup_alert(
            db=db,
            src_ip="1.2.3.4",
            fingerprint="fp1",
            alert_type="attacker.high_risk",
            level="high",
            title="High risk",
            evidence={"k": 2},
            window_minutes=10,
        )
        assert a2.id == a1.id
        assert a2.hit_count == 2
        assert a2.evidence["k"] == 2

        # simulate old window_end
        a2.window_end = datetime.now(timezone.utc) - timedelta(minutes=20)
        db.commit()

        a3 = upsert_dedup_alert(
            db=db,
            src_ip="1.2.3.4",
            fingerprint="fp1",
            alert_type="attacker.high_risk",
            level="high",
            title="High risk",
            evidence={"k": 3},
            window_minutes=10,
        )
        assert a3.id != a1.id
        assert a3.hit_count == 1
    finally:
        db.close()