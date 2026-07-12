---
name: phase-cycle
description: "Trigger: nueva fase, iniciar fase, phase start, fase N. Workflow de implementación por fases del ROADMAP de Hatsik."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## Activation Contract

Activate when:
- Starting a new ROADMAP phase (Phase 1–6)
- Resuming work on an in-progress phase
- Asking about phase status or next steps

Do not activate for bug fixes, hotfixes, or work outside the ROADMAP phases.

## Hard Rules

- Every phase follows the EXACT same lifecycle. No shortcuts.
- Implementation NEVER starts without explicit user approval of the spec.
- One phase completes entirely before the next begins.
- The branch naming convention is `phase-{N}/{slug}` (e.g., `phase-1/foundation`).
- All specs live in `.kiro/specs/phase-{N}-{slug}/` using Kiro's native format.

## Phase Lifecycle

```
┌─────────────────────────────────────────────────┐
│  1. SPEC (Planning & Documentation)             │
│     → requirements.md (user stories, criteria)  │
│     → design.md (technical decisions)           │
│     → tasks.md (granular implementation tasks)  │
├─────────────────────────────────────────────────┤
│  2. APPROVAL GATE                               │
│     → Present spec summary to user              │
│     → STOP. Wait for explicit approval.         │
├─────────────────────────────────────────────────┤
│  3. BRANCH                                      │
│     → Create branch: phase-{N}/{slug}           │
│     → Base: main (or previous phase branch)     │
├─────────────────────────────────────────────────┤
│  4. IMPLEMENT                                   │
│     → Follow tasks.md step by step              │
│     → Work-unit commits per logical chunk       │
│     → Run tests/verification per task           │
├─────────────────────────────────────────────────┤
│  5. VERIFY                                      │
│     → All done criteria from ROADMAP pass       │
│     → All tasks.md items checked off            │
│     → Tests pass, lint clean, build succeeds    │
├─────────────────────────────────────────────────┤
│  6. REPORT                                      │
│     → Phase completion summary                  │
│     → What was built, what was tested           │
│     → PR or merge to main                       │
│     → Engram mem_save with phase results        │
└─────────────────────────────────────────────────┘
```

## Decision Gates

| Situation | Action |
|-----------|--------|
| Phase has Stitch screens | Reference screen IDs in requirements.md |
| Phase has no UI (e.g., Phase 1) | Skip screen references, focus on infra criteria |
| Task is too large for one commit | Split into sub-tasks in tasks.md |
| Blocker found during implementation | Stop, document in report, ask user |
| Done criteria ambiguous | Clarify with user BEFORE implementing |

## Execution Steps

1. Read `docs/ROADMAP.md` for the target phase's "What gets built" and "Done criteria".
2. Read related docs (`DATABASE_SCHEMA.md`, `ARCHITECTURE_AND_STACK.md`, `UI_UX_SPEC.md`) as needed.
3. Generate `.kiro/specs/phase-{N}-{slug}/requirements.md` — user stories mapped to done criteria.
4. Generate `.kiro/specs/phase-{N}-{slug}/design.md` — technical decisions, patterns, dependencies.
5. Generate `.kiro/specs/phase-{N}-{slug}/tasks.md` — ordered, granular, checkable tasks.
6. Present summary and STOP for approval.
7. After approval: create branch, implement, verify, report.

## Output Contract

Each phase produces:
- `.kiro/specs/phase-{N}-{slug}/requirements.md`
- `.kiro/specs/phase-{N}-{slug}/design.md`
- `.kiro/specs/phase-{N}-{slug}/tasks.md`
- Branch: `phase-{N}/{slug}`
- Engram memory: phase completion state

## References

- `docs/ROADMAP.md` — phase definitions and done criteria
- `docs/ARCHITECTURE_AND_STACK.md` — stack and folder structure
- `docs/DATABASE_SCHEMA.md` — full database schema
- `docs/UI_UX_SPEC.md` — design tokens and UI patterns
- `docs/hatsik-brand-identity.md` — brand colors and typography
