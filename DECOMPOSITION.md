# DECOMPOSITION.md - Task 2: Subagent Pipeline

Feature: user notification preference. A user's `notification_pref` is `email`, `sms` or `none` (default `none`), stored on the user record. `PATCH /users/{id}/notifications` updates it and rejects invalid values with `ValidationError`; `GET /users/{id}/notifications` returns it; the user list and user detail endpoints include it.

Design decisions made before running any subagent:
- task-manager has no database, so the "new nullable column" is a new `notification_pref` key on every record in the in-memory `USERS` dict in repositories/users.py, typed `str | None`. Seed users and new users get `"none"`.
- `GET /users/{id}` (user detail) already returns the stored user dict, so it includes `notification_pref` as soon as the record has it. There is no user list endpoint yet, so SA-3 adds `GET /users`.
- Layer order follows CLAUDE.md: routes/api.py -> services/ -> repositories/. Each subagent owns exactly one layer.

## Subagents

### SA-1: Data layer
| Field | Value |
|---|---|
| Input | repositories/users.py, repositories/tasks.py (pattern for `find_all`), CLAUDE.md |
| Task | Add `notification_pref` storage to user records plus repository functions to list all users and update one user's preference. |
| Output | repositories/users.py (modified only). **pytest -q result:** `20 passed in 0.07s` (fresh session; same 20 as before, no new tests in this layer). `git status` showed only repositories/users.py modified; `ruff check .` clean. |
| Constraint | Do not touch services/users.py, services/tasks.py, routes/api.py, anything in tests/ or repositories/tasks.py. No validation or AppError raising in repositories/users.py. |
| Hand-off | `find_all() -> list[dict]` and `update_notification_pref(user_id: int, pref: str) -> dict \| None` in repositories/users.py; every user record has a `notification_pref` key defaulting to `"none"`. |

Exact prompt:
```
SA-1: Data layer
Input: repositories/users.py, repositories/tasks.py (for the find_all pattern), CLAUDE.md.
Task: In repositories/users.py, add a "notification_pref": "none" key to both seed records in USERS and to the record built by insert (insert's signature stays the same). Add find_all() -> list[dict] that returns every user record, and update_notification_pref(user_id: int, pref: str) -> dict | None that stores pref on the user and returns the updated record, or None if no user has that ID.
Constraints:
- Only modify repositories/users.py.
- Do not touch services/users.py, services/tasks.py, routes/api.py, any file in tests/, or repositories/tasks.py.
- No validation and no AppError raising in the repository.
Output: repositories/users.py only. Run pytest -q at the end and show the result.
Follow all conventions in CLAUDE.md.
```

### SA-2: Service layer
| Field | Value |
|---|---|
| Input | services/users.py, repositories/users.py (SA-1 output), utils/errors.py, CLAUDE.md |
| Task | Add service functions that list users, read a user's preference and validate and update it, raising AppError subclasses. |
| Output | services/users.py (modified only). **pytest -q result:** `20 passed in 0.06s` (fresh session; no new tests, as the constraint required). `git status` showed only services/users.py modified; no tests/test_users.py created despite CLAUDE.md's "every new service function gets a test" convention; `ruff check .` clean. |
| Constraint | Do not touch routes/api.py, any file in repositories/, any file in tests/ or services/tasks.py. Do not change `get_user` or `create_user`. |
| Hand-off | `list_users() -> list[dict]`, `get_notification_pref(user_id: int) -> str` (NotFoundError) and `update_notification_pref(user_id: int, pref: str) -> dict` (ValidationError for anything other than `email`/`sms`/`none`, NotFoundError for a missing user) in services/users.py. |

Exact prompt:
```
SA-2: Service layer
Input: services/users.py, repositories/users.py (which now has find_all() and update_notification_pref(user_id, pref) returning dict | None), utils/errors.py, CLAUDE.md.
Task: In services/users.py, add list_users() -> list[dict] that returns all users; get_notification_pref(user_id: int) -> str that returns the user's notification_pref and raises NotFoundError("User") if the user does not exist; and update_notification_pref(user_id: int, pref: str) -> dict that raises ValidationError("notification_pref", ...) unless pref is exactly "email", "sms", or "none", raises NotFoundError("User") if the user does not exist, and otherwise returns the updated user record. Call only repositories/users.py functions for data.
Constraints:
- Only modify services/users.py.
- Do not touch routes/api.py, any file in repositories/, any file in tests/, or services/tasks.py.
- Do not change get_user or create_user.
- Do not write tests; SA-4 writes them.
Output: services/users.py only. Run pytest -q at the end and show the result.
Follow all conventions in CLAUDE.md.
```

### SA-3: API layer
| Field | Value |
|---|---|
| Input | routes/api.py, services/users.py (SA-2 output), CLAUDE.md |
| Task | Expose the list, read-preference and update-preference endpoints, calling only services/users.py. |
| Output | routes/api.py (modified only). **pytest -q result:** `20 passed in 0.07s` (fresh session). `git status` showed only routes/api.py modified; it imports only from services/, adds the three routes and leaves existing routes unchanged. Gap: the 20 tests call services/ only and Flask is not installed, so this green result does not exercise any route in routes/api.py. |
| Constraint | Do not touch services/users.py, services/tasks.py, any file in repositories/ or any file in tests/. Do not import from repositories/. Do not change existing routes. |
| Hand-off | `GET /users` (list), `GET /users/<id>/notifications` -> `{"notification_pref": ...}`, `PATCH /users/<id>/notifications` with body `{"notification_pref": ...}` -> updated user; errors become 404/422 through the existing `handle_app_error`. |

Exact prompt:
```
SA-3: API layer
Input: routes/api.py, services/users.py (which now has list_users(), get_notification_pref(user_id), and update_notification_pref(user_id, pref)), CLAUDE.md.
Task: In routes/api.py, add GET /users returning list_users(); GET /users/<int:user_id>/notifications returning {"notification_pref": get_notification_pref(user_id)}; and PATCH /users/<int:user_id>/notifications that reads notification_pref from the JSON body with data.get("notification_pref") and returns update_notification_pref(user_id, value). Rely on the existing handle_app_error for 404/422; add no try/except.
Constraints:
- Only modify routes/api.py.
- Do not touch services/users.py, services/tasks.py, any file in repositories/, or any file in tests/.
- Do not import anything from repositories/.
- Do not change existing routes.
Output: routes/api.py only. Run pytest -q at the end and show the result.
Follow all conventions in CLAUDE.md.
```

### SA-4: Tests
| Field | Value |
|---|---|
| Input | services/users.py (SA-2 output), tests/test_tasks.py (style only), utils/errors.py, CLAUDE.md |
| Task | Write tests for the new service functions, covering valid updates, invalid values, missing users, the default and the list. |
| Output | tests/test_users.py (new file). **pytest -q result:** `29 passed in 0.09s` (fresh session; 20 existing + 9 new). `git status` showed only tests/test_users.py added; tests/test_tasks.py unchanged; every update test calls create_user first; `ruff check .` clean. |
| Constraint | Do not edit tests/test_tasks.py or any non-test file (services/, repositories/, routes/api.py). Tests call services/users.py only, never USERS or repositories/users.py directly. Tests that update a preference create their own user with create_user instead of changing seed users 1-2. |
| Hand-off | Green `pytest -q` output for the full suite. |

Exact prompt:
```
SA-4: Tests
Input: services/users.py (list_users, get_notification_pref, update_notification_pref, create_user, get_user), tests/test_tasks.py (for style only), utils/errors.py, CLAUDE.md.
Task: Create tests/test_users.py with tests that: a new user's notification_pref defaults to "none"; update_notification_pref stores each of "email", "sms", and "none"; an invalid value such as "pager" raises ValidationError; updating or reading a missing user raises NotFoundError; get_user and every record from list_users include notification_pref.
Constraints:
- Only create tests/test_users.py.
- Do not edit tests/test_tasks.py or any file in services/, repositories/, or routes/.
- Call service functions only; never import USERS or repositories/users.py.
- Any test that updates a preference must first create its own user with create_user; do not change seed users 1 and 2.
Output: tests/test_users.py only. Run the full pytest -q at the end; every test must pass before you finish.
Follow all conventions in CLAUDE.md.
```

## Divergence

**Did Claude follow the constraint field for every subagent?**

Yes for all four. I checked `git status` and the diff after each subagent: SA-1 changed only repositories/users.py, SA-2 only services/users.py, SA-3 only routes/api.py and SA-4 only added tests/test_users.py. The constraint under the most pressure was SA-2's "Do not write tests; SA-4 writes them", because CLAUDE.md's Conventions say "every new service function gets a test in tests/test_<module>.py". Claude followed the prompt over CLAUDE.md and did not create tests/test_users.py so for that rule the subagent prompt won over the project file. SA-3 also did not import from repositories/ and did not try to start Flask, even though every Task 1 plan (PLAN_LOG.md sessions 1-3) had proposed a `flask run` + curl check.

**Did any subagent's output break the next subagent's assumption? How did you recover?**

No output broke the next subagent's code: SA-2 called SA-1's `find_all()` and `update_notification_pref()` with the exact names and `dict | None` return from the SA-1 hand-off, SA-3 called SA-2's three functions with the hand-off signatures and SA-4's 9 tests passed on the first run. What broke was my assumption that "pytest -q green after each subagent" meant each layer was verified. After SA-1, SA-2 and SA-3 the result was the same 20 passed, all pre-existing tests, so the new `list_users`, `get_notification_pref` and `update_notification_pref` had zero test coverage until SA-4, and the three routes added by SA-3 are still not exercised by any test because Flask is not installed and every test calls services/ directly. I recovered partially: SA-4 brought the suite to 29 passed and covers every service function, but SA-4's prompt never asked for a successful `get_notification_pref` read so only its NotFoundError path is tested.

**Would you write the decomposition differently a second time? What would you change?**

Yes, in three ways. 
(1) Move each layer's tests into that layer's subagent (SA-2 writes the service tests in tests/test_users.py), so the per-subagent `pytest -q` actually checks the new code and the decomposition no longer conflicts with CLAUDE.md's "every new service function gets a test" rule; SA-4 would then only add cross-layer tests. 
(2) Make SA-3 install requirements.txt and add Flask test-client tests for GET /users, GET /users/<id>/notifications and PATCH /users/<id>/notifications, so the API layer has its own verification instead of an unrelated green run. 
(3) In SA-4's prompt, list one test per hand-off function and outcome, including a successful `get_notification_pref` read after an update, instead of a feature-level list that let that case slip.
