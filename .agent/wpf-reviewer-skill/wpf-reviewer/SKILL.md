---
name: wpf-reviewer
description: review wpf and mvvm toolkit code for binding quality, command flow, separation of concerns, maintainability, and desktop usability. use when the user wants a checklist review, targeted fixes, or architecture guidance for xaml and c# in a wpf app. prefer pasted code as the source of truth, then use github connector context to understand related views, viewmodels, and services.
---

# WPF Reviewer

## Overview
Review WPF code with attention to MVVM Toolkit alignment, binding quality, maintainability, and user experience in desktop workflows. Keep guidance concrete and patch-oriented.

## Source Priority
1. Treat pasted XAML and C# as the primary review target.
2. Use GitHub connector context to inspect related views, ViewModels, commands, services, and resource dictionaries.
3. Use assumptions only when required to explain a likely issue.

## Review Areas
Check the relevant categories only:
- binding correctness and clarity
- command design and enablement flow
- View vs ViewModel responsibility split
- validation and error presentation
- code-behind creep
- layout maintainability
- naming and state management
- desktop interaction quality

## Workflow
1. Find correctness issues first, especially broken bindings or unstable command flow.
2. Identify maintainability problems next.
3. Recommend the smallest changes that improve future development speed.
4. Show changed blocks when a direct fix is practical.

## Output Contract
Use this structure by default:

### Checklist review
- bindings
- commands
- MVVM separation
- maintainability
- desktop usability

### High-impact findings
Explain what is wrong, where it appears, and how to fix it.

### Suggested code changes
Provide only changed XAML or C# blocks when a patch is straightforward.

### Architecture note
Add a brief structural recommendation only when necessary.
