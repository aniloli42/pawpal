"""
app.py
PawPal+ — Streamlit UI connected to pawpal_system.py logic layer.

Session state:
    st.session_state.owner  — the single Owner instance for this session
"""

from datetime import date
import streamlit as st
from pawpal_system import Owner, Pet

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your personal pet care planning assistant.")
st.divider()

# ---------------------------------------------------------------------------
# Session state — create Owner only once per session
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None   # will be set after setup form

owner: Owner | None = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 1 — Owner Setup
# ---------------------------------------------------------------------------

st.subheader("👤 Owner Setup")

if owner is None:
    with st.form("owner_form"):
        owner_name       = st.text_input("Your name", value="Jordan")
        available_minutes = st.number_input(
            "Daily time budget (minutes)", min_value=10, max_value=480, value=90, step=10
        )
        submitted = st.form_submit_button("Start →")

    if submitted:
        st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
        st.rerun()
    st.stop()   # nothing else renders until owner is created

else:
    col1, col2, col3 = st.columns([3, 2, 1])
    col1.markdown(f"**{owner.name}**")
    col2.markdown(f"⏱ {owner.available_minutes} min/day")
    if col3.button("Reset", help="Clear session and start over"):
        del st.session_state.owner
        st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Pets
# ---------------------------------------------------------------------------

st.subheader("🐾 My Pets")

with st.expander("Add a new pet", expanded=len(owner.get_pets()) == 0):
    with st.form("add_pet_form"):
        col1, col2, col3, col4 = st.columns(4)
        pet_name    = col1.text_input("Name")
        pet_species = col2.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        pet_breed   = col3.text_input("Breed (optional)")
        pet_age     = col4.number_input("Age", min_value=0, max_value=30, value=1)
        add_pet_btn = st.form_submit_button("Add pet")

    if add_pet_btn:
        if pet_name.strip():
            new_pet = Pet(name=pet_name.strip(), species=pet_species,
                          breed=pet_breed.strip(), age=pet_age)
            owner.add_pet(new_pet)
            st.success(f"Added **{new_pet.name}** the {new_pet.species}!")
            st.rerun()
        else:
            st.warning("Please enter a pet name.")

pets = owner.get_pets()
if not pets:
    st.info("No pets yet. Add one above.")
    st.stop()

for pet in pets:
    task_count = len(pet.get_tasks())
    col1, col2 = st.columns([5, 1])
    col1.markdown(f"**{pet.name}** — {pet.species}"
                  + (f", {pet.breed}" if pet.breed else "")
                  + f" · {pet.age}y · {task_count} task(s)")
    if col2.button("Remove", key=f"remove_pet_{pet.id}"):
        owner.remove_pet(pet.id)
        st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Tasks
# ---------------------------------------------------------------------------

st.subheader("✅ Tasks")

pet_options = {p.name: p for p in pets}
selected_pet_name = st.selectbox("Select pet", list(pet_options.keys()), key="task_pet_select")
selected_pet = pet_options[selected_pet_name]

with st.expander("Add a task", expanded=True):
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        task_title    = col1.text_input("Task title", value="Morning Walk")
        duration      = col2.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        col3, col4    = st.columns(2)
        priority      = col3.selectbox("Priority", ["high", "medium", "low"])
        category      = col4.selectbox("Category",
                          ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
        notes         = st.text_input("Notes (optional)", value="")
        add_task_btn  = st.form_submit_button("Add task")

    if add_task_btn:
        if task_title.strip():
            owner.create_task(
                pet_id=selected_pet.id,
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                notes=notes.strip(),
            )
            st.success(f"Added **{task_title}** to {selected_pet.name}.")
            st.rerun()
        else:
            st.warning("Please enter a task title.")

# Show existing tasks for selected pet
tasks = selected_pet.get_tasks()
if tasks:
    for task in tasks:
        status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}.get(task.status, "⬜")
        col1, col2, col3 = st.columns([5, 2, 1])
        col1.markdown(f"{status_icon} **{task.title}** — {task.duration_minutes} min "
                      f"[{task.priority}, {task.category}]")
        new_status = col2.selectbox(
            "Status", ["pending", "in_progress", "completed"],
            index=["pending", "in_progress", "completed"].index(task.status),
            key=f"status_{task.id}",
            label_visibility="collapsed",
        )
        if new_status != task.status:
            task.set_status(new_status)
            st.rerun()
        if col3.button("🗑", key=f"remove_task_{task.id}"):
            owner.remove_task(task.id)
            st.rerun()
else:
    st.info(f"No tasks for {selected_pet.name} yet.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Schedule
# ---------------------------------------------------------------------------

st.subheader("📅 Today's Schedule")

sched_pet_name = st.selectbox("Schedule for", list(pet_options.keys()), key="sched_pet_select")
sched_pet = pet_options[sched_pet_name]

if st.button("Generate schedule 🗓", type="primary"):
    if not sched_pet.get_tasks():
        st.warning(f"{sched_pet.name} has no tasks to schedule.")
    else:
        schedule = owner.build_schedule(sched_pet.id, str(date.today()))
        st.success(f"Schedule built for **{sched_pet.name}** — "
                   f"{schedule.total_duration_minutes} min used of {owner.available_minutes} min")

        if schedule.scheduled_tasks:
            st.markdown("#### ✅ Scheduled")
            for task in schedule.scheduled_tasks:
                st.markdown(f"- **{task.title}** — {task.duration_minutes} min "
                            f"[{task.priority} priority · {task.category}]")

        if schedule.unscheduled_tasks:
            st.markdown("#### ⏭ Skipped (didn't fit in time budget)")
            for task in schedule.unscheduled_tasks:
                st.markdown(f"- **{task.title}** — {task.duration_minutes} min "
                            f"[{task.priority} priority]")

        with st.expander("Full explanation"):
            st.text(schedule.explain())
