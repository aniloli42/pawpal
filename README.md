# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ now features an advanced scheduling engine to streamline pet care:

- **Automated Recurring Tasks:** Marking a daily or weekly task as 'completed' automatically calculates (via Python's `timedelta`) and schedules the next occurrence.
- **Conflict Detection:** Identifies and securely warns the user if two tasks are accidentally scheduled to start at the exact same time.
- **Sorting and Filtering:** You can easily sort tasks by chronological order using lambda functions, and dynamically filter them by pending/completed status or specific pet names.

## Testing PawPal+

The automated test suite lives in `tests/test_pawpal.py` and is run with **pytest**.

### How to run tests

```bash
# Activate your virtual environment first
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Run all tests with verbose output
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains **70 tests** across 8 test classes:

| Class | Tests | What's verified |
|---|---|---|
| `TestTask` | 11 | Status transitions (`pending → in_progress → completed`), priority flags, `to_dict()` serialization, unique ID generation |
| `TestPet` | 9 | Task add/remove/get operations, mismatched `pet_id` guard, defensive copy returned by `get_tasks()` |
| `TestOwner` | 16 | Full pet & task CRUD, cross-pet task lookup, attribute update validation |
| `TestScheduler` | 5 | Greedy scheduling, priority ordering, budget overflow, empty-pet edge case |
| `TestSchedule` | 7 | `explain()` output, `to_dict()` structure, task retrieval by ID |
| `TestBuildSchedule` | 4 | Schedule deduplication, multi-pet isolation, removal |
| `TestSortingCorrectness` | 5 | `sort_by_time()` returns tasks in chronological `HH:MM` order; guards against list mutation |
| `TestRecurrenceLogic` | 6 | Daily (+1 day), weekly (+7 days), weekdays (skips Saturday & Sunday) recurrence; non-recurring tasks produce no follow-up |
| `TestConflictDetection` | 7 | `detect_time_conflicts()` flags duplicate start times, names the clashing tasks, and never false-positives on distinct times |

### Confidence Level

⭐⭐⭐⭐⭐ **4 / 5**

All 70 tests pass against the current implementation with a run time of < 0.1 s.
The suite covers happy paths, edge cases (empty pets, zero-budget schedules, single-task lists), and boundary conditions (exact-fit budget, Friday → Monday weekday skip), giving high confidence in the reliability of the core scheduling and recurrence logic.
