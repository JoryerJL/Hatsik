# USER_STORIES.md — Hatsik

> **Versión:** 0.1 — Draft inicial
> **Fecha:** 2026-05-23
> **Estado:** En definición

---

## Convenciones

- **Formato:** `Como [rol], quiero [acción], para [beneficio].`
- **Roles posibles:** Usuario (sin contexto de evento), Owner, Co-admin, Participante.
- **Criterios de aceptación:** condiciones mínimas para considerar la historia completa.
- **Prioridad MVP:** 🔴 Crítico · 🟡 Importante · 🟢 Deseable

---

## Bloque 1 — Registro y cuenta

---

### US-01 · Registro de cuenta
**Como** usuario nuevo,
**quiero** registrarme con nombre de pantalla, email y contraseña,
**para** tener una cuenta en Hatsik y poder crear o unirme a eventos.

**Criterios de aceptación:**
- El formulario solicita: nombre de pantalla, email y contraseña.
- El email debe tener formato válido.
- La contraseña debe tener mínimo 8 caracteres, al menos 1 letra y al menos 1 número.
- Al registrarse, se envía un correo de verificación.
- El usuario no puede usar funcionalmente la app hasta verificar su email.
- Si inicia sesión sin verificar, ve una pantalla de verificación pendiente.
- Desde la pantalla de verificación pendiente puede reenviar el correo de verificación.
- El reenvío de correo de verificación está limitado a 1 solicitud cada 60 segundos por usuario.
- Si el email ya existe, se muestra un mensaje de error.

**Prioridad:** 🔴 Crítico

---

### US-02 · Verificación de email
**Como** usuario recién registrado,
**quiero** verificar mi email desde el correo que me llegó,
**para** activar mi cuenta y poder usar Hatsik.

**Criterios de aceptación:**
- El correo de verificación contiene un link con token único.
- El token de verificación expira en 24 horas.
- Al hacer clic en el link, la cuenta queda activa.
- Si el token expiró, el usuario puede solicitar reenviar el correo.
- Una cuenta no verificada puede iniciar sesión, pero solo accede a la pantalla de verificación pendiente.
- Desde la pantalla de verificación pendiente, el usuario puede reenviar el correo de verificación.
- El reenvío de correo de verificación está limitado a 1 solicitud cada 60 segundos por usuario.

**Prioridad:** 🔴 Crítico

---

### US-03 · Inicio de sesión
**Como** usuario registrado y verificado,
**quiero** iniciar sesión con mi email y contraseña,
**para** acceder a mi cuenta y mis eventos.

**Criterios de aceptación:**
- El formulario solicita email y contraseña.
- Si las credenciales son incorrectas, se muestra un mensaje de error genérico (no especificar cuál campo falló).
- Al iniciar sesión correctamente, el usuario ve su pantalla principal.

**Prioridad:** 🔴 Crítico

---

### US-04 · Recuperación de contraseña
**Como** usuario que olvidó su contraseña,
**quiero** recibir un link para restablecerla,
**para** recuperar el acceso a mi cuenta.

**Criterios de aceptación:**
- El usuario ingresa su email y solicita el link de recuperación.
- Si el email existe, se envía el link. Si no existe, se muestra mensaje genérico (no confirmar si el email está registrado).
- El link de recuperación expira en 1 hora.
- La solicitud de recuperación está limitada a 1 solicitud cada 60 segundos por email.
- Al usar el link, el usuario puede establecer una nueva contraseña.

**Prioridad:** 🔴 Crítico

---

### US-05 · Cerrar sesión
**Como** usuario autenticado,
**quiero** cerrar sesión,
**para** salir de mi cuenta de forma segura.

**Criterios de aceptación:**
- Existe una opción visible para cerrar sesión.
- Al cerrar sesión, la sesión se invalida y se redirige al login.

**Prioridad:** 🔴 Crítico

---

## Bloque 2 — Crear y gestionar eventos

---

### US-06 · Crear un evento
**Como** usuario registrado,
**quiero** crear un evento,
**para** organizar un convivio y compartir la lista de lo que se necesita.

**Criterios de aceptación:**
- El formulario solicita obligatoriamente: nombre del evento y fecha del evento.
- Los campos opcionales son: descripción y fecha límite de asignaciones.
- Al crear el evento, se genera automáticamente un link compartible y un código QR descargable (PNG).
- Crear un evento no requiere confirmación obligatoria adicional al envío del formulario.
- El usuario queda automáticamente como Owner del evento con estado de acceso `aceptado`.
- El evento aparece en la pantalla principal del Owner.

**Prioridad:** 🔴 Crítico

---

### US-07 · Editar un evento
**Como** Owner de un evento,
**quiero** editar los datos del evento después de crearlo,
**para** corregir o actualizar la información.

**Criterios de aceptación:**
- El Owner puede editar: nombre, descripción, fecha del evento y fecha límite de asignaciones.
- Editar datos del evento no requiere confirmación obligatoria.
- El link compartible y el QR no cambian al editar.
- Los cambios se reflejan de inmediato para todos los participantes.
- No se puede editar un evento cancelado.

**Prioridad:** 🔴 Crítico

---

### US-08 · Cancelar un evento
**Como** Owner de un evento,
**quiero** cancelar el evento,
**para** informar a todos los participantes que ya no se llevará a cabo.

**Criterios de aceptación:**
- El Owner puede cancelar el evento en cualquier momento.
- Cancelar un evento requiere confirmación obligatoria del Owner.
- Al cancelar, el estado del evento cambia a `cancelado`.
- Todos los participantes ven el evento marcado como cancelado.
- Un evento cancelado no puede recibir nuevas asignaciones ni solicitudes de entrada.
- Un evento cancelado no permite crear, modificar, cancelar ni marcar como compradas asignaciones.
- El evento permanece en la base de datos (no se elimina).
- El Owner puede ver sus eventos cancelados en su historial.

**Prioridad:** 🔴 Crítico

---

### US-09 · Compartir el link y QR del evento
**Como** Owner de un evento,
**quiero** compartir el link y descargar el QR del evento,
**para** que mis invitados puedan encontrar el evento y solicitar unirse.

**Criterios de aceptación:**
- El link es único por evento y no cambia.
- El QR es descargable como imagen PNG.
- Ambos están disponibles desde la vista del evento.

**Prioridad:** 🔴 Crítico

---

### US-10 · Cerrar un evento manualmente
**Como** Owner de un evento,
**quiero** cerrar el evento manualmente,
**para** indicar que ya no se aceptan nuevas asignaciones.

**Criterios de aceptación:**
- El Owner puede cerrar el evento en cualquier momento mientras esté activo.
- Cerrar manualmente un evento requiere confirmación obligatoria del Owner.
- Al cerrar, el estado cambia a `cerrado` y ya no se aceptan nuevas asignaciones.
- Los participantes ya asignados pueden seguir marcando sus ítems como comprado.
- El Owner puede reabrir el evento si lo desea.

**Prioridad:** 🔴 Crítico

---

### US-11 · Cierre automático por fecha límite
**Como** sistema,
**quiero** cerrar automáticamente las asignaciones al llegar la fecha límite definida por el Owner,
**para** que la lista se congele sin que el Owner tenga que hacerlo manualmente.

**Criterios de aceptación:**
- Si el evento tiene fecha límite de asignaciones, al llegar esa fecha el evento pasa a `cerrado` automáticamente.
- Los participantes ya asignados siguen pudiendo marcar como comprado.
- No se aceptan nuevas asignaciones ni solicitudes de entrada tras el cierre.

**Prioridad:** 🔴 Crítico

---

### US-12 · Reabrir un evento cerrado
**Como** Owner de un evento cerrado,
**quiero** reabrirlo,
**para** permitir nuevas asignaciones si el convivio sigue en pie.

**Criterios de aceptación:**
- El Owner puede reabrir un evento con estado `cerrado`.
- Reabrir un evento cerrado requiere confirmación obligatoria del Owner.
- Al reabrir, el estado vuelve a `activo` y se pueden hacer nuevas asignaciones.
- No se puede reabrir un evento `cancelado`.

**Prioridad:** 🟡 Importante

---

## Bloque 3 — Unirse a un evento

---

### US-13 · Solicitar unirse a un evento
**Como** usuario registrado,
**quiero** solicitar unirme a un evento desde su link o QR,
**para** participar en la lista del convivio.

**Criterios de aceptación:**
- Al abrir el link o escanear el QR, el usuario ve la ficha del evento (nombre, descripción, fecha).
- Si no tiene cuenta, el sistema lo lleva al registro y al terminar lo redirige de vuelta al evento.
- El usuario envía una solicitud de entrada.
- Solicitar entrada a un evento no requiere confirmación obligatoria adicional.
- Su estado queda en `pendiente`.
- Mientras espera, ve la ficha del evento con un mensaje indicando que su participación está en proceso de aceptación.
- No puede ver la lista ni interactuar con ella hasta ser aceptado.
- No se puede solicitar unirse a un evento `cerrado` o `cancelado`.
- Si su solicitud fue rechazada, no puede volver a solicitar acceso al mismo evento.

**Prioridad:** 🔴 Crítico

---

### US-14 · Gestionar solicitudes de entrada
**Como** Owner o co-admin de un evento,
**quiero** ver y gestionar las solicitudes de entrada pendientes,
**para** decidir quién puede participar en el evento.

**Criterios de aceptación:**
- El Owner y los co-admins ven una sección de "Solicitudes pendientes" en el evento.
- Cada solicitud muestra el nombre de pantalla y email del solicitante.
- Pueden aceptar o rechazar cada solicitud.
- Al aceptar, el usuario pasa a `participante` con estado `aceptado` y puede acceder a la lista.
- Al rechazar, el usuario ve en la ficha del evento que su solicitud fue rechazada.
- Aprobar una solicitud no requiere confirmación obligatoria.
- Rechazar una solicitud requiere confirmación obligatoria y no incluye motivo en el MVP.
- Si una solicitud fue rechazada por error, Owner o Co-admin pueden cambiarla a `aceptado`.
- No se envían notificaciones de evento en el MVP; el estado se consulta desde la ficha o detalle del evento.
- Si hay solicitudes pendientes, se muestra un badge con el conteo.

**Prioridad:** 🔴 Crítico

---

### US-15 · Ver mis eventos
**Como** usuario registrado,
**quiero** ver todos los eventos en los que participo,
**para** acceder rápidamente a cualquiera de ellos.

**Criterios de aceptación:**
- La pantalla principal muestra todos los eventos del usuario: los que creó y los que participa.
- Se distingue visualmente si el usuario es Owner, co-admin o participante en cada evento.
- Se muestran eventos activos, cerrados y cancelados (con su estado visible).

**Prioridad:** 🔴 Crítico

---

### US-15b · Salirse de un evento
**Como** Participante de un evento,
**quiero** salirme voluntariamente,
**para** dejar de participar si ya no formaré parte del convivio.

**Criterios de aceptación:**
- El Participante puede salirse si no tiene asignaciones activas.
- Salirse voluntariamente de un evento requiere confirmación obligatoria del participante.
- Si tiene asignaciones no compradas, debe cancelarlas antes de salirse.
- Si tiene asignaciones compradas, no puede salirse del evento en el MVP.
- Si es Co-admin, al salirse su rol se revoca automáticamente.
- El Owner no puede salirse de su propio evento.
- Al salirse, el evento deja de aparecer en su dashboard.
- El usuario puede volver a solicitar entrada usando el link o QR del evento.
- Si antes fue rechazado, luego aceptado por Owner/Co-admin y después se salió voluntariamente, también puede volver a solicitar entrada.
- Si reingresa, vuelve siempre como Participante normal; no recupera automáticamente el rol de Co-admin.

**Prioridad:** 🟡 Importante

---

## Bloque 4 — Lista de ítems

---

### US-16 · Agregar un ítem a la lista
**Como** Owner de un evento,
**quiero** agregar ítems a la lista,
**para** definir qué se necesita para el convivio.

**Criterios de aceptación:**
- El campo obligatorio es el nombre del ítem.
- La cantidad es opcional. Si el Owner define una cantidad, también debe seleccionar la unidad correspondiente desde un catálogo controlado.
- El catálogo inicial de unidades incluye: `kg`, `g`, `litros`, `ml`, `piezas`, `paquetes`, `bolsas`, `cajas`, `latas`, `botellas`, `garrafones`, `charolas`, `docenas`.
- Si no se define cantidad, el ítem se trata como "sin cantidad definida" (solo se puede marcar como llevado o no).
- Agregar un ítem no requiere confirmación obligatoria adicional al envío del formulario.
- No hay límite de ítems por evento.
- El ítem aparece de inmediato en la lista para todos los participantes aceptados.

**Prioridad:** 🔴 Crítico

---

### US-17 · Editar un ítem de la lista
**Como** Owner de un evento,
**quiero** editar un ítem de la lista,
**para** corregir el nombre, cantidad o unidad.

**Criterios de aceptación:**
- El Owner puede editar cualquier ítem mientras el evento esté activo (no cerrado ni cancelado).
- Si el ítem no tiene asignaciones, el Owner puede editar nombre, cantidad y unidad.
- Editar un ítem sin asignaciones no requiere confirmación obligatoria.
- Si el ítem ya tiene asignaciones, el Owner solo puede editar la cantidad total.
- Si el ítem ya tiene asignaciones, no puede reducir la cantidad total por debajo de la suma ya asignada.
- Si el ítem ya tiene asignaciones, se muestra una advertencia antes de guardar cambios de cantidad.
- Guardar cambios de cantidad en un ítem con asignaciones requiere confirmación obligatoria del Owner.
- Los cambios se reflejan de inmediato para todos.

**Prioridad:** 🔴 Crítico

---

### US-18 · Eliminar un ítem de la lista
**Como** Owner de un evento,
**quiero** eliminar un ítem de la lista,
**para** quitarlo si ya no se necesita.

**Criterios de aceptación:**
- El Owner puede eliminar un ítem mientras el evento esté activo.
- Eliminar cualquier ítem requiere confirmación obligatoria del Owner.
- Si el ítem tiene asignaciones activas, se muestra una advertencia antes de confirmar.
- Al eliminar, las asignaciones asociadas también se eliminan.
- No se puede eliminar ítems en un evento cerrado o cancelado.

**Prioridad:** 🔴 Crítico

---

## Bloque 5 — Asignaciones

---

### US-19 · Asignarse un ítem
**Como** participante de un evento,
**quiero** asignarme un ítem de la lista indicando cuánto puedo llevar,
**para** que todos sepan qué voy a traer yo.

**Criterios de aceptación:**
- El participante puede asignarse cualquier ítem que no esté completamente cubierto.
- Si el ítem tiene cantidad definida, el participante ingresa cuánto puede llevar.
- El sistema valida que la suma de asignaciones no supere la cantidad total del ítem.
- Si el ítem no tiene cantidad definida, el participante solo confirma que lo lleva.
- Crear una asignación no requiere confirmación obligatoria.
- El estado del ítem se actualiza automáticamente al asignarse.
- El Owner también puede asignarse ítems de su propio evento.

**Prioridad:** 🔴 Crítico

---

### US-20 · Modificar una asignación
**Como** participante asignado a un ítem,
**quiero** modificar la cantidad que me asigné,
**para** ajustar lo que puedo llevar.

**Criterios de aceptación:**
- El participante puede cambiar la cantidad mientras el evento esté activo.
- Una asignación marcada como comprada no puede modificarse.
- Modificar una asignación propia no comprada no requiere confirmación obligatoria.
- El sistema valida que la nueva cantidad no supere lo disponible (total − otras asignaciones).
- El estado del ítem se recalcula automáticamente.

**Prioridad:** 🔴 Crítico

---

### US-21 · Cancelar una asignación
**Como** participante asignado a un ítem,
**quiero** cancelar mi asignación,
**para** liberar mi parte si ya no puedo llevarlo.

**Criterios de aceptación:**
- El participante puede cancelar su asignación mientras el evento esté activo (no cerrado ni cancelado).
- Cancelar una asignación propia requiere confirmación obligatoria del participante.
- Una asignación marcada como comprada no puede cancelarse.
- Al cancelar, la cantidad queda disponible para que otro la tome.
- El estado del ítem se recalcula automáticamente.

**Prioridad:** 🔴 Crítico

---

### US-21b · Cancelar asignación ajena
**Como** Owner de un evento,
**quiero** cancelar asignaciones no compradas de otros participantes,
**para** liberar compromisos cuando necesito gestionar la lista o remover participantes.

**Criterios de aceptación:**
- El Owner puede cancelar asignaciones no compradas de cualquier participante.
- El Owner no puede modificar la cantidad de asignaciones de otros participantes; solo puede cancelarlas si no están compradas.
- Cancelar una asignación ajena requiere confirmación obligatoria del Owner.
- El Co-admin no puede cancelar asignaciones de otros participantes.
- Una asignación marcada como comprada no puede cancelarse.
- Al cancelar, la cantidad queda disponible para que otro la tome.
- El estado del ítem se recalcula automáticamente.

**Prioridad:** 🔴 Crítico

---

### US-22 · Marcar ítem como comprado
**Como** participante asignado a un ítem, o como Owner/co-admin,
**quiero** marcar una asignación como comprada según mis permisos,
**para** que todos sepan qué partes ya fueron compradas.

**Criterios de aceptación:**
- Cada asignado puede marcar su propia parte como `comprado` de forma independiente.
- El Owner y co-admins pueden marcar como comprado cualquier asignación, incluso si el evento está cerrado.
- Marcar una asignación como comprada requiere confirmación obligatoria, porque no puede desmarcarse en el MVP.
- En el MVP no se puede desmarcar una asignación comprada.
- El estado global del ítem se recalcula automáticamente:
  - Algunos asignados marcaron comprado → `parcialmente_comprado`.
  - Todos los asignados marcaron comprado → `comprado`.
- En la lista se muestra quién ya compró y quién no, con indicador individual.

**Prioridad:** 🔴 Crítico

---

## Bloque 6 — Sugerencias

---

### US-23 · Sugerir un ítem
**Como** participante de un evento,
**quiero** sugerir un ítem nuevo para la lista,
**para** proponer algo que creo que hace falta.

**Criterios de aceptación:**
- El participante puede sugerir un ítem con nombre obligatorio y cantidad opcional. Si define una cantidad, también debe seleccionar la unidad correspondiente desde un catálogo controlado.
- Crear una sugerencia no requiere confirmación obligatoria adicional al envío del formulario.
- La sugerencia queda en estado `pendiente_aprobacion` y no aparece en la lista activa.
- El Owner y co-admins pueden ver las sugerencias pendientes.
- El participante puede ver el estado de su sugerencia (pendiente, aprobada, rechazada).

**Prioridad:** 🔴 Crítico

---

### US-24 · Editar una sugerencia pendiente
**Como** participante que hizo una sugerencia,
**quiero** editarla antes de que sea revisada,
**para** corregir algo que puse mal.

**Criterios de aceptación:**
- El participante puede editar su sugerencia solo si está en estado `pendiente_aprobacion`.
- Editar una sugerencia pendiente propia no requiere confirmación obligatoria.
- Una vez que fue aprobada o rechazada, no puede editarse.

**Prioridad:** 🟡 Importante

---

### US-24b · Eliminar una sugerencia pendiente
**Como** participante que hizo una sugerencia,
**quiero** eliminarla antes de que sea revisada,
**para** retirar una propuesta que ya no considero necesaria.

**Criterios de aceptación:**
- El participante puede eliminar su sugerencia solo si está en estado `pendiente_aprobacion`.
- Eliminar una sugerencia pendiente propia requiere confirmación obligatoria.
- Una vez que fue aprobada o rechazada, no puede eliminarse.
- Al eliminarse, deja de aparecer para revisión de Owner y Co-admins.

**Prioridad:** 🟡 Importante

---

### US-25 · Aprobar o rechazar una sugerencia
**Como** Owner o co-admin de un evento,
**quiero** aprobar o rechazar las sugerencias de los participantes,
**para** controlar qué entra a la lista oficial.

**Criterios de aceptación:**
- El Owner y co-admins ven todas las sugerencias pendientes en una sección dedicada.
- Pueden aprobar (el ítem entra a la lista activa) o rechazar (con nota opcional).
- Antes de aprobar, pueden modificar nombre, cantidad y unidad de la sugerencia.
- Aprobar una sugerencia no requiere confirmación obligatoria.
- Rechazar una sugerencia requiere confirmación obligatoria.
- Al aprobar, el ítem aparece en la lista con estado `sin_asignar`.
- El ítem aprobado no muestra "sugerido por" en la lista oficial.
- Al rechazar, el participante ve la sugerencia marcada como rechazada con la nota.
- La sugerencia rechazada no aparece en la lista activa pero sí en el historial del participante.
- Si se rechaza con nota, la nota también queda visible para Owner y Co-admins en el historial de sugerencias.
- No se envían notificaciones de evento en el MVP; el estado de la sugerencia se consulta dentro del evento.

**Prioridad:** 🔴 Crítico

---

## Bloque 7 — Roles dentro del evento

---

### US-26 · Asignar co-admin
**Como** Owner de un evento,
**quiero** asignar el rol de co-admin a uno o más participantes,
**para** que me ayuden a gestionar solicitudes y sugerencias.

**Criterios de aceptación:**
- El Owner puede asignar co-admin a cualquier participante con estado `aceptado`.
- Puede haber múltiples co-admins en un mismo evento.
- El co-admin puede aprobar/rechazar sugerencias y gestionar solicitudes de entrada.
- El co-admin puede asignarse ítems como cualquier participante.
- El co-admin no puede editar la lista base ni nombrar otros co-admins.

**Prioridad:** 🔴 Crítico

---

### US-27 · Revocar rol de co-admin
**Como** Owner de un evento,
**quiero** revocar el rol de co-admin de un participante,
**para** ajustar los permisos del evento.

**Criterios de aceptación:**
- El Owner puede revocar el rol de co-admin en cualquier momento.
- Revocar Co-admin requiere confirmación obligatoria del Owner.
- Al revocar, el usuario queda como participante regular con sus asignaciones intactas.
- El usuario pierde permisos administrativos desde ese momento.

**Prioridad:** 🟡 Importante

---

### US-28 · Remover participante del evento
**Como** Owner de un evento,
**quiero** remover a un participante,
**para** quitar del evento a alguien que ya no debe participar.

**Criterios de aceptación:**
- El Owner puede remover Participantes o Co-admins.
- Remover un participante requiere confirmación obligatoria del Owner.
- Si el usuario a remover tiene asignaciones no compradas, debe cancelarlas antes de removerlo.
- Si el usuario a remover tiene asignaciones compradas, no puede ser removido en el MVP.
- El Owner no puede removerse a sí mismo.
- Si el usuario removido era Co-admin, su rol se revoca automáticamente.
- Al removerse, el evento deja de aparecer en el dashboard del usuario removido.
- El usuario removido puede volver a solicitar entrada usando el link o QR del evento.
- Si reingresa, vuelve siempre como Participante normal.

**Prioridad:** 🟡 Importante

---

## Bloque 8 — Correos y notificaciones

---

### Decisión MVP · Correos transaccionales y notificaciones de evento

**Incluido en MVP:**
- Correo de verificación de cuenta.
- Correo de recuperación de contraseña.

**Fuera del MVP:**
- Notificaciones in-app de evento.
- Notificaciones por email de evento.
- Push notifications.
- Centro o historial de notificaciones.

**Decisión post-MVP:**
- Cuando se implementen notificaciones de evento, el canal definido será email.

**Criterio funcional:**
- Los estados de solicitudes, sugerencias, asignaciones y compras se consultan desde el detalle del evento.
- Los eventos candidatos a email de evento se definirán en una fase post-MVP.

---

## Resumen de historias

| ID | Historia | Rol | Prioridad |
|---|---|---|---|
| US-01 | Registro de cuenta | Usuario | 🔴 |
| US-02 | Verificación de email | Usuario | 🔴 |
| US-03 | Inicio de sesión | Usuario | 🔴 |
| US-04 | Recuperación de contraseña | Usuario | 🔴 |
| US-05 | Cerrar sesión | Usuario | 🔴 |
| US-06 | Crear un evento | Usuario | 🔴 |
| US-07 | Editar un evento | Owner | 🔴 |
| US-08 | Cancelar un evento | Owner | 🔴 |
| US-09 | Compartir link y QR | Owner | 🔴 |
| US-10 | Cerrar evento manualmente | Owner | 🔴 |
| US-11 | Cierre automático por fecha | Sistema | 🔴 |
| US-12 | Reabrir evento cerrado | Owner | 🟡 |
| US-13 | Solicitar unirse al evento | Usuario | 🔴 |
| US-14 | Gestionar solicitudes de entrada | Owner/Co-admin | 🔴 |
| US-15 | Ver mis eventos | Usuario | 🔴 |
| US-15b | Salirse de un evento | Participante | 🟡 |
| US-16 | Agregar ítem a la lista | Owner | 🔴 |
| US-17 | Editar ítem de la lista | Owner | 🔴 |
| US-18 | Eliminar ítem de la lista | Owner | 🔴 |
| US-19 | Asignarse un ítem | Participante/Owner | 🔴 |
| US-20 | Modificar una asignación | Participante | 🔴 |
| US-21 | Cancelar una asignación | Participante | 🔴 |
| US-21b | Cancelar asignación ajena | Owner | 🔴 |
| US-22 | Marcar ítem como comprado | Participante/Owner/Co-admin | 🔴 |
| US-23 | Sugerir un ítem | Participante | 🔴 |
| US-24 | Editar sugerencia pendiente | Participante | 🟡 |
| US-24b | Eliminar sugerencia pendiente | Participante | 🟡 |
| US-25 | Aprobar o rechazar sugerencia | Owner/Co-admin | 🔴 |
| US-26 | Asignar co-admin | Owner | 🔴 |
| US-27 | Revocar co-admin | Owner | 🟡 |
| US-28 | Remover participante del evento | Owner | 🟡 |
