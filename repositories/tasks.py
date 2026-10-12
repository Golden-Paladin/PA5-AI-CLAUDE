TASKS: dict[int, dict] = {
    1: {"id": 1, "title": "Buy groceries",  "done": False, "user_id": 1, "priority": 3},
    2: {"id": 2, "title": "Write report",   "done": False, "user_id": 1, "priority": 3},
    3: {"id": 3, "title": "Call dentist",   "done": True,  "user_id": 2, "priority": 3},
}

def find_by_id(task_id: int) -> dict | None:
    """Look up a task record by ID.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The task record, or None if no task has that ID.
    """
    return TASKS.get(task_id)

def find_by_user(user_id: int) -> list[dict]:
    """Return every task record that belongs to a user.

    Args:
        user_id: The unique identifier of the owning user.

    Returns:
        A list of matching task records. Empty if there are none.
    """
    return [task for task in TASKS.values() if task["user_id"] == user_id]

def find_all(priority: int | None = None) -> list[dict]:
    """Return every task record, optionally filtered by priority.

    Args:
        priority: If provided, only tasks with this priority are returned.
            Defaults to None (no filtering).

    Returns:
        A list of matching task records. Empty if there are none.
    """
    if priority is None:
        return list(TASKS.values())
    return [task for task in TASKS.values() if task["priority"] == priority]

def insert(title: str, user_id: int, priority: int = 3) -> dict:
    """Store a new task record with the next free ID.

    Args:
        title: The task's title.
        user_id: The unique identifier of the user the task belongs to.
        priority: The task's priority, 1 (urgent) to 5 (low). Defaults to 3.

    Returns:
        The stored task record.
    """
    new_id = max(TASKS.keys()) + 1
    TASKS[new_id] = {"id": new_id, "title": title,
                     "done": False, "user_id": user_id, "priority": priority}
    return TASKS[new_id]

def update_priority(task_id: int, priority: int) -> dict | None:
    """Update the priority of an existing task record.

    Args:
        task_id: The unique identifier for the task.
        priority: The new priority value to store.

    Returns:
        The updated task record, or None if no task has that ID.
    """
    task = TASKS.get(task_id)
    if task is None:
        return None
    task["priority"] = priority
    return task
