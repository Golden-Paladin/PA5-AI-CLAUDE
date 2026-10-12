USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "notification_pref": "none"},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "notification_pref": "none"},
}

def find_by_id(user_id: int) -> dict | None:
    """Look up a user record by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user record, or None if no user has that ID.
    """
    return USERS.get(user_id)

def insert(name: str, email: str) -> dict:
    """Store a new user record with the next free ID.

    Args:
        name: The user's display name.
        email: The user's email address.

    Returns:
        The stored user record.
    """
    new_id = max(USERS.keys()) + 1
    USERS[new_id] = {"id": new_id, "name": name, "email": email, "notification_pref": "none"}
    return USERS[new_id]

def find_all() -> list[dict]:
    """Return every user record.

    Returns:
        A list of all user records.
    """
    return list(USERS.values())

def update_notification_pref(user_id: int, pref: str) -> dict | None:
    """Update the notification preference of an existing user record.

    Args:
        user_id: The unique identifier for the user.
        pref: The new notification preference value to store.

    Returns:
        The updated user record, or None if no user has that ID.
    """
    user = USERS.get(user_id)
    if user is None:
        return None
    user["notification_pref"] = pref
    return user
