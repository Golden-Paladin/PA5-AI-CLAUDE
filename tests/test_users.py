import pytest
from services.users import (
    list_users,
    get_notification_pref,
    update_notification_pref,
    create_user,
    get_user,
)
from utils.errors import NotFoundError, ValidationError


def test_create_user_defaults_notification_pref_to_none() -> None:
    """A newly created user's notification_pref defaults to 'none'."""
    user = create_user("Test User", "test.user@example.com")
    assert user["notification_pref"] == "none"


def test_update_notification_pref_email() -> None:
    """Updating a user's preference to 'email' is stored and returned."""
    user = create_user("Email User", "email.user@example.com")
    result = update_notification_pref(user["id"], "email")
    assert result["notification_pref"] == "email"


def test_update_notification_pref_sms() -> None:
    """Updating a user's preference to 'sms' is stored and returned."""
    user = create_user("Sms User", "sms.user@example.com")
    result = update_notification_pref(user["id"], "sms")
    assert result["notification_pref"] == "sms"


def test_update_notification_pref_none() -> None:
    """Updating a user's preference to 'none' is stored and returned."""
    user = create_user("None User", "none.user@example.com")
    result = update_notification_pref(user["id"], "none")
    assert result["notification_pref"] == "none"


def test_update_notification_pref_invalid_value() -> None:
    """An invalid preference value raises ValidationError."""
    user = create_user("Invalid Pref User", "invalid.pref@example.com")
    with pytest.raises(ValidationError):
        update_notification_pref(user["id"], "pager")


def test_update_notification_pref_missing_user() -> None:
    """Updating the preference of a missing user raises NotFoundError."""
    with pytest.raises(NotFoundError):
        update_notification_pref(999, "email")


def test_get_notification_pref_missing_user() -> None:
    """Reading the preference of a missing user raises NotFoundError."""
    with pytest.raises(NotFoundError):
        get_notification_pref(999)


def test_get_user_includes_notification_pref() -> None:
    """get_user's returned record includes notification_pref."""
    user = create_user("Get User", "get.user@example.com")
    result = get_user(user["id"])
    assert "notification_pref" in result


def test_list_users_every_record_includes_notification_pref() -> None:
    """Every record from list_users includes notification_pref."""
    create_user("List User", "list.user@example.com")
    result = list_users()
    assert len(result) > 0
    assert all("notification_pref" in user for user in result)
