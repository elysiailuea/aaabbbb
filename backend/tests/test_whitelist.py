from backend.app.services.net import ip_in_csv_whitelist


def test_whitelist_single_ip():
    assert ip_in_csv_whitelist("127.0.0.1", "127.0.0.1") is True
    assert ip_in_csv_whitelist("127.0.0.2", "127.0.0.1") is False


def test_whitelist_cidr():
    assert ip_in_csv_whitelist("192.168.1.20", "192.168.0.0/16") is True
    assert ip_in_csv_whitelist("10.0.0.5", "192.168.0.0/16") is False