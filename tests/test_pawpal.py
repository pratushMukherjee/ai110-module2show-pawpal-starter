import datetime
from pawpal_system import Task, Pet


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
