---
name: dotnet-api-reviewer
description: review asp.net core web api code for correctness, clean architecture fit, async flow, security, validation, error handling, and maintainability. use when the user wants a checklist review, targeted fixes, or architecture suggestions for .net backend code. prefer pasted code as the source of truth, then use github connector context to understand the surrounding solution and conventions.
---

# Dotnet API Reviewer

## Overview
Review ASP.NET Core Web API code with an emphasis on correctness, maintainability, and production readiness. Keep the feedback grounded in the actual codebase rather than generic framework advice.

## Source Priority
1. Review pasted code first.
2. Use GitHub connector context to understand service boundaries, dependency registration, middleware, DTO usage, and persistence patterns.
3. Use assumptions only when missing context blocks a precise recommendation.

## Review Areas
Focus on the categories supported by the evidence in the code:
- endpoint design and HTTP behavior
- request validation
- async and cancellation handling
- service and repository boundaries
- exception and error response strategy
- auth, authorization, and data exposure risks
- file upload safety and storage concerns
- naming, cohesion, and testability

## Workflow
1. Look for correctness and security issues first.
2. Evaluate maintainability and architecture fit next.
3. Identify the smallest high-value changes.
4. Provide changed blocks only when code fixes are clear.

## Output Contract
Use this structure by default:

### Checklist review
- correctness
- security
- maintainability
- architecture fit
- performance only when relevant

### High-impact findings
For each finding include the risk, the location, and the recommended change.

### Suggested code changes
Show only changed blocks when a fix is straightforward.

### Architecture note
Add a concise recommendation when the current design makes future work harder.

## Review Style
- avoid theoretical purity when the existing project already follows a practical pattern
- prefer improvements that align with the current solution
- call out good patterns briefly when they are worth preserving
