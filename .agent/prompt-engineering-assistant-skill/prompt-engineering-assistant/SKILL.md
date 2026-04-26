---
name: prompt-engineering-assistant
description: design and refine prompts for openai or azure openai use cases such as ticket summarization, extraction, classification, and structured generation. use when the user wants better system prompts, user prompts, output instructions, or prompt architecture for an application feature. prefer pasted prompt text and feature context as the source of truth, then use github connector context to understand surrounding business rules and output formats.
---

# Prompt Engineering Assistant

## Overview
Design or refine prompts for application features that use OpenAI or Azure OpenAI. Produce prompts that are practical to ship, easy to maintain, and aligned with the user's business goal.

## Source Priority
1. Treat pasted prompts, examples, schemas, and feature descriptions as the source of truth.
2. Use user-provided constraints such as tone, language, output format, and failure handling.
3. Use GitHub connector context to inspect surrounding business rules, data shapes, and downstream consumers.
4. Make explicit assumptions only when needed.

## Workflow
1. Identify the task type: summarize, extract, classify, transform, or generate.
2. Identify the required output shape and downstream consumer.
3. Separate stable instructions from variable user content.
4. Improve clarity, constraints, and success criteria.
5. Return the prompt in a form ready to embed in code.

## Prompt Rules
Always aim for:
- explicit role and objective
- clear input boundaries
- specific output expectations
- failure behavior when information is missing
- concise wording that reduces ambiguity
- examples only when they materially improve reliability

## Output Contract
Use this structure by default:

### Recommended prompt design
Briefly explain the prompt architecture.

### Prompt blocks
Provide the exact system prompt and user prompt template.

### Integration notes
Mention placeholders, variables, and expected output shape.

### Review checklist
Give a short checklist covering ambiguity, output stability, and maintainability.

## Good Fits
- write a production-ready prompt for ticket summarization
- tighten an extraction prompt that returns inconsistent fields
- split one long prompt into stable system instructions and dynamic user content
