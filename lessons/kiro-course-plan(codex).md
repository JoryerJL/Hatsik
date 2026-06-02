# Plan de curso práctico de Kiro construyendo Hatsik

Este documento define una planeación inicial para grabar un curso completo donde el alumno aprende Kiro mientras construye **Hatsik**, una web app para organizar convivios, compartir una lista de ítems por link/QR y coordinar quién lleva qué.

La intención del curso no es enseñar Kiro como una lista aislada de funciones, sino como una herramienta de trabajo real: aparece un problema de producto o ingeniería, se entiende la teoría mínima necesaria y se resuelve usando Kiro en contexto.

## Decisión recomendada de stack

Para el curso principal conviene usar:

| Capa | Recomendación | Por qué |
|---|---|---|
| Frontend | Next.js + TypeScript | Permite enseñar una app real con rutas, layouts, auth, formularios, estado de UI, consumo de API y despliegue en Amplify sin quedarse en React aislado. |
| Backend | Django + Django REST Framework | Da estructura clara para Auth, permisos, modelos, validaciones y endpoints sin convertir el curso en caos de infraestructura. |
| Base de datos | PostgreSQL | Encaja con el modelo relacional documentado en `docs/DATABASE_SCHEMA.md`. |
| Infra | AWS Elastic Beanstalk + RDS | Buen equilibrio: despliegue real en AWS sin meter microservicios demasiado pronto. |
| Archivos | AWS S3 | Permite enseñar uploads, storage seguro, URLs firmadas y assets sin mezclar archivos con la base de datos. |
| Tareas puntuales | AWS Lambda como módulo avanzado | Ideal para cierre automático de eventos, emails transaccionales o jobs, pero no como base del MVP. |
| Frontend deploy opcional | Amplify Hosting | Útil si se separa frontend/backend, pero no debería dominar el curso. |

### Por qué no arrancar con microservicios

Hatsik todavía es un MVP con reglas de dominio bastante conectadas: eventos, participantes, ítems, asignaciones y sugerencias dependen mucho entre sí. Separarlo en microservicios desde el inicio obligaría a enseñar comunicación distribuida, consistencia, despliegues múltiples y observabilidad antes de que el alumno entienda el producto.

Mejor enfoque:

1. Construir un **monolito modular** con Django.
2. Separar responsabilidades internas por módulos: `Auth`, `Events`, `EventAccess`, `Items`, `Assignments`, `Moderation`.
3. Agregar AWS Lambda solo cuando exista un problema que lo justifique.

Así el curso enseña arquitectura con criterio, no tecnología por ansiedad.

## Enfoque didáctico

Cada clase debe seguir esta estructura:

1. **Problema real:** algo que Hatsik necesita resolver.
2. **Teoría mínima:** concepto necesario para no copiar código a ciegas.
3. **Uso de Kiro:** steering, specs, prompts, tareas, revisión o generación guiada.
4. **Implementación:** construir una parte real del producto.
5. **Cierre profesional:** pruebas, commit, documentación o refactor.

Ejemplo de framing:

> “Necesitamos que el proyecto mantenga commits consistentes. Antes de programar más, vamos a crear steering en Kiro para que entienda nuestra convención de commits, estructura de módulos y reglas de calidad.”

## Capacidades de Kiro que debe cubrir el curso

El curso debe enseñar Kiro como sistema de trabajo, no solo como chat. Las capacidades se introducirán cuando el proyecto las necesite.

| Capacidad de Kiro | Qué es | Cómo se usará en Hatsik |
|---|---|---|
| Agentic Chat | Conversación con contexto del proyecto para explicar, generar, modificar o depurar código. | Para explorar el código, pedir explicaciones, resolver errores y hacer cambios pequeños. |
| Vibe mode | Modo conversacional sin artefactos estructurados. | Para exploración rápida, prototipos y dudas puntuales donde no hace falta planificación formal. |
| Specs | Sistema estructurado para convertir ideas en `requirements.md`, `design.md` y `tasks.md`. | Para construir módulos grandes: Auth, Events, Assignments, S3 uploads y deploy. |
| Feature Specs | Specs para nuevas funcionalidades. | Para desarrollar vertical slices completos del producto. |
| Bugfix Specs | Specs para diagnosticar bugs y prevenir regresiones. | Para clases de debugging: permisos mal aplicados, cálculo incorrecto de estado, uploads fallidos. |
| Requirements-First | Flujo de planning que empieza por comportamiento esperado y luego diseña solución técnica. | Para módulos guiados por producto, como solicitudes de entrada, sugerencias y asignaciones. |
| Design-First | Flujo de planning que empieza por arquitectura/diseño técnico y luego deriva requisitos. | Para decisiones técnicas como S3, despliegue AWS, Lambda/EventBridge o permisos complejos. |
| Quick Plan | Modo que genera requirements, design y tasks en una sola pasada, sin aprobaciones entre fases. | Para features conocidas y de bajo riesgo, como pantallas simples o ajustes de UI. |
| Task execution | Ejecución y seguimiento de tareas desde `tasks.md`; Kiro puede correr tareas independientes en paralelo por waves. | Para enseñar cómo ejecutar por partes, revisar progreso y no perder trazabilidad. |
| Steering | Archivos markdown persistentes que le dan contexto, reglas y estándares a Kiro. | Para producto, stack, estructura, arquitectura, UI, testing, seguridad, commits y deploy. |
| Steering con inclusión | Steering `always`, `fileMatch`, `manual` y `auto` para cargar contexto solo cuando corresponde. | Para evitar sobrecargar contexto: reglas de Next.js solo en frontend, reglas Django solo en backend, reglas AWS solo en deploy. |
| Hooks | Automatizaciones por eventos del IDE: guardar archivo, crear archivo, prompt submit, agent stop, pre/post tool use, pre/post spec task, manual. | Para lint/test al guardar, revisión post-tarea, seguridad antes de comandos sensibles y checklist manual de PR. |
| Hook actions | Acciones de hook: `Ask Kiro` o `Run Command`. | `Run Command` para lint/tests deterministas; `Ask Kiro` para revisión contextual o generación de resumen. |
| MCP Servers | Integración con herramientas y fuentes externas. | Para conectar documentación, servicios o herramientas cuando haga falta ampliar contexto técnico. |
| Agent Skills | Paquetes reutilizables de instrucciones, scripts y plantillas que se activan por tarea. | Para enseñar workflows repetibles: review, documentación, deploy o testing. |
| Powers | Paquetes on-demand que combinan MCP, steering y hooks para tecnologías específicas. | Para módulos AWS: Amplify, Lambda, infraestructura, PostgreSQL/Aurora, testing API o documentación externa. |

### Regla pedagógica para elegir modo de Kiro

| Situación | Modo recomendado |
|---|---|
| Pregunta rápida o explicación de código | Agentic Chat / Vibe |
| Feature grande con reglas de negocio | Feature Spec Requirements-First |
| Feature técnicamente compleja | Feature Spec Design-First |
| Feature conocida y de bajo riesgo | Quick Plan |
| Bug con riesgo de regresión | Bugfix Spec |
| Reglas permanentes del proyecto | Steering |
| Automatización repetible | Hook |
| Integración con herramienta externa | MCP o Power |
| Workflow compartible/reutilizable | Skill o Power |

### Steering recomendado para Hatsik

El curso debe crear steering progresivamente. No todo desde el día uno: primero los fundamentos, luego steering especializado cuando aparezca el problema.

| Archivo sugerido | Inclusión | Contenido |
|---|---|---|
| `.kiro/steering/product.md` | `always` | Qué es Hatsik, roles, MVP, exclusiones y propuesta de valor. |
| `.kiro/steering/tech.md` | `always` | Next.js, Django REST Framework, PostgreSQL, S3, Amplify, Elastic Beanstalk, Lambda/EventBridge. |
| `.kiro/steering/structure.md` | `always` | Organización del repo, módulos backend/frontend y naming. |
| `.kiro/steering/domain-rules.md` | `auto` | Reglas de negocio: roles, accesos, asignaciones, estados calculados, sugerencias. |
| `.kiro/steering/ui-brand.md` | `fileMatch` | Tokens visuales, tono de voz, componentes y UX de Hatsik. |
| `.kiro/steering/nextjs-patterns.md` | `fileMatch` | Rutas, layouts, componentes, formularios, fetchers y manejo de auth en frontend. |
| `.kiro/steering/django-api-patterns.md` | `fileMatch` | Serializers, viewsets, permisos, servicios, validaciones y errores API. |
| `.kiro/steering/testing-standards.md` | `auto` | Qué probar, estilo de tests, escenarios Gherkin y prevención de regresiones. |
| `.kiro/steering/security.md` | `always` | Tokens hasheados, respuestas genéricas, permisos, secretos, uploads seguros. |
| `.kiro/steering/git-commits.md` | `manual` | Commits convencionales, tamaño de cambios y checklist antes de commit. |
| `.kiro/steering/aws-deploy.md` | `manual` | Amplify, Elastic Beanstalk, RDS, S3, variables, dominios y rollback. |

### Hooks recomendados para Hatsik

| Hook | Trigger | Acción | Uso didáctico |
|---|---|---|---|
| Format frontend on save | File Save `*.ts`, `*.tsx` | Run Command | Ejecutar formatter/linter en frontend. |
| Run backend checks on save | File Save `*.py` | Run Command | Ejecutar formatting o tests focalizados de Django. |
| Review changed code after agent stops | Agent Stop | Ask Kiro | Pedir revisión de cambios generados y riesgos. |
| Protect secrets before tool use | Pre Tool Use `write` / `shell` | Ask Kiro o Run Command | Detectar `.env`, keys o tokens antes de escribir/ejecutar. |
| Validate spec task completion | Post Task Execution | Run Command | Correr tests/lint después de completar una tarea de spec. |
| Generate commit summary | Manual Trigger | Ask Kiro | Crear resumen de cambios y sugerir commit convencional. |
| API contract check | Manual Trigger | Run Command | Validar endpoints o colección de pruebas API. |

### Powers recomendados para el curso

Los powers se deben enseñar como “especialistas que cargo cuando el problema lo amerita”, no como magia permanente.

| Power o tipo de power | Cuándo usarlo en el curso |
|---|---|
| AWS Amplify | Despliegue del frontend Next.js en Amplify Hosting. |
| AWS Lambda / Lambda durable functions | Cierre automático por fecha límite o tareas serverless avanzadas. |
| AWS Infrastructure as Code / CDK / CloudFormation | Si se decide enseñar infraestructura reproducible. |
| Aurora PostgreSQL / PostgreSQL | Cuando se despliegue o inspeccione la base en AWS. |
| Postman / API Testing | Para validar endpoints del backend. |
| Context7 o web research | Para traer documentación actualizada de librerías sin pegar contexto manualmente. |
| SonarQube / seguridad | Como módulo de calidad o revisión avanzada. |

> Nota importante: **Steering, Hooks, Skills y Powers no son lo mismo**. Steering guarda reglas del proyecto; Hooks automatizan eventos; Skills empaquetan workflows reutilizables; Powers combinan herramientas MCP, steering y hooks para una tecnología o dominio específico.

## Qué se necesita para el proyecto

### Herramientas locales

- Kiro instalado y configurado.
- Git y cuenta de GitHub.
- Node.js LTS.
- Python 3.12+.
- PostgreSQL local o Docker.
- Docker Desktop, recomendado para base de datos local.
- Editor auxiliar opcional, aunque el curso debe trabajar principalmente desde Kiro.

### Cuentas externas

- AWS account.
- Bucket S3 para imágenes y archivos del curso.
- Dominio opcional para despliegue final.
- Servicio de email transaccional o AWS SES para verificación y recuperación de contraseña.

### Conocimientos previos recomendados

- HTML/CSS básico.
- JavaScript básico.
- Python básico.
- Git básico.
- Conceptos mínimos de HTTP: request, response, status codes, JSON.

## Proyecto que se construye

Hatsik es una app web responsiva para organizar convivios.

El usuario puede:

- Crear cuenta con email y contraseña.
- Verificar email y recuperar contraseña.
- Crear eventos privados.
- Compartir eventos por link o QR.
- Solicitar entrada a eventos.
- Aprobar o rechazar participantes.
- Agregar ítems con cantidad o sin cantidad.
- Asignarse ítems total o parcialmente.
- Marcar asignaciones como compradas.
- Sugerir ítems nuevos.
- Delegar gestión a co-admins.

Como extensión práctica para enseñar S3, el curso puede agregar **imagen/banner del evento** después del MVP base. No conviene usar imágenes por ítem en el MVP porque la documentación actual las deja fuera de alcance, pero una imagen opcional del evento funciona bien como módulo didáctico sin contaminar el dominio principal.

## Módulos del curso

### Módulo 0 — Preparación del curso y mentalidad de Kiro

**Objetivo:** que el alumno entienda cómo se trabajará durante todo el curso.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 0.1 | Tenemos una idea, pero necesitamos convertirla en proyecto ejecutable. | Cómo usar Kiro como copiloto de producto, no solo generador de código. | Visión del producto Hatsik. |
| 0.2 | Si no damos contexto, la IA inventa. | Steering inicial del proyecto. | `.kiro/steering/product.md`, `.kiro/steering/tech.md`, `.kiro/steering/structure.md`. |
| 0.3 | No todo requiere el mismo nivel de planificación. | Vibe vs Specs, Requirements-First, Design-First y Quick Plan. | Guía de decisión para elegir modo de trabajo. |
| 0.4 | Necesitamos commits consistentes desde el inicio. | Steering para Git y commits. | Regla de commits convencionales y formato de mensajes. |
| 0.5 | Hay tareas repetitivas que no deberíamos pedir manualmente siempre. | Hooks y hook actions. | Primer hook manual para generar resumen de commit. |
| 0.6 | Algunas tecnologías necesitan conocimiento especializado. | Powers, MCP y Skills. | Lista de powers sugeridos para AWS, API testing y documentación. |

### Módulo 1 — Análisis del producto y especificación

**Objetivo:** enseñar a convertir documentación de producto en tareas técnicas.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 1.1 | El producto tiene muchos módulos y podemos perdernos. | Cómo pedir resumen estructurado desde documentación. | Mapa de módulos: Auth, Dashboard, Events, EventAccess, Items, Assignments, Moderation. |
| 1.2 | Necesitamos saber qué entra y qué NO entra al MVP. | Feature Specs Requirements-First para controlar scope. | `requirements.md` de alcance MVP. |
| 1.3 | Las historias de usuario deben transformarse en criterios verificables. | EARS notation, análisis de requisitos y generación de tareas. | Backlog inicial priorizado y verificable. |
| 1.4 | El curso necesita enseñar rapidez sin perder estructura. | Quick Plan para una feature simple. | Spec completo generado en una pasada para una pantalla menor. |

### Módulo 2 — Arquitectura base

**Objetivo:** crear el esqueleto técnico sin sobrearquitectura.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 2.1 | Hay que elegir stack sin perseguir moda. | Pedir comparación con tradeoffs. | Decisión: Next.js + Django + PostgreSQL + AWS. |
| 2.2 | Necesitamos estructura modular para crecer. | Steering de arquitectura modular. | Estructura backend por apps/módulos. |
| 2.3 | Necesitamos frontend ordenado. | Steering de componentes y diseño. | Estructura Next.js por rutas, layouts, features y componentes. |
| 2.4 | Queremos que Kiro respete las reglas del proyecto. | Refinar steering con convenciones reales. | Steering actualizado para backend, frontend, testing y commits. |

### Módulo 3 — Base de datos y dominio

**Objetivo:** implementar el modelo relacional documentado.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 3.1 | Tenemos entidades conectadas y reglas de historial. | Generar modelos desde schema documentado. | Modelos: users, events, participations, items, assignments, suggestions. |
| 3.2 | Los estados no siempre se guardan. | Diseñar propiedades calculadas. | Estado calculado de ítems y progreso. |
| 3.3 | No podemos borrar historial de participación. | Traducir reglas de negocio a modelo. | Estados `pending`, `accepted`, `rejected`, `left`, `removed`. |
| 3.4 | Cantidades y unidades deben ser consistentes. | Pedir validaciones de dominio. | Validaciones para ítems binarios/cuantiﬁcados. |

### Módulo 4 — Auth y cuenta

**Objetivo:** construir la entrada segura a Hatsik.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 4.1 | Todo usuario debe tener cuenta. | Generar flujo Auth desde criterios de aceptación. | Registro con email y contraseña. |
| 4.2 | Una cuenta no verificada no debe usar la app. | Pedir middleware/guards con reglas claras. | Bloqueo por email no verificado. |
| 4.3 | Los tokens no deben guardarse planos. | Preguntar por seguridad antes de implementar. | Verificación de email con token hasheado. |
| 4.4 | Recuperar contraseña sin filtrar emails. | Implementar respuestas genéricas. | Flujo de recuperación seguro. |
| 4.5 | El frontend necesita pantallas limpias. | Generación UI guiada por tokens de marca. | Login, registro, verificación pendiente y recuperación. |

### Módulo 5 — Eventos y dashboard

**Objetivo:** construir el flujo principal del owner.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 5.1 | El usuario necesita ver sus eventos. | Construir endpoint + pantalla desde historia de usuario. | Dashboard `Mis eventos`. |
| 5.2 | Crear evento también crea participación owner. | Pedir implementación atómica. | Crear evento + owner aceptado. |
| 5.3 | El evento necesita link privado estable. | Diseñar token opaco. | `public_share_token` y link compartible. |
| 5.4 | El QR no debe persistirse en DB. | Resolver generación on-demand. | QR descargable PNG. |
| 5.5 | Cerrar, reabrir y cancelar tienen reglas distintas. | Kiro como revisor de estados. | Acciones de ciclo de vida del evento. |

### Módulo 6 — Acceso por link y solicitudes

**Objetivo:** enseñar permisos reales y estados de acceso.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 6.1 | Tener link no significa tener acceso total. | Modelar permisos por estado. | Ficha pública limitada del evento. |
| 6.2 | El usuario solicita entrada. | Crear flujo backend/frontend completo. | Solicitud `pending`. |
| 6.3 | Owner y co-admin pueden aprobar/rechazar. | Pedir control de permisos por rol. | Gestión de solicitudes. |
| 6.4 | Un rechazo no permite reintento automático. | Casos borde con Kiro. | Validaciones de reingreso/rechazo. |
| 6.5 | Salirse del evento tiene reglas. | Kiro revisa escenarios negativos. | Salida voluntaria con bloqueos por asignaciones. |

### Módulo 7 — Lista de ítems

**Objetivo:** construir el corazón visual del producto.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 7.1 | Owner define qué se necesita. | Formularios generados desde reglas. | Crear ítem. |
| 7.2 | Un ítem puede tener cantidad o ser binario. | Pedir validaciones condicionales. | Ítems cuantificados y binarios. |
| 7.3 | Editar con asignaciones puede romper datos. | Generar restricciones de negocio. | Edición segura de cantidad. |
| 7.4 | Eliminar puede borrar asignaciones. | Confirmaciones obligatorias. | Eliminación con modal de advertencia. |
| 7.5 | La UI debe ser escaneable. | Aplicar diseño Hatsik. | Tarjetas de ítems con estados visuales. |

### Módulo 8 — Asignaciones y compras

**Objetivo:** resolver el flujo más importante para participantes.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 8.1 | Un participante se apunta a llevar algo. | Generar flujo full-stack. | Crear asignación. |
| 8.2 | Nadie debe superar la cantidad disponible. | Validaciones de concurrencia y dominio. | Límite por cantidad disponible. |
| 8.3 | Modificar asignación recalcula estado. | Kiro ayuda a cubrir casos borde. | Modificar asignación propia. |
| 8.4 | Cancelar libera cantidad. | Implementar transición segura. | Cancelación propia y por owner. |
| 8.5 | Comprar es irreversible en MVP. | Confirmación obligatoria + inmutabilidad. | Marcar como comprado. |
| 8.6 | El estado del ítem no se guarda. | Derivar estado desde asignaciones. | Estados: sin asignar, parcial, cubierto, parcialmente comprado, comprado. |

### Módulo 9 — Sugerencias y moderación

**Objetivo:** enseñar flujos de revisión sin crear un sistema de notificaciones.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 9.1 | Participantes pueden proponer ítems. | Modelar sugerencias separadas de ítems oficiales. | Crear sugerencia pendiente. |
| 9.2 | El participante puede editar antes de revisión. | Reglas por estado. | Editar/eliminar sugerencia pendiente. |
| 9.3 | Owner/co-admin revisan. | Permisos por rol. | Aprobar/rechazar sugerencias. |
| 9.4 | Aprobar convierte sugerencia en ítem. | Transacción de negocio. | Conversión a `event_items`. |
| 9.5 | Rechazar puede incluir nota. | UX humana para errores/rechazos. | Nota de rechazo visible. |

### Módulo 10 — Co-admins y permisos avanzados

**Objetivo:** enseñar autorización granular.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 10.1 | El owner necesita ayuda. | Diseñar matriz de permisos. | Asignar co-admin. |
| 10.2 | Co-admin no es owner. | Revisión de permisos con Kiro. | Bloqueos: no edita evento, no edita lista base, no remueve participantes. |
| 10.3 | Revocar rol no borra asignaciones. | Separar rol de historial. | Revocar co-admin. |
| 10.4 | Remover participante tiene restricciones. | Casos borde de dominio. | Remoción con bloqueos por compras. |

### Módulo 11 — UI, marca y experiencia responsive

**Objetivo:** que el producto se sienta como Hatsik, no como CRUD genérico.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 11.1 | La UI necesita identidad. | Pasar brand identity a steering de UI. | Tokens: coral, blanco, radios, tipografías. |
| 11.2 | La navegación debe ser simple. | Generar layout responsive con restricciones. | Header adaptativo y drawer móvil. |
| 11.3 | El detalle del evento concentra muchas acciones. | Organizar secciones sin crear ruido. | Detalle con resumen, solicitudes, lista, sugerencias y participantes. |
| 11.4 | Los mensajes no deben sonar robóticos. | Steering de tono de voz. | Microcopy cálido y directo. |

### Módulo 12 — Testing, revisión y calidad con Kiro

**Objetivo:** enseñar que IA sin verificación es deuda técnica.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 12.1 | Necesitamos pruebas de reglas críticas. | Generar tests desde escenarios Gherkin. | Tests de Auth, Events, Assignments. |
| 12.2 | Kiro puede equivocarse con permisos. | Revisión adversarial de permisos. | Checklist de autorización. |
| 12.3 | Los cambios deben ser revisables. | Pedir resumen de diff y riesgos. | PR/commit por módulo. |
| 12.4 | Refactor sin romper comportamiento. | Kiro como asistente de refactor. | Limpieza modular y tests verdes. |

### Módulo 13 — Deploy en AWS

**Objetivo:** llevar Hatsik a producción básica sin perder el foco.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 13.1 | Local no es producción. | Crear checklist de deploy. | Variables, settings y configuración por ambiente. |
| 13.2 | Backend necesita servidor y base real. | Guiar despliegue a Elastic Beanstalk + RDS. | API Django desplegada. |
| 13.3 | Frontend necesita hosting. | Opciones con tradeoff. | Frontend desplegado en Amplify Hosting o hosting equivalente. |
| 13.4 | Emails transaccionales necesitan proveedor. | Integrar SES o proveedor similar. | Verificación y reset funcionando en producción. |
| 13.5 | El producto necesita validación final. | Kiro para checklist de QA. | MVP navegable end-to-end. |

### Módulo 14 — Imágenes con S3 como extensión práctica

**Objetivo:** enseñar manejo real de archivos en AWS sin convertir la base de datos en almacenamiento de imágenes.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 14.1 | Queremos que cada evento tenga una imagen/banner opcional. | Diseñar una extensión post-MVP sin romper el alcance base. | Campo opcional de imagen del evento. |
| 14.2 | Las imágenes no deben guardarse en PostgreSQL. | Separar metadata de archivo y storage. | S3 bucket + columna con key/path del archivo. |
| 14.3 | Subir archivos directo al backend puede ser pesado. | Comparar upload vía backend vs URL firmada. | Flujo recomendado con presigned URLs. |
| 14.4 | No cualquier archivo debe aceptarse. | Validaciones de tipo, tamaño y seguridad. | Restricciones de imagen: MIME type, peso máximo y nombre seguro. |
| 14.5 | La UI necesita preview y estado de carga. | Kiro para UX de uploads. | Selector de imagen, preview, loading y error states. |

### Módulo 15 — Lambda como extensión avanzada

**Objetivo:** introducir serverless solo cuando existe un problema concreto.

| Clase | Problema práctico | Kiro enseña | Entregable |
|---|---|---|---|
| 15.1 | El cierre por fecha límite no debería depender de un usuario. | Diseñar tarea programada. | Lambda/EventBridge para cierre automático. |
| 15.2 | Las notificaciones de evento son post-MVP. | Diseñar extensión sin romper MVP. | Diseño de emails de evento post-MVP. |
| 15.3 | ¿Cuándo sí conviene separar un servicio? | Tradeoffs de microservicios. | Criterios para extraer servicios futuros. |

## Orden recomendado de grabación

1. Presentación del problema y demo objetivo.
2. Kiro como sistema de trabajo: chat, vibe, specs, planning modes, steering, hooks, skills, MCP y powers.
3. Setup del proyecto.
4. Backend base y modelo de datos.
5. Auth completo.
6. Eventos y dashboard.
7. Acceso por link/QR.
8. Ítems.
9. Asignaciones.
10. Sugerencias.
11. Roles y permisos.
12. UI/UX y responsive.
13. Testing y revisión.
14. Deploy.
15. Imágenes con S3 como extensión práctica.
16. Lambda/serverless como bonus avanzado.

## Momentos clave para enseñar Kiro

| Momento del proyecto | Cómo se enseña Kiro |
|---|---|
| Antes de programar | Crear steering para producto, arquitectura, UI, testing y commits. |
| Al recibir documentación larga | Pedir síntesis y extracción de requisitos. |
| Al definir módulo | Elegir entre Requirements-First, Design-First o Quick Plan según el riesgo. |
| Al planificar una feature grande | Convertir historias en Specs con `requirements.md`, `design.md` y `tasks.md`. |
| Al implementar | Pedir cambios pequeños, revisar diff, pedir riesgos. |
| Al encontrar regla complicada | Pedir tabla de casos borde antes de codear. |
| Al completar una spec task | Usar hooks post-task para correr tests/lint y validar avance. |
| Al cerrar una clase | Generar commit message, resumen de avance y próximos pasos. |
| Al romper algo | Usar Kiro para diagnóstico guiado, no para pegar soluciones a ciegas. |
| Al integrar AWS | Activar powers específicos para Amplify, Lambda, PostgreSQL/Aurora o infraestructura. |

## Lecciones donde el problema enseña la herramienta

Estos son buenos ganchos narrativos para grabar:

- “Kiro no sabe qué es Hatsik: vamos a enseñárselo con steering.”
- “No todo se resuelve igual: cuándo usar Vibe, Requirements-First, Design-First o Quick Plan.”
- “Tenemos demasiadas historias: vamos a convertirlas en tareas accionables.”
- “Repetimos esta revisión en cada tarea: vamos a automatizarla con hooks.”
- “Ahora necesitamos conocimiento especializado de AWS: vamos a usar powers en vez de saturar el chat.”
- “El modelo dice que el estado del ítem no se guarda: vamos a derivarlo.”
- “El usuario tiene link, pero no acceso: vamos a diseñar permisos correctamente.”
- “El co-admin puede moderar, pero no editar la lista: vamos a probar permisos.”
- “Comprar es irreversible: vamos a proteger una acción crítica con confirmación.”
- “La IA generó código, pero ahora toca revisar como ingenieros.”
- “Queremos subir imágenes, pero la base de datos no es un disco duro: vamos a usar S3.”
- “Este problema sí justifica Lambda; antes no.”

## Riesgos del curso y cómo evitarlos

| Riesgo | Cómo evitarlo |
|---|---|
| Meter demasiadas tecnologías desde el inicio. | Mantener el MVP en monolito modular y dejar Lambda como extensión avanzada. |
| Que el curso parezca tutorial de copiar prompts. | Cada clase empieza con problema y termina con entregable verificable. |
| Que Kiro reemplace el criterio del alumno. | Explicar teoría mínima antes de pedir generación. |
| Que el proyecto se vuelva gigante. | Respetar el scope MVP documentado y dejar notificaciones/eventos avanzados fuera. |
| Que la UI se vea genérica. | Usar `docs/hatsik-brand-identity.md` como steering de diseño. |

## Pendientes por decidir antes de grabar

1. Duración deseada del curso: intensivo corto o curso completo largo.
2. Nivel objetivo del alumno: principiante con bases o intermedio.
3. Si el frontend y backend vivirán en un solo repo o en repos separados.
4. Si se usará Docker obligatorio desde la primera clase.
5. Si AWS SES será obligatorio o se usará un proveedor más simple durante desarrollo.
6. Si el módulo de S3 será parte del curso principal o bonus final.
7. Si el módulo de Lambda será parte del curso principal o bonus final.

## Resultado esperado del curso

Al finalizar, el alumno debería tener:

- Una app Hatsik funcional end-to-end.
- Un repo con commits profesionales por módulo.
- Steering de Kiro para producto, arquitectura, UI, testing y commits.
- Specs de Kiro con requirements, design y tasks para módulos críticos.
- Hooks de Kiro para automatizar validaciones, revisiones y resúmenes.
- Criterio para usar Vibe, Quick Plan, Feature Specs, Bugfix Specs, Skills, MCP y Powers.
- Backend Django con reglas de dominio reales.
- Frontend Next.js responsive alineado a la marca.
- Base PostgreSQL coherente con el schema.
- Deploy básico en AWS.
- Manejo de imágenes con S3 usando buenas prácticas.
- Criterio para decidir cuándo usar o no microservicios/serverless.
