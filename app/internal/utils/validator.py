from ipaddress import ip_address


def validate_ip_address(ip_str: str) -> bool:
    """
    Validate the given IP address syntatically.
    """

    try:
        _ = ip_address(ip_str)
    except ValueError:
        return False
    return True
