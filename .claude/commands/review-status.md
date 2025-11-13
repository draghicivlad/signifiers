# /review-status

Reviews all project tracking files to understand the current state.

## Purpose
This command helps you quickly get context about:
- Current project status and active work
- What's on the roadmap
- Recent implementation history

## Usage
```
/review-status
```

## What It Does
1. Reads docs/STATUS.md to see current state and blockers
2. Reads docs/ROADMAP.md to see what's planned and what's done
3. Reads docs/IMPLEMENTATION_LOG.md to see recent changes
4. Provides a summary of where the project stands

## Process
Please perform the following steps:

1. Read docs/STATUS.md
2. Read docs/ROADMAP.md  
3. Read the most recent entries in docs/IMPLEMENTATION_LOG.md
4. Provide a clear summary including:
   - Current active work
   - Any blockers
   - Next priority items from roadmap
   - Recent completions

## Output Format
Present the information clearly without emojis. Use this structure:

```
PROJECT STATUS REVIEW
====================

CURRENT STATE:
[Summary from STATUS.md]

ACTIVE WORK:
[What's being worked on now]

BLOCKERS:
[Any issues blocking progress]

NEXT PRIORITIES:
[Top 3-5 items from roadmap]

RECENT COMPLETIONS:
[Last few completed items]
```
