import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, TimeWindow, TaskManager

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("New pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Persist Owner in session_state so it survives reruns
if "owner_obj" not in st.session_state:
    st.session_state.owner_obj = Owner(id=1, name=owner_name)
    st.session_state.next_pet_id = 1
    st.session_state.next_task_id = 1
else:
    # keep owner name in sync with the text input
    st.session_state.owner_obj.name = owner_name

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "task_manager" not in st.session_state:
    st.session_state.task_manager = TaskManager()

st.markdown("### Pets")
colp1, colp2 = st.columns([3, 1])
with colp1:
    new_pet_name = pet_name
    new_species = species
with colp2:
    if st.button("Add pet"):
        pid = st.session_state.next_pet_id
        pet = Pet(id=pid, owner_id=st.session_state.owner_obj.id, name=new_pet_name, species=new_species)
        st.session_state.owner_obj.add_pet(pet)
        st.session_state.next_pet_id += 1

if st.session_state.owner_obj.pets:
    st.write("Owned pets:")
    pet_rows = [{"id": p.id, "name": p.name, "species": p.species} for p in st.session_state.owner_obj.pets]
    st.table(pet_rows)
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
if st.session_state.owner_obj.pets:
    pet_options = {p.name: p.id for p in st.session_state.owner_obj.pets}
    selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))
    task_title = st.text_input("Task title", value="Morning walk")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    priority_map = {"low": 1, "medium": 5, "high": 10}
    if st.button("Add task"):
        tid = st.session_state.next_task_id
        pet_id = pet_options[selected_pet_name]
        task = Task(id=tid, pet_id=pet_id, title=task_title, type="general", duration_minutes=int(duration), priority=priority_map[priority_label])
        # add to the pet object
        for p in st.session_state.owner_obj.pets:
            if p.id == pet_id:
                p.add_task(task)
                break
        st.session_state.next_task_id += 1

    # show tasks per pet
    tasks_display = []
    for p in st.session_state.owner_obj.pets:
        for t in p.get_tasks():
            tasks_display.append({"pet": p.name, "title": t.title, "duration": t.duration_minutes, "priority": t.priority})
    if tasks_display:
        st.write("Current tasks:")
        st.table(tasks_display)
else:
    st.info("Add a pet first to attach tasks to.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    plan = scheduler.generate_daily_plan(date.today(), tasks=[], owner=st.session_state.owner_obj)
    if not plan.slots:
        st.warning(plan.explanation)
    else:
        rows = []
        pet_names = {p.id: p.name for p in st.session_state.owner_obj.pets}
        for start_time, task in plan.slots:
            rows.append({"time": start_time.strftime("%H:%M"), "pet": pet_names.get(task.pet_id, "-"), "task": task.title, "duration": task.duration_minutes})
        st.table(rows)
