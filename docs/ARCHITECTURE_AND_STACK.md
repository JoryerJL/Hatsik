# ARCHITECTURE_AND_STACK.md — Hatsik

> **Version:** 1.1
> **Date:** 2026-07-14
> **Status:** Active
> **Project:** Hatsik Unified Web System

Este documento es la fuente de verdad para el stack tecnológico, la arquitectura del sistema, la estructura de carpetas y las convenciones de código. Cualquier agente de IA o desarrollador que trabaje en este proyecto **debe leer este archivo antes de escribir una sola línea de código.**

---

## Stack tecnológico

| Capa | Tecnología | Versión | Notas |
|---|---|---|---|
| Backend framework | Django | 5.2.x | Web framework principal. Templates + lógica de negocio. |
| Interactividad frontend | HTMX | 2.x | Peticiones AJAX declarativas desde HTML. Sin JavaScript manual. |
| Estilos | Tailwind CSS | 4.x | Utility-first. Sin componentes externos salvo los propios. |
| Base de datos | PostgreSQL | 16.x | Hosted en Neon (serverless). Driver: `psycopg[binary]`. |
| ORM / Migraciones | Django ORM | (incluido en Django) | Migraciones gestionadas con `manage.py migrate`. |
| Email transaccional | Resend | SDK Python latest | Verificación de cuenta y recuperación de contraseña. |
| Autenticación | Django auth + sesiones | (incluido en Django) | HTTP-only cookie. Sin JWT en MVP. |
| Generación de QR | `qrcode` (lib Python) | 7.x | Generado on-demand. No se persiste en DB. |
| Deploy | AWS Lightsail Containers | — | Servicio de containers con HTTPS incluido (plan Nano, costo fijo). Health check contra `/login/`. |
| Contenedor | Docker | 27.x | Un solo `Dockerfile` para la app. Build `linux/amd64`. |
| Container registry | Lightsail (integrado) | — | Push directo con `aws lightsail push-container-image`. Sin ECR. |
| CI/CD | GitHub Actions | — | Lint + tests → build Docker → push a Lightsail → `create-container-service-deployment`. |
| Cron jobs | AWS EventBridge Scheduler + Lambda | — | Scheduler dispara la Lambda `hatsik-cron-trigger` cada 5 min; esta llama al endpoint protegido de Django para cierre automático de eventos. Logs en CloudWatch. |
| Variables de entorno | Lightsail deployment + `.env` local | — | En producción: inyectadas en cada deployment desde GitHub Secrets (ver `deploy.yml`). En local: archivo `.env` (nunca commiteado). |
| Python runtime | Python | 3.12.x | Versión fija en `Dockerfile` y `.python-version`. |

---

## Arquitectura del sistema

### Patrón: Django Monolito con Template-Driven Views

No es una SPA. No hay API REST pública. El servidor renderiza HTML completo en la carga inicial; HTMX maneja las actualizaciones parciales sin recargar la página.

```
Browser
  │
  │  GET /events/          → Django View → Template → HTML completo
  │  POST /events/1/close/ → Django View → HX-Redirect o partial HTML
  │
  ↓
Django (Gunicorn)
  │
  ├── URLs → Views → Templates
  ├── Django ORM → PostgreSQL (Neon)
  ├── Django Auth → Session Cookie (HTTP-only)
  └── Resend SDK → Email transaccional
```

### Flujo de deploy

```
GitHub (push a main)
  ↓
GitHub Actions
  ├── Job 1: lint (ruff check + format) + tests (pytest vs postgres:16-alpine)
  └── Job 2 (solo push a main):
        ├── Buildea imagen Docker (linux/amd64)
        ├── aws lightsail push-container-image
        └── aws lightsail create-container-service-deployment
              (env vars desde GitHub Secrets + public endpoint con health check /login/)
          ↓
    Lightsail levanta la versión nueva y enruta tráfico
    solo cuando el health check pasa (zero-downtime)
          ↓
    App en producción (HTTPS incluido por Lightsail)
```

### Cron job — Cierre automático de eventos

```
AWS EventBridge Scheduler (cada 5 min)
  ↓
AWS Lambda (hatsik-cron-trigger) — logs en CloudWatch
  ↓
POST /internal/close-expired-events/
  Headers: X-Internal-Token: <secret>
  ↓
Django View (verifica token, cierra eventos vencidos)
  ↓
UPDATE events SET status='closed' WHERE assignment_deadline_at <= NOW()
```

---

## Estructura de carpetas

```
hatsik/                          ← raíz del proyecto
│
├── .github/
│   └── workflows/
│       └── deploy.yml           ← CI/CD: lint + test → build → push a Lightsail → deploy
│
├── config/                      ← configuración de Django (settings, urls, wsgi)
│   ├── settings/
│   │   ├── base.py              ← settings compartidos
│   │   ├── local.py             ← overrides para desarrollo local
│   │   └── production.py        ← overrides para producción (Lightsail)
│   ├── urls.py                  ← URL root del proyecto
│   └── wsgi.py
│
├── apps/                        ← módulos de producto (una app Django por módulo)
│   ├── accounts/                ← Auth: registro, login, logout, verificación, recuperación
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── accounts/        ← login.html, register.html, verify_email.html, etc.
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── models.py            ← User model (AbstractBaseUser o AbstractUser)
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── events/                  ← Events + Dashboard: crear, editar, cerrar, compartir
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── events/
│   │   ├── forms.py
│   │   ├── models.py            ← Event, EventParticipation
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── items/                   ← Items + Assignments: lista de ítems y asignaciones
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── items/
│   │   ├── forms.py
│   │   ├── models.py            ← EventItem, ItemAssignment
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── moderation/              ← Sugerencias: sugerir, aprobar, rechazar ítems
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── moderation/
│   │   ├── forms.py
│   │   ├── models.py            ← ItemSuggestion
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── internal/                ← Endpoints internos (cron jobs, EventBridge)
│       ├── urls.py
│       └── views.py             ← close_expired_events view
│
├── templates/                   ← templates base y compartidos
│   ├── base.html                ← layout principal: nav, head, scripts
│   ├── partials/                ← fragmentos HTMX reutilizables
│   │   ├── _event_card.html
│   │   ├── _item_row.html
│   │   └── _toast.html
│   └── components/              ← componentes UI sin lógica de servidor
│       ├── _button.html
│       ├── _badge.html
│       └── _modal.html
│
├── static/                      ← assets estáticos (compilados por Tailwind)
│   ├── css/
│   │   └── main.css             ← output de Tailwind CSS (generado, no editar a mano)
│   ├── js/
│   │   └── htmx.min.js          ← HTMX bundle (sin npm, copia directa)
│   └── img/
│       └── logo.svg
│
├── docs/                        ← documentación del proyecto
│   ├── ARCHITECTURE_AND_STACK.md  ← este archivo
│   ├── DATABASE_SCHEMA.md
│   ├── PRODUCT_OVERVIEW.md
│   ├── ROADMAP.md
│   └── ...
│
├── .env.example                 ← plantilla de variables de entorno (commiteado)
├── .env                         ← valores reales locales (NO commiteado — en .gitignore)
├── .gitignore
├── .python-version              ← "3.12.x" — fija la versión de Python
├── Dockerfile                   ← imagen de producción
├── docker-compose.yml           ← entorno local: Django + PostgreSQL local
├── manage.py
├── pyproject.toml               ← dependencias con pip-tools o uv
└── requirements/
    ├── base.txt                 ← dependencias compartidas
    ├── local.txt                ← dependencias solo para desarrollo
    └── production.txt           ← dependencias de producción
```

---

## Convenciones de código

### Python / Django

| Convención | Regla |
|---|---|
| Variables y funciones | `snake_case` |
| Clases | `PascalCase` |
| Constantes | `UPPER_SNAKE_CASE` |
| Archivos y módulos | `snake_case` |
| Apps Django | Sustantivo plural en minúsculas: `events`, `items`, `accounts` |
| Models | Sustantivo singular en `PascalCase`: `Event`, `EventItem`, `ItemAssignment` |
| Views (Function-Based) | `snake_case` + sufijo `_view`: `event_detail_view`, `create_event_view` |
| Views (Class-Based) | `PascalCase` + sufijo `View`: `EventDetailView`, `CreateEventView` |
| URLs (paths) | `kebab-case`: `/events/create/`, `/events/<uuid:pk>/close/` |
| URLs (names) | `snake_case` con prefijo de app: `events:create`, `events:detail` |
| Forms | `PascalCase` + sufijo `Form`: `CreateEventForm`, `RegisterUserForm` |
| Imports | stdlib → third-party → Django → apps propias. Separados por línea en blanco. |

### Base de datos

| Convención | Regla |
|---|---|
| Tablas | `snake_case` plural: `event_items`, `item_assignments` |
| Columnas | `snake_case`: `owner_user_id`, `created_at` |
| PKs | Siempre `uuid`, nunca autoincrement |
| FKs | `{entidad_referenciada}_id`: `event_id`, `user_id` |
| Timestamps | Siempre `created_at` + `updated_at` en toda tabla. Tipo `timestamptz`. |
| Soft deletes | No se borran filas. Se usan estados terminales y timestamps (`cancelled_at`, `removed_at`). |
| Enums | `snake_case` en minúsculas: `event_status`, `access_status` |

### Templates HTML

| Convención | Regla |
|---|---|
| Archivos de template | `kebab-case`: `event-detail.html`, `create-event.html` |
| Partiales HTMX | Prefijo `_`: `_event_card.html`, `_item_row.html` |
| Bloques Django | `snake_case`: `{% block page_content %}` |
| CSS (Tailwind) | Utility classes directamente en HTML. Sin `@apply` salvo casos justificados. |
| IDs de HTML | `kebab-case`: `id="event-list"`, `id="close-modal"` |
| Atributos HTMX | Siempre en el elemento más cercano al trigger. `hx-target` apunta a un ID explícito. |

### Tailwind CSS

| Convención | Regla |
|---|---|
| Tokens de color | Usar los tokens del design system Hatsik (ver `hatsik-brand-identity.md`). No usar colores hardcodeados. |
| Responsive | Mobile-first: clases base para móvil, prefijos `md:` y `lg:` para breakpoints mayores. El caso de uso principal es en celular (compartir listas en eventos, marcar ítems al momento). |
| Dark mode | Fuera del MVP. No implementar. |
| Componentes | No crear archivos CSS de componentes. Usar partiales de templates en su lugar. |

### HTMX

| Convención | Regla |
|---|---|
| Respuestas parciales | Una view HTMX retorna solo el fragmento HTML necesario, no la página completa. |
| Detección HTMX en view | Usar `request.htmx` (con `django-htmx`) para distinguir request normal vs HTMX. |
| Errores | Retornar HTTP 4xx con fragmento de error. HTMX lo inyecta en el target. |
| Confirmaciones | Usar `hx-confirm` o modales propios. No `window.confirm()`. |
| Redirecciones | Usar header `HX-Redirect` para redirigir después de una acción HTMX. |

---

## Variables de entorno

Todas las variables se definen en `.env` (local) o como GitHub Secrets que el pipeline inyecta al contenedor de Lightsail en cada deployment (producción). El archivo `.env.example` documenta todas las claves necesarias **sin valores reales**.

```bash
# Django
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=

# Database (Neon)
DATABASE_URL=postgres://user:password@host/dbname

# Email (Resend)
RESEND_API_KEY=
RESEND_FROM_DOMAIN=

# Internal endpoints
INTERNAL_CRON_TOKEN=

# AWS (solo GitHub Secrets para CI/CD — no van al contenedor)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
LIGHTSAIL_SERVICE=
```

**Regla estricta:** ningún valor real de secretos se commitea al repositorio. Si se commitea accidentalmente, rotar el secreto inmediatamente.

---

## Dependencias principales

```
# base.txt
Django==5.2.*
psycopg[binary]==3.2.*
django-htmx==1.21.*
resend==2.*
qrcode==7.*
gunicorn==23.*
whitenoise==6.*          # sirve static files desde el container sin S3
python-decouple==3.*     # lee variables de entorno desde .env

# local.txt
-r base.txt
django-debug-toolbar==4.*

# production.txt
-r base.txt
```

---

## Dockerfile (referencia)

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements/production.txt requirements/base.txt requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Descargar Tailwind CSS standalone (sin Node.js)
RUN curl -sLo /usr/local/bin/tailwindcss \
    https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
    && chmod +x /usr/local/bin/tailwindcss

# Copiar código
COPY . .

# Compilar Tailwind CSS (minificado)
RUN tailwindcss -i static/css/input.css -o static/css/main.css --minify

# collectstatic corre al arrancar el contenedor (start.sh), antes de gunicorn
EXPOSE 8000

CMD ["/app/start.sh"]  # → collectstatic --noinput && gunicorn :8000 --workers 2 --timeout 120
```

Ver el [`Dockerfile`](../Dockerfile) real para el detalle completo (esta es una referencia condensada).

---

## Decisiones de arquitectura y por qué

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| Django templates + HTMX en lugar de SPA | Astro + API REST | Un solo container, un solo deploy, cero complejidad de CORS/auth cross-origin. Suficiente para el MVP. |
| Sin JWT — sesiones Django con cookie HTTP-only | JWT en localStorage | Las sesiones Django son más simples, más seguras por defecto (no expuestas a XSS), y no requieren refresh token logic. |
| Lightsail Containers en lugar de App Runner | App Runner + ECR (stack original), EC2 t3.micro | Costo fijo y predecible (plan Nano, ~$7/mes) con HTTPS incluido, sin ECR aparte. Se migró desde App Runner manteniendo el mismo Dockerfile. Cero administración de servidor. |
| Neon en lugar de RDS | RDS PostgreSQL | Neon tiene tier gratuito real. Migración a RDS es cambiar solo `DATABASE_URL`. Sin lock-in. |
| Resend en lugar de SES | AWS SES | Resend tiene 3000 emails/mes gratis y se integra en minutos. SES requiere aprobación para salir del sandbox. |
| EventBridge Scheduler + Lambda para cron | Celery + Redis | Sin workers adicionales. Sin segundo container. Sin Redis. Costo prácticamente $0. |
| Un solo `Dockerfile` — sin Docker Compose en producción | Docker Compose en prod | Lightsail Containers no usa Compose. Compose es solo para desarrollo local (Django + Postgres local). |
| `whitenoise` para static files | S3 + CloudFront | Suficiente para MVP. Sin configuración extra de buckets, permisos ni CDN. Migrable después. |

---

## Lo que está fuera del MVP (no implementar)

| Tema | Estado |
|---|---|
| OAuth / Login con Google | Post-MVP |
| Notificaciones en tiempo real (WebSockets) | Post-MVP |
| S3 para static files | Post-MVP si whitenoise no escala |
| CDN (CloudFront) | Post-MVP |
| Redis / Celery | Post-MVP si cron logic se vuelve compleja |
| Dark mode | Post-MVP |
| API REST pública | No planeado |
| App móvil nativa | No planeado |

---

## Checklist de setup inicial (Fase 1)

- [ ] Repositorio creado con esta estructura de carpetas
- [ ] `Dockerfile` funcional — buildea sin errores
- [ ] `docker-compose.yml` local funcional — Django + Postgres corren con `docker compose up`
- [ ] `.env.example` con todas las variables documentadas
- [ ] `DATABASE_URL` apuntando a Neon configurada
- [ ] Migraciones iniciales corren limpias contra Neon
- [ ] `RESEND_API_KEY` configurada — envía un email de prueba
- [ ] GitHub Actions: pipeline corre lint + tests en cada push a `main`
- [ ] Lightsail container service creado — despliega la imagen correctamente
- [ ] Dominio custom configurado con SSL en Lightsail
- [ ] EventBridge Scheduler + Lambda creados — llaman al endpoint interno cada 5 minutos

---

## Siguiente paso

Con el stack definido, la siguiente acción es **la Fase 1 del ROADMAP**: crear el esqueleto del proyecto con esta estructura exacta, correr las migraciones de `DATABASE_SCHEMA.md`, y verificar que el pipeline de deploy funciona de punta a punta antes de escribir una sola línea de lógica de producto.

Ver: [`ROADMAP.md → Phase 1 — Foundation`](./ROADMAP.md)
