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
# Add 3 tasks for Mochi
# ---------------------------------------------------------------------------

owner.create_task(mochi.id, "Morning Walk",    duration_minutes=25, priority="high",   category="walk")
owner.create_task(mochi.id, "Breakfast",       duration_minutes=10, priority="high",   category="feeding")
owner.create_task(mochi.id, "Flea Medication", duration_minutes=5,  priority="medium", category="meds")

# ---------------------------------------------------------------------------
# Add 3 tasks for Luna
# ---------------------------------------------------------------------------

owner.create_task(luna.id, "Feeding",          duration_minutes=10, priority="high",   category="feeding")
owner.create_task(luna.id, "Litter Box Clean", duration_minutes=10, priority="medium", category="grooming")
owner.create_task(luna.id, "Enrichment Play",  duration_minutes=20, priority="low",    category="enrichment")

# ---------------------------------------------------------------------------
# Generate and print today's schedule for each pet
# ---------------------------------------------------------------------------

today = str(date.today())

for pet in owner.get_pets():
    schedule = owner.build_schedule(pet.id, today)
    print(f"{'=' * 50}")
    print(f"🐶 Pet: {pet.name} ({pet.species})")
    print(f"{'=' * 50}")
    print(schedule.explain())
    print()
