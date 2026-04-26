---
name: openai-integration-builder
description: build and modify openai or azure openai integrations in asp.net core, react, next.js, or wpf applications. use when the user wants provider clients, service wrappers, request shaping, response parsing, or safe api integration patterns. prefer pasted code as the source of truth, then use github connector context for surrounding architecture. return only the changed blocks by default and keep the integration consistent with the existing stack.
---

# OpenAI Integration Builder

## Overview
Implement OpenAI or Azure OpenAI integrations in .NET, React, Next.js, or WPF projects while staying aligned with the existing application's architecture and configuration style.

## Source Priority
1. Treat pasted code as the source of truth.
2. Use explicit provider details from the user: OpenAI vs Azure OpenAI, model names, endpoint style, and where the call should live.
3. Use GitHub connector context to inspect current service layers, configuration handling, secret loading, and API calling patterns.
4. Keep assumptions minimal and explicit.

## Workflow
1. Identify the host application and the correct integration boundary.
2. Decide whether the change belongs in controller, application service, background worker, UI command, or client wrapper.
3. Reuse existing configuration and HTTP abstractions when possible.
4. Implement only the blocks required for the requested integration.
5. Mention required environment variables or options bindings briefly.

## Integration Rules
Prefer:
- server-side provider calls for secrets whenever possible
- thin controller endpoints with service-level orchestration
- typed request and response models when the project already uses them
- centralized configuration for endpoint, deployment, model, and key names
- concise prompt assembly that is easy to test

## Output Contract
Default response structure:
1. One short implementation note.
2. Changed files only.
3. Only modified blocks.
4. A short configuration note listing the exact environment variables or app settings needed.

## Good Fits
- integrate Azure OpenAI into a .NET service
- add a prompt-based summary endpoint
- wire a frontend call to an existing AI backend endpoint
- refactor raw API calls into a dedicated service wrapper
