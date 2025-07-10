import pwd

def get_uid(username: str) -> int:
    """Get the UID for a given username."""
    return pwd.getpwnam(username).pw_uid
