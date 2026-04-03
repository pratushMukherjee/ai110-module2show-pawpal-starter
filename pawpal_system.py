from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any, Set, Tuple


@dataclass
class TimeWindow:
	start_time: time
	end_time: time
	weekdays: Set[int] = field(default_factory=set)

	def contains(self, dt: datetime) -> bool:
		"""Return True if datetime `dt` falls inside this window."""
		raise NotImplementedError()

	def intersect(self, other: "TimeWindow") -> Optional["TimeWindow"]:
		"""Return intersection of two time windows or None."""
		raise NotImplementedError()


@dataclass
class Owner:
	id: int
	name: str
	contact: Optional[str] = None
	availability: List[TimeWindow] = field(default_factory=list)
	preferences: Dict[str, Any] = field(default_factory=dict)
	timezone: Optional[str] = None

	def update_preferences(self, preferences: Dict[str, Any]) -> None:
		raise NotImplementedError()

	def set_availability(self, windows: List[TimeWindow]) -> None:
		raise NotImplementedError()

	def add_pet(self, pet: "Pet") -> None:
		raise NotImplementedError()

	def get_available_windows(self, on_date: date) -> List[TimeWindow]:
		raise NotImplementedError()


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

	def update_info(self, **data: Any) -> None:
		raise NotImplementedError()

	def add_task_template(self, task_template: "Task") -> None:
		raise NotImplementedError()

	def needs_medication_on(self, on_date: date) -> bool:
		raise NotImplementedError()


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
		raise NotImplementedError()

	def next_occurrence(self, after_date: date) -> Optional[date]:
		raise NotImplementedError()

	def mark_complete(self, on_date: date) -> None:
		raise NotImplementedError()

	def overlaps_with(self, other: "Task") -> bool:
		raise NotImplementedError()


class TaskManager:
	def __init__(self) -> None:
		self.tasks: List[Task] = []
		self.task_templates: List[Task] = []

	def add_task(self, task: Task) -> None:
		raise NotImplementedError()

	def edit_task(self, task_id: int, **fields: Any) -> None:
		raise NotImplementedError()

	def delete_task(self, task_id: int) -> None:
		raise NotImplementedError()

	def get_tasks_for_date(self, on_date: date) -> List[Task]:
		raise NotImplementedError()

	def get_tasks_for_pet(self, pet_id: int) -> List[Task]:
		raise NotImplementedError()


@dataclass
class Schedule:
	date: date
	slots: List[Tuple[time, Task]] = field(default_factory=list)
	total_duration: int = 0
	score: float = 0.0
	explanation: Optional[str] = None

	def to_display(self) -> Dict[str, Any]:
		raise NotImplementedError()

	def get_tasks(self) -> List[Task]:
		return [t for _, t in self.slots]

	def serialize(self) -> Dict[str, Any]:
		raise NotImplementedError()


class Scheduler:
	def __init__(self, constraints: Optional[Dict[str, Any]] = None, scoring_rules: Optional[Dict[str, float]] = None) -> None:
		self.constraints = constraints or {}
		self.scoring_rules = scoring_rules or {}

	def generate_daily_plan(self, on_date: date, tasks: List[Task], owner: Owner) -> Schedule:
		raise NotImplementedError()

	def score_task(self, task: Task, context: Dict[str, Any]) -> float:
		raise NotImplementedError()

	def place_tasks_into_slots(self, tasks: List[Task], windows: List[TimeWindow]) -> Schedule:
		raise NotImplementedError()

	def explain_choice(self, plan: Schedule) -> str:
		raise NotImplementedError()

