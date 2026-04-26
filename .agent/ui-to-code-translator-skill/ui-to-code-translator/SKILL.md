---
name: ui-to-code-translator
description: translate a screenshot or mockup into react, next.js, or wpf implementation patches. use when the user provides an image and wants code that matches the layout, sections, and interaction structure of the design. prefer the image and pasted code as the source of truth, then use github connector context to fit the generated patch into the existing codebase. return only the blocks that need to change unless the user asks for full files.
---

# UI To Code Translator

## Overview
Translate screenshots or mockups into implementation-ready UI patches for React, Next.js, or WPF projects. Reconstruct layout and hierarchy carefully, then fit the result into the existing codebase with minimal disruption.

## Source Priority
1. Treat the image and any pasted code as the primary source of truth.
2. Use the user's named target file, framework, and styling conventions.
3. Use GitHub connector context to inspect adjacent components, shared controls, and theme patterns.
4. State minimal assumptions for any behavior the image does not reveal.

## Workflow
1. Identify the target stack: React, Next.js, or WPF.
2. Break the image into sections, repeated elements, and likely components.
3. Map visual structure to the project's existing component or view model patterns.
4. Implement only the changed blocks by default.
5. Note missing interactions or states briefly.

## Translation Rules
Always preserve:
- layout hierarchy
- spacing and alignment intent
- text grouping and label relationships
- accessibility basics for forms and actions
- reusable component opportunities when obvious

Avoid inventing detailed interactions that are not visible in the image unless the user asks.

## Output Contract
Default response structure:
1. A short mapping note from image sections to code structure.
2. Changed files only.
3. Only the modified blocks.
4. A brief note for any assets, icons, or data states that are implied but not shown.

## Good Fits
- convert a profile screen screenshot into React component patches
- map a dashboard mockup into WPF XAML and ViewModel changes
- restyle an existing page to match a provided image while keeping current logic
