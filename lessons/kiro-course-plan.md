# Curso práctico de Kiro — Construyendo Hatsik

> **Enfoque:** cada clase parte de un problema real del proyecto, introduce el concepto de Kiro que lo resuelve, lo implementa y cierra profesionalmente.
> **Duración objetivo por clase:** 8–10 minutos.
> **Producto que construimos:** Hatsik — app web para coordinar convivios (Next.js + TypeScript · Django REST · PostgreSQL · AWS).

---

## Estructura pedagógica de cada clase

```
1. PROBLEMA    — "Hatsik necesita X / tenemos este problema"
2. CONCEPTO    — Qué herramienta/modo de Kiro lo resuelve y por qué
3. KIRO EN ACCIÓN — Lo usamos en vivo dentro del proyecto
4. CIERRE      — Test, commit, steering actualizado o revisión
```

---

## Mapa de capacidades de Kiro en el curso

| Capacidad | Bloque donde aparece |
|---|---|
| Tour IDE + Agentic Chat | Bloque 0 |
| Vibe mode | Bloque 0 |
| Steering `always` | Bloque 1 |
| Steering `fileMatch` / `auto` / `manual` + inclusión modes | Bloque 1, 3, 5 |
| Feature Spec · Requirements-First | Bloque 2, 3, 4 |
| Feature Spec · Design-First | Bloque 5, 6, 8 |
| Quick Plan | Bloque 3, 5 |
| Task execution + waves | Bloque 2, 3, 4 |
| Bugfix Spec | Bloque 4 |
| Hooks `onFileSave` · `Run Command` | Bloque 2 |
| Hooks `onSpecTaskComplete` · `Ask Kiro` | Bloque 4 |
| Hook `manual` (checklist de PR) | Bloque 3 |
| MCP Servers | Bloque 7 |
| Powers (AWS) | Bloque 6, 8 |
| Agent Skills | Bloque 8 |

---

## BLOQUE 0 — Bienvenida y entorno del IDE

### Clase 0.1 — ¿Qué es Kiro y en qué se diferencia?

**Problema:** tienes un IDE con IA pero no sabes cuándo usar chat genérico vs cuándo dejar que el agente planifique y ejecute.

**Concepto:** Kiro como IDE agéntico — diferencias con Copilot/Cursor. Modos: Agentic Chat, Vibe, Specs, Steering, Hooks, Powers.

**Kiro en acción:** instalación, tour del IDE en vivo — panel de chat, panel de specs, panel de steering, panel de hooks, panel de powers. Primera conversación sin proyecto abierto.

**Cierre:** mapa mental de cuándo usar cada modo. Pregunta que guiará el curso: *"¿Qué problema estamos resolviendo?"*

---

### Clase 0.2 — Abrimos Hatsik en Kiro por primera vez

**Problema:** Kiro no sabe nada de nuestro proyecto todavía. Le hacemos una pregunta y su respuesta es genérica.

**Concepto:** contexto del workspace. Kiro lee el repo pero necesita guía explícita. Vibe mode para exploración rápida.

**Kiro en acción:** abrir el repositorio de Hatsik, Vibe mode — preguntarle a Kiro *"¿qué hace este proyecto?"*. Ver la diferencia entre respuesta sin contexto vs respuesta después de señalarle los docs.

**Cierre:** entendemos por qué el siguiente bloque existe — Kiro necesita instrucciones permanentes.

---

## BLOQUE 1 — Steering: darle memoria permanente a Kiro

> Cuatro clases que construyen los archivos de steering fundacionales del proyecto.

### Clase 1.1 — Steering de producto (`product.md`)

**Problema:** cada vez que abrimos Kiro hay que explicarle de nuevo qué es Hatsik, quiénes son los roles y cuál es el MVP.

**Concepto:** Steering — archivos markdown en `.kiro/steering/` que Kiro carga automáticamente. Inclusión mode `always`: siempre presente en el contexto, sin importar el archivo abierto.

**Kiro en acción:** crear `.kiro/steering/product.md` con descripción del producto, roles (Owner, Co-admin, Participante), módulos del MVP y lo que está explícitamente fuera del MVP. Probamos con la misma pregunta del Bloque 0: la respuesta ahora es completamente específica.

**Cierre:** commit inicial del proyecto. Convención: `docs: add kiro steering product context`.

---

### Clase 1.2 — Steering de stack y estructura (`tech.md` + `structure.md`)

**Problema:** Kiro sugiere código con patrones incorrectos — usa React puro en vez de Next.js, o Django sin DRF.

**Concepto:** steering de arquitectura técnica. Diferencia entre `always` (stack y estructura, siempre relevante) y `fileMatch` (reglas que aplican solo a ciertos archivos).

**Kiro en acción:** crear `.kiro/steering/tech.md` (Next.js + TypeScript, Django REST, PostgreSQL, S3, Beanstalk, Amplify) y `.kiro/steering/structure.md` (organización de carpetas, módulos backend/frontend, naming). Comparar sugerencias antes y después.

**Cierre:** commit `docs: add stack and structure steering`.

---

### Clase 1.3 — Steering de seguridad (`security.md`)

**Problema:** Kiro genera código que expone si un email existe al hacer login — viola la regla de respuestas genéricas del módulo Auth de Hatsik.

**Concepto:** steering de seguridad con inclusión `always`. Por qué las reglas de seguridad deben estar siempre en contexto, no solo cuando el archivo coincide.

**Kiro en acción:** crear `.kiro/steering/security.md` — tokens hasheados, respuestas genéricas en auth, validaciones de permisos, secretos fuera del código, uploads seguros. Le pedimos a Kiro que genere el endpoint de login y observamos cómo aplica las reglas automáticamente.

**Cierre:** commit `docs: add security steering`.

---

### Clase 1.4 — Steering de commits + primer commit real (`git-commits.md`)

**Problema:** llegamos al primer commit de código y nadie del equipo conoce la convención. Kiro tampoco.

**Concepto:** steering con inclusión `manual` — no se carga automáticamente, lo activamos cuando lo necesitamos. Conventional Commits: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

**Kiro en acción:** crear `.kiro/steering/git-commits.md` con la convención de commits, ejemplos y checklist antes de commitear. Activar el steering manualmente para que Kiro genere el mensaje de commit perfecto para nuestros cambios actuales.

**Cierre:** commit `chore: add kiro steering for conventional commits`. El alumno ya entiende qué es steering, modos de inclusión y cuándo elegir cada uno.

---

## BLOQUE 2 — Módulo Auth con Feature Specs

> Aprendemos Specs mientras construimos autenticación real.

### Clase 2.1 — ¿Qué es un Feature Spec y cuándo usarlo?

**Problema:** necesitamos construir el módulo de Auth — registro, verificación de email, login, recuperación de contraseña. Son muchas reglas de negocio interrelacionadas.

**Concepto:** Feature Specs — flujo estructurado que genera `requirements.md`, `design.md` y `tasks.md`. Requirements-First: empezamos por comportamiento esperado, no por código. Cuándo NO usar specs (features triviales, Vibe para eso).

**Kiro en acción:** abrir panel de Specs en Kiro. Crear nueva Feature Spec para Auth con el prompt inicial. Ver cómo Kiro propone el flujo de planificación.

**Cierre:** entendemos el ciclo: requirements → design → tasks → ejecución.

---

### Clase 2.2 — Requirements del módulo Auth

**Problema:** Kiro genera requirements genéricos de auth. Los nuestros son específicos: rate limiting de 60s, tokens que expiran, respuestas genéricas, contraseña con reglas propias.

**Concepto:** iterar y refinar `requirements.md`. Los requirements son una conversación, no un monólogo de la IA.

**Kiro en acción:** revisar el `requirements.md` generado, corregir y agregar las reglas específicas de Hatsik (US-01 a US-05 del doc de User Stories). Aprobar requirements.

**Cierre:** requirements aprobados y comprometidos al repo.

---

### Clase 2.3 — Design del módulo Auth

**Problema:** requirements aprobados, pero ¿cómo los implementamos? ¿Django sessions? ¿JWT? ¿Dónde va la lógica?

**Concepto:** `design.md` — Kiro propone arquitectura técnica basada en los requirements. Podemos aceptar, modificar o rechazar. El diseño dirige el código, no al revés.

**Kiro en acción:** revisar `design.md` para Auth — modelos de Django, endpoints DRF, manejo de tokens, servicio de email. Ajustar para que encaje con el steering de stack y seguridad.

**Cierre:** design aprobado. Primer vistazo a `tasks.md` — waves de ejecución.

---

### Clase 2.4 — Task execution: construir Auth por partes

**Problema:** tenemos 15 tareas de Auth. ¿Cómo ejecutarlas sin perder el hilo ni romper lo que ya funciona?

**Concepto:** Task execution en Kiro — waves, dependencias entre tareas, ejecución paralela de tareas independientes. Kiro no adivina el orden: `tasks.md` lo define.

**Kiro en acción:** ejecutar primera wave — modelos de usuario, migraciones, endpoint de registro. Ver Kiro trabajar por tareas, revisando cada una antes de continuar.

**Cierre:** registro funcionando. Commit `feat(auth): add user registration endpoint`.

---

### Clase 2.5 — Completar Auth: login, verificación y recuperación

**Problema:** todavía faltan waves de Auth — verificación de email, login, rate limiting, recuperación de contraseña.

**Concepto:** continuación de task execution. Cómo manejar tareas que dependen de servicios externos (email). Pausar y reanudar specs.

**Kiro en acción:** ejecutar waves restantes de Auth. Integrar servicio de email transaccional. Probar flujo completo con Kiro ayudando en el debugging.

**Cierre:** módulo Auth completo. Commit `feat(auth): complete auth module with email verification`.

---

### Clase 2.6 — Hooks: automatizar pruebas al guardar archivos

**Problema:** cada vez que tocamos código de Auth tenemos que recordar correr los tests manualmente. El equipo lo olvida.

**Concepto:** Hooks — automatizaciones por eventos del IDE. Hook `onFileSave` con acción `Run Command`. Diferencia entre `Run Command` (determinista, para tests/lint) y `Ask Kiro` (contextual, para revisiones).

**Kiro en acción:** crear hook `onFileSave` que corre `pytest` en los archivos de Auth modificados. Ver el hook dispararse en tiempo real al guardar un archivo.

**Cierre:** commit `chore: add kiro hook for auto-test on save`. Introducción al segundo tipo de hook (Ask Kiro) que veremos más adelante.

---

## BLOQUE 3 — Dashboard y Events

### Clase 3.1 — Quick Plan para el Dashboard

**Problema:** necesitamos el Dashboard — vista de eventos propios y donde participa el usuario. Es simple: no hay lógica nueva, solo leer y mostrar datos.

**Concepto:** Quick Plan — genera requirements, design y tasks en una sola pasada sin aprobaciones intermedias. Para features conocidas y de bajo riesgo. Cuándo usar Quick Plan vs Feature Spec completo.

**Kiro en acción:** Quick Plan para el módulo Dashboard. Ver cómo Kiro comprime el flujo. Ejecutar tasks y tener el Dashboard funcionando en una sola clase.

**Cierre:** commit `feat(dashboard): add events dashboard`.

---

### Clase 3.2 — Feature Spec Requirements-First para Events

**Problema:** el módulo Events tiene reglas complejas — ciclo de vida del evento, roles internos, confirmaciones obligatorias, estados que bloquean acciones. No es quick plan.

**Concepto:** Requirements-First para features con reglas de dominio densas. Por qué es mejor que Design-First aquí: el comportamiento del negocio dicta la arquitectura, no al revés.

**Kiro en acción:** iniciar Feature Spec para Events. Alimentar Kiro con las reglas del `MODULES_SPEC.md` de Hatsik. Ver cómo los requirements capturan: ciclo de vida activo/cerrado/cancelado, restricciones de Owner, confirmaciones obligatorias.

**Cierre:** requirements aprobados para Events.

---

### Clase 3.3 — Steering de dominio (`domain-rules.md`)

**Problema:** al construir Events, Kiro sigue sugiriendo código sin recordar las reglas del dominio — confunde el rol Co-admin con Owner, o no aplica las restricciones de estado.

**Concepto:** steering con inclusión `auto` — Kiro decide cuándo cargarlo basado en relevancia. Para reglas de dominio que no siempre aplican pero que Kiro debe conocer cuando trabaja en lógica de negocio.

**Kiro en acción:** crear `.kiro/steering/domain-rules.md` — roles por evento, estados de acceso, estados calculados de ítems, estados de sugerencias, confirmaciones obligatorias. Probar que Kiro ahora respeta las restricciones al generar código del módulo Events.

**Cierre:** commit `docs: add domain rules steering`.

---

### Clase 3.4 — Implementar ciclo de vida de eventos

**Problema:** ejecutar las tareas del módulo Events — crear evento, cerrar, reabrir, cancelar, link compartible, QR.

**Concepto:** task execution con waves — primero el modelo y endpoints básicos, luego las reglas de estado, luego QR y link. Ver cómo Kiro detecta dependencias entre tareas.

**Kiro en acción:** ejecutar waves del spec de Events. Kiro implementa; nosotros revisamos que se aplican las confirmaciones obligatorias del diseño.

**Cierre:** commit `feat(events): add event lifecycle management`.

---

### Clase 3.5 — Gestión de co-admins + Hook manual de PR

**Problema:** implementamos asignación y revocación de co-admins. Al terminar, ¿cómo hacemos el PR sin olvidar ningún paso?

**Concepto:** Hook manual — se activa cuando tú lo pides, no automáticamente. Ideal para checklists de PR, revisiones antes de merge o cualquier flujo que requiere control humano explícito.

**Kiro en acción:** implementar co-admins. Luego crear un hook manual `PR Checklist` que usa `Ask Kiro` para revisar cambios, generar descripción del PR y verificar cobertura de tests. Activarlo manualmente antes del commit.

**Cierre:** commit `feat(events): add co-admin management`. El alumno domina los cuatro tipos de hooks.

---

## BLOQUE 4 — EventAccess, Items, Assignments y Moderation

### Clase 4.1 — Feature Spec para EventAccess

**Problema:** EventAccess tiene reglas de estados de solicitud complejas — pendiente, aceptado, rechazado, reingreso, corrección de rechazo. Además, visualmente vive dentro del detalle del evento, no como pantalla propia.

**Concepto:** Requirements-First para módulos con estados entrecruzados. Cómo documentar restricciones de acceso en requirements antes de diseñar.

**Kiro en acción:** Feature Spec para EventAccess. Revisamos que los requirements capturen los edge cases — usuario rechazado que reingresa, co-admin que se sale y pierde su rol.

**Cierre:** requirements y design aprobados.

---

### Clase 4.2 — Implementar solicitudes de entrada

**Problema:** ejecutar las tareas de EventAccess. Los permisos son complicados: Owner y Co-admin aprueban; nadie más.

**Concepto:** task execution con permisos en DRF — cómo los tasks de Kiro manejan lógica de permisos sin mezclar responsabilidades.

**Kiro en acción:** ejecutar waves de EventAccess. Kiro implementa los endpoints de solicitud, aprobación y rechazo con los permisos correctos según el steering de dominio.

**Cierre:** commit `feat(event-access): add entry request flow`.

---

### Clase 4.3 — Feature Spec para Items y Assignments

**Problema:** Items tiene validaciones de cantidad vs asignado que interactúan con Assignments. Si separo los specs mal, Kiro no entiende la dependencia.

**Concepto:** specs de módulos dependientes — cómo estructurar requirements para que Kiro entienda que Items y Assignments comparten invariantes. Estados calculados automáticos del ítem.

**Kiro en acción:** spec conjunto para Items + Assignments. Requirements capturan: ítem binario vs con cantidad, no superar cantidad asignada, estados calculados, confirmaciones obligatorias en marcar comprado.

**Cierre:** requirements y design aprobados para ambos módulos.

---

### Clase 4.4 — Implementar Items, Assignments y estados calculados

**Problema:** los estados de ítem (`sin_asignar`, `parcialmente_cubierto`, `cubierto`, `parcialmente_comprado`, `comprado`) se calculan dinámicamente. Fácil de romper.

**Concepto:** task execution en módulos con lógica derivada. Cómo las waves separan primero la estructura (modelo, endpoints básicos) de la lógica derivada (estados calculados).

**Kiro en acción:** ejecutar waves de Items y Assignments. Verificar que los estados calculados funcionan en todos los escenarios Gherkin del documento.

**Cierre:** commit `feat(items): add items and assignments with calculated states`.

---

### Clase 4.5 — Bugfix Spec: el estado del ítem calcula mal

**Problema:** descubrimos un bug — cuando el Owner cancela una asignación ajena, el estado del ítem no se recalcula correctamente.

**Concepto:** Bugfix Spec — flujo especializado para bugs. Diferente a Feature Spec: empieza con diagnóstico del bug, hipótesis, fix y tests de regresión para que no vuelva a aparecer.

**Kiro en acción:** crear Bugfix Spec para el bug de recálculo. Kiro genera: descripción del bug, pasos para reproducir, hipótesis de causa raíz, fix propuesto y tests de regresión. Ejecutar fix y tests.

**Cierre:** commit `fix(assignments): recalculate item state on owner cancel`. El alumno sabe usar Bugfix Spec, no solo Feature Spec.

---

### Clase 4.6 — Hook post-tarea: revisión automática de permisos

**Problema:** cada vez que Kiro termina de ejecutar una tarea de spec en estos módulos, olvidamos verificar que los permisos están correctamente aplicados.

**Concepto:** Hook `onSpecTaskComplete` con acción `Ask Kiro` — revisión contextual automática después de cada tarea de spec. `Ask Kiro` para análisis que requieren razonamiento; `Run Command` para checks deterministas.

**Kiro en acción:** crear hook `onSpecTaskComplete` que le pregunta a Kiro: "¿el código de esta tarea aplica correctamente los permisos de Owner, Co-admin y Participante?". Ver el hook dispararse al completar una tarea.

**Cierre:** commit `chore: add kiro hook for post-task permission review`.

---

### Clase 4.7 — Moderation: Quick Plan

**Problema:** el módulo Moderation — sugerencias de ítems, aprobación/rechazo — sigue el mismo patrón de permisos que ya construimos. Es conocido y de bajo riesgo.

**Concepto:** Quick Plan cuando ya tienes patrones establecidos. Reutilizar steering de dominio y permisos que ya está en contexto.

**Kiro en acción:** Quick Plan para Moderation. Ver cómo Kiro reutiliza los patrones del steering de dominio para generar código consistente con lo que ya existe.

**Cierre:** commit `feat(moderation): add item suggestions and moderation flow`. Backend MVP completo.

---

## BLOQUE 5 — Frontend con Next.js

### Clase 5.1 — Steering de frontend (`nextjs-patterns.md` + `ui-brand.md`)

**Problema:** empezamos el frontend y Kiro genera componentes React puros, sin Server Components, sin las convenciones de Hatsik, sin los tokens visuales de la marca.

**Concepto:** steering con `fileMatch` — reglas que solo se cargan cuando el archivo abierto coincide con un patrón (ej. `*.tsx`, `app/**`). No contaminar el contexto de backend con reglas de frontend.

**Kiro en acción:** crear `.kiro/steering/nextjs-patterns.md` (Server Components, Client Components, routing de App Router, manejo de auth, formularios) y `.kiro/steering/ui-brand.md` (tokens de color, tipografía, tono, componentes base de Hatsik). Configurar `fileMatch` para cada uno. Comparar componente generado antes y después.

**Cierre:** commit `docs: add nextjs and brand steering for frontend`.

---

### Clase 5.2 — Feature Spec Design-First para arquitectura del frontend

**Problema:** el frontend tiene decisiones arquitectónicas que deben tomarse antes de codear — rutas protegidas, layout compartido, manejo de sesión, consumo de API. Si Kiro improvisa esto, el proyecto queda inconsistente.

**Concepto:** Design-First — empezamos por arquitectura/diseño técnico, no por comportamiento. Cuándo usar Design-First: cuando las decisiones técnicas dictan cómo deben verse los requirements.

**Kiro en acción:** Feature Spec Design-First para la arquitectura del frontend de Hatsik. Kiro propone: estructura de rutas (App Router), layout de autenticación, layout de dashboard, estrategia de fetching, manejo de estado. Revisamos y aprobamos design antes de requirements.

**Cierre:** design aprobado. Estructura de carpetas del frontend definida.

---

### Clase 5.3 — Implementar pantallas de Auth en Next.js

**Problema:** pantallas de registro, login, verificación pendiente y recuperación de contraseña con el stack decidido.

**Concepto:** task execution sobre diseño frontend. Las waves del spec frontend separan estructura (layout, routing) de lógica (formularios, validación, llamadas a API).

**Kiro en acción:** ejecutar primera wave — estructura de rutas y layouts. Segunda wave — pantallas de Auth con formularios y manejo de errores. Kiro respeta los tokens del steering de UI y los patrones de Next.js.

**Cierre:** commit `feat(frontend): add auth screens`.

---

### Clase 5.4 — Implementar Dashboard y pantallas de Events

**Problema:** Dashboard, creación de evento, detalle de evento con lista. Son tres pantallas con lógica de permisos que debe reflejarse en el UI.

**Concepto:** task execution en frontend que consume permisos del backend. Cómo el steering de dominio ayuda a Kiro a generar UI que refleja correctamente los roles.

**Kiro en acción:** ejecutar waves para Dashboard, creación de evento y detalle de evento. Kiro genera UI que deshabilita acciones según el rol del usuario actual.

**Cierre:** commit `feat(frontend): add dashboard and event screens`.

---

### Clase 5.5 — Steering de testing frontend (`testing-standards.md`)

**Problema:** terminamos pantallas y queremos añadir tests, pero no sabemos qué convención usar ni Kiro sabe qué nivel de cobertura esperamos.

**Concepto:** steering `auto` para testing — Kiro lo carga cuando está trabajando en archivos de test o cuando el contexto es claramente sobre pruebas. Incluir escenarios Gherkin como referencia de comportamiento esperado.

**Kiro en acción:** crear `.kiro/steering/testing-standards.md` — qué probar (unitario vs integración vs e2e), herramientas (pytest, Jest/Testing Library), nivel de cobertura esperado, cómo los escenarios Gherkin del `MODULES_SPEC.md` se traducen a tests. Generar los primeros tests de Auth con Kiro usando este steering.

**Cierre:** commit `docs: add testing standards steering` + `test(auth): add auth module tests`.

---

## BLOQUE 6 — S3 y manejo de imágenes

### Clase 6.1 — Feature Spec Design-First para S3

**Problema:** Hatsik necesita soporte para imágenes — perfil de usuario y foto del evento. S3, URLs firmadas, seguridad de uploads: hay decisiones técnicas que tomar antes de codear.

**Concepto:** Design-First cuando la tecnología es el constraint — aquí S3 dicta cómo se verán los requirements. Cuándo ir design-first en lugar de requirements-first.

**Kiro en acción:** Feature Spec Design-First para integración S3. Kiro propone: bucket policies, URL firmadas para upload directo desde frontend, referencias en base de datos, expiración de URLs. Revisamos contra las reglas de seguridad del steering.

**Cierre:** design aprobado con decisiones de seguridad explícitas.

---

### Clase 6.2 — Powers: activar el Power de AWS para contexto especializado

**Problema:** implementando S3, Kiro comete errores en las APIs de AWS — confunde SDK v2 con v3, no sabe cómo manejar presigned URLs correctamente.

**Concepto:** Powers — paquetes on-demand que combinan MCP tools, steering y hooks especializados para una tecnología. Se activan solo cuando los necesitas. Diferencia entre Power y steering genérico.

**Kiro en acción:** activar un Power de AWS S3. Ver qué agrega al contexto — documentación técnica precisa del SDK, mejores prácticas de IAM, patrones de URL firmadas. Comparar calidad del código generado antes y después.

**Cierre:** el alumno entiende el concepto de Power como amplificador de contexto especializado.

---

### Clase 6.3 — Implementar upload seguro de imágenes

**Problema:** ejecutar las tareas del spec S3 — endpoint para generar URL firmada, upload directo desde el frontend, referencia en base de datos, validación de tipo y tamaño.

**Concepto:** task execution sobre infraestructura cloud. Cómo las waves separan backend (endpoint, IAM, S3 config) de frontend (componente de upload, preview).

**Kiro en acción:** ejecutar waves del spec S3. Verificar que el upload no pasa por nuestro servidor (directo a S3) y que las URLs tienen expiración correcta.

**Cierre:** commit `feat(media): add S3 image upload for user and event profiles`.

---

## BLOQUE 7 — Deploy en AWS

### Clase 7.1 — Steering de deploy (`aws-deploy.md`)

**Problema:** llegamos al deploy y Kiro no sabe nada de nuestra configuración AWS — regiones, variables de entorno, nombres de buckets, estrategia de rollback.

**Concepto:** steering `manual` para deploy — lo activamos solo cuando vamos a hacer deploy. Por qué `manual` y no `always`: las instrucciones de deploy no deben estar en el contexto mientras desarrollamos.

**Kiro en acción:** crear `.kiro/steering/aws-deploy.md` — Elastic Beanstalk para backend, RDS PostgreSQL, Amplify para frontend, S3 bucket config, variables de entorno por ambiente, dominios y rollback. Activar el steering y hacer una pregunta de deploy para ver la diferencia.

**Cierre:** commit `docs: add AWS deploy steering`.

---

### Clase 7.2 — MCP Servers: conectar herramientas externas

**Problema:** durante el deploy necesitamos consultar documentación de AWS, estado de recursos y logs — sin salir del IDE.

**Concepto:** MCP Servers — protocolo que conecta Kiro con herramientas y fuentes externas en tiempo real. Diferencia entre MCP y steering: MCP consulta sistemas vivos; steering es conocimiento estático.

**Kiro en acción:** configurar un MCP Server para consultar documentación de AWS. Ver cómo Kiro puede responder preguntas sobre Elastic Beanstalk con documentación actualizada directamente en el chat.

**Cierre:** el alumno entiende MCP como el mecanismo para ampliar Kiro con cualquier herramienta externa.

---

### Clase 7.3 — Deploy del backend en Elastic Beanstalk + RDS

**Problema:** desplegar Django + PostgreSQL en AWS. Hay muchas variables de entorno, configuraciones de seguridad y un orden específico para no romper la base de datos.

**Concepto:** usar Kiro con steering de deploy activado + MCP para guiar el proceso de deploy paso a paso sin errores.

**Kiro en acción:** con steering de deploy activado, pedirle a Kiro el plan de deploy para Elastic Beanstalk — variables de entorno, migraciones, health check, security groups. Ejecutar cada paso con Kiro verificando que sea correcto.

**Cierre:** backend desplegado. Commit `chore: add beanstalk deploy configuration`.

---

### Clase 7.4 — Deploy del frontend en Amplify

**Problema:** desplegar Next.js en Amplify — variables de entorno del frontend, build config, apuntar a la API de backend en producción.

**Concepto:** deploy frontend separado del backend. Cómo Kiro ayuda con la configuración de Amplify sin necesitar salir al dashboard de AWS.

**Kiro en acción:** guiar el deploy de Amplify con Kiro. Configurar `amplify.yml`, variables de entorno de producción, dominio personalizado.

**Cierre:** app completa en producción. Commit `chore: add amplify deploy configuration`. MVP desplegado.

---

## BLOQUE 8 — Lambda: funciones asíncronas avanzadas

### Clase 8.1 — Feature Spec Design-First para cierre automático de eventos

**Problema:** los eventos de Hatsik deben cerrarse automáticamente cuando pasa su fecha límite. Esto no puede ser un cron job en Django — el servidor de Beanstalk podría estar apagado o escalado a cero.

**Concepto:** Design-First cuando la constraint técnica (ejecución asíncrona y desacoplada) dicta la solución. AWS Lambda + EventBridge Scheduler como arquitectura para jobs async.

**Kiro en acción:** Feature Spec Design-First para cierre automático. Kiro propone: Lambda function que consulta eventos vencidos, EventBridge Scheduler que la dispara cada hora, actualización de estado via API interna o acceso directo a RDS.

**Cierre:** design aprobado con decisión de arquitectura documentada.

---

### Clase 8.2 — Power de AWS Lambda: implementar el cierre automático

**Problema:** escribir la Lambda correctamente — permisos IAM mínimos, manejo de errores, idempotencia, logging a CloudWatch.

**Concepto:** Power de AWS Lambda — trae al contexto las mejores prácticas específicas de Lambda: cold starts, timeouts, permisos de VPC, manejo de errores y logging.

**Kiro en acción:** activar Power de Lambda. Ejecutar tasks del spec — function handler, IAM role, EventBridge rule, deploy config. Kiro genera código idiomático de Lambda sin errores comunes.

**Cierre:** commit `feat(jobs): add lambda for automatic event closure`.

---

### Clase 8.3 — Agent Skills: crear un skill reutilizable para deploy de Lambdas

**Problema:** cada vez que necesitemos deployar una nueva Lambda tenemos que repetir los mismos pasos — empaquetar, subir a S3, actualizar función, verificar. Debería ser un workflow reutilizable.

**Concepto:** Agent Skills — paquetes de instrucciones, scripts y plantillas que se activan por tarea y son reutilizables por cualquier miembro del equipo. Diferencia entre Skill, Hook y Power.

**Kiro en acción:** crear un Agent Skill `deploy-lambda` — instrucciones de empaquetado, upload, actualización de función y verificación de health. Activar el skill para deployar la función de cierre automático. Ver cómo el workflow es completamente reproducible.

**Cierre:** commit `chore: add kiro skill for lambda deployment`. El alumno domina todas las herramientas de Kiro.

---

## BLOQUE 9 — Cierre del curso

### Clase 9.1 — Mapa completo de Kiro en el proyecto

**Problema:** llegamos al final del curso con un producto en producción pero ¿sabemos cuándo usar qué herramienta de Kiro?

**Concepto:** síntesis del curso — el árbol de decisión completo para elegir entre Vibe, Specs (Requirements-First / Design-First / Quick Plan), Bugfix Spec, Steering (always/fileMatch/auto/manual), Hooks (onFileSave/onSpecTaskComplete/manual), MCP, Powers y Skills.

**Kiro en acción:** recorrer el repositorio de Hatsik completo y señalar dónde está cada capacidad de Kiro en uso — steering activo, hooks configurados, specs archivadas, powers instalados.

**Cierre:** el alumno tiene un mental model claro de Kiro como sistema de trabajo, no como chat.

---

### Clase 9.2 — Kiro en equipos: cómo mantener el proyecto a largo plazo

**Problema:** el curso termina pero el proyecto sigue. ¿Cómo mantienen el contexto de Kiro actualizado? ¿Cómo onboardean a un nuevo desarrollador?

**Concepto:** Kiro como inversión de equipo — steering evoluciona con el proyecto, hooks se mejoran, specs son documentación viva, powers se actualizan con nuevas versiones de AWS.

**Kiro en acción:** simular onboarding de un nuevo dev — abrir el proyecto en Kiro por primera vez, ver cómo el steering le da contexto inmediato, cómo los specs explican decisiones pasadas, cómo los hooks ya están configurados.

**Cierre:** el alumno sabe que Kiro no es solo para escribir código — es para mantener el conocimiento del proyecto vivo y accesible.

---

## Resumen del curso

| Bloque | Nombre | Clases | Tiempo aprox. |
|---|---|---|---|
| 0 | Bienvenida y entorno | 2 | ~20 min |
| 1 | Steering fundacional | 4 | ~40 min |
| 2 | Auth con Feature Specs | 6 | ~60 min |
| 3 | Dashboard y Events | 5 | ~50 min |
| 4 | EventAccess, Items, Assignments, Moderation | 7 | ~70 min |
| 5 | Frontend con Next.js | 5 | ~50 min |
| 6 | S3 e imágenes | 3 | ~30 min |
| 7 | Deploy en AWS | 4 | ~40 min |
| 8 | Lambda avanzado | 3 | ~30 min |
| 9 | Cierre | 2 | ~20 min |
| **Total** | | **41 clases** | **~410 min (~7 h)** |

---

## Árbol de decisión: ¿qué uso en Kiro?

```
¿Tengo un problema de producto o ingeniería?
│
├─ Es una pregunta rápida o exploración inicial
│   └─ Agentic Chat / Vibe mode
│
├─ Es una regla o convención que debe persistir
│   └─ Steering
│       ├─ Siempre relevante → always
│       ├─ Solo para ciertos archivos → fileMatch
│       ├─ Kiro decide cuándo es relevante → auto
│       └─ Lo activo yo manualmente → manual
│
├─ Es una feature nueva
│   ├─ Feature conocida, bajo riesgo → Quick Plan
│   ├─ Reglas de negocio complejas → Feature Spec Requirements-First
│   └─ Decisión técnica dicta el diseño → Feature Spec Design-First
│
├─ Es un bug con riesgo de regresión
│   └─ Bugfix Spec
│
├─ Es una automatización del IDE
│   └─ Hook
│       ├─ Al guardar archivo → onFileSave
│       ├─ Al completar tarea de spec → onSpecTaskComplete
│       └─ Activación manual → manual
│       │
│       └─ Acción:
│           ├─ Determinista (tests, lint) → Run Command
│           └─ Contextual (revisión, resumen) → Ask Kiro
│
├─ Necesito conectar una herramienta externa
│   └─ MCP Server
│
├─ Necesito expertise en una tecnología específica
│   └─ Power (AWS, PostgreSQL, etc.)
│
└─ Tengo un workflow repetible que quiero compartir
    └─ Agent Skill
```

---

## Materiales por clase (a preparar)

Cada clase necesita:
- [ ] Pantalla inicial: el estado del repo ANTES de la clase
- [ ] El "problema" planteado en voz alta al inicio (no más de 30 segundos)
- [ ] La demo de Kiro en vivo (la parte que justifica la clase)
- [ ] El commit final que deja el repo en estado limpio
- [ ] Slide de cierre: resumen del concepto visto y cuándo aplicarlo

---

*Plan generado el 2026-06-01. Basado en docs/PRODUCT_OVERVIEW.md, docs/MODULES_SPEC.md, docs/DATABASE_SCHEMA.md, docs/UI_UX_SPEC.md y docs/hatsik-brand-identity.md.*
