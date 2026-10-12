from repositories import users as user_repo
from utils.errors import NotFoundError, ValidationError

def get_user(user_id: int) -> dict:
    """Retrieve a user by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user record as a dictionary.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    user = user_repo.find_by_id(user_id)
    if user is None:
        raise NotFoundError("User")
    return user

def create_user(name: str, email: str) -> dict:
    """Create a new user.

    Args:
        name: The user's display name.
        email: The user's email address.

    Returns:
        The newly created user record.

    Raises:
        ValidationError: If name or email is empty.
    """
    if not name or not name.strip():
        raise ValidationError("name", "cannot be empty")
    if not email or "@" not in email:
        raise ValidationError("email", "must be a valid email address")
    return user_repo.insert(name, email)

def list_users() -> list[dict]:
    """Retrieve all users.

    Returns:
        A list of all user records.
    """
    return user_repo.find_all()

def get_notification_pref(user_id: int) -> str:
    """Retrieve a user's notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user's notification preference.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    user = user_repo.find_by_id(user_id)
    if user is None:
        raise NotFoundError("User")
    return user["notification_pref"]

def update_notification_pref(user_id: int, pref: str) -> dict:
    """Update a user's notification preference.

    Args:
        user_id: The unique identifier for the user.
        pref: The new notification preference. Must be "email", "sms", or "none".

    Returns:
        The updated user record.

    Raises:
        ValidationError: If pref is not "email", "sms", or "none".
        NotFoundError: If no user exists with the given ID.
    """
    if pref not in ("email", "sms", "none"):
        raise ValidationError("notification_pref", "must be 'email', 'sms', or 'none'")
    user = user_repo.update_notification_pref(user_id, pref)
    if user is None:
        raise NotFoundError("User")
    return user
