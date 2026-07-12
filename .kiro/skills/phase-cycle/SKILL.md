---
name: phase-cycle
description: "Trigger: nueva fase, iniciar fase, phase start, fase N. Workflow de implementación por fases del ROADMAP de Hatsik."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.1"
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

## Stitch Design Fidelity Rules (MANDATORY)

### Before implementing ANY template/UI:

1. **ALWAYS fetch the Stitch screen** via MCP `get_screen` using the screen ID from `docs/ROADMAP.md`.
2. **Download the HTML code** from the screen's `htmlCode.downloadUrl` to see the exact structure.
3. **Match the design pixel-for-pixel** — layout, spacing, icons, text hierarchy, colors.
4. **Respect Stitch's element decisions:**
   - If Stitch has icons in inputs → implement icons in inputs (use Material Icons or inline SVGs)
   - If Stitch has a specific button style (icon + text) → replicate exactly
   - If Stitch shows a fullscreen auth layout (no nav header) → use a separate base template without nav
   - If Stitch has decorative elements → include them
   - If Stitch has a visibility toggle on password → implement it
5. **Omit Stitch elements that are out-of-scope** but document why:
   - "Continuar con Google" → out of scope for MVP, omit entirely (don't show disabled)
   - "Contactar soporte" → out of scope, omit
6. **Auth pages are standalone** — they do NOT use the main app header/nav. Use a dedicated `auth-base.html` template that only has the Hatsik logo centered.

### Stitch Project Reference

- **Project ID:** `17560302013947311339`
- **Design System:** `assets/4b0bfd162b1d461cbdd85c1d0ab945ef` (Warm Kitchen Board)

### Screen IDs (Phase 2)

| Screen | ID |
|---|---|
| Iniciar Sesión | `31616452da9645128f2c492244260487` |
| Registro de Usuario | `4e62e0c5470344a8acba2468d6b8cecd` |
| Verificación Pendiente | `8612ccf1e1304ff9bd3a5090ddf8f9c7` |
| Recuperar Contraseña | `b533a824d16a4fd39fcc7135a1404392` |

## Language Rules (MANDATORY)

### Code & Technical Artifacts — ENGLISH

Everything that lives in source code MUST be in English:
- Variable names, function names, class names, module names
- Comments and docstrings
- Commit messages (Conventional Commits format)
- Test names and test descriptions
- Django model fields, URL names, view function names
- Form field names (`display_name`, `password_confirm`, NOT `nombre_mostrar`)
- Error codes and internal constants
- README technical content, architecture docs, specs (requirements.md, design.md, tasks.md)
- Git branch names

### User-Facing UI — SPANISH

Everything the end user SEES in the browser MUST be in Spanish:
- Template text content (headings, paragraphs, labels)
- Form labels displayed to the user (`Nombre`, `Correo electrónico`, `Contraseña`)
- Button text (`Crear cuenta`, `Iniciar sesión`, `Enviar`)
- Error messages shown to users (`Correo o contraseña incorrectos`)
- Success/info/warning toast messages
- Navigation text, page titles in `<title>` tags
- Placeholder text in inputs (`tu@correo.com`, `Mínimo 8 caracteres`)
- Empty states and help text
- Email subject lines and body content sent to users

### Boundary Rules

| Context | Language | Example |
|---------|----------|---------|
| Django form class field name | English | `password_confirm` |
| Django form `label` kwarg (rendered in HTML) | Spanish | `label="Confirmar contraseña"` |
| Django form widget `placeholder` | Spanish | `"Repetir contraseña"` |
| Template `{% block title %}` content | Spanish | `Registro — Hatsik` |
| URL path segments | English kebab-case | `/password-reset/` |
| URL name | English snake_case | `password_reset_request` |
| Python validation error message | Spanish (user sees it) | `"Las contraseñas no coinciden."` |
| Python `ValidationError.code` | English | `code="passwords_do_not_match"` |
| HTML `id` and `class` attributes | English | `id="resend-section"` |
| ARIA labels | Spanish | `aria-label="Cerrar modal"` |
| `alt` text on images | Spanish | `alt="Logo de Hatsik"` |
| Commit messages | English | `feat(accounts): add login view` |
| HTML phase report content | Spanish | (user documentation) |

### TL;DR

> Código piensa en inglés. La pantalla habla español.

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
│  6. TESTING DOC                                 │
│     → Generate HTML testing guide               │
│     → Step-by-step manual QA instructions       │
│     → Save to docs/html/phase-{N}-testing.html  │
│     → Open in browser for user to follow        │
├─────────────────────────────────────────────────┤
│  7. REPORT (via phase-close skill)              │
│     → Atomic commits                            │
│     → Phase completion HTML report              │
│     → PR or merge to main                       │
│     → Engram mem_save with phase results        │
└─────────────────────────────────────────────────┘
```

## Testing Doc Generation (Step 6)

After implementation is complete and all automated tests pass, generate a manual testing guide as an HTML file.

### Purpose

This document lets the user (or a QA person) manually verify EVERY user-facing feature built in the phase by following step-by-step instructions in the browser.

### File Location

`docs/html/phase-{N}-testing.html`

### Content Structure (ALL in Spanish)

1. **Encabezado** — Phase name, goal, prerequisite setup instructions
2. **Requisitos previos** — How to start the dev server, seed data if needed
3. **Flujos de prueba** — One section per user story / feature:
   - Título del flujo
   - Precondiciones (state needed before testing)
   - Pasos numerados (click X, fill Y, expect Z)
   - Resultado esperado (what should happen)
   - Screenshot placeholder or visual reference
   - ✅ Checkbox to mark as verified
4. **Casos límite** — Edge cases to try manually:
   - Rate limiting behavior
   - Invalid input responses
   - Expired tokens
   - Concurrent actions
5. **Errores conocidos / Limitaciones** — Anything the user should know
6. **Checklist final** — All ROADMAP "Done criteria" as interactive checkboxes

### HTML Template Rules

- Self-contained single HTML file (inline CSS, no external deps except optional CDN for icons)
- Responsive design (usable on mobile for testing on device)
- Use the Hatsik brand tokens (colors, fonts) for visual consistency
- Interactive checkboxes that persist state via `localStorage`
- Collapsible sections for long flows
- Print-friendly (can be printed as a QA checklist)
- Mermaid diagrams for flow visualization where helpful

### Example Flow Section Structure

```html
<section class="test-flow">
  <h3>🔐 Registro de usuario</h3>
  <p class="preconditions">Precondiciones: No estar logueado. Servidor corriendo en localhost:8000.</p>
  <ol class="steps">
    <li>Navegar a <code>http://localhost:8000/register/</code></li>
    <li>Completar: Nombre = "Test User", Email = "test@correo.com", Contraseña = "segura123", Confirmar = "segura123"</li>
    <li>Click en "Crear cuenta"</li>
    <li><strong>Esperado:</strong> Redirige a pantalla de verificación pendiente</li>
    <li>Verificar en consola que el email de verificación fue enviado (o revisar logs de Resend)</li>
  </ol>
  <label class="checkbox"><input type="checkbox" data-test="register-happy-path"> Verificado ✓</label>
</section>
```

## Decision Gates

| Situation | Action |
|-----------|--------|
| Phase has Stitch screens | Reference screen IDs in requirements.md |
| Phase has no UI (e.g., Phase 1) | Skip screen references, focus on infra criteria |
| Task is too large for one commit | Split into sub-tasks in tasks.md |
| Blocker found during implementation | Stop, document in report, ask user |
| Done criteria ambiguous | Clarify with user BEFORE implementing |
| Phase has UI flows | Testing doc MUST cover every screen interaction |
| Phase is infra-only | Testing doc covers CLI/API verification steps |

## Execution Steps

1. Read `docs/ROADMAP.md` for the target phase's "What gets built" and "Done criteria".
2. Read related docs (`DATABASE_SCHEMA.md`, `ARCHITECTURE_AND_STACK.md`, `UI_UX_SPEC.md`) as needed.
3. Generate `.kiro/specs/phase-{N}-{slug}/requirements.md` — user stories mapped to done criteria.
4. Generate `.kiro/specs/phase-{N}-{slug}/design.md` — technical decisions, patterns, dependencies.
5. Generate `.kiro/specs/phase-{N}-{slug}/tasks.md` — ordered, granular, checkable tasks.
6. Present summary and STOP for approval.
7. After approval: create branch, implement, verify.
8. **Generate testing doc** (`docs/html/phase-{N}-testing.html`) and open in browser.
9. Close phase via `phase-close` skill (atomic commits, report, PR).

## Output Contract

Each phase produces:
- `.kiro/specs/phase-{N}-{slug}/requirements.md`
- `.kiro/specs/phase-{N}-{slug}/design.md`
- `.kiro/specs/phase-{N}-{slug}/tasks.md`
- `docs/html/phase-{N}-testing.html` ← **NEW: manual QA guide**
- Branch: `phase-{N}/{slug}`
- Engram memory: phase completion state

## References

- `docs/ROADMAP.md` — phase definitions and done criteria
- `docs/ARCHITECTURE_AND_STACK.md` — stack and folder structure
- `docs/DATABASE_SCHEMA.md` — full database schema
- `docs/UI_UX_SPEC.md` — design tokens and UI patterns
- `docs/hatsik-brand-identity.md` — brand colors and typography
