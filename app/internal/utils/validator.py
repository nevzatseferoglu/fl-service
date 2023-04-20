from ipaddress import ip_address


def validate_ip_address(ip_str: str) -> bool:
    try:
        _ = ip_address(ip_str)
    except ValueError:
        return False
    return True
