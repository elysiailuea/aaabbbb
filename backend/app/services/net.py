import ipaddress


def ip_in_csv_whitelist(ip: str, csv: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip)
    except Exception:
        return False

    for part in [p.strip() for p in (csv or "").split(",") if p.strip()]:
        try:
            if "/" in part:
                net = ipaddress.ip_network(part, strict=False)
                if ip_obj in net:
                    return True
            else:
                if ip_obj == ipaddress.ip_address(part):
                    return True
        except Exception:
            continue
    return False