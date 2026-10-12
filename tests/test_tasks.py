import pytest
from services.tasks import process_order, get_task, get_tasks_for_user
from services.tasks import create_task
from services.tasks import update_task_priority
from services.tasks import list_tasks
from utils.errors import ValidationError
from utils.errors import NotFoundError

def test_process_order_valid():
    result = process_order(1)
    assert result["done"] is True

def test_process_order_invalid():
    with pytest.raises(Exception):
        process_order(999)

def test_get_task_valid():
    result = get_task(2)
    assert result["title"] == "Write report"

def test_get_task_invalid():
    with pytest.raises(Exception):
        get_task(999)


def test_get_tasks_for_user_with_tasks() -> None:
    """User 1 owns tasks 1 and 2, so both are returned."""
    result = get_tasks_for_user(1)
    assert sorted(task["id"] for task in result) == [1, 2]
    assert all(task["user_id"] == 1 for task in result)


def test_get_tasks_for_user_with_no_tasks() -> None:
    """A user ID that owns no tasks gets an empty list, not an error."""
    result = get_tasks_for_user(999)
    assert result == []


def test_create_task_default_priority() -> None:
    """Omitting priority defaults the new task to priority 3."""
    result = create_task("Test task", 1)
    assert result["priority"] == 3


def test_create_task_explicit_priority() -> None:
    """An explicit, valid priority is stored as given."""
    result = create_task("Urgent task", 1, priority=1)
    assert result["priority"] == 1


def test_create_task_invalid_priority() -> None:
    """A priority outside 1-5 is rejected."""
    with pytest.raises(ValidationError):
        create_task("Bad priority task", 1, priority=6)


def test_create_task_invalid_priority_type() -> None:
    """A non-integer priority is rejected."""
    with pytest.raises(ValidationError):
        create_task("Bad priority type task", 1, priority="urgent")


def test_update_task_priority_valid() -> None:
    """A valid priority update is persisted and returned."""
    task = create_task("Task to update", 1)
    result = update_task_priority(task["id"], 2)
    assert result["priority"] == 2


def test_update_task_priority_invalid_range() -> None:
    """A priority outside 1-5 is rejected."""
    task = create_task("Task with bad range update", 1)
    with pytest.raises(ValidationError):
        update_task_priority(task["id"], 6)


def test_update_task_priority_invalid_type() -> None:
    """A non-integer priority is rejected."""
    task = create_task("Task with bad type update", 1)
    with pytest.raises(ValidationError):
        update_task_priority(task["id"], "urgent")


def test_update_task_priority_not_found() -> None:
    """Updating a nonexistent task raises NotFoundError."""
    with pytest.raises(NotFoundError):
        update_task_priority(999, 2)


def test_list_tasks_all() -> None:
    """With no filter, the seeded tasks are included among the results."""
    result = list_tasks()
    result_ids = {task["id"] for task in result}
    assert {1, 2, 3}.issubset(result_ids)


def test_list_tasks_filtered_by_priority() -> None:
    """Filtering by priority returns only tasks with that exact priority."""
    high = create_task("High priority task", 1, priority=5)
    low = create_task("Low priority task", 1, priority=1)
    result = list_tasks(5)
    result_ids = [task["id"] for task in result]
    assert high["id"] in result_ids
    assert low["id"] not in result_ids
    assert all(task["priority"] == 5 for task in result)


def test_list_tasks_filter_excludes_other_priorities() -> None:
    """A task is excluded from the results when its priority doesn't match the filter."""
    task = create_task("Medium priority task", 1, priority=2)
    result = list_tasks(4)
    assert task["id"] not in [t["id"] for t in result]


def test_list_tasks_invalid_priority_range() -> None:
    """A priority outside 1-5 is rejected."""
    with pytest.raises(ValidationError):
        list_tasks(6)


def test_list_tasks_invalid_priority_type() -> None:
    """A non-integer priority is rejected."""
    with pytest.raises(ValidationError):
        list_tasks("high")


def test_list_tasks_includes_newly_created_tasks() -> None:
    """Creating a task grows the task list by one and includes the new task."""
    before_count = len(list_tasks())
    task = create_task("New task for list test", 1, priority=4)
    after = list_tasks()
    assert len(after) == before_count + 1
    all_ids = [t["id"] for t in after]
    assert task["id"] in all_ids
    filtered_ids = [t["id"] for t in list_tasks(4)]
    assert task["id"] in filtered_ids
