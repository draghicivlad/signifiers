# /update-status

Updates the project STATUS.md file with current state.

## Purpose
Keep STATUS.md current with what's being worked on, blockers, and next steps.

## Usage
```
/update-status [optional: specific update notes]
```

## What It Does
Updates docs/STATUS.md with:
- Current date
- Current active work
- Any blockers
- Recent changes (keeping last 5)
- Next steps

## Process

1. Read the current docs/STATUS.md
2. Ask the user what has changed since the last update:
   - What work is now active?
   - Are there new blockers?
   - What are the next steps?
3. Update the file with new information:
   - Update "Last Updated" date
   - Update "Current State" if changed
   - Update "Active Work" section
   - Update "Blockers" section
   - Add new entry to "Recent Changes" (keep only last 5)
   - Update "Next Steps" section
4. Write the updated content back to docs/STATUS.md

## Guidelines
- Be concise but clear
- Keep "Recent Changes" to last 5 entries
- Format dates as YYYY-MM-DD
- No emojis
- Move completed items from "Active Work" to "Recent Changes"

## Example Workflow

User runs: `/update-status`

You ask:
```
What updates should I make to STATUS.md?
- What work is currently active?
- Any new blockers?
- What should the next steps be?
```

User provides updates, and you update the file accordingly.
