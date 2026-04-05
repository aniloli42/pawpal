# PawPal+ Project Reflection

## 1. System Design
User can able to add pet
User can able to add tasks
User can able to see schedule of today
User can able to edit pet
User can able to edit tasks
User can able to delete pet
User can able to delete tasks

**a. Initial design**

- Briefly describe your initial UML design.
  - The initial UML design includes four classes: `Owner`, `Pet`, `Task`, and `Schedule`. An `Owner` holds a daily time budget and a list of pets. Each `Pet` holds a list of care `Task` objects. The `Schedule` class takes an owner and a pet, selects tasks that fit within the owner's time budget (sorted by priority), and stores both the chosen tasks and the ones that were skipped.

- What classes did you include, and what responsibilities did you assign to each?
  - **Owner** — stores owner info and daily available time; manages a list of pets.
  - **Pet** — stores pet info and manages a list of care tasks.
  - **Task** — represents a single care activity with a title, duration, priority, and category.
  - **Schedule** — acts as the planner; reads the owner's time budget, selects and orders tasks by priority, and explains why tasks were included or skipped.

**b. Design changes**

- Did your design change during implementation?
    - Yes
- If yes, describe at least one change and why you made it.
    - During creating UML using Claude, I realized that their is no implementation of id in the object which will create issue in long run, so I instructed to add id in each object.
    - Also, Implemented get each item by id method in each class.

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
