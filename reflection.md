# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Add a pet: Create a pet profile (name, species, age, owner preferences).
Manage tasks: Add/edit/delete care tasks (type, duration, priority, recurrence).
Generate today's plan: Create and view a prioritized daily schedule with explanations.

- Briefly describe your initial UML design.

I designed a small, modular UML: data classes (Owner, Pet, Task) hold profiles and task details, TaskManager handles CRUD, and Scheduler with TimeWindow/Schedule handles planning against availability. This separation keeps data, management, and planning responsibilities isolated for easier testing and iteration.

- What classes did you include, and what responsibilities did you assign to each?
I modeled PawPal+ with simple objects: Owner and Pet hold profiles, Task represents care actions, TaskManager handles CRUD, and Scheduler builds a daily Schedule from tasks + availability.
In short: data (owners/pets/tasks), management (TaskManager), and planning (Scheduler) — each with a single clear responsibility.
**b. Design changes**

I added an explicit `pets` list to `Owner` and implemented basic `TaskManager` methods so tasks can be linked to pets and queried by date. This simplifies lookups and reduces scheduler complexity when selecting tasks for a given owner and day.



---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

- The scheduler enforces **owner availability windows** (when tasks may be placed), **task priority** (higher-priority items are placed first), **task duration** (to ensure tasks fit in windows), and simple **earliest/latest** time constraints on tasks. It also respects basic **recurrence** semantics when deciding which tasks are due.

- How did you decide which constraints mattered most?

- I prioritized feasibility and importance: owner availability and task priority directly determine whether a task can and should be scheduled, so they drive placement decisions. Duration and earliest/latest constraints are used to ensure scheduled items fit the owner's time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

- The scheduler uses a greedy, priority-first placement strategy rather than attempting an exhaustive, optimal scheduling search.

- Why is that tradeoff reasonable for this scenario?

- This tradeoff keeps the algorithm simple, fast, and predictable for users; it avoids complex combinatorial search (which can be slow and hard to explain) while delivering good practical results for everyday pet-care planning.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used VS Code Copilot and the Chat assistant extensively: Copilot helped generate class skeletons, docstrings, and unit-test scaffolding; the chat assisted with algorithm ideas (greedy placement, simple conflict detection) and small refactors. Prompts that worked well were concrete requests ("implement Task.mark_complete recurrence handling") and small, testable steps ("add a test that marks a task complete").

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I rejected an AI suggestion to attempt an exhaustive scheduling search (optimal placement) because it would add complexity and risk to the starter project; instead I implemented a greedy, predictable algorithm that is easy to reason about and test. I verified alternatives by writing quick scripts in `main.py` and unit tests.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested core behaviors: task completion bookkeeping, pet-task association, sorting by time, recurrence (creating the next occurrence), and conflict warnings for identical start times. These tests focus on correctness of the scheduling primitives the UI relies on.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am reasonably confident in core behaviors (4/5). Next tests would exercise overlapping-duration conflicts, timezone handling, and resilience when availability windows are small or empty.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Separating the scheduling logic from the UI made iterative development straightforward — I could unit-test algorithms without Streamlit. The AI collaboration accelerated scaffolding and helped brainstorm tradeoffs.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve recurrence handling (store explicit next-due dates), add robust overlap detection, and persist state to disk or a lightweight DB to survive server restarts.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI is a powerful assistant for scaffolding and iteration, but the human must remain the architect: choose tradeoffs, keep complexity manageable, and verify behaviors with tests.



