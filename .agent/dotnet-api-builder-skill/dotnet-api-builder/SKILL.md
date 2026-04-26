---
name: dotnet-api-builder
description: build and modify asp.net core web api code for endpoints, services, validation, auth, file upload flows, and integration layers. use when the user wants controller, service, dto, or infrastructure changes in an existing .net api. prefer pasted code as the source of truth, then use github connector context for surrounding architecture. return only the blocks that need to change unless the user asks for full files.
---

# Dotnet API Builder

## Overview
Build or modify ASP.NET Core Web API code in a way that fits the existing solution structure, naming, and dependency boundaries. Favor small, production-usable patches.

## Source Priority
1. Treat pasted code as the source of truth.
2. Use explicitly mentioned file paths and project conventions.
3. Use GitHub connector context to inspect controllers, services, DTOs, validators, storage abstractions, and startup wiring.
4. Make the smallest necessary assumptions and state them briefly.

## Workflow
1. Determine the change type: endpoint, business logic, validation, integration, or infrastructure.
2. Identify the current architectural pattern from the provided code or repo context.
3. Reuse existing abstractions before adding new ones.
4. Keep the change scoped to the user's request.
5. Return only the modified blocks by default.

## Backend Conventions
Prefer:
- async all the way for I/O
- explicit request and response DTOs when they already exist in the codebase
- dependency injection through existing registration patterns
- validation close to the request boundary
- consistent error handling with the existing style
- clear file upload handling and storage abstraction for binary assets

## Output Contract
Default response structure:
1. One short implementation note.
2. Changed files only.
3. Only the modified blocks for each file.
4. A short note for any required registration, environment variable, or storage dependency.

Do not rewrite the whole API layer unless asked.
Do not introduce new architecture layers unless the user requests a larger redesign.

## Good Fits
- add an avatar upload endpoint
- wire a new service into an existing controller
- add request validation and response shaping
- integrate a provider client into an existing application service
