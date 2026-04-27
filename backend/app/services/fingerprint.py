import hashlib


def _h(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def make_http_fingerprint(ua: str, top_paths: list[str], peak_rpm: int) -> str:
    base = f"http|ua={ua}|paths={','.join(top_paths[:5])}|rpm={peak_rpm//10}"
    return _h(base)


def make_ssh_fingerprint(top_users: list[str], peak_rpm: int) -> str:
    base = f"ssh|users={','.join(top_users[:5])}|rpm={peak_rpm//10}"
    return _h(base)