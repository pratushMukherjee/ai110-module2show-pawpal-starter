from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any, Set, Tuple


@dataclass
class TimeWindow:
	start_time: time
	end_time: time
	weekdays: Set[int] = field(default_factory=set)

	def contains(self, dt: datetime) -> bool:
		"""Return True if datetime `dt` falls inside this window."""
		if self.weekdays and dt.weekday() not in self.weekdays:
			return False
		t = dt.time()
		return self.start_time <= t < self.end_time

	def intersect(self, other: "TimeWindow") -> Optional["TimeWindow"]:
		"""Return the intersection of two time windows or None if they don't overlap."""
		start = max(self.start_time, other.start_time)
		end = min(self.end_time, other.end_time)
		if start >= end:
			return None
		# For weekdays: if both specify weekdays, intersect; if one empty, use the other
		if self.weekdays and other.weekdays:
			weekdays = self.weekdays & other.weekdays
		else:
			weekdays = self.weekdays or other.weekdays
		return TimeWindow(start_time=start, end_time=end, weekdays=weekdays)


@dataclass
class Owner:
	id: int
	name: str
	contact: Optional[str] = None
	availability: List[TimeWindow] = field(default_factory=list)
	preferences: Dict[str, Any] = field(default_factory=dict)
	timezone: Optional[str] = None
	pets: List["Pet"] = field(default_factory=list)

	def update_preferences(self, preferences: Dict[str, Any]) -> None:
		"""Update owner preferences with provided mapping."""
		self.preferences.update(preferences)

	def set_availability(self, windows: List[TimeWindow]) -> None:
		"""Set the owner's availability windows."""
		self.availability = windows

	def add_pet(self, pet: "Pet") -> None:
		"""Attach a Pet to this owner and set ownership."""
		pet.owner_id = self.id
		self.pets.append(pet)

	def get_available_windows(self, on_date: date) -> List[TimeWindow]:
		"""Return availability windows applicable to the given date."""
		result: List[TimeWindow] = []
		for w in self.availability:
			if not w.weekdays or on_date.weekday() in w.weekdays:
				result.append(w)
		return result

	def get_all_tasks(self) -> List["Task"]:
		"""Aggregate and return all tasks from every pet owned by this owner."""
		tasks: List[Task] = []
		for p in self.pets:
			tasks.extend(p.get_tasks())
		return tasks


@dataclass
class Pet:
	id: int
	owner_id: int
	name: str
	species: str
	age: Optional[int] = None
	weight: Optional[float] = None
	special_needs: List[str] = field(default_factory=list)
	default_tasks: List["Task"] = field(default_factory=list)
	tasks: List["Task"] = field(default_factory=list)

	def update_info(self, **data: Any) -> None:
		"""Update pet fields from provided keyword arguments."""
		for k, v in data.items():
			if hasattr(self, k):
				setattr(self, k, v)

	def add_task_template(self, task_template: "Task") -> None:
		"""Add a task template to this pet's defaults."""
		self.default_tasks.append(task_template)

	def add_task(self, task: "Task") -> None:
		"""Add a concrete Task instance to this pet."""
		task.pet_id = self.id
		self.tasks.append(task)

	def get_tasks(self) -> List["Task"]:
		"""Return active tasks for the pet, including templates."""
		return list(self.tasks) + list(self.default_tasks)

	def needs_medication_on(self, on_date: date) -> bool:
		"""Return True if any medication task is due for this pet on the given date."""
		return any(t.type == "med" and t.is_due_on(on_date) for t in self.get_tasks())


@dataclass
class Task:
	id: int
	pet_id: int
	title: str
	type: str
	duration_minutes: int
	priority: int = 0
	earliest_time: Optional[time] = None
	latest_time: Optional[time] = None
	recurrence: Optional[str] = None
	location: Optional[str] = None
	notes: Optional[str] = None
	completed_dates: List[date] = field(default_factory=list)

	def is_due_on(self, on_date: date) -> bool:
		"""Return True if the task should be performed on the given date."""
		if on_date in self.completed_dates:
			return False
		if not self.recurrence:
			return True
		if self.recurrence == "daily":
			return True
		if self.recurrence == "weekly":
			return on_date.weekday() in {d for d in range(7)}
		return True

	def next_occurrence(self, after_date: date) -> Optional[date]:
		"""Return the next occurrence date after the given date for recurring tasks."""
		if not self.recurrence:
			return None
		if self.recurrence == "daily":
			return after_date + timedelta(days=1)
		if self.recurrence == "weekly":
			return after_date + timedelta(days=7)
		# unsupported recurrence format -> None
		return None

	def mark_complete(self, on_date: date) -> Optional["Task"]:
		"""Mark the task as completed on the given date.

		If the task is recurring (`daily` or `weekly`), returns a new Task instance
		representing the next occurrence; otherwise returns None.
		"""
		if on_date not in self.completed_dates:
			self.completed_dates.append(on_date)
		# Create next occurrence task stub when recurring
		if self.recurrence == "daily":
			# return a shallow copy representing next day's task
			return Task(
				id=-1,
				pet_id=self.pet_id,
				title=self.title,
				type=self.type,
				duration_minutes=self.duration_minutes,
				priority=self.priority,
				earliest_time=self.earliest_time,
				latest_time=self.latest_time,
				recurrence=self.recurrence,
				location=self.location,
				notes=self.notes,
			)
		if self.recurrence == "weekly":
			return Task(
				id=-1,
				pet_id=self.pet_id,
				title=self.title,
				type=self.type,
				duration_minutes=self.duration_minutes,
				priority=self.priority,
				earliest_time=self.earliest_time,
				latest_time=self.latest_time,
				recurrence=self.recurrence,
				location=self.location,
				notes=self.notes,
			)
		return None

	def overlaps_with(self, other: "Task") -> bool:
		"""Return True if this task's time window overlaps with another task's time window."""
		if self.earliest_time and self.latest_time and other.earliest_time and other.latest_time:
			return not (self.latest_time <= other.earliest_time or other.latest_time <= self.earliest_time)
		return False


class TaskManager:
	def __init__(self) -> None:
		self.tasks: List[Task] = []
		self.task_templates: List[Task] = []

	def add_task(self, task: Task) -> None:
		"""Add a task to the manager's collection."""
		self.tasks.append(task)

	def edit_task(self, task_id: int, **fields: Any) -> None:
		"""Edit fields on a task identified by `task_id`."""
		for t in self.tasks:
			if t.id == task_id:
				for k, v in fields.items():
					if hasattr(t, k):
						setattr(t, k, v)
				return
		raise ValueError(f"Task id={task_id} not found")

	def delete_task(self, task_id: int) -> None:
		"""Remove a task from the manager by id."""
		self.tasks = [t for t in self.tasks if t.id != task_id]

	def get_tasks_for_date(self, on_date: date) -> List[Task]:
		"""Return tasks from the manager that are due on the given date."""
		return [t for t in self.tasks if t.is_due_on(on_date)]

	def get_tasks_for_pet(self, pet_id: int) -> List[Task]:
		"""Return tasks owned by a specific pet id."""
		return [t for t in self.tasks if t.pet_id == pet_id]


@dataclass
class Schedule:
	date: date
	slots: List[Tuple[time, Task]] = field(default_factory=list)
	total_duration: int = 0
	score: float = 0.0
	explanation: Optional[str] = None

	def to_display(self) -> Dict[str, Any]:
		"""Return a display-friendly representation of the schedule."""
		raise NotImplementedError()

	def get_tasks(self) -> List[Task]:
		return [t for _, t in self.slots]

	def serialize(self) -> Dict[str, Any]:
		"""Serialize the schedule to a dictionary suitable for JSON output."""
		raise NotImplementedError()


class Scheduler:
	def __init__(self, constraints: Optional[Dict[str, Any]] = None, scoring_rules: Optional[Dict[str, float]] = None) -> None:
		self.constraints = constraints or {}
		self.scoring_rules = scoring_rules or {}

	def generate_daily_plan(self, on_date: date, tasks: List[Task], owner: Owner) -> Schedule:
		"""Generate a daily Schedule for the given date, tasks, and owner."""
		# If no tasks provided, retrieve from owner
		if not tasks:
			tasks = owner.get_all_tasks()
		# Filter tasks due on date
		due = [t for t in tasks if t.is_due_on(on_date)]
		windows = owner.get_available_windows(on_date)
		plan = self.place_tasks_into_slots(due, windows)
		plan.date = on_date
		plan.explanation = self.explain_choice(plan)
		plan.score = sum(self.score_task(t, {}) for t in plan.get_tasks())
		plan.total_duration = sum(t.duration_minutes for t in plan.get_tasks())
		return plan

	def score_task(self, task: Task, context: Dict[str, Any]) -> float:
		"""Compute a simple heuristic score for a task in context."""
		# Simple heuristic: higher priority -> higher score, shorter tasks slightly preferred
		return float(task.priority) - (task.duration_minutes / 60.0) * 0.05

	def sort_by_time(self, tasks: List[Task]) -> List[Task]:
		"""Return tasks sorted by earliest_time (tasks without time go last)."""
		def key_fn(t: Task):
			if t.earliest_time:
				return (t.earliest_time.hour, t.earliest_time.minute)
			# place tasks without time at end
			return (24, 0)

		return sorted(tasks, key=key_fn)

	def filter_tasks(self, tasks: List[Task], owner: Optional[Owner] = None, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
		"""Filter tasks by pet name and/or completion status.

		If `pet_name` is provided, `owner` must be provided to map names to pet ids.
		If `completed` is True, returns tasks that have at least one completed date; False returns not completed.
		"""
		result = list(tasks)
		if pet_name and owner:
			pet_ids = [p.id for p in owner.pets if p.name == pet_name]
			result = [t for t in result if t.pet_id in pet_ids]
		if completed is not None:
			if completed:
				result = [t for t in result if len(t.completed_dates) > 0]
			else:
				result = [t for t in result if len(t.completed_dates) == 0]
		return result

	def detect_conflicts(self, plan: Schedule) -> List[str]:
		"""Return lightweight conflict warnings for tasks scheduled at the same start time."""
		warnings: List[str] = []
		seen: Dict[str, List[Task]] = {}
		for start_time, task in plan.slots:
			key = start_time.strftime("%H:%M")
			seen.setdefault(key, []).append(task)
		for k, tasks_at_time in seen.items():
			if len(tasks_at_time) > 1:
				pet_ids = {t.pet_id for t in tasks_at_time}
				warnings.append(f"Conflict at {k}: {len(tasks_at_time)} tasks scheduled (pets: {sorted(list(pet_ids))}).")
		return warnings

	def place_tasks_into_slots(self, tasks: List[Task], windows: List[TimeWindow]) -> Schedule:
		"""Place tasks greedily into available time windows and return a Schedule."""
		# Greedy placement: sort by priority then duration and fit into windows earliest-first
		sorted_tasks = sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))
		slots: List[Tuple[time, Task]] = []
		remaining = list(sorted_tasks)
		for w in sorted(windows, key=lambda w: w.start_time):
			current_dt = datetime.combine(date.today(), w.start_time)
			end_dt = datetime.combine(date.today(), w.end_time)
			i = 0
			while i < len(remaining):
				task = remaining[i]
				# Determine earliest possible start
				earliest = task.earliest_time or current_dt.time()
				candidate_start_dt = datetime.combine(current_dt.date(), earliest)
				if candidate_start_dt < current_dt:
					candidate_start_dt = current_dt
				candidate_end_dt = candidate_start_dt + timedelta(minutes=task.duration_minutes)
				# Respect latest_time if provided
				if task.latest_time and candidate_end_dt.time() > task.latest_time:
					i += 1
					continue
				if candidate_end_dt <= end_dt:
					slots.append((candidate_start_dt.time(), task))
					current_dt = candidate_end_dt
					remaining.pop(i)
				else:
					i += 1
		# Construct schedule
		schedule = Schedule(date=date.today(), slots=slots)
		return schedule

	def explain_choice(self, plan: Schedule) -> str:
		"""Return a brief human-readable explanation of why tasks were scheduled as they were."""
		if not plan.slots:
			return "No tasks were scheduled; either none were due or they didn't fit availability."
		return f"Scheduled {len(plan.slots)} tasks, prioritizing higher-priority items and fitting tasks into available windows."

