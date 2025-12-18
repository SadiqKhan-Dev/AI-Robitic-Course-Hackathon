---
id: 1
title: Create AI Book RAG Chatbot Constitution
stage: constitution
date: 2025-12-17
surface: agent
model: GPT-4
feature: ai-book-rag-chatbot
branch: main
user: user
command: sp.constitution
labels: [constitution, spec-first, ai-authoring, rag-chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
---

## Prompt

---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.


/sp.constitution Project

Unified AI‑Spec Driven Book with Integrated RAG Chatbot

Vision

Create a production‑grade, AI‑authored technical book that demonstrates modern AI‑native documentation workflows. The book must be written, structured, and maintained through specifications using Spec‑Kit Plus and Claude Code, published via Docusaurus on GitHub Pages, and enhanced with an embedded Retrieval‑Augmented Generation (RAG) chatbot that provides precise, context‑aware answers strictly grounded in the book’s content.

Core Principles

Specification‑First Authoring: All book content, structure, and behavior must originate from formal specs (Spec‑Kit Plus).

Source‑Grounded Accuracy: All explanations must be derived from the authored book content; no hallucinated or external knowledge in the chatbot.

Clarity for Technical Learners: Content must be understandable for beginner to intermediate developers with a computer science or web background.

Reproducibility: Every step (authoring, deployment, indexing, chatbot behavior) must be fully reproducible from the repository.

AI‑Native Workflow Integrity: Claude Code must be used as the primary authoring agent, guided strictly by the constitution.

Key Standards

Authoring Stack:

Documentation: Docusaurus

Specification System: Spec‑Kit Plus

AI Authoring Tool: Claude Code

Publishing:

Hosting: GitHub Pages

Version control: GitHub (public repository)

RAG Chatbot Stack:

Agent Framework: OpenAI Agents / ChatKit SDKs

Backend API: FastAPI

Vector Database: Qdrant Cloud (Free Tier)

Relational Database: Neon Serverless Postgres

Chatbot Behavior Rules:

Answers must be derived only from indexed book content

Must support question‑answering based on user‑selected text only

Must explicitly refuse questions outside the book’s scope

Responses must be concise, technical, and citation‑aware

Content Standards

Writing level: Beginner to Intermediate

Tone: Professional, instructional, and precise

Structure:

Clear chapters and sections

Progressive difficulty

Practical examples and explanations

No filler content or speculative claims

Constraints

The book must be fully generated and structured via Spec‑Kit Plus specs

Claude Code must follow specs without improvising architecture

RAG chatbot must not access external APIs for knowledge retrieval

Free‑tier compatible infrastructure only (Qdrant Free, Neon Serverless)

Deployment must require no proprietary or paid services beyond free tiers

Verification & Quality Controls

All chatbot answers must be verifiable against stored embeddings

Manual and automated checks to ensure no hallucinated responses

Book build must succeed via a clean repository clone and install

Clear README with setup, deployment, and usage instructions

Deliverables

Docusaurus Book Repository

Spec‑Kit Plus specifications

AI‑generated content via Claude Code

Clean, structured documentation

Published Documentation Site

Deployed on GitHub Pages

Publicly accessible

Integrated RAG Chatbot

Embedded UI within the documentation site

FastAPI backend with vector search

Qdrant‑indexed book content

Neon‑backed metadata and session storage

Technical Documentation

Architecture overview

RAG data flow explanation

Setup and deployment guide

Success Criteria

Book is fully spec‑driven and AI‑authored

GitHub Pages site builds and deploys successfully

RAG chatbot answers accurately using only book content

Selected‑text question answering works reliably

No hallucinated or out-of-scope responses

Repository can be cloned, built, and deployed without errors

Non‑Goals

No general‑purpose chatbot behavior

No reliance on external knowledge bases

No manual content writing outside Claude Code execution

This constitution is binding. Claude Code must follow it strictly when generating, modifying, or extending any part of the project.

## Response snapshot

The updated constitution has been created and saved to `.specify/memory/constitution.md` with the following details:

- **New version**: 1.0.0 (initial version)
- **Version bump rationale**: This is the initial creation of the project constitution based on the requirements for the Unified AI-Spec Driven Book with Integrated RAG Chatbot project
- **Files flagged for manual follow-up**: The Sync Impact Report notes that template files may need review:
  - `.specify/templates/plan-template.md`
  - `.specify/templates/spec-template.md`
  - `.specify/templates/tasks-template.md`
- **Suggested commit message**: `docs: add initial constitution for AI-spec driven book project with RAG chatbot`

The constitution includes 6 core principles along with detailed standards, workflow requirements, and governance rules as specified in your requirements.

## Outcome

- ✅ Impact: Created initial project constitution with 6 core principles and detailed standards
- 🧪 Tests: N/A (documentation task)
- 📁 Files: Updated .specify/memory/constitution.md with new constitution content
- 🔁 Next prompts: N/A
- 🧠 Reflection: The task was successfully completed following all required steps, including placeholder identification, value collection, drafting, template consistency check, validation, and file writing.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A