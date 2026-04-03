from datetime import date, time as dtime
from pawpal_system import Owner, Pet, Task, TimeWindow, Scheduler


def pretty_print_schedule(plan, owner):
    pet_names = {p.id: p.name for p in owner.pets}
    print(f"Today's Schedule for {plan.date} - {len(plan.slots)} tasks")
    if not plan.slots:
        print(plan.explanation)
        return
    for start_time, task in plan.slots:
        pet_name = pet_names.get(task.pet_id, f'pet:{task.pet_id}')
        print(f"{start_time.strftime('%H:%M')} - {pet_name}: {task.title} ({task.duration_minutes}m) [prio={task.priority}]")
    print('\nSummary:')
    print(f"  Total duration: {plan.total_duration} minutes")
    print(f"  Score: {plan.score}")
    print(f"  Explanation: {plan.explanation}")


if __name__ == '__main__':
    # Owner and availability
    owner = Owner(id=1, name='Alex')
    morning = TimeWindow(start_time=dtime(7, 0), end_time=dtime(10, 0))
    evening = TimeWindow(start_time=dtime(17, 0), end_time=dtime(20, 0))
    owner.set_availability([morning, evening])

    # Pets
    dog = Pet(id=1, owner_id=owner.id, name='Rex', species='dog')
    cat = Pet(id=2, owner_id=owner.id, name='Mittens', species='cat')
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Tasks
    t1 = Task(id=1, pet_id=dog.id, title='Morning walk', type='walk', duration_minutes=30, priority=8, earliest_time=dtime(7,30))
    t2 = Task(id=2, pet_id=cat.id, title='Feed breakfast', type='feed', duration_minutes=10, priority=6, earliest_time=dtime(8,0))
    t3 = Task(id=3, pet_id=dog.id, title='Give meds', type='med', duration_minutes=5, priority=10, earliest_time=dtime(8,15), recurrence='daily')

    dog.add_task(t1)
    dog.add_task(t3)
    cat.add_task(t2)

    # Scheduler
    scheduler = Scheduler()
    plan = scheduler.generate_daily_plan(date.today(), tasks=[], owner=owner)

    pretty_print_schedule(plan, owner)
    # Demonstrate sorting and filtering
    print("\n--- Sorting tasks by time (raw tasks from owner) ---")
    tasks = owner.get_all_tasks()
    sorted_tasks = scheduler.sort_by_time(tasks)
    for t in sorted_tasks:
        print(f"{t.earliest_time} - {t.title} (pet {t.pet_id})")

    print("\n--- Filter tasks: only uncompleted ---")
    uncompleted = scheduler.filter_tasks(tasks, owner=owner, completed=False)
    for t in uncompleted:
        print(f"{t.title} (pet {t.pet_id}) - completed_dates={t.completed_dates}")

    # Demonstrate recurring task creation
    print("\n--- Marking first task complete and creating next occurrence if recurring ---")
    if tasks:
        next_t = tasks[0].mark_complete(date.today())
        print(f"Marked complete: {tasks[0].title}, next occurrence created: {bool(next_t)}")
        if next_t:
            # assign a new id and add to pet
            next_t.id = 999
            for p in owner.pets:
                if p.id == next_t.pet_id:
                    p.add_task(next_t)
                    break

    # Conflict detection demo: create two tasks at same time
    print("\n--- Conflict detection demo ---")
    t_conf1 = Task(id=101, pet_id=dog.id, title='Overlap1', type='play', duration_minutes=15, earliest_time=dtime(9,0))
    t_conf2 = Task(id=102, pet_id=cat.id, title='Overlap2', type='play', duration_minutes=15, earliest_time=dtime(9,0))
    dog.add_task(t_conf1)
    cat.add_task(t_conf2)
    plan2 = scheduler.generate_daily_plan(date.today(), tasks=[], owner=owner)
    warnings = scheduler.detect_conflicts(plan2)
    print('Warnings:', warnings)
