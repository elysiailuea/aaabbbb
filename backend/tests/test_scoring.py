from backend.app.services.scoring import score_profile


def test_scoring_sensitive_path_and_high_rate():
    score, level, reasons = score_profile(
        http_count_1h=600,
        ssh_fail_1h=0,
        peak_rpm_1h=200,
        top_paths=["/.env", "/wp-login.php"],
        top_users=[],
        sensitive_paths=["/.env", "/.git/config"],
    )
    assert score >= 70
    assert level in ("high", "critical")
    assert any("敏感路径" in r for r in reasons)
    assert any("高频" in r for r in reasons)


def test_scoring_ssh_bruteforce():
    score, level, reasons = score_profile(
        http_count_1h=0,
        ssh_fail_1h=25,
        peak_rpm_1h=10,
        top_paths=[],
        top_users=["root"],
        sensitive_paths=["/.env"],
    )
    assert score >= 45
    assert level in ("medium", "high", "critical")
    assert any("SSH 爆破" in r for r in reasons)
    assert any("高危用户名" in r for r in reasons)