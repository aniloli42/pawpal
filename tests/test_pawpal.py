"""
tests/test_pawpal.py
Unit tests for PawPal+ logic layer using pytest.
"""

import pytest
from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule, Scheduler


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def pet():
    return Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)


@pytest.fixture
def owner():
    return Owner(name="Jordan", available_minutes=60)


@pytest.fixture
def owner_with_pet(owner, pet):
    owner.add_pet(pet)
    return owner, pet


@pytest.fixture
def task(pet):
    return Task(pet_id=pet.id, title="Morning Walk", duration_minutes=20, priority="high", category="walk")


# ===========================================================================
# Task tests
# ===========================================================================

class TestTask:

    def test_default_status_is_pending(self, task):
        assert task.status == "pending"

    def test_mark_complete_sets_status_to_completed(self, task):
        task.mark_complete()
        assert task.status == "completed"

    def test_set_status_in_progress(self, task):
        task.set_status("in_progress")
        assert task.status == "in_progress"

    def test_set_status_completed(self, task):
        task.set_status("completed")
        assert task.status == "completed"

    def test_set_status_pending(self, task):
        task.set_status("completed")
        task.set_status("pending")   # reset back
        assert task.status == "pending"

    def test_set_status_invalid_raises(self, task):
        with pytest.raises(ValueError, match="Invalid status"):
            task.set_status("done")

    def test_is_high_priority_true(self, task):
        assert task.is_high_priority() is True

    def test_is_high_priority_false(self, pet):
        low_task = Task(pet_id=pet.id, title="Play", duration_minutes=15, priority="low")
        assert low_task.is_high_priority() is False

    def test_to_dict_contains_all_fields(self, task):
        d = task.to_dict()
        assert d["title"] == "Morning Walk"
        assert d["priority"] == "high"
        assert d["status"] == "pending"
        assert d["pet_id"] == task.pet_id
        assert "id" in d

    def test_to_dict_status_updates_with_mark_complete(self, task):
        task.mark_complete()
        assert task.to_dict()["status"] == "completed"

    def test_task_has_unique_id(self, pet):
        t1 = Task(pet_id=pet.id, title="Walk", duration_minutes=10)
        t2 = Task(pet_id=pet.id, title="Walk", duration_minutes=10)
        assert t1.id != t2.id


# ===========================================================================
# Pet tests
# ===========================================================================

class TestPet:

    def test_add_task_increases_count(self, pet, task):
        assert len(pet.get_tasks()) == 0
        pet.add_task(task)
        assert len(pet.get_tasks()) == 1

    def test_add_multiple_tasks_increases_count(self, pet):
        for i in range(3):
            pet.add_task(Task(pet_id=pet.id, title=f"Task {i}", duration_minutes=10))
        assert len(pet.get_tasks()) == 3

    def test_add_task_wrong_pet_raises(self, pet):
        wrong_task = Task(pet_id="wrong-id", title="Walk", duration_minutes=10)
        with pytest.raises(ValueError):
            pet.add_task(wrong_task)

    def test_remove_task_decreases_count(self, pet, task):
        pet.add_task(task)
        pet.remove_task(task.id)
        assert len(pet.get_tasks()) == 0

    def test_remove_task_unknown_id_is_silent(self, pet):
        pet.remove_task("nonexistent-id")   # should not raise

    def test_get_task_by_id_returns_correct_task(self, pet, task):
        pet.add_task(task)
        found = pet.get_task(task.id)
        assert found is task

    def test_get_task_unknown_id_returns_none(self, pet):
        assert pet.get_task("no-such-id") is None

    def test_get_tasks_returns_copy(self, pet, task):
        pet.add_task(task)
        result = pet.get_tasks()
        result.clear()
        assert len(pet.get_tasks()) == 1   # original unchanged


# ===========================================================================
# Owner tests
# ===========================================================================

class TestOwner:

    def test_add_pet_increases_count(self, owner, pet):
        assert len(owner.get_pets()) == 0
        owner.add_pet(pet)
        assert len(owner.get_pets()) == 1

    def test_add_two_pets_increases_count_to_two(self, owner):
        owner.add_pet(Pet(name="Mochi", species="dog"))
        owner.add_pet(Pet(name="Luna", species="cat"))
        assert len(owner.get_pets()) == 2

    def test_remove_pet_decreases_count(self, owner, pet):
        owner.add_pet(pet)
        owner.remove_pet(pet.id)
        assert len(owner.get_pets()) == 0

    def test_remove_pet_unknown_id_is_silent(self, owner):
        owner.remove_pet("nonexistent-id")  # should not raise

    def test_get_pet_by_id(self, owner, pet):
        owner.add_pet(pet)
        found = owner.get_pet(pet.id)
        assert found is pet

    def test_get_pet_unknown_returns_none(self, owner):
        assert owner.get_pet("no-such-id") is None

    def test_update_pet_changes_attribute(self, owner, pet):
        owner.add_pet(pet)
        owner.update_pet(pet.id, name="Max")
        assert owner.get_pet(pet.id).name == "Max"

    def test_update_pet_unknown_raises(self, owner):
        with pytest.raises(ValueError):
            owner.update_pet("bad-id", name="Ghost")

    def test_create_task_adds_to_pet(self, owner, pet):
        owner.add_pet(pet)
        owner.create_task(pet.id, "Feeding", duration_minutes=10)
        assert len(pet.get_tasks()) == 1

    def test_create_task_returns_task_object(self, owner, pet):
        owner.add_pet(pet)
        task = owner.create_task(pet.id, "Walk", duration_minutes=20, priority="high")
        assert isinstance(task, Task)
        assert task.title == "Walk"

    def test_create_task_invalid_pet_raises(self, owner):
        with pytest.raises(ValueError):
            owner.create_task("bad-pet-id", "Walk", duration_minutes=20)

    def test_get_tasks_returns_pet_tasks(self, owner, pet):
        owner.add_pet(pet)
        owner.create_task(pet.id, "Walk", duration_minutes=20)
        owner.create_task(pet.id, "Feed", duration_minutes=10)
        assert len(owner.get_tasks(pet.id)) == 2

    def test_get_tasks_invalid_pet_raises(self, owner):
        with pytest.raises(ValueError):
            owner.get_tasks("bad-pet-id")

    def test_get_task_by_id_across_pets(self, owner):
        p1 = Pet(name="Mochi", species="dog")
        p2 = Pet(name="Luna",  species="cat")
        owner.add_pet(p1)
        owner.add_pet(p2)
        t = owner.create_task(p2.id, "Feeding", duration_minutes=10)
        found = owner.get_task(t.id)
        assert found is t

    def test_remove_task_removes_from_pet(self, owner, pet):
        owner.add_pet(pet)
        task = owner.create_task(pet.id, "Walk", duration_minutes=20)
        owner.remove_task(task.id)
        assert len(pet.get_tasks()) == 0

    def test_update_task_changes_attribute(self, owner, pet):
        owner.add_pet(pet)
        task = owner.create_task(pet.id, "Walk", duration_minutes=20, priority="low")
        owner.update_task(task.id, priority="high")
        assert task.priority == "high"

    def test_update_task_unknown_raises(self, owner):
        with pytest.raises(ValueError):
            owner.update_task("bad-id", priority="high")


# ===========================================================================
# Scheduler tests
# ===========================================================================

class TestScheduler:

    def test_high_priority_tasks_scheduled_first(self, pet):
        pet.add_task(Task(pet_id=pet.id, title="Low task",  duration_minutes=10, priority="low"))
        pet.add_task(Task(pet_id=pet.id, title="High task", duration_minutes=10, priority="high"))
        scheduler = Scheduler()
        schedule = scheduler.generate(pet, available_minutes=60, date="2026-04-05")
        assert schedule.scheduled_tasks[0].title == "High task"

    def test_tasks_within_budget_are_scheduled(self, pet):
        pet.add_task(Task(pet_id=pet.id, title="Walk",    duration_minutes=20, priority="high"))
        pet.add_task(Task(pet_id=pet.id, title="Feeding", duration_minutes=10, priority="high"))
        schedule = Scheduler().generate(pet, available_minutes=60, date="2026-04-05")
        assert len(schedule.scheduled_tasks) == 2
        assert len(schedule.unscheduled_tasks) == 0

    def test_tasks_over_budget_are_skipped(self, pet):
        pet.add_task(Task(pet_id=pet.id, title="Long task", duration_minutes=50, priority="low"))
        pet.add_task(Task(pet_id=pet.id, title="Walk",      duration_minutes=20, priority="high"))
        schedule = Scheduler().generate(pet, available_minutes=30, date="2026-04-05")
        titles_scheduled   = [t.title for t in schedule.scheduled_tasks]
        titles_unscheduled = [t.title for t in schedule.unscheduled_tasks]
        assert "Walk" in titles_scheduled
        assert "Long task" in titles_unscheduled

    def test_total_duration_is_accurate(self, pet):
        pet.add_task(Task(pet_id=pet.id, title="Walk",    duration_minutes=20, priority="high"))
        pet.add_task(Task(pet_id=pet.id, title="Feeding", duration_minutes=15, priority="medium"))
        schedule = Scheduler().generate(pet, available_minutes=60, date="2026-04-05")
        assert schedule.total_duration_minutes == 35

    def test_empty_pet_produces_empty_schedule(self, pet):
        schedule = Scheduler().generate(pet, available_minutes=60, date="2026-04-05")
        assert schedule.scheduled_tasks == []
        assert schedule.unscheduled_tasks == []
        assert schedule.total_duration_minutes == 0


# ===========================================================================
# Schedule tests
# ===========================================================================

class TestSchedule:

    @pytest.fixture
    def schedule(self, pet):
        pet.add_task(Task(pet_id=pet.id, title="Walk",    duration_minutes=20, priority="high"))
        pet.add_task(Task(pet_id=pet.id, title="Feeding", duration_minutes=10, priority="medium"))
        return Scheduler().generate(pet, available_minutes=60, date=str(date.today()))

    def test_explain_returns_string(self, schedule):
        result = schedule.explain()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_explain_mentions_scheduled_tasks(self, schedule):
        result = schedule.explain()
        assert "Walk" in result
        assert "Feeding" in result

    def test_explain_mentions_skipped_when_present(self, pet):
        pet.add_task(Task(pet_id=pet.id, title="Walk",     duration_minutes=20, priority="high"))
        pet.add_task(Task(pet_id=pet.id, title="Long task", duration_minutes=50, priority="low"))
        schedule = Scheduler().generate(pet, available_minutes=25, date="2026-04-05")
        assert "Skipped" in schedule.explain()

    def test_get_task_by_id(self, schedule):
        task = schedule.scheduled_tasks[0]
        found = schedule.get_task(task.id)
        assert found is task

    def test_get_task_unknown_returns_none(self, schedule):
        assert schedule.get_task("no-such-id") is None

    def test_to_dict_has_required_keys(self, schedule):
        d = schedule.to_dict()
        for key in ("id", "pet_id", "date", "scheduled_tasks", "unscheduled_tasks", "total_duration_minutes"):
            assert key in d

    def test_to_dict_scheduled_tasks_are_dicts(self, schedule):
        d = schedule.to_dict()
        assert all(isinstance(t, dict) for t in d["scheduled_tasks"])


# ===========================================================================
# Owner.build_schedule integration test
# ===========================================================================

class TestBuildSchedule:

    def test_build_schedule_stores_schedule(self, owner, pet):
        owner.add_pet(pet)
        owner.create_task(pet.id, "Walk", duration_minutes=20, priority="high")
        schedule = owner.build_schedule(pet.id, "2026-04-05")
        assert owner.get_schedule(schedule.id) is schedule

    def test_build_schedule_invalid_pet_raises(self, owner):
        with pytest.raises(ValueError):
            owner.build_schedule("bad-pet-id", "2026-04-05")

    def test_get_schedules_filters_by_pet(self, owner):
        p1 = Pet(name="Mochi", species="dog")
        p2 = Pet(name="Luna",  species="cat")
        owner.add_pet(p1)
        owner.add_pet(p2)
        owner.create_task(p1.id, "Walk",    duration_minutes=20)
        owner.create_task(p2.id, "Feeding", duration_minutes=10)
        owner.build_schedule(p1.id, "2026-04-05")
        owner.build_schedule(p2.id, "2026-04-05")
        assert len(owner.get_schedules(p1.id)) == 1
        assert len(owner.get_schedules(p2.id)) == 1

    def test_remove_schedule(self, owner, pet):
        owner.add_pet(pet)
        owner.create_task(pet.id, "Walk", duration_minutes=20)
        schedule = owner.build_schedule(pet.id, "2026-04-05")
        owner.remove_schedule(schedule.id)
        assert owner.get_schedule(schedule.id) is None
