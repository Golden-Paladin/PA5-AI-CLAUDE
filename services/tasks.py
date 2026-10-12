from repositories import tasks as task_repo
from utils.errors import NotFoundError, ValidationError

def process_order(task_id: int) -> dict:
    task = task_repo.find_by_id(task_id)
    if task is None:
        raise NotFoundError("Task")
    task["done"] = True
    return task

def get_task(task_id: int) -> dict:
    """Retrieve a task by ID.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    task = task_repo.find_by_id(task_id)
    if task is None:
        raise NotFoundError("Task")
    return task

def get_tasks_for_user(user_id: int) -> list[dict]:
    """Retrieve all tasks belonging to a given user.

    Args:
        user_id: The unique identifier of the user whose tasks to retrieve.

    Returns:
        A list of task records for the user. Empty if the user has no tasks.
    """
    return task_repo.find_by_user(user_id)

def list_tasks(priority: int | None = None) -> list[dict]:
    """Retrieve all tasks, optionally filtered by priority.

    Args:
        priority: If provided, only tasks with this priority are returned.
            Defaults to None (no filtering).

    Returns:
        A list of task records matching the filter. Empty if none match.

    Raises:
        ValidationError: If priority is provided and is not an integer
            between 1 and 5.
    """
    if priority is not None:
        _validate_priority(priority)
    return task_repo.find_all(priority)

def _validate_priority(priority: int) -> None:
    """Validate that a priority value is usable.

    Args:
        priority: The priority value to validate.

    Raises:
        ValidationError: If priority is not an integer between 1 and 5.
    """
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise ValidationError("priority", "must be an integer")
    if priority < 1 or priority > 5:
        raise ValidationError("priority", "must be between 1 and 5")

def create_task(title: str, user_id: int, priority: int = 3) -> dict:
    """Create a new task.

    Args:
        title: The task's title.
        user_id: The unique identifier of the user the task belongs to.
        priority: The task's priority, 1 (urgent) to 5 (low). Defaults to 3.

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is empty, or priority is not an integer
            between 1 and 5.
    """
    if not title or not title.strip():
        raise ValidationError("title", "cannot be empty")
    _validate_priority(priority)
    return task_repo.insert(title, user_id, priority)

def update_task_priority(task_id: int, priority: int) -> dict:
    """Update the priority of an existing task.

    Args:
        task_id: The unique identifier for the task.
        priority: The task's new priority, 1 (urgent) to 5 (low).

    Returns:
        The updated task record.

    Raises:
        ValidationError: If priority is not an integer between 1 and 5.
        NotFoundError: If no task exists with the given ID.
    """
    _validate_priority(priority)
    task = task_repo.update_priority(task_id, priority)
    if task is None:
        raise NotFoundError("Task")
    return task
