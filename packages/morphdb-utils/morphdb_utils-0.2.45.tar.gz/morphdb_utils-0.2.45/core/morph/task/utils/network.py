import re
import socket


def extract_hostname(hostname):
    pattern = re.compile(
        r"^(vm)-"
        r"([0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12})-"
        r"([a-zA-Z0-9]+)-"
        r"[a-zA-Z0-9]+-"
        r"[a-zA-Z0-9]+$"
    )

    match = pattern.match(hostname)
    if match:
        prefix = match.group(1)
        id = match.group(2)
        val = match.group(3)
        return prefix, id, val
    else:
        return None


def is_cloud():
    hostname = socket.gethostname()
    return extract_hostname(hostname) is not None
