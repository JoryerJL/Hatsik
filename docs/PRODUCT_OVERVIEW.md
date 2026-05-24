# PRODUCT_OVERVIEW.md — Hatsik 🫱

> **Nombre:** Hatsik — del maya *"dividir, compartir"*
> **Versión:** 0.2 — Alineado con USER_STORIES.md
> **Fecha:** 2026-05-23
> **Estado:** En definición

---

## 1. Problema

Cada vez que alguien organiza un convivio —asado, posada, cumpleaños, picnic— el proceso se convierte en caos:

- El organizador termina respondiendo decenas de mensajes en WhatsApp preguntando "¿qué llevo?".
- La lista vive en notas de voz, capturas de pantalla o una hoja de papel que nadie tiene.
- Dos personas compran lo mismo (sobran refrescos, faltan limones).
- No hay forma de saber en tiempo real qué ya está cubierto y qué sigue pendiente.
- Si la persona que organizó no está disponible, nadie sabe qué falta.

**El dolor central:** la logística de "¿qué llevo?" no tiene un lugar digital, colaborativo y en tiempo real hecho específicamente para grupos de amigos y familia.

---

## 2. Solución y propuesta de valor

**Hatsik** es una app web donde cualquier persona puede crear un evento, definir la lista de artículos necesarios con o sin cantidades, compartir el evento vía link y dejar que los invitados se "apunten" a llevar lo que pueden —parcial o totalmente.

### Propuesta de valor por rol

| Rol | Qué gana |
|---|---|
| **Organizador** | Deja de ser el cuello de botella. Define la lista una vez y la app hace el seguimiento. |
| **Invitado** | Sabe exactamente qué falta, elige lo que puede traer y no tiene que preguntar. |
| **Co-admin** | Puede gestionar solicitudes y sugerencias sin que el organizador tenga que estar al pendiente. |

### Diferenciador

No es un gestor de tareas, no es un chat grupal. Es una herramienta de logística ligera, social y visual pensada específicamente para convivios. La lista avanza en tiempo real y cualquiera puede ver el estado de cada artículo con un vistazo.

---

## 3. Usuarios y roles

### 3.1 El usuario — entidad única del sistema

Existe un solo tipo de usuario en el sistema. Cualquier persona que quiera usar Hatsik **debe crear una cuenta** (email + contraseña). No hay acceso anónimo.

Un mismo usuario puede simultáneamente:
- Ser **Owner** de los eventos que él creó.
- Ser **Co-admin** en eventos donde otro le delegó ese rol.
- Ser **Participante** en eventos a los que fue invitado.

> **Decisión MVP:** El registro es por email + contraseña, con verificación de email y recuperación de contraseña. OAuth (Google) queda fuera del MVP pero en el roadmap.

### 3.2 Roles dentro de un evento

Los roles son exclusivos del contexto de cada evento. Un usuario no tiene un rol "global" — su rol depende del evento en que se encuentra.

| Rol en el evento | Quién lo tiene | Permisos |
|---|---|---|
| **Owner** | Quien creó el evento. | Crear y editar el evento, gestionar la lista base, agregar/editar/eliminar ítems, aprobar o rechazar solicitudes de entrada, aprobar/rechazar/modificar sugerencias antes de aprobar, asignar y revocar co-admins, remover participantes, cancelar asignaciones no compradas de otros participantes, marcar cualquier asignación como comprada, asignarse ítems, cerrar/reabrir/cancelar el evento. |
| **Co-admin** | Participante al que el Owner delegó permisos. | Aprobar o rechazar solicitudes de entrada, aprobar/rechazar/modificar sugerencias antes de aprobar y marcar cualquier asignación como comprada. No puede editar el evento, editar la lista base, nombrar otros co-admins, remover participantes ni cancelar asignaciones de otros. Puede asignarse ítems igual que cualquier participante. |
| **Participante** | Cualquier usuario que se unió al evento vía link/QR. | Ver la lista, asignarse ítems (parcial o total), modificar/cancelar sus asignaciones no compradas, sugerir nuevos ítems (van a aprobación), editar/eliminar sus sugerencias pendientes, marcar como comprado lo que le tocó y salirse del evento si cumple las reglas de salida. |

> El Owner también es participante: puede asignarse ítems de su propia lista.

---

## 4. Flujo principal (happy path)

```
Owner crea evento
    ↓
Agrega ítems a la lista (nombre obligatorio; cantidad opcional; unidad obligatoria si hay cantidad)
    ↓
Comparte link o QR del evento
    ↓
Usuario abre el link → inicia sesión o crea cuenta → envía solicitud de entrada
    ↓
Owner o co-admin ve la solicitud pendiente y la acepta o rechaza
    ↓          ↓
 Rechazado   Aceptado → usuario queda como Participante
                ↓
Cada participante selecciona qué puede llevar y, si aplica, cuánto puede llevar de cada ítem
(también pueden sugerir ítems nuevos, que el Owner o co-admin aprueban)
    ↓
La lista actualiza en tiempo real: "Quedan 800g de carne / 2kg asignados"
    ↓
Participante marca ítem como "comprado" cuando ya lo tiene
    ↓
Owner y todos ven el estado final del evento
```

---

## 5. Entidades principales

### 5.1 Evento

| Campo | Tipo | Notas |
|---|---|---|
| `nombre` | string | "Asado del sábado" |
| `descripcion` | string (opcional) | Contexto del convivio |
| `fecha_evento` | date | Cuándo es el convivio |
| `fecha_cierre_lista` | date (opcional) | Límite para asignarse ítems. **Incluido en MVP.** |
| `link_compartible` | string único | UUID o slug corto |
| `qr_code` | imagen generada | Generado automáticamente al crear el evento, descargable |
| `owner_id` | ref usuario | |
| `estado` | enum | `activo`, `cerrado`, `cancelado` |

### 5.2 Ítem de lista

| Campo | Tipo | Notas |
|---|---|---|
| `nombre` | string | "Carne" |
| `cantidad_total` | número (opcional) | 2. Si no se define, el ítem se trata como binario: alguien lo lleva o no lo lleva. |
| `unidad` | enum/catálogo (opcional) | Requerida solo cuando hay cantidad definida. Se selecciona desde catálogo controlado inicial: `kg`, `g`, `litros`, `ml`, `piezas`, `paquetes`, `bolsas`, `cajas`, `latas`, `botellas`, `garrafones`, `charolas`, `docenas`. |
| `estado` | enum | Ver sección 6 |

> Las sugerencias no son ítems oficiales hasta que Owner o Co-admin las aprueban. Mientras están pendientes/revisadas, se modelan como sugerencias de ítem, no como ítems activos de la lista.

### 5.3 Participación en el evento

Registra la relación entre un usuario y un evento, incluyendo su estado de acceso y rol.

| Campo | Tipo | Notas |
|---|---|---|
| `evento_id` | ref evento | |
| `usuario_id` | ref usuario | |
| `rol` | enum | `owner`, `co_admin`, `participante` |
| `estado_acceso` | enum | `pendiente`, `aceptado`, `rechazado` |
| `fecha_solicitud` | timestamp | Cuando envió la solicitud de entrada |
| `fecha_resolucion` | timestamp | Cuando fue aceptado o rechazado |

> El Owner se agrega automáticamente con `estado_acceso: aceptado` al crear el evento.
> Si un usuario se sale voluntariamente o es removido, deja de tener participación activa en el evento. La representación exacta del historial se definirá en `DATA_MODEL.md`.

### 5.4 Asignación

| Campo | Tipo | Notas |
|---|---|---|
| `item_id` | ref ítem | |
| `usuario_id` | ref usuario | Quién se apunta |
| `cantidad_asignada` | número (opcional) | Cuánto se lleva (ej. 0.5 kg). En ítems sin cantidad definida puede quedar vacío. |
| `estado` | enum | `asignado`, `comprado` |

> Un ítem con cantidad definida puede tener múltiples asignaciones de distintos invitados, siempre que la suma no supere la cantidad total. Un ítem sin cantidad definida funciona como asignación binaria: alguien confirma que lo lleva.

### 5.5 Sugerencia de ítem

Registra propuestas de nuevos ítems hechas por participantes antes de entrar a la lista oficial.

| Campo | Tipo | Notas |
|---|---|---|
| `evento_id` | ref evento | Evento donde se sugiere el ítem |
| `sugerido_por` | ref usuario | Participante que hizo la sugerencia |
| `nombre` | string | Nombre propuesto |
| `cantidad_total` | número (opcional) | Si se define, requiere unidad |
| `unidad` | enum/catálogo (opcional) | Requerida solo cuando hay cantidad definida |
| `estado` | enum | `pendiente_aprobacion`, `aprobada`, `rechazada` |
| `nota_rechazo` | string (opcional) | Visible para quien sugirió y para Owner/Co-admins en el historial |

> Si una sugerencia se aprueba, se crea un ítem oficial en la lista activa sin mostrar "sugerido por".

---

## 6. Estados de un ítem

Los estados se calculan automáticamente. En ítems con cantidad definida, el cálculo usa la suma de asignaciones. En ítems sin cantidad definida, el cálculo funciona de forma binaria: sin asignar, asignado/cubierto y comprado.

```
Sin asignar  →  Parcialmente cubierto  →  Cubierto  →  Parcialmente comprado  →  Comprado
     ↑                   ↑                   ↑                   ↑                    ↑
 Nadie lo ha       Hay asignaciones       La suma de       Al menos uno de       Todos los
 tomado aún        pero no cubren         asignaciones     los asignados         asignados
                   el total               = cantidad       marcó "comprado"      marcaron
                                          total            pero no todos         "comprado"
```

| Estado | Visualización sugerida | ¿Quién puede cambiarlo? |
|---|---|---|
| `sin_asignar` | Rojo / gris vacío | Sistema (automático) |
| `parcialmente_cubierto` | Amarillo / barra parcial | Sistema (automático) |
| `cubierto` | Verde / barra llena | Sistema (automático) |
| `parcialmente_comprado` | Verde azulado / barra con sección sólida y sección rayada | Sistema (automático) |
| `comprado` | Verde oscuro + ícono de check | Sistema (automático cuando todos los asignados marcan "comprado") |

---

## 7. Casos de uso detallados (MVP)

### CU-00: Registro y cuenta
- El usuario se registra con nombre de pantalla, email y contraseña.
- La contraseña debe tener mínimo 8 caracteres, al menos 1 letra y al menos 1 número.
- El sistema envía un correo de verificación y no permite usar la app hasta verificar la cuenta.
- Una cuenta no verificada puede iniciar sesión, pero solo ve una pantalla de verificación pendiente.
- Desde esa pantalla, el usuario puede reenviar el correo de verificación si no recibió o perdió el anterior.
- El reenvío de correo de verificación está limitado a 1 solicitud cada 60 segundos por usuario.
- El token de verificación de email expira en 24 horas.
- El token de recuperación de contraseña expira en 1 hora.
- La solicitud de recuperación de contraseña está limitada a 1 solicitud cada 60 segundos por email.
- El usuario puede iniciar sesión, cerrar sesión y solicitar recuperación de contraseña.
- Los correos de verificación y recuperación son transaccionales de cuenta; no son notificaciones sociales del evento.

### CU-01: Crear evento
- El Owner ingresa: nombre, fecha del convivio, fecha límite de asignaciones (opcional), descripción (opcional).
- Crear un evento no requiere confirmación obligatoria adicional al envío del formulario.
- El sistema genera el link compartible.

### CU-02: Gestionar lista de ítems
- El Owner puede agregar, editar y eliminar ítems de la lista mientras el evento esté activo.
- Cada ítem tiene nombre obligatorio. La cantidad total y la unidad son opcionales.
- Si un ítem no tiene cantidad definida, se trata como binario: alguien lo lleva o no lo lleva.
- Agregar un ítem no requiere confirmación obligatoria adicional al envío del formulario.
- Si un ítem no tiene asignaciones, el Owner puede editar nombre, cantidad y unidad.
- Editar un ítem sin asignaciones no requiere confirmación obligatoria.
- Si un ítem ya tiene asignaciones, el Owner solo puede editar la cantidad total.
- La cantidad total no puede reducirse por debajo de la suma ya asignada.
- Si un ítem ya tiene asignaciones, el sistema debe mostrar una advertencia antes de guardar cambios de cantidad.
- Guardar cambios de cantidad en un ítem con asignaciones requiere confirmación obligatoria del Owner.
- Eliminar cualquier ítem requiere confirmación obligatoria del Owner.

### CU-03: Compartir evento
- El sistema genera automáticamente un **link compartible** y un **código QR** al crear el evento.
- El QR es descargable (imagen PNG) para mandarlo por WhatsApp, imprimir o compartir por cualquier medio.
- Todos los eventos son **privados**: solo quien tenga el link o el QR puede acceder.
- No existe directorio ni búsqueda pública de eventos en el MVP ni en el roadmap inmediato.

### CU-04: Unirse al evento
- El usuario abre el link o escanea el QR.
- Si no tiene cuenta, el sistema lo lleva al registro. Una vez creada, el link lo redirige de vuelta al evento.
- El usuario envía una **solicitud de entrada**. Su estado queda en `pendiente`.
- Solicitar entrada a un evento no requiere confirmación obligatoria adicional.
- No se puede solicitar entrada a un evento `cerrado` o `cancelado`.
- Mientras espera aprobación, el usuario ve la **ficha del evento** (nombre, descripción, fecha) con un mensaje que indica que su participación está en proceso de aceptación por el organizador. No puede ver la lista ni interactuar con ella.
- El Owner y los co-admins ven la solicitud pendiente dentro del detalle del evento. No hay notificaciones de evento en el MVP.
- El Owner o un co-admin acepta o rechaza la solicitud.
- Si es **aceptado**, el usuario queda registrado como Participante y puede ver la lista y asignarse ítems.
- Si es **rechazado**, el usuario ve el estado rechazado al abrir la ficha del evento y no puede acceder a la lista.
- Un usuario rechazado no puede volver a solicitar acceso al mismo evento.
- Owner y Co-admin pueden cambiar una solicitud rechazada a aceptada si fue un error.

### CU-04b: Gestionar solicitudes de entrada
- El Owner y co-admins ven una sección "Solicitudes pendientes" dentro del evento.
- Pueden ver el nombre y email del solicitante.
- Aceptar → el usuario pasa a Participante y puede acceder a la lista al entrar al evento.
- Rechazar → el usuario ve el estado rechazado al abrir la ficha del evento y no tiene acceso a la lista.
- Aprobar una solicitud no requiere confirmación obligatoria.
- Rechazar una solicitud requiere confirmación obligatoria y no incluye motivo en el MVP.
- Una solicitud rechazada puede cambiarse a aceptada por Owner o Co-admin si fue un error.
- Si hay solicitudes sin revisar, se muestra un badge con el conteo en la vista del evento.

### CU-04c: Salirse de un evento
- Un Participante puede salirse voluntariamente de un evento si no tiene asignaciones activas.
- Salirse voluntariamente de un evento requiere confirmación obligatoria del participante.
- Si tiene asignaciones no compradas, debe cancelarlas antes de salirse.
- Si tiene asignaciones compradas, no puede salirse del evento en el MVP.
- Si un Co-admin se sale del evento, su rol de Co-admin se revoca automáticamente.
- El Owner no puede salirse de su propio evento.
- Un usuario que se salió voluntariamente puede volver a solicitar entrada usando el link o QR del evento.
- Si un usuario fue rechazado, luego aceptado por Owner/Co-admin y después se salió voluntariamente, puede volver a solicitar entrada.
- Si reingresa, vuelve siempre como Participante normal; no recupera automáticamente el rol de Co-admin.

### CU-05: Asignarse un ítem
- El participante selecciona un ítem de la lista.
- Si el ítem tiene cantidad definida, ingresa la cantidad que puede llevar (puede ser menor al total).
- Si el ítem no tiene cantidad definida, confirma que lo llevará.
- Crear una asignación no requiere confirmación obligatoria.
- Modificar una asignación propia no comprada no requiere confirmación obligatoria.
- En ítems con cantidad definida, el sistema valida que la suma total de asignaciones no supere la cantidad total del ítem.
- Si ya está "cubierto", el botón se desactiva pero puede verse quiénes lo tienen.
- El Owner puede cancelar asignaciones no compradas de cualquier participante.
- El Owner no puede modificar la cantidad de asignaciones de otros participantes; solo puede cancelarlas si no están compradas.
- Cancelar una asignación ajena requiere confirmación obligatoria del Owner.
- Cancelar una asignación propia requiere confirmación obligatoria del participante.
- El Co-admin no puede cancelar asignaciones de otros participantes.
- Al cancelar una asignación no comprada, la cantidad vuelve a estar disponible.

### CU-06: Sugerir un ítem
- Cualquier participante puede proponer una sugerencia de ítem con nombre obligatorio y cantidad opcional. Si define cantidad, también debe seleccionar unidad desde el catálogo controlado.
- Crear una sugerencia no requiere confirmación obligatoria adicional al envío del formulario.
- La sugerencia queda en estado `pendiente_aprobacion` y no aparece en la lista activa hasta ser aprobada.
- El participante puede editar o eliminar su sugerencia mientras esté pendiente de aprobación.
- Editar una sugerencia pendiente propia no requiere confirmación obligatoria.
- Eliminar una sugerencia pendiente propia requiere confirmación obligatoria.
- El Owner y los co-admins ven la sugerencia en la sección "Pendientes".
- Si se aprueba, el ítem entra a la lista activa sin mostrar "sugerido por". Si se rechaza (con nota opcional), el participante ve el estado de la sugerencia dentro del evento.

### CU-07: Aprobar/rechazar sugerencias
- El Owner o co-admin ve una sección "Sugerencias pendientes".
- Puede aprobar (el ítem entra a la lista activa) o rechazar (con nota opcional).
- Antes de aprobar, puede modificar nombre, cantidad y unidad de la sugerencia.
- Aprobar una sugerencia no requiere confirmación obligatoria.
- Rechazar una sugerencia requiere confirmación obligatoria.
- Si se rechaza con nota, la nota queda visible para quien sugirió y para Owner/Co-admins en el historial de sugerencias.

### CU-08: Asignar co-admin
- El Owner puede elevar a co-admin a cualquier Participante del evento.
- El co-admin puede aprobar/rechazar solicitudes de entrada y sugerencias; como cualquier participante, también puede asignarse ítems.
- El Owner puede revocar el rol en cualquier momento; el usuario queda como Participante regular.
- Asignar Co-admin no requiere confirmación obligatoria.
- Revocar Co-admin requiere confirmación obligatoria del Owner.
- Al revocar el rol, el usuario pierde permisos administrativos desde ese momento y conserva sus asignaciones existentes.

### CU-08b: Remover participante
- El Owner puede remover Participantes o Co-admins del evento.
- Remover un participante requiere confirmación obligatoria del Owner.
- Si el usuario a remover tiene asignaciones no compradas, debe cancelarlas antes de removerlo.
- Si el usuario a remover tiene asignaciones compradas, no puede ser removido en el MVP.
- El Owner no puede removerse a sí mismo.
- Si el Owner remueve a un Co-admin, el rol de Co-admin se revoca automáticamente.
- Un usuario removido por el Owner puede volver a solicitar entrada usando el link o QR del evento.
- Si reingresa, vuelve siempre como Participante normal.

### CU-09: Marcar ítem como comprado
- Cada participante asignado a un ítem puede marcar **su parte** como `comprado` de forma independiente.
- Owner y Co-admin pueden marcar cualquier asignación como comprada, incluso si el evento está cerrado.
- Marcar una asignación como comprada requiere confirmación obligatoria, porque no puede desmarcarse en el MVP.
- En el MVP no se puede desmarcar una asignación comprada.
- Una asignación marcada como comprada no puede modificarse.
- Una asignación marcada como comprada no puede cancelarse.
- El sistema calcula el estado global del ítem automáticamente:
  - Si solo algunos asignados marcaron "comprado" → `parcialmente_comprado`.
  - Si todos los asignados marcaron "comprado" → `comprado`.
- En la lista se muestra quién ya compró su parte y quién no, con íconos de check individuales.
- Al marcar como comprado, el estado se refleja en la lista del evento. No hay notificaciones de evento en el MVP.

### CU-10: Ver resumen del evento
- Cualquier participante puede ver:
  - Barra de progreso general del evento (% cubierto).
  - Estado de cada ítem con nombre de quién lo trae.
  - Ítems sin asignar resaltados.

### CU-11: Cierre por fecha límite
- Si el Owner definió fecha de cierre, al llegar esa fecha el evento pasa a `cerrado` automáticamente.
- Un evento `cerrado` no acepta nuevas asignaciones ni nuevas solicitudes de entrada.
- La lista queda en modo "solo lectura" para nuevas asignaciones, pero los asignados pueden marcar como "comprado".

### CU-11b: Cerrar, reabrir o cancelar evento
- Editar datos del evento no requiere confirmación obligatoria.
- El Owner puede cerrar manualmente un evento activo para impedir nuevas asignaciones.
- Cerrar manualmente un evento requiere confirmación obligatoria del Owner.
- El Owner puede reabrir un evento `cerrado`; al reabrir, vuelve a `activo`.
- Reabrir un evento cerrado requiere confirmación obligatoria del Owner.
- El Owner puede cancelar un evento; un evento `cancelado` no acepta solicitudes, asignaciones ni reapertura.
- Cancelar un evento requiere confirmación obligatoria del Owner.
- Un evento `cancelado` no permite crear, modificar, cancelar ni marcar como compradas asignaciones.
- Los eventos cancelados permanecen visibles como historial y no se eliminan físicamente.

### CU-12: Ítem sin asignar al cierre
- Si hay ítems en `sin_asignar` o `parcialmente_cubierto` al llegar a la fecha de cierre, se resaltan en rojo en la vista del evento para todos los participantes.
- No hay notificación automática al Owner — el estado visual es suficiente.
- No hay reasignación automática en el MVP.

---

## 8. Correos y notificaciones

### 8.1 Incluido en MVP

En el MVP solo existen correos transaccionales de cuenta:

| Evento | Canal | Quién recibe |
|---|---|---|
| Verificación de cuenta | Email | Usuario registrado |
| Recuperación de contraseña | Email | Usuario que solicita recuperación |

### 8.2 Fuera del MVP

Las notificaciones de evento quedan fuera del MVP, tanto in-app como email o push.

Cuando se implementen post-MVP, el canal definido para notificaciones de evento será **email**.

Eventos candidatos para post-MVP:

| Evento candidato | Canal post-MVP | Posibles destinatarios |
|---|---|---|
| Nueva solicitud de entrada al evento | Email | Owner + Co-admins |
| Solicitud aceptada o rechazada | Email | Solicitante |
| Nueva sugerencia de ítem | Email | Owner + Co-admins |
| Sugerencia aprobada o rechazada | Email | Quien sugirió |
| Ítem marcado como "comprado" | Email | Participantes aceptados |
| Evento cerrado o cancelado | Email | Participantes aceptados |

> Decisión MVP: los cambios de solicitudes, sugerencias, asignaciones y compras se consultan desde el detalle del evento. No existe centro de notificaciones ni historial de notificaciones en esta fase.

---

## 9. Alcance estricto del MVP — qué NO se hace en esta fase

| Funcionalidad | Razón de exclusión |
|---|---|
| Autenticación con Google / redes sociales (OAuth) | Complejidad de implementación. Se agrega post-MVP. |
| Notificaciones de evento in-app, email o push | Fuera del MVP. Los correos transaccionales de cuenta sí están incluidos. |
| Chat o comentarios en el evento | Fuera del scope de logística. |
| Pago compartido / vaquita | Producto diferente. Roadmap futuro. |
| Múltiples listas por evento | El MVP asume una sola lista por evento. |
| Historial de convivios anteriores / estadísticas | Post-MVP. |
| Plantillas de listas (ej. "Kit asado básico") | Post-MVP, cuando haya suficientes eventos para inferir patrones. |
| Invitación por email/teléfono desde la app | MVP usa link compartible + QR. El envío de invitaciones desde la app es post-MVP. |
| Eventos públicos buscables | Todos los eventos son privados (solo por link/QR). Directorio público es post-MVP. |
| Modo offline / PWA | Post-MVP. |
| App móvil nativa | La web app debe ser responsive. App nativa es roadmap. |
| Foto o imagen por ítem | Post-MVP. |

---

## 10. Decisiones de diseño relevantes (registradas)

| Decisión | Opción elegida | Alternativas descartadas |
|---|---|---|
| Cierre de lista | El Owner define fecha límite explícita (opcional) | Cierre automático al cubrirse todo |
| Acceso al evento | Solo por link o QR (privado por defecto) | Eventos públicos buscables (post-MVP) |
| Registro obligatorio | Sí, todos deben tener cuenta para participar | Modo anónimo con nombre de pantalla (descartado) |
| Aprobación de entrada | Owner o co-admin acepta/rechaza solicitudes | Entrada automática al tener el link |
| Vista mientras espera aprobación | Ve la ficha del evento con mensaje "participación en proceso de aceptación", sin acceso a la lista | Solo pantalla de "solicitud enviada" sin contexto del evento |
| Ítems sin asignar | Solo resaltado visual en rojo, sin notificación | Notificación al Owner, reasignación automática |
| Quién edita la lista base | Solo Owner; co-admin no edita, solo gestiona solicitudes y sugerencias | Edición abierta a todos |
| Estados del ítem | 5 estados: Sin asignar / Parcialmente cubierto / Cubierto / Parcialmente comprado / Comprado | 2 estados (muy simple) o 3 (sin "parcialmente") |
| Autenticación | Email + contraseña, con verificación y recuperación | OAuth (post-MVP) |
| Invitado sin cuenta | No soportado: todos deben registrarse para participar | Modo anónimo con nombre de pantalla |

---

## 11. Métricas de éxito del MVP

- Al menos un evento creado con 5+ ítems y 3+ participantes que se asignan ítems.
- 0 ítems "dobles" reportados (dos personas comprando lo mismo sin coordinación).
- El Owner no necesita enviar mensajes manuales para coordinar la lista.

---

## 12. Próximos pasos (post este documento)

1. `MODULES_SPEC.md` — Mapa de módulos, funcionalidades y escenarios Gherkin.
2. `DATA_MODEL.md` — Esquema de base de datos (ERD), derivado de los módulos.
3. `API_SPEC.md` — Endpoints del backend.
4. `UI_FLOWS.md` — Wireframes / flujos de pantallas.
