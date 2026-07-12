---
name: phase-close
description: "Trigger: cerrar fase, phase close, finalizar fase, commit fase, close phase. Atomic commits + HTML phase report."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## Activation Contract

Activate when:
- User says "cerrar fase", "close phase", "commit fase", "finalizar fase"
- Phase implementation is complete and needs to be wrapped up
- User wants atomic commits + final documentation for a completed phase

Do not activate for mid-phase work or individual commits (use `atomic-commits` skill directly).

## Hard Rules

- ALWAYS follow `atomic-commits` skill for every commit made.
- ALWAYS generate an HTML phase report at `docs/html/phase-{N}-report.html`.
- The HTML report uses the cognitive-doc-design template with Mermaid diagrams.
- Open the HTML file in the browser after generating it.
- Ask the user BEFORE committing if there are unstaged changes to review.

## Execution Steps

### Step 1: Audit changes

1. Run `git status` to see all modified/untracked files.
2. Run `git diff --stat` to see change volume.
3. Group changes by LOGICAL concern (one concern = one commit).
4. Present the commit plan to the user:
   ```
   Proposed commits:
   1. feat(scope): description — [files]
   2. build(scope): description — [files]
   3. docs: description — [files]
   ```
5. Wait for user approval before committing.

### Step 2: Atomic commits

For each logical group:
1. Stage ONLY the files for that group.
2. Write a Conventional Commit message (see `atomic-commits` skill).
3. Commit.
4. Repeat for next group.

### Step 3: Generate HTML Phase Report

Create `docs/html/phase-{N}-report.html` using the cognitive-doc-design template:

**Content structure:**
1. **Header** — Phase name, goal, date, status
2. **What was built** — Summary of deliverables with Mermaid architecture diagram
3. **Commits** — Table of all commits in the phase with type, scope, description
4. **Verification** — Checklist of done criteria (interactive checkboxes)
5. **Metrics** — Files changed, lines added, tests passing
6. **Next phase** — What comes next per the ROADMAP
7. **Pending items** — Anything deferred or blocked

**Mermaid diagrams to include:**
- Architecture/flow diagram of what was built
- Module dependency graph (what this phase enables)

### Step 4: Commit the report

```
docs(phase-{N}): add HTML phase completion report
```

### Step 5: Open in browser

```bash
open docs/html/phase-{N}-report.html
```

## Output Contract

Return:
- List of commits made (hash + message)
- Path to generated HTML report
- Confirmation browser was opened
- Git log showing the phase commits

## References

- `~/.kiro/skills/atomic-commits/SKILL.md` — commit format rules
- `~/.kiro/skills/cognitive-doc-design/SKILL.md` — HTML doc patterns
- `~/.kiro/skills/cognitive-doc-design/assets/html-template.html` — HTML template
- `.kiro/specs/phase-{N}-{slug}/tasks.md` — task checklist for verification
- `docs/ROADMAP.md` — phase definitions and done criteria
