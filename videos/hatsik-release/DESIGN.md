# Design System — Hatsik

## Overview

Hatsik is a warm, friendly collaborative-logistics app for organizing get-togethers ("convivios"). The visual identity is light and approachable: cream/off-white surfaces, near-black text, and a single bold brick-red accent used for CTAs and brand moments. Layout patterns are card-driven (event cards with food photography, item lists with status chips, participant lists with avatar initials). Status is communicated through soft pastel chips (green = comprado, amber = parcial). The tone is human and casual — headline copy speaks in first person ("¿qué llevo?").

## Colors

- **Brand Red (Primary)**: `#B51D0C` — CTAs, logo, links, progress bars, key highlights.
- **Ink**: `#1C1B1B` — all headings and body text.
- **Cream Background**: `#FCF9F8` — page background, warm off-white.
- **Card White**: `#FFFFFF` — cards and elevated surfaces.
- **Red Tint**: `#FDE8E4` — soft red wash for active states / highlighted rows.
- **Warm Neutral**: `#5B403B` — secondary text, muted brown.
- **Success Green**: `#4BDC82` / chip bg `#DCFCE7` — "Comprado" status.
- **Warning Amber**: `#FDBA74` / chip bg `#FEF3C7` — "Parcialmente comprado".
- **Border Quiet**: `#EAE7E7` — card borders and dividers.

## Typography

- **Display**: Nunito (700, 800). Rounded, friendly headings. Hero at 56px/700.
- **Body/UI**: Plus Jakarta Sans (400, 600, 700). Body 16px, section headings 28px/700, card titles 20px/700.
- **Icons**: Material Symbols Outlined (variable 100–700), used inline with labels.

## Elevation

Flat and soft: white cards on cream background separated by quiet 1px borders (`#EAE7E7`) and generous border-radius (~12–16px). Depth comes from soft diffuse shadows on floating elements (toast notifications, hero mockup), never hard drop shadows. Status chips are fully rounded pills with pastel backgrounds.

## Components

- **Event Card**: full-bleed food photo header with dark gradient, "Activo" pill, event title + date overlaid in white.
- **Progress Bar**: thin brand-red bar with percentage label ("Progreso del evento — 83%").
- **Item Rows**: list rows with item name, quantity, assignee avatar-initial, and status pill (Comprado / Parcialmente comprado).
- **Participant List**: circular avatar initials (red-tint bg, red letter) + name + role ("Organizador", "Confirmado").
- **Toast Notification**: white pill with green check icon ("¡Juan trajo el carbón!").
- **CTA Buttons**: brand-red filled, fully rounded (`Crear mi primer evento`); secondary outlined with play icon (`Ver cómo funciona`).

## Do's and Don'ts

### Do's

- Use Nunito 700/800 for every video title/caption headline; Plus Jakarta Sans for supporting lines.
- Keep backgrounds cream `#FCF9F8` or ink `#1C1B1B` — the red is an accent, not a surface.
- Use rounded pills and soft shadows for any overlay chips or labels.
- Use the green/amber status colors only for state semantics (comprado / parcial).

### Don'ts

- Don't introduce blues/purples — the palette is warm (red, cream, brown, green accents only).
- Don't use sharp corners or hard shadows; everything is rounded and soft.
- Don't set long text in Nunito — it's display-only; body copy is Plus Jakarta Sans.
- Don't put red text on red tint backgrounds at small sizes — contrast drops fast.
