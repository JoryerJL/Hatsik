# STORYBOARD — Hatsik "Ver cómo funciona"

**Format:** 1080×1920 vertical (Instagram/landing modal)
**Audio:** NONE — silent autoplay video; captions carry the story
**Style basis:** DESIGN.md — cream `#FCF9F8` surfaces, ink `#1C1B1B`, brand red `#B51D0C`, Nunito 800 headlines, Plus Jakarta Sans support
**Device framing:** every screen-recording beat shows the clip inside a rounded "phone" frame (border-radius ~48px, ink bezel, soft shadow) floating over cream; captions live above the phone; the phone occupies ~72% of frame height.
**Camera language:** on every logged click, the phone group zooms toward the click point (scale 1 → 1.35–1.6, transform-origin at click), holds while the UI responds, then settles back. Zoom-ins ease `power2.out`, settle `power2.inOut`.
**Speed:** clips are pre-processed with ffmpeg (trim + setpts). Event timestamps below are ALREADY divided by the speed factor.

## Asset Audit

| Asset | Type | Assign to Beat | Role |
| --- | --- | --- | --- |
| capture/assets/ (logo mark, hatsik wordmark from site header) | SVG/img | Beat 0, Beat 6 | brand open/close |
| clips/clip-01-crear-evento.mp4 (1.8x) | Screen rec | Beat 1 | crear evento |
| clips/clip-02-anadir-items.mp4 (2x/3.5x) | Screen rec | Beat 2 | añadir ítems |
| clips/clip-03-compartir.mp4 (1.5x) | Screen rec | Beat 3 | compartir link + QR |
| clips/clip-04-tomar.mp4 (1.8x) | Screen rec | Beat 4 | asignarse ítems |
| clips/clip-05-comprado.mp4 (1.5x) | Screen rec | Beat 5 | comprar + 100% |
| capture/screenshots/scroll-000.png | Screenshot | SKIP | landing already shown live |

## Beats

### BEAT 0 — INTRO (0.0–4.0s) `compositions/beat-0-intro.html`
Cream canvas with the subtle dot texture. hatsik wordmark (Nunito 800, brand red) pops in with a soft scale-spring. Headline staggers per line: "Organiza tus convivios" (ink) / "sin el caos del" + «"¿qué llevo?"» in brand red with a marker-sweep highlight. A row of floating food emoji chips (🥩🍺🔥) drifts up gently behind. Transition OUT: headline lifts up + phone frame slides in from bottom (velocity matched).

### BEAT 1 — CREAR EVENTO (4.0–15.5s) — clip-01 @1.8x (trim 1.2s→20.5s ⇒ 10.7s)
Caption top: chip "1" (red pill) + "Crea tu evento" (Nunito 800 36px) + support "Nombre, fecha y listo" (Jakarta 400).
Clip events (post-speed, relative to clip start): click Crear evento @2.4s (270,299) → zoom 1.4; typing nombre @3.8–4.5s zoom 1.35 at input (270,271); submit @7.8s (270,690) zoom 1.4; event detail lands @8.6s — release zoom to 1.0 and let the food-photo header breathe.

### BEAT 2 — AÑADIR ÍTEMS (15.5–26.5s) — clip-02 two-speed (2.2s→13.5s @2x, 13.5s→33.9s @3.5x ⇒ ~11s)
Caption: "Añade lo que hace falta" / "Carne, carbón, bebidas…". First item add at normal-ish pace with zooms (modal open @0.7s, typing, guardar @4.4s); then a "time-lapse" chip (⏩) appears while items 2-3 fly by at 3.5x. Ends with 3 items listed.

### BEAT 3 — COMPARTIR (26.5–33.5s) — clip-03 @1.5x (trim 2.5s→12.6s ⇒ 6.7s)
Caption: chip "2" + "Comparte el link" / "O deja que escaneen el QR".
Events: click Invitar amigos @1.1s (270,729) zoom 1.4; click Copiar link @3.3s (270,316) zoom 1.5 → hold on green "¡Copiado!"; then camera pans down/zooms to the QR (270,515) and HOLDS — a red scan-line sweeps the QR once (overlay effect).

### BEAT 4 — TOMAR ÍTEMS (33.5–41.8s) — clip-04 @1.8x (trim 2.5s→17.4s ⇒ 8.3s)
Caption: "Cada quien elige qué llevar" / "Un clic y el ítem es tuyo".
Events: Asignarme Carbón @0.8s (91,867) zoom 1.45; Confirmar @2.7s (92,917); Asignarme Cerveza @4.2s (91,480) zoom 1.45; Confirmar @6.1s (92,530); settle out.

### BEAT 5 — COMPRADO (41.8–49.4s) — clip-05 @1.5x (trim 2.5s→13.9s ⇒ 7.6s)
Caption: "¿Ya lo compraste? Márcalo" / "Todos ven el progreso en tiempo real".
Events: carrito 1 @1.0s (411,848) zoom 1.5 → badge verde; carrito 2 @3.1s (411,480) zoom 1.5; scroll-back to top ~@5s — zoom to progress card as it shows **100%** (hero moment: caption swaps to "3 de 3 ítems cubiertos ✓").

### BEAT 6 — CIERRE (49.4–55.0s) `compositions/beat-6-cierre.html`
Phone exits downward; cream card: chip "3" + "¡Y listo!" (Nunito 800 64px) spring-pop, then "hatsik.jjjl.dev" in a red pill button (pulse once) + "Organiza tu próximo convivio" support line. Logo mark bottom-center. Hold 1.5s.

## Production Architecture

```
videos/hatsik-release/
├── index.html                 root composition (orchestrates beats)
├── DESIGN.md / SCRIPT.md / STORYBOARD.md
├── capture/                   site capture (tokens, assets)
├── clips/                     raw recordings + *.events.json + state.json
├── beats/                     speed-processed clips (ffmpeg output)
├── compositions/
│   ├── beat-0-intro.html
│   ├── beat-1..5 (phone-frame + zoom choreography, one per clip)
│   └── beat-6-cierre.html
└── record/                    playwright recording scripts
```
