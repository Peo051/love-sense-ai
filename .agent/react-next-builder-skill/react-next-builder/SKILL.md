---
name: react-next-builder
description: build and modify react or next.js ui code from feature requests, pasted code, existing repo context, or screenshot-driven ui changes. use when the user wants components, pages, forms, api wiring, layout refactors, or responsive improvements. prefer pasted code as the source of truth, then use github connector for surrounding context. return only the blocks that need to change unless the user explicitly asks for full files.
---

# React Next Builder

## Overview
Build or modify React and Next.js code from user requests, pasted code, screenshots, and repository context. Focus on practical implementation that can be pasted directly into the user's codebase with minimal editing.

## Source Priority
Use this order whenever multiple sources exist:
1. Treat code pasted in chat as the source of truth.
2. Use file paths, snippets, and constraints the user names explicitly.
3. Use GitHub connector context to understand surrounding components, hooks, routes, and styles.
4. Make minimal assumptions only when required, and label them.

## Workflow
1. Identify whether the task is creation, modification, refactor, or bug fix.
2. Infer the stack details that matter: React vs Next.js, App Router vs Pages Router when visible, styling approach, state management, and data fetching pattern.
3. Reuse existing naming, folder structure, component boundaries, and styling conventions from pasted code or repo context.
4. Implement the smallest safe change that satisfies the request.
5. Return only the code blocks that need to change by default.

## Screenshot-to-UI Handling
When the user provides a UI image:
- Extract layout hierarchy before writing code.
- Map visible sections to reusable components.
- Preserve spacing, alignment, and responsive behavior.
- Prefer semantic HTML and accessible form controls.
- Note any missing interaction states briefly.

## Output Contract
Default response structure:
1. One short note on the approach.
2. A file-by-file list only for changed files.
3. For each file, provide only the changed block.
4. Add a short integration note only if the patch depends on a route, prop, hook, or API that is not obvious.

Do not rewrite entire files unless the user explicitly asks for full files.
Do not invent libraries, hooks, or design systems that are not present in the pasted code or repo context.

## Quality Bar
Always optimize for:
- clean component boundaries
- readable props and state flow
- accessible markup
- responsive layout
- minimal diffs
- consistency with the existing codebase

## Good Fits
- convert a profile screen from an image into a React component
- modify a Next.js page while touching only the needed blocks
- add a form section and wire it to an existing API hook
- refactor a large component into smaller parts without changing behavior
