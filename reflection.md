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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
