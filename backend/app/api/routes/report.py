from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.api.deps import get_db, require_user
from backend.app.models.profile import AttackerProfile
from backend.app.models.alert import Alert
from backend.app.models.ban import BanRecord
from backend.app.models.event import Event

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/ip/{ip}")
def export_ip_report(ip: str, hours: int = 24, user=Depends(require_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)

    prof = db.execute(select(AttackerProfile).where(AttackerProfile.src_ip == ip)).scalar_one_or_none()
    alerts = db.execute(select(Alert).where(Alert.src_ip == ip).order_by(Alert.window_end.desc()).limit(200)).scalars().all()
    bans = db.execute(select(BanRecord).where(BanRecord.src_ip == ip).order_by(BanRecord.created_at.desc()).limit(50)).scalars().all()
    events = db.execute(select(Event).where(and_(Event.src_ip == ip, Event.ts >= since)).order_by(Event.ts.desc()).limit(500)).scalars().all()

    return {
        "generated_at": now.isoformat(),
        "range_hours": hours,
        "ip": ip,
        "profile": None if not prof else {
            "src_ip": prof.src_ip,
            "first_seen": prof.first_seen,
            "last_seen": prof.last_seen,
            "http_count_1h": prof.http_count_1h,
            "ssh_fail_count_1h": prof.ssh_fail_count_1h,
            "peak_rpm_1h": prof.peak_rpm_1h,
            "risk_score": prof.risk_score,
            "risk_level": prof.risk_level,
            "risk_reasons": (prof.risk_reasons or {}).get("reasons", []),
            "fingerprint": prof.fingerprint,
            "top_paths": prof.top_paths,
            "top_usernames": prof.top_usernames,
        },
        "alerts": [
            {
                "id": a.id,
                "type": a.alert_type,
                "level": a.level,
                "status": a.status,
                "title": a.title,
                "window_start": a.window_start,
                "window_end": a.window_end,
                "hit_count": a.hit_count,
                "fingerprint": a.fingerprint,
                "evidence": a.evidence,
            }
            for a in alerts
        ],
        "bans": [
            {
                "id": b.id,
                "src_ip": b.src_ip,
                "level": b.level,
                "reason": b.reason,
                "status": b.status,
                "created_at": b.created_at,
                "expires_at": b.expires_at,
                "created_by": b.created_by,
                "evidence": b.evidence,
            }
            for b in bans
        ],
        "recent_events": [
            {
                "id": e.id,
                "ts": e.ts,
                "protocol": e.protocol,
                "event_type": e.event_type,
                "payload": e.payload,
                "honeypot": {"name": e.honeypot_name, "instance_id": e.honeypot_instance_id},
            }
            for e in events
        ],
    }


@router.get("/ip/{ip}/html")
def export_ip_report_html(ip: str, hours: int = 24, user=Depends(require_user), db: Session = Depends(get_db)):
    data = export_ip_report(ip=ip, hours=hours, user=user, db=db)
    now = data["generated_at"]
    prof = data["profile"] or {}
    reasons = prof.get("risk_reasons", [])

    def esc(s):
        return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html = f"""
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>调查报告 - {esc(ip)}</title>
<style>
body {{ font-family: Arial, "Microsoft YaHei", sans-serif; background:#f6f7fb; margin:0; }}
.container {{ max-width: 1100px; margin: 18px auto; padding: 0 12px; }}
.card {{ background:#fff; border:1px solid #e9e9e9; border-radius:8px; padding:14px; margin-bottom:12px; }}
h1,h2 {{ margin: 0 0 10px 0; }}
table {{ border-collapse: collapse; width:100%; }}
th,td {{ border:1px solid #eee; padding:8px; text-align:left; vertical-align:top; }}
.tag {{ display:inline-block; padding:3px 8px; border-radius:999px; background:#fff7e6; border:1px solid #ffd591; margin: 4px 6px 0 0; }}
.small {{ color:#666; font-size: 12px; }}
pre {{ background:#111; color:#ddd; padding:10px; border-radius:6px; overflow:auto; }}
</style>
</head>
<body>
<div class="container">
  <div class="card">
    <h1>攻击者调查报告</h1>
    <div class="small">IP：<b>{esc(ip)}</b> ｜ 生成时间：{esc(now)} ｜ 时间范围：近 {esc(hours)} 小时</div>
  </div>

  <div class="card">
    <h2>画像概要</h2>
    <table>
      <tr><th>风险等级</th><td>{esc(prof.get("risk_level",""))}</td><th>风险评分</th><td>{esc(prof.get("risk_score",""))}</td></tr>
      <tr><th>首次出现</th><td>{esc(prof.get("first_seen",""))}</td><th>最近出现</th><td>{esc(prof.get("last_seen",""))}</td></tr>
      <tr><th>HTTP(1h)</th><td>{esc(prof.get("http_count_1h",""))}</td><th>SSH失败(1h)</th><td>{esc(prof.get("ssh_fail_count_1h",""))}</td></tr>
      <tr><th>峰值RPM(1h)</th><td>{esc(prof.get("peak_rpm_1h",""))}</td><th>指纹</th><td>{esc(prof.get("fingerprint",""))}</td></tr>
    </table>

    <div style="margin-top:10px;">
      <div><b>命中规则/评分原因：</b></div>
      {"".join([f'<span class="tag">{esc(r)}</span>' for r in reasons]) or '<span class="small">（无）</span>'}
    </div>
  </div>

  <div class="card">
    <h2>告警（最近 200 条）</h2>
    <table>
      <tr><th>时间窗结束</th><th>级别</th><th>状态</th><th>标题</th><th>命中次数</th></tr>
      {"".join([f"<tr><td>{esc(a['window_end'])}</td><td>{esc(a['level'])}</td><td>{esc(a['status'])}</td><td>{esc(a['title'])}</td><td>{esc(a['hit_count'])}</td></tr>" for a in data["alerts"]]) or "<tr><td colspan='5' class='small'>（无）</td></tr>"}
    </table>
  </div>

  <div class="card">
    <h2>封禁记录（最近 50 条）</h2>
    <table>
      <tr><th>创建时间</th><th>到期时间</th><th>级别</th><th>状态</th><th>原因</th></tr>
      {"".join([f"<tr><td>{esc(b['created_at'])}</td><td>{esc(b['expires_at'])}</td><td>{esc(b['level'])}</td><td>{esc(b['status'])}</td><td>{esc(b['reason'])}</td></tr>" for b in data["bans"]]) or "<tr><td colspan='5' class='small'>（无）</td></tr>"}
    </table>
  </div>

  <div class="card">
    <h2>最近事件（最多 500 条）</h2>
    <div class="small">为避免报告过大，此处仅展示简要字段；完整字段可导出 JSON。</div>
    <table>
      <tr><th>时间</th><th>协议</th><th>类型</th><th>摘要</th></tr>
      {"".join([
        f"<tr><td>{esc(e['ts'])}</td><td>{esc(e['protocol'])}</td><td>{esc(e['event_type'])}</td><td>{esc((e.get('payload') or {}).get('path') or (e.get('payload') or {}).get('username') or '')}</td></tr>"
        for e in data["recent_events"]
      ]) or "<tr><td colspan='4' class='small'>（无）</td></tr>"}
    </table>
  </div>

  <div class="card">
    <div class="small">本报告由“蜜罐联动防护平台”自动生成，用于安全分析与取证展示。</div>
  </div>
</div>
</body>
</html>
"""
    return HTMLResponse(content=html, headers={"Content-Disposition": f'attachment; filename="report-{ip}.html"'})