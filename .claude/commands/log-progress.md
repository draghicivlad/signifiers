# /log-progress

Logs completed work to IMPLEMENTATION_LOG.md

## Purpose
Document what was implemented, in which files, and any important decisions or notes.

## Usage
```
/log-progress [optional: brief description]
```

## What It Does
Adds a new entry to docs/IMPLEMENTATION_LOG.md documenting:
- Date
- Feature/task that was completed
- Files that were modified
- Description of changes
- Important notes or decisions

## Process

1. Ask the user for details about the work completed:
   - What feature or task was completed?
   - Which files were created or modified?
   - Brief description of the changes
   - Any important notes or decisions?

2. Format the entry following the template:
```
## YYYY-MM-DD

### [Feature/Task Name]
**Files:** 
- path/to/file1.py
- path/to/file2.py

**Description:**
[What was implemented and why]

**Notes:**
- [Important decisions]
- [Trade-offs considered]
- [Future improvements needed]
```

3. Add the entry to docs/IMPLEMENTATION_LOG.md (prepend it after the current log entries, maintaining chronological order with newest first)

4. Ask if the user wants to also update STATUS.md and ROADMAP.md to reflect this completion

## Additional Updates

After logging, suggest:
- Updating docs/STATUS.md to move completed work to "Recent Changes"
- Updating docs/ROADMAP.md to mark tasks as [DONE] with completion date

## Guidelines
- Be specific about file paths
- Include meaningful descriptions
- Capture important technical decisions
- Note any future work or improvements needed
- No emojis
- Use clear, professional language

## Example

User runs: `/log-progress`

You ask:
```
What work was completed?
1. Feature/task name:
2. Files created or modified:
3. Brief description of changes:
4. Any important notes or decisions:
```

User provides details, you create the log entry, and offer to update other tracking files.
