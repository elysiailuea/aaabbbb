def score_profile(
    http_count_1h: int,
    ssh_fail_1h: int,
    peak_rpm_1h: int,
    top_paths: list[str],
    top_users: list[str],
    *,
    sensitive_paths: list[str],
) -> tuple[int, str, list[str]]:
    score = 0
    reasons: list[str] = []

    if any(p in top_paths for p in sensitive_paths):
        score += 35
        reasons.append("命中敏感路径特征")

    if peak_rpm_1h > 120:
        score += 25
        reasons.append("高频扫描：请求速率 > 120 rpm")
    elif peak_rpm_1h > 30:
        score += 10
        reasons.append("中等频率：请求速率 30-120 rpm")

    if http_count_1h > 500:
        score += 15
        reasons.append("HTTP 总量高：> 500 次/小时")

    if ssh_fail_1h >= 20:
        score += 35
        reasons.append("SSH 爆破阈值：失败登录 >= 20 次/小时")
    elif ssh_fail_1h >= 5:
        score += 10
        reasons.append("存在 SSH 失败登录")

    if any(u in ["root", "admin", "test", "oracle"] for u in top_users):
        score += 10
        reasons.append("命中高危用户名（root/admin/test/oracle）")

    score = min(score, 100)

    if score >= 80:
        level = "critical"
    elif score >= 60:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    return score, level, reasons