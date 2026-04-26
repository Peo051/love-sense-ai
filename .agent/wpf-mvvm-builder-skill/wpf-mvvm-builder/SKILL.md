---
name: wpf-mvvm-builder
description: build and modify wpf screens and mvvm toolkit code for views, viewmodels, bindings, commands, dialogs, and desktop workflows. use when the user wants xaml or c# changes in a wpf app that follows mvvm toolkit patterns. prefer pasted code as the source of truth, then use github connector context for surrounding view, viewmodel, and service patterns. return only the blocks that need to change by default.
---

# WPF MVVM Builder

## Overview
Build or modify WPF code for applications that follow MVVM Toolkit patterns. Keep the UI and ViewModel responsibilities clean and return patches that slot into the existing desktop application with minimal friction.

## Source Priority
1. Treat pasted XAML and C# as the source of truth.
2. Use explicit file names, control names, and workflow descriptions from the user.
3. Use GitHub connector context to inspect related views, ViewModels, services, dialogs, and styles.
4. Make minimal assumptions and label them.

## Workflow
1. Determine whether the request affects the View, ViewModel, command flow, navigation, dialog handling, or validation.
2. Identify the established MVVM Toolkit pattern in the existing code.
3. Keep UI logic in XAML and presentation behavior in the ViewModel unless the current project already uses a different convention.
4. Return only the changed blocks by default.

## WPF Guidelines
Prefer:
- observable properties and relay commands consistent with MVVM Toolkit
- clear binding names
- reusable DataTemplates and styles when already used
- minimal code-behind
- predictable dialog and navigation flow
- desktop-friendly validation and loading states

## Output Contract
Default response structure:
1. One short implementation note.
2. Changed files only.
3. Only the modified XAML or C# blocks.
4. A brief note if a new command, service registration, or resource dictionary entry is required.

## Good Fits
- build a profile screen from a mockup
- wire a save command into an existing ViewModel
- add validation state to a form
- restructure bindings without rewriting the whole window
