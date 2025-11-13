# /update-roadmap

Updates the project ROADMAP.md with task status changes or new tasks.

## Purpose
Keep the roadmap current by:
- Marking tasks as started [IN PROGRESS]
- Marking tasks as completed [DONE]
- Adding new tasks
- Reorganizing priorities

## Usage
```
/update-roadmap
```

## What It Does
Interactively helps you update docs/ROADMAP.md by:
- Marking tasks as in progress or completed with dates
- Adding new tasks to appropriate priority sections
- Moving completed tasks to archive

## Process

1. Read current docs/ROADMAP.md

2. Ask the user what update is needed:
   - Mark a task as started? (add [IN PROGRESS] and date)
   - Mark a task as completed? (change to [DONE] and add date)
   - Add a new task?
   - Move a task between priority levels?

3. Based on the user's choice, make the appropriate update:

   **For starting a task:**
   - Change [ ] to [IN PROGRESS]
   - Add start date: (YYYY-MM-DD)
   
   **For completing a task:**
   - Change [IN PROGRESS] to [DONE]
   - Add completion date: (YYYY-MM-DD)
   
   **For adding a task:**
   - Ask for: task name, description, priority level
   - Add to appropriate section with [ ] status
   
   **For moving a task:**
   - Move task to different priority section

4. Update the file

5. Optionally suggest moving completed tasks to "Completed Archive" section to keep active roadmap clean

## Guidelines
- Use date format: YYYY-MM-DD
- Keep task descriptions clear and actionable
- Group related tasks together
- No emojis
- Maintain consistent formatting

## Example Interaction

User runs: `/update-roadmap`

You ask:
```
What would you like to update in the roadmap?
1. Mark a task as started
2. Mark a task as completed
3. Add a new task
4. Move a task between priorities
5. Archive completed tasks
```

User chooses option, provides details, and you update the file accordingly.

## Task Format Example

```
### Feature Name
- [ ] Task description
- [IN PROGRESS] Another task (2025-11-11)
- [DONE] Completed task (2025-11-10)
```
