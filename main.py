"""
main.py
Demo script for PawPal+ — shows the full system working end-to-end.
"""

from datetime import date
from pawpal_system import Owner, Pet

# ---------------------------------------------------------------------------
# Setup: create the owner
# ---------------------------------------------------------------------------

owner = Owner(name="Jordan", available_minutes=90)
print(f"👤 Owner: {owner.name} (daily budget: {owner.available_minutes} min)\n")

# ---------------------------------------------------------------------------
# Create two pets
# ---------------------------------------------------------------------------

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
luna  = Pet(name="Luna",  species="cat", breed="Ragdoll",   age=2)

owner.add_pet(mochi)
owner.add_pet(luna)

print(f"🐾 Pets added: {', '.join(p.name for p in owner.get_pets())}\n")

# ---------------------------------------------------------------------------
# Add tasks out of order with explicit HH:MM time
# ---------------------------------------------------------------------------

owner.create_task(mochi.id, "Evening Walk",    duration_minutes=25, priority="high", time="19:00", status="pending")
owner.create_task(mochi.id, "Morning Walk",    duration_minutes=25, priority="high", time="07:30", status="completed")
owner.create_task(mochi.id, "Lunchtime Walk",  duration_minutes=15, priority="medium", time="13:00", status="pending")

owner.create_task(luna.id, "Late Snack",       duration_minutes=10, priority="low", time="22:00", status="pending")
owner.create_task(luna.id, "Morning Feed",     duration_minutes=10, priority="high", time="08:00", status="completed")

# ---------------------------------------------------------------------------
# 1. Test filtering logic 
# ---------------------------------------------------------------------------

print("=== Testing Filtering ===")
pending_mochi_tasks = owner.filter_tasks_by_pet_or_status(pet_name="Mochi", status="pending")
print(f"Pending tasks for Mochi: {len(pending_mochi_tasks)}")
for task in pending_mochi_tasks:
    print(f" - [{task.status}] {task.time} {task.title}")
print()

# ---------------------------------------------------------------------------
# 2. Test sorting logic
# ---------------------------------------------------------------------------

print("=== Testing Sorting ===")
# Gather all tasks across all pets for a demonstration
all_tasks = owner.filter_tasks_by_pet_or_status()

# Sort tasks using our lambda function
sorted_tasks = owner.scheduler.sort_by_time(all_tasks)

print("All app tasks, sorted strictly by time:")
for task in sorted_tasks:
    # Lookup pet name for printing
    pet = owner.get_pet(task.pet_id)
    print(f" 🕐 {task.time} | {pet.name:^6} | {task.title}")
print()
