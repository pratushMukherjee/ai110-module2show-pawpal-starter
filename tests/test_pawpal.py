import datetime
from datetime import time, date, timedelta
from pawpal_system import Task, Pet, Scheduler, Schedule


def test_task_mark_complete():
    t = Task(id=1, pet_id=1, title='Test', type='feed', duration_minutes=5)
    today = datetime.date.today()
    assert today not in t.completed_dates
    t.mark_complete(today)
    assert today in t.completed_dates
    assert not t.is_due_on(today)


def test_pet_add_task():
    p = Pet(id=1, owner_id=0, name='Buddy', species='dog')
    # start with no explicit tasks or templates
    assert len(p.get_tasks()) == 0
    t = Task(id=2, pet_id=p.id, title='Walk', type='walk', duration_minutes=20)
    p.add_task(t)
    tasks = p.get_tasks()
    assert any(task.id == 2 for task in tasks)
    assert len([task for task in tasks if task.id == 2]) == 1


def test_sort_by_time():
    s = Scheduler()
    t1 = Task(id=10, pet_id=1, title='A', type='feed', duration_minutes=10, earliest_time=time(8, 0))
    t2 = Task(id=11, pet_id=1, title='B', type='walk', duration_minutes=20, earliest_time=time(7, 30))
    t3 = Task(id=12, pet_id=1, title='C', type='play', duration_minutes=15)
    sorted_tasks = s.sort_by_time([t1, t2, t3])
    assert sorted_tasks[0].id == 11
    assert sorted_tasks[1].id == 10
    assert sorted_tasks[2].id == 12


def test_recurrence_mark_complete_creates_next():
    today = date.today()
    t = Task(id=20, pet_id=1, title='Daily med', type='med', duration_minutes=5, recurrence='daily')
    next_task = t.mark_complete(today)
    assert next_task is not None
    # original task should report next occurrence as tomorrow
    assert t.next_occurrence(today) == today + timedelta(days=1)


def test_conflict_detection():
    # create two tasks and a schedule with identical start times
    t1 = Task(id=30, pet_id=1, title='X', type='feed', duration_minutes=10)
    t2 = Task(id=31, pet_id=2, title='Y', type='walk', duration_minutes=15)
    sched = Schedule(date=date.today(), slots=[(time(9, 0), t1), (time(9, 0), t2)])
    s = Scheduler()
    warnings = s.detect_conflicts(sched)
    assert len(warnings) >= 1
    assert '09:00' in warnings[0] or '9:00' in warnings[0]
