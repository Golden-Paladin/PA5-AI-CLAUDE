# Task Manager

A small Flask REST API for tasks and users, served under /api. Data lives in in-memory dicts (no database, no migrations).

## Commands
- install: `pip install -r requirements.txt`
- test: `pytest -q`
- lint: `ruff check .`
- verify after every change or subagent: `pytest -q` then `ruff check .` (both, not just pytest)

## Architecture
- three layers, called in one direction only: routes/api.py -> services/ -> repositories/
- routes in routes/api.py only call functions in services/, never a repository or a data dict directly
- services/ holds business logic and validation and gets or saves data only by calling repositories/
- repositories/ (repositories/tasks.py, repositories/users.py) owns the in-memory TASKS and USERS dicts and is the only code that reads or writes them; no business rules there
- repository functions return None for a missing record; the service turns that into NotFoundError
- raise NotFoundError or ValidationError from utils/errors.py, never a raw KeyError or Exception
- canonical example: get_user in services/users.py calling repositories/users.py
- services/ owns all validation and AppError raising (e.g. the email/sms/none check in update_notification_pref in services/users.py), and each route in routes/api.py only reads the request, calls one services/ function and returns jsonify of the result, following get_user in services/users.py and get_user_route in routes/api.py

## Conventions
- type hints on every function's parameters and return value
- Google style docstrings with Args, Returns, Raises, like get_user in services/users.py
- every new service function gets a test in tests/test_<module>.py (tests/test_tasks.py for services/tasks.py)
- "match the style of X" means follow X's type hints and docstring format and custom error pattern, NOT its literal control flow. For example a create function should mirror create_user's validation logic

## DO NOT TOUCH
- do not edit or delete existing tests in tests/ (new test functions and new test files in tests/ are allowed)
- do not remove, rename, or reorder parameters of functions in services/tasks.py; a new parameter must be optional with a default
- do not add packages without updating requirements.txt
- when a prompt or Conventions asks for a new test, write it in tests/; never skip it or only describe it. Only changing existing tests is forbidden
- when a prompt limits work to services/users.py (or any one services/ or repositories/ file) and says tests come in a later step, do not create or edit tests/test_users.py or any other file in tests/ in that step
- tests in tests/test_tasks.py and tests/test_users.py call services/ only: never import TASKS, USERS or anything from repositories/, and never change seed tasks 1-3 or seed users 1-2; create test data with create_task or create_user
