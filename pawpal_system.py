"""
pawpal_system.py
Logic layer for PawPal+ — pet care planning assistant.

Owner is the root of the application. There is no PawPal wrapper class.
The Streamlit app.py will create one Owner instance and work with it directly.

SOLID design:
  S — Task/Pet = data models; Scheduler = algorithm; Schedule = result; Owner = root
  O — Scheduler can be subclassed for new strategies without modifying Schedule
  L — Any Scheduler subclass can replace the default in Owner
  I — Each class exposes only what its consumers need
  D — Owner depends on Scheduler abstraction, not a hardcoded algorithm

Classes:
    Task      — a single pet care activity (data)
    Pet       — a pet and its task list
    Schedule  — immutable result of a scheduling run (data + explain)
    Scheduler — scheduling algorithm
    Owner     — root app user; manages pets, tasks, and schedules
"""

import uuid
from dataclasses import dataclass, field
from typing import ClassVar, Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet care activity."""

    VALID_PRIORITIES: ClassVar[set] = {"low", "medium", "high"}
    VALID_CATEGORIES: ClassVar[set] = {"walk", "feeding", "meds", "grooming", "enrichment", "other"}

    pet_id: str
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "other"
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)

    def is_high_priority(self) -> bool:
        """Returns True if the task priority is 'high'."""
        return self.priority == "high"

    def to_dict(self) -> dict:
        """Serializes the task to a plain dictionary."""
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet with a list of care tasks.

    Responsibility: manage its own task list.
    """

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)

    def add_task(self, task: Task) -> None:
        """Appends a task to this pet's list.

        Raises:
            ValueError: if task.pet_id does not match this pet's id.
        """
        if task.pet_id != self.id:
            raise ValueError(
                f"Task '{task.title}' belongs to pet '{task.pet_id}', "
                f"not to this pet '{self.id}'."
            )
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Removes a task by its unique ID. Silently ignores unknown IDs."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> list[Task]:
        """Returns all tasks assigned to this pet."""
        return list(self.tasks)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Returns a specific task by ID, or None if not found."""
        return next((t for t in self.tasks if t.id == task_id), None)


# ---------------------------------------------------------------------------
# Schedule  (result data container — SRP: stores and explains, nothing more)
# ---------------------------------------------------------------------------

@dataclass
class Schedule:
    """Immutable result of a scheduling run for one pet.

    Responsibility: store the result and explain it.
    Does NOT generate itself — that is Scheduler's job (SRP + OCP).
    """

    pet_id: str
    date: str
    scheduled_tasks: list[Task]
    unscheduled_tasks: list[Task]
    total_duration_minutes: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)

    def explain(self) -> str:
        """Returns a human-readable explanation of which tasks were chosen and why."""
        lines = [f"📅 Schedule for {self.date}", ""]

        if self.scheduled_tasks:
            lines.append(f"✅ Scheduled ({self.total_duration_minutes} min total):")
            for task in self.scheduled_tasks:
                lines.append(
                    f"  • {task.title} — {task.duration_minutes} min "
                    f"[{task.priority} priority, {task.category}]"
                )
        else:
            lines.append("No tasks were scheduled.")

        if self.unscheduled_tasks:
            lines.append("")
            lines.append("⏭ Skipped (did not fit in time budget):")
            for task in self.unscheduled_tasks:
                lines.append(
                    f"  • {task.title} — {task.duration_minutes} min "
                    f"[{task.priority} priority]"
                )

        return "\n".join(lines)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Returns a specific scheduled task by ID, or None if not found."""
        return next((t for t in self.scheduled_tasks if t.id == task_id), None)

    def to_dict(self) -> dict:
        """Serializes the full schedule to a plain dictionary."""
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "date": self.date,
            "scheduled_tasks": [t.to_dict() for t in self.scheduled_tasks],
            "unscheduled_tasks": [t.to_dict() for t in self.unscheduled_tasks],
            "total_duration_minutes": self.total_duration_minutes,
        }


# ---------------------------------------------------------------------------
# Scheduler  (algorithm — SRP + OCP: one job, open to subclassing)
# ---------------------------------------------------------------------------

class Scheduler:
    """Encapsulates the scheduling algorithm.

    Responsibility: decide which tasks fit in the time budget and in what order.
    Open for extension: subclass to implement alternative strategies
    (e.g. CategoryScheduler, TimeSlotScheduler) without modifying Schedule or Owner.
    """

    PRIORITY_ORDER: ClassVar[dict] = {"high": 0, "medium": 1, "low": 2}

    def generate(self, pet: Pet, available_minutes: int, date: str) -> Schedule:
        """Sorts pet tasks by priority (high → medium → low), fills up to
        available_minutes, and returns a Schedule result object.

        Args:
            pet: the pet whose tasks will be scheduled.
            available_minutes: the owner's daily time budget.
            date: ISO-format date string for this schedule.

        Returns:
            A populated Schedule instance.
        """
        sorted_tasks = sorted(
            pet.get_tasks(),
            key=lambda t: self.PRIORITY_ORDER.get(t.priority, 99)
        )

        scheduled: list[Task] = []
        unscheduled: list[Task] = []
        time_used = 0

        for task in sorted_tasks:
            if time_used + task.duration_minutes <= available_minutes:
                scheduled.append(task)
                time_used += task.duration_minutes
            else:
                unscheduled.append(task)

        return Schedule(
            pet_id=pet.id,
            date=date,
            scheduled_tasks=scheduled,
            unscheduled_tasks=unscheduled,
            total_duration_minutes=time_used,
        )


# ---------------------------------------------------------------------------
# Owner  (root — single entry point for the entire app session)
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """The root of the application. One Owner per session.

    Responsibility: manage the user profile, pets, tasks, and schedule history.
    Delegates scheduling work to the injected Scheduler (DIP).
    """

    name: str
    available_minutes: int = 120
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)
    schedules: list[Schedule] = field(default_factory=list)
    scheduler: Scheduler = field(default_factory=Scheduler)
    id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)

    # --- Pet management ---

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Removes a pet by ID. Silently ignores unknown IDs."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_pets(self) -> list[Pet]:
        """Returns all pets."""
        return list(self.pets)

    def get_pet(self, pet_id: str) -> Optional[Pet]:
        """Returns a specific pet by ID, or None if not found."""
        return next((p for p in self.pets if p.id == pet_id), None)

    def update_pet(self, pet_id: str, **kwargs) -> None:
        """Updates attributes of an existing pet by ID.

        Raises:
            ValueError: if pet_id is not found.
        """
        allowed = {"name", "species", "breed", "age"}
        pet = self.get_pet(pet_id)
        if pet is None:
            raise ValueError(f"Pet '{pet_id}' not found.")
        for key, value in kwargs.items():
            if key in allowed:
                setattr(pet, key, value)

    # --- Task management ---

    def create_task(self, pet_id: str, title: str, duration_minutes: int,
                    priority: str = "medium", category: str = "other",
                    notes: str = "") -> Task:
        """Creates a Task for a specific pet, sets pet_id, and appends it.

        Raises:
            ValueError: if pet_id is not found among this owner's pets.
        """
        pet = self.get_pet(pet_id)
        if pet is None:
            raise ValueError(f"Pet '{pet_id}' not found.")
        task = Task(
            pet_id=pet_id,
            title=title,
            duration_minutes=duration_minutes,
            priority=priority,
            category=category,
            notes=notes,
        )
        pet.add_task(task)
        return task

    def remove_task(self, task_id: str) -> None:
        """Removes a task by ID from whichever pet holds it."""
        for pet in self.pets:
            pet.remove_task(task_id)

    def get_tasks(self, pet_id: str) -> list[Task]:
        """Returns all tasks for a specific pet.

        Raises:
            ValueError: if pet_id is not found.
        """
        pet = self.get_pet(pet_id)
        if pet is None:
            raise ValueError(f"Pet '{pet_id}' not found.")
        return pet.get_tasks()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Returns a specific task by ID across all pets, or None if not found."""
        for pet in self.pets:
            task = pet.get_task(task_id)
            if task is not None:
                return task
        return None

    def update_task(self, task_id: str, **kwargs) -> None:
        """Updates attributes of an existing task by ID.

        Raises:
            ValueError: if task_id is not found.
        """
        allowed = {"title", "duration_minutes", "priority", "category", "notes"}
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"Task '{task_id}' not found.")
        for key, value in kwargs.items():
            if key in allowed:
                setattr(task, key, value)

    # --- Schedule management ---

    def build_schedule(self, pet_id: str, date: str) -> Schedule:
        """Looks up the pet, runs the scheduler, stores and returns the result.

        Raises:
            ValueError: if pet_id is not found.
        """
        pet = self.get_pet(pet_id)
        if pet is None:
            raise ValueError(f"Pet '{pet_id}' not found.")
        schedule = self.scheduler.generate(pet, self.available_minutes, date)
        self.schedules.append(schedule)
        return schedule

    def get_schedules(self, pet_id: str) -> list[Schedule]:
        """Returns all schedules for a specific pet."""
        return [s for s in self.schedules if s.pet_id == pet_id]

    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Returns a specific schedule by ID, or None if not found."""
        return next((s for s in self.schedules if s.id == schedule_id), None)

    def remove_schedule(self, schedule_id: str) -> None:
        """Removes a schedule by ID. Silently ignores unknown IDs."""
        self.schedules = [s for s in self.schedules if s.id != schedule_id]
