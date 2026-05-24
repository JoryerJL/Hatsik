# MODULES_SPEC.md — Hatsik

> **Versión:** 0.1 — Draft inicial  
> **Fecha:** 2026-05-23  
> **Estado:** En definición  
> **Fuente:** Derivado de `PRODUCT_OVERVIEW.md` y `USER_STORIES.md`

---

## 1. Propósito

Este documento define los módulos funcionales de Hatsik antes de diseñar la base de datos.

La intención es mapear **qué hace el sistema**, qué reglas tiene cada área y qué casos de uso deben existir. El modelo de datos vendrá después, derivado de estos procesos.

> Regla guía: la funcionalidad dicta los datos, no al revés.

---

## 2. Criterios de modularidad

Los módulos se organizan por **responsabilidad de negocio**, no necesariamente por pantallas.

Un módulo lógico puede vivir visualmente dentro de otro flujo del frontend.

| Módulo lógico | Responsabilidad | Ubicación visual prevista |
|---|---|---|
| `Auth` | Cuenta, acceso y correos transaccionales | Pantallas de auth |
| `Dashboard` | Vista principal de eventos del usuario | Pantalla principal |
| `Events` | Ciclo de vida del evento y roles internos | Listado y detalle del evento |
| `EventAccess` | Solicitudes de entrada y control de acceso | Detalle del evento |
| `Items` | Lista oficial de ítems del evento | Detalle del evento |
| `Assignments` | Asignación, modificación, cancelación y compra de ítems | Detalle del evento |
| `Moderation` | Sugerencias de ítems y revisión | Detalle del evento |
| `Notifications` | Notificaciones de evento futuras por email | Fuera del MVP |

---

## 3. Alcance MVP por módulo

| Módulo | Entra en MVP | Notas |
|---|---:|---|
| `Auth` | Sí | Incluye verificación de email y recuperación de contraseña. |
| `Dashboard` | Sí | Muestra eventos creados y eventos donde participa el usuario. |
| `Events` | Sí | Crear, editar, cerrar, reabrir, cancelar y gestionar co-admins. |
| `EventAccess` | Sí | Solicitudes de entrada, aprobación/rechazo y permisos de acceso. |
| `Items` | Sí | Gestión de la lista base por Owner. |
| `Assignments` | Sí | Participantes se asignan ítems y marcan su parte como comprada. |
| `Moderation` | Sí | Sugerencias de ítems gestionadas desde el detalle del evento. |
| `Notifications` | No | Las notificaciones de evento quedan post-MVP y serán por email. |

### Decisión sobre notificaciones

En el MVP solo existen **correos transaccionales de cuenta**:

- Verificación de email.
- Recuperación de contraseña.

Quedan fuera del MVP:

- Notificaciones in-app de evento.
- Notificaciones por email de evento.
- Push notifications.
- Centro o historial de notificaciones.

Los cambios de solicitudes, sugerencias, asignaciones y compras se reflejan en las vistas correspondientes cuando el usuario entra al evento.

---

# 4. Módulos funcionales

---

## 4.1 `Auth`

### Responsabilidad

Gestiona la identidad del usuario y el acceso a la aplicación.

### Funcionalidades

- Registrar usuario con nombre de pantalla, email y contraseña.
- Enviar correo de verificación.
- Validar cuenta verificada antes de permitir uso funcional de la app.
- Permitir que una cuenta no verificada inicie sesión solo para ver la pantalla de verificación pendiente.
- Reenviar correo de verificación desde la pantalla de verificación pendiente.
- Iniciar sesión.
- Cerrar sesión.
- Solicitar recuperación de contraseña.
- Enviar correo de recuperación.
- Permitir cambio de contraseña desde link válido.

### Reglas de negocio

- No existe acceso anónimo en el MVP.
- Todo usuario debe tener cuenta para crear o unirse a eventos.
- Una cuenta no verificada puede iniciar sesión, pero solo ve una pantalla para verificar su correo.
- Una cuenta no verificada no puede crear eventos, solicitar entrada ni interactuar con eventos.
- El usuario puede reenviar el correo de verificación si no recibió o perdió el correo anterior.
- El reenvío de correo de verificación está limitado a 1 solicitud cada 60 segundos por usuario.
- La contraseña debe tener mínimo 8 caracteres, al menos 1 letra y al menos 1 número.
- El token de verificación de email expira en 24 horas.
- El token de recuperación de contraseña expira en 1 hora.
- La solicitud de recuperación de contraseña está limitada a 1 solicitud cada 60 segundos por email.
- Los errores de login y recuperación no deben revelar si un email existe.
- OAuth queda fuera del MVP.

### Historias relacionadas

- US-01 Registro de cuenta.
- US-02 Verificación de email.
- US-03 Inicio de sesión.
- US-04 Recuperación de contraseña.
- US-05 Cerrar sesión.

### Escenarios Gherkin

```gherkin
Feature: Registro de cuenta

Scenario: Usuario crea una cuenta nueva
  Given que el visitante no tiene cuenta
  When completa nombre de pantalla, email válido y contraseña válida
  Then el sistema crea la cuenta en estado no verificado
  And envía un correo de verificación
  And bloquea el uso de la app hasta verificar el email
```

```gherkin
Feature: Cuenta no verificada

Scenario: Usuario no verificado inicia sesión
  Given que el usuario tiene una cuenta no verificada
  When inicia sesión con credenciales válidas
  Then el sistema muestra una pantalla de verificación pendiente
  And no permite crear eventos
  And no permite solicitar entrada a eventos
  And ofrece la opción de reenviar el correo de verificación
```

```gherkin
Feature: Reenvío de correo de verificación

Scenario: Usuario solicita reenviar correo de verificación
  Given que el usuario tiene una cuenta no verificada
  And no solicitó un reenvío en los últimos 60 segundos
  When solicita reenviar el correo de verificación
  Then el sistema envía un nuevo correo de verificación
  And bloquea nuevos reenvíos durante 60 segundos
```

```gherkin
Feature: Verificación de email

Scenario: Usuario verifica su cuenta con un token válido
  Given que el usuario tiene una cuenta no verificada
  And recibió un link de verificación vigente
  When abre el link de verificación
  Then el sistema marca la cuenta como verificada
  And permite iniciar sesión en Hatsik
```

```gherkin
Feature: Recuperación de contraseña

Scenario: Usuario solicita recuperar su contraseña
  Given que el usuario olvidó su contraseña
  When ingresa su email en el formulario de recuperación
  Then el sistema muestra una respuesta genérica
  And si el email existe, envía un correo con link de recuperación
```

```gherkin
Feature: Rate limit de recuperación de contraseña

Scenario: Usuario solicita recuperación más de una vez en menos de 60 segundos
  Given que un email ya solicitó recuperación de contraseña en los últimos 60 segundos
  When se solicita nuevamente la recuperación para ese email
  Then el sistema no envía un nuevo correo
  And muestra una respuesta genérica sin revelar si el email existe
```

---

## 4.2 `Dashboard`

### Responsabilidad

Muestra al usuario sus eventos y accesos principales.

### Funcionalidades

- Ver eventos creados por el usuario.
- Ver eventos donde participa.
- Distinguir visualmente el rol del usuario en cada evento.
- Mostrar estado del evento: activo, cerrado o cancelado.
- Acceder al detalle del evento.

### Reglas de negocio

- Un usuario puede ser Owner, Co-admin o Participante según el evento.
- El rol no es global; siempre depende del contexto del evento.
- Los eventos cancelados permanecen visibles como historial.

### Historias relacionadas

- US-15 Ver mis eventos.

### Escenarios Gherkin

```gherkin
Feature: Dashboard de eventos

Scenario: Usuario ve sus eventos
  Given que el usuario inició sesión
  And participa en uno o más eventos
  When entra a la pantalla principal
  Then ve los eventos que creó
  And ve los eventos donde participa
  And cada evento muestra su rol y estado actual
```

---

## 4.3 `Events`

### Responsabilidad

Gestiona el ciclo de vida del evento y los roles internos del evento.

### Funcionalidades

- Crear evento.
- Editar evento.
- Generar link compartible.
- Generar QR descargable.
- Cerrar evento manualmente.
- Cerrar evento automáticamente por fecha límite.
- Reabrir evento cerrado.
- Cancelar evento.
- Asignar co-admin.
- Revocar co-admin.
- Remover participantes del evento.

### Reglas de negocio

- El creador del evento queda automáticamente como Owner.
- El Owner también puede participar y asignarse ítems.
- Solo el Owner puede editar datos del evento.
- Crear un evento no requiere confirmación obligatoria adicional al envío del formulario.
- Editar datos del evento no requiere confirmación obligatoria.
- Solo el Owner puede cerrar, reabrir o cancelar el evento.
- Cerrar manualmente un evento requiere confirmación obligatoria del Owner.
- Reabrir un evento cerrado requiere confirmación obligatoria del Owner.
- Solo el Owner puede asignar o revocar co-admins.
- Asignar Co-admin no requiere confirmación obligatoria.
- Revocar Co-admin requiere confirmación obligatoria del Owner.
- Un co-admin no puede editar el evento, editar la lista base ni nombrar otros co-admins.
- Al revocar un co-admin, el usuario pierde permisos administrativos desde ese momento y queda como Participante regular.
- Revocar un co-admin no afecta sus asignaciones existentes.
- El Owner puede remover Participantes o Co-admins del evento.
- Remover un participante requiere confirmación obligatoria del Owner.
- Si el usuario a remover tiene asignaciones no compradas, debe cancelarlas antes de removerlo.
- Si el usuario a remover tiene asignaciones compradas, no puede ser removido en el MVP.
- El Owner no puede removerse a sí mismo.
- Si el Owner remueve a un Co-admin, el rol de Co-admin se revoca automáticamente.
- Un usuario removido por el Owner puede volver a solicitar entrada usando el link o QR del evento.
- Si un usuario removido reingresa, vuelve siempre como Participante normal.
- Un evento cancelado no puede reabrirse.
- Cancelar un evento requiere confirmación obligatoria del Owner.
- Un evento cerrado no acepta nuevas solicitudes ni nuevas asignaciones, pero los asignados pueden marcar como comprado.

### Historias relacionadas

- US-06 Crear un evento.
- US-07 Editar un evento.
- US-08 Cancelar un evento.
- US-09 Compartir link y QR del evento.
- US-10 Cerrar un evento manualmente.
- US-11 Cierre automático por fecha límite.
- US-12 Reabrir un evento cerrado.
- US-26 Asignar co-admin.
- US-27 Revocar rol de co-admin.

### Escenarios Gherkin

```gherkin
Feature: Crear evento

Scenario: Usuario crea un evento válido
  Given que el usuario tiene una cuenta verificada
  When crea un evento con nombre y fecha del convivio
  Then el sistema crea el evento en estado activo
  And genera un link compartible único
  And genera un QR descargable
  And registra al usuario como Owner aceptado del evento
```

```gherkin
Feature: Cerrar evento

Scenario: Owner cierra un evento activo
  Given que el evento está activo
  And el usuario es Owner del evento
  When cierra manualmente el evento
  Then el sistema pide confirmación obligatoria
  And si el Owner confirma, cambia el estado del evento a cerrado
  And bloquea nuevas solicitudes de entrada
  And bloquea nuevas asignaciones
  And permite que asignados existentes marquen su parte como comprada
```

```gherkin
Feature: Reabrir evento

Scenario: Owner reabre un evento cerrado
  Given que el evento está cerrado
  And el usuario es Owner del evento
  When solicita reabrir el evento
  Then el sistema pide confirmación obligatoria
  And si el Owner confirma, cambia el estado del evento a activo
  And permite nuevas solicitudes de entrada y asignaciones
```

```gherkin
Feature: Cancelar evento

Scenario: Owner cancela un evento activo
  Given que el evento está activo
  And el usuario es Owner del evento
  When solicita cancelar el evento
  Then el sistema pide confirmación obligatoria
  And si el Owner confirma, cambia el estado del evento a cancelado
  And bloquea nuevas acciones sobre solicitudes, ítems y asignaciones
```

```gherkin
Feature: Gestión de co-admins

Scenario: Owner asigna co-admin
  Given que el usuario es Owner del evento
  And existe un participante aceptado
  When el Owner lo asigna como co-admin
  Then el participante obtiene permisos para gestionar solicitudes de entrada
  And obtiene permisos para aprobar o rechazar sugerencias
  And conserva sus asignaciones existentes
```

```gherkin
Feature: Gestión de co-admins

Scenario: Owner revoca co-admin
  Given que el usuario es Owner del evento
  And existe un Co-admin en el evento
  When el Owner revoca su rol de Co-admin
  Then el sistema pide confirmación obligatoria
  And si el Owner confirma, el usuario queda como Participante regular
  And pierde permisos administrativos desde ese momento
  And conserva sus asignaciones existentes
```

```gherkin
Feature: Remover participantes

Scenario: Owner remueve participante sin asignaciones
  Given que el usuario actual es Owner del evento
  And existe un Participante sin asignaciones activas
  When el Owner remueve al Participante
  Then el sistema pide confirmación obligatoria
  And si el Owner confirma, retira su participación del evento
  And el evento deja de aparecer en el dashboard del usuario removido
```

```gherkin
Feature: Reingreso después de remoción

Scenario: Usuario removido solicita entrar de nuevo
  Given que el usuario fue removido del evento por el Owner
  And el evento está activo
  When abre nuevamente el link o QR del evento
  And solicita entrar
  Then el sistema registra una nueva solicitud en estado pendiente
  And si la solicitud es aceptada, el usuario reingresa como Participante normal
```

```gherkin
Feature: Remover participantes

Scenario: Owner intenta remover participante con asignaciones no compradas
  Given que el usuario actual es Owner del evento
  And existe un Participante con asignaciones no compradas
  When el Owner intenta removerlo
  Then el sistema bloquea la remoción
  And indica que primero deben cancelarse sus asignaciones no compradas
```

```gherkin
Feature: Remover participantes

Scenario: Owner intenta remover participante con asignaciones compradas
  Given que el usuario actual es Owner del evento
  And existe un Participante con asignaciones compradas
  When el Owner intenta removerlo
  Then el sistema bloquea la remoción
  And mantiene la participación del usuario en el evento
```

---

## 4.4 `EventAccess`

### Responsabilidad

Controla cómo un usuario entra a un evento privado y qué puede ver según su estado de acceso.

> Visualmente, este módulo vive dentro del detalle del evento. No requiere una pantalla independiente en el MVP.

### Funcionalidades

- Abrir evento desde link compartible o QR.
- Mostrar ficha pública limitada del evento.
- Solicitar entrada al evento.
- Salirse voluntariamente de un evento.
- Mostrar estado pendiente mientras espera aprobación.
- Aprobar solicitud de entrada.
- Rechazar solicitud de entrada.
- Bloquear acceso a la lista hasta aceptación.
- Bloquear solicitudes para eventos cerrados o cancelados.

### Reglas de negocio

- Todos los eventos son privados por link o QR.
- No existe búsqueda pública de eventos.
- Tener el link no da acceso automático a la lista.
- Un usuario pendiente solo ve la ficha del evento y su estado de solicitud.
- Solicitar entrada a un evento no requiere confirmación obligatoria adicional.
- Solo Owner y Co-admin pueden aceptar o rechazar solicitudes.
- Aprobar una solicitud de entrada no requiere confirmación obligatoria.
- Rechazar una solicitud de entrada requiere confirmación obligatoria y no incluye motivo en el MVP.
- Si una solicitud es rechazada, el usuario no puede volver a solicitar acceso al mismo evento.
- Owner y Co-admin pueden cambiar una solicitud rechazada a aceptada si el rechazo fue un error.
- Un Participante puede salirse voluntariamente de un evento si no tiene asignaciones activas.
- Salirse voluntariamente de un evento requiere confirmación obligatoria del participante.
- Si tiene asignaciones no compradas, debe cancelarlas antes de salirse.
- Si tiene asignaciones compradas, no puede salirse del evento en el MVP.
- Si un Co-admin se sale del evento, su rol de Co-admin se revoca automáticamente.
- El Owner no puede salirse de su propio evento.
- Un usuario que se salió voluntariamente puede volver a solicitar entrada usando el link o QR del evento.
- Si un usuario fue rechazado, luego aceptado por Owner/Co-admin y después se salió voluntariamente, puede volver a solicitar entrada.
- Si un usuario reingresa después de salirse, vuelve siempre como Participante normal; no recupera automáticamente el rol de Co-admin.
- No hay notificación de evento en MVP; el solicitante ve el estado al entrar al evento.

### Historias relacionadas

- US-13 Solicitar unirse a un evento.
- US-14 Gestionar solicitudes de entrada.

### Escenarios Gherkin

```gherkin
Feature: Solicitud de entrada

Scenario: Usuario solicita acceso a un evento activo
  Given que el evento está activo
  And el usuario tiene una cuenta verificada
  When abre el link del evento
  And solicita unirse
  Then el sistema registra la solicitud en estado pendiente
  And muestra la ficha del evento con mensaje de espera
  And no muestra la lista de ítems
```

```gherkin
Feature: Gestión de solicitudes

Scenario: Co-admin acepta una solicitud pendiente
  Given que existe una solicitud de entrada pendiente
  And el usuario actual es Co-admin del evento
  When acepta la solicitud
  Then el solicitante pasa a Participante aceptado
  And puede ver la lista del evento al entrar
```

```gherkin
Feature: Gestión de solicitudes

Scenario: Co-admin rechaza una solicitud pendiente
  Given que existe una solicitud de entrada pendiente
  And el usuario actual es Co-admin del evento
  When rechaza la solicitud
  Then el sistema pide confirmación obligatoria
  And si el Co-admin confirma, marca la solicitud como rechazada
  And no solicita motivo de rechazo en el MVP
```

```gherkin
Feature: Solicitud rechazada

Scenario: Usuario rechazado intenta volver a solicitar acceso
  Given que el usuario tiene una solicitud rechazada para el evento
  When intenta solicitar acceso nuevamente
  Then el sistema bloquea la nueva solicitud
  And muestra el estado rechazado en la ficha del evento
```

```gherkin
Feature: Corrección de solicitud rechazada

Scenario: Owner acepta una solicitud previamente rechazada
  Given que existe una solicitud rechazada
  And el usuario actual es Owner del evento
  When cambia el estado de la solicitud a aceptada
  Then el solicitante pasa a Participante aceptado
  And puede ver la lista del evento al entrar
```

```gherkin
Feature: Salirse de un evento

Scenario: Participante sin asignaciones sale del evento
  Given que el usuario es Participante aceptado del evento
  And no tiene asignaciones activas
  When decide salirse del evento
  Then el sistema pide confirmación obligatoria
  And si el participante confirma, retira su participación del evento
  And el evento deja de aparecer en su dashboard
```

```gherkin
Feature: Salirse de un evento

Scenario: Co-admin sin asignaciones sale del evento
  Given que el usuario es Co-admin del evento
  And no tiene asignaciones activas
  When decide salirse del evento
  Then el sistema pide confirmación obligatoria
  And si el Co-admin confirma, retira su participación del evento
  And revoca automáticamente su rol de Co-admin
  And el evento deja de aparecer en su dashboard
```

```gherkin
Feature: Reingreso después de salir

Scenario: Usuario que salió voluntariamente solicita entrar de nuevo
  Given que el usuario se salió voluntariamente del evento
  And el evento está activo
  When abre nuevamente el link o QR del evento
  And solicita entrar
  Then el sistema registra una nueva solicitud en estado pendiente
  And si la solicitud es aceptada, el usuario reingresa como Participante normal
```

```gherkin
Feature: Reingreso después de rechazo corregido

Scenario: Usuario rechazado, luego aceptado, sale y solicita entrar de nuevo
  Given que el usuario fue rechazado previamente
  And después Owner o Co-admin cambió su estado a aceptado
  And el usuario se salió voluntariamente del evento
  And el evento está activo
  When solicita entrar nuevamente usando el link o QR
  Then el sistema permite crear una nueva solicitud en estado pendiente
```

```gherkin
Feature: Salirse de un evento

Scenario: Participante con asignaciones no compradas intenta salir
  Given que el usuario es Participante aceptado del evento
  And tiene asignaciones no compradas
  When intenta salirse del evento
  Then el sistema bloquea la salida
  And indica que debe cancelar sus asignaciones antes de salir
```

```gherkin
Feature: Salirse de un evento

Scenario: Participante con asignaciones compradas intenta salir
  Given que el usuario es Participante aceptado del evento
  And tiene asignaciones compradas
  When intenta salirse del evento
  Then el sistema bloquea la salida
  And mantiene su participación en el evento
```

---

## 4.5 `Items`

### Responsabilidad

Gestiona la lista oficial de ítems necesarios para el evento.

### Funcionalidades

- Agregar ítem.
- Editar ítem.
- Eliminar ítem.
- Soportar ítems con cantidad definida.
- Soportar ítems sin cantidad definida.
- Calcular estado visual del ítem según sus asignaciones.
- Resaltar ítems no cubiertos al cierre.

### Reglas de negocio

- Solo el Owner puede gestionar la lista base.
- El nombre del ítem es obligatorio.
- La cantidad es opcional.
- Si hay cantidad, la unidad es obligatoria.
- La unidad debe seleccionarse desde un catálogo controlado, no escribirse como texto libre.
- Si no hay cantidad, el ítem funciona como binario.
- Agregar un ítem no requiere confirmación obligatoria adicional al envío del formulario.
- Si el ítem no tiene asignaciones, el Owner puede editar nombre, cantidad y unidad.
- Editar un ítem sin asignaciones no requiere confirmación obligatoria.
- Si el ítem ya tiene asignaciones, el Owner solo puede editar la cantidad total.
- Si el ítem ya tiene asignaciones, no se puede reducir la cantidad total por debajo de la suma ya asignada.
- Si el ítem ya tiene asignaciones, el sistema muestra una advertencia antes de guardar cambios de cantidad.
- Guardar cambios de cantidad en un ítem con asignaciones requiere confirmación obligatoria del Owner.
- No se pueden editar ni eliminar ítems en eventos cerrados o cancelados.
- Eliminar cualquier ítem requiere confirmación obligatoria del Owner.
- Si se elimina un ítem, se eliminan sus asignaciones asociadas.
- Los estados del ítem son calculados automáticamente por el sistema.

### Catálogo inicial de unidades

El MVP usará un catálogo controlado con unidades comunes para convivios:

| Unidad | Uso típico |
|---|---|
| `kg` | Carne, pollo, tortillas por peso, hielo por peso |
| `g` | Ingredientes pequeños o cantidades menores |
| `litros` | Refrescos, agua, bebidas, salsas líquidas |
| `ml` | Bebidas o líquidos en cantidades menores |
| `piezas` | Vasos, platos, cubiertos, panes, limones |
| `paquetes` | Servilletas, vasos, platos, botanas empaquetadas |
| `bolsas` | Hielo, carbón, botanas, dulces |
| `cajas` | Refrescos, cervezas, botellas, insumos agrupados |
| `latas` | Refrescos, cervezas, alimentos enlatados |
| `botellas` | Refrescos, agua, bebidas alcohólicas, salsas |
| `garrafones` | Agua para grupos grandes |
| `charolas` | Comida preparada, postres, botanas |
| `docenas` | Pan, tortillas, huevos u otros ítems contables por docena |

### Historias relacionadas

- US-16 Agregar un ítem a la lista.
- US-17 Editar un ítem de la lista.
- US-18 Eliminar un ítem de la lista.

### Escenarios Gherkin

```gherkin
Feature: Gestión de ítems

Scenario: Owner agrega un ítem con cantidad definida
  Given que el evento está activo
  And el usuario es Owner del evento
  When agrega un ítem con nombre, cantidad y unidad
  Then el ítem aparece en la lista oficial
  And su estado inicial es sin asignar
```

```gherkin
Feature: Gestión de ítems

Scenario: Owner elimina un ítem con asignaciones
  Given que el evento está activo
  And el usuario es Owner del evento
  And el ítem tiene asignaciones activas
  When intenta eliminar el ítem
  Then el sistema pide confirmación obligatoria con advertencia sobre asignaciones existentes
  And si el Owner confirma, elimina el ítem
  And elimina sus asignaciones asociadas
```

```gherkin
Feature: Edición de ítems asignados

Scenario: Owner intenta reducir la cantidad por debajo de lo asignado
  Given que el evento está activo
  And el usuario es Owner del evento
  And existe un ítem con 10 piezas como cantidad total
  And hay 8 piezas asignadas entre participantes
  When el Owner intenta cambiar la cantidad total a 5 piezas
  Then el sistema rechaza el cambio
  And informa que la cantidad total no puede ser menor a la cantidad ya asignada
```

---

## 4.6 `Assignments`

### Responsabilidad

Gestiona lo que cada participante se compromete a llevar y el estado de compra de su parte.

### Funcionalidades

- Asignarse un ítem.
- Definir cantidad asignada cuando el ítem tiene cantidad total.
- Modificar una asignación.
- Cancelar una asignación.
- Cancelar asignaciones no compradas de otros participantes como Owner.
- Marcar la propia parte como comprada.
- Permitir que Owner o Co-admin marquen como comprada cualquier asignación.
- Recalcular estado global del ítem.

### Reglas de negocio

- Solo participantes aceptados pueden asignarse ítems.
- El Owner también puede asignarse ítems.
- Crear una asignación no requiere confirmación obligatoria.
- Modificar una asignación propia no comprada no requiere confirmación obligatoria.
- No se puede superar la cantidad total del ítem.
- Un ítem cubierto no acepta nuevas asignaciones.
- En ítems sin cantidad definida, la asignación es binaria.
- Cada asignado marca su propia parte como comprada.
- Owner y Co-admin pueden marcar cualquier asignación como comprada.
- Marcar una asignación como comprada requiere confirmación obligatoria, porque no puede desmarcarse en el MVP.
- En el MVP, ninguna persona puede desmarcar una asignación comprada.
- Las asignaciones no pueden modificarse ni cancelarse si el evento está cerrado o cancelado.
- Una asignación marcada como comprada no puede modificarse.
- Una asignación marcada como comprada no puede cancelarse.
- El Owner puede cancelar asignaciones no compradas de cualquier participante.
- El Owner no puede modificar la cantidad de asignaciones de otros participantes; solo puede cancelarlas si no están compradas.
- Cancelar una asignación ajena requiere confirmación obligatoria del Owner.
- Cancelar una asignación propia requiere confirmación obligatoria del participante.
- El Co-admin no puede cancelar asignaciones de otros participantes.
- Al cancelar una asignación no comprada, la cantidad vuelve a estar disponible.
- Los asignados sí pueden marcar comprado aunque el evento esté cerrado.
- Owner y Co-admin también pueden marcar cualquier asignación como comprada aunque el evento esté cerrado.
- En eventos cancelados no se pueden crear, modificar, cancelar ni marcar como compradas asignaciones.

### Historias relacionadas

- US-19 Asignarse un ítem.
- US-20 Modificar una asignación.
- US-21 Cancelar una asignación.
- US-21b Cancelar asignación ajena.
- US-22 Marcar ítem como comprado.

### Escenarios Gherkin

```gherkin
Feature: Asignación de ítems

Scenario: Participante se asigna parte de un ítem con cantidad
  Given que el evento está activo
  And el usuario es Participante aceptado
  And existe un ítem con cantidad total de 2 kg
  And queda al menos 1 kg disponible
  When el participante se asigna 1 kg
  Then el sistema registra la asignación
  And recalcula el estado del ítem
  And muestra cuánto queda pendiente
```

```gherkin
Feature: Validación de cantidad asignada

Scenario: Participante intenta asignar más de lo disponible
  Given que el ítem tiene 2 kg como cantidad total
  And ya hay 1.5 kg asignados
  When un participante intenta asignarse 1 kg
  Then el sistema rechaza la asignación
  And informa que la cantidad supera lo disponible
```

```gherkin
Feature: Compra de asignaciones

Scenario: Participante marca su parte como comprada
  Given que el usuario tiene una asignación activa
  When marca su parte como comprada
  Then el sistema pide confirmación obligatoria
  And si el usuario confirma, actualiza el estado de esa asignación
  And recalcula el estado global del ítem
```

```gherkin
Feature: Compra en evento cerrado

Scenario: Co-admin marca una asignación como comprada en evento cerrado
  Given que el evento está cerrado
  And existe una asignación no comprada
  And el usuario actual es Co-admin del evento
  When marca la asignación como comprada
  Then el sistema pide confirmación obligatoria
  And si el Co-admin confirma, actualiza la asignación a comprada
  And recalcula el estado global del ítem
```

```gherkin
Feature: Bloqueo de asignaciones en evento cancelado

Scenario: Participante intenta marcar comprado en evento cancelado
  Given que el evento está cancelado
  And el usuario tiene una asignación no comprada
  When intenta marcar su asignación como comprada
  Then el sistema rechaza la acción
  And mantiene el estado previo de la asignación
```

```gherkin
Feature: Cancelación de asignaciones compradas

Scenario: Participante intenta cancelar una asignación comprada
  Given que el usuario tiene una asignación marcada como comprada
  When intenta cancelar la asignación
  Then el sistema rechaza la cancelación
  And mantiene la asignación como comprada
```

```gherkin
Feature: Cancelación de asignación propia

Scenario: Participante cancela su asignación no comprada
  Given que el usuario tiene una asignación no comprada
  And el evento está activo
  When solicita cancelar su asignación
  Then el sistema pide confirmación obligatoria
  And si el participante confirma, elimina la asignación
  And la cantidad queda disponible para otros participantes
  And recalcula el estado global del ítem
```

```gherkin
Feature: Cancelación de asignaciones por Owner

Scenario: Owner cancela una asignación no comprada de un participante
  Given que el usuario actual es Owner del evento
  And existe una asignación no comprada de otro participante
  When el Owner cancela la asignación
  Then el sistema pide confirmación obligatoria
  And si el Owner confirma, elimina la asignación
  And la cantidad queda disponible para otros participantes
  And recalcula el estado global del ítem
```

```gherkin
Feature: Cancelación de asignaciones por Co-admin

Scenario: Co-admin intenta cancelar una asignación de otro participante
  Given que el usuario actual es Co-admin del evento
  And existe una asignación no comprada de otro participante
  When intenta cancelar la asignación
  Then el sistema rechaza la acción
  And mantiene la asignación existente
```

```gherkin
Feature: Modificación de asignaciones compradas

Scenario: Participante intenta modificar una asignación comprada
  Given que el usuario tiene una asignación marcada como comprada
  When intenta modificar la cantidad asignada
  Then el sistema rechaza la modificación
  And mantiene la asignación como comprada con su cantidad original
```

---

## 4.7 `Moderation`

### Responsabilidad

Gestiona sugerencias de ítems hechas por participantes.

> Visualmente, este módulo vive dentro del detalle del evento. No requiere una pantalla independiente en el MVP.

### Funcionalidades

- Crear sugerencia de ítem.
- Editar sugerencia pendiente.
- Eliminar sugerencia pendiente propia.
- Ver sugerencias pendientes.
- Aprobar sugerencia.
- Modificar una sugerencia antes de aprobarla.
- Rechazar sugerencia con nota opcional.
- Mostrar estado de la sugerencia al participante.

### Reglas de negocio

- Solo participantes aceptados pueden sugerir ítems.
- Crear una sugerencia no requiere confirmación obligatoria adicional al envío del formulario.
- Una sugerencia no aparece en la lista oficial hasta ser aprobada.
- Owner y Co-admin pueden aprobar o rechazar sugerencias.
- Owner y Co-admin pueden modificar nombre, cantidad y unidad de una sugerencia antes de aprobarla.
- Aprobar una sugerencia no requiere confirmación obligatoria.
- Rechazar una sugerencia requiere confirmación obligatoria.
- El rechazo de sugerencia puede incluir una nota opcional.
- Una sugerencia aprobada entra a la lista oficial como ítem sin asignar.
- Cuando una sugerencia se aprueba y entra a la lista oficial, el ítem no muestra "sugerido por".
- Una sugerencia rechazada no aparece en la lista oficial.
- Si una sugerencia es rechazada con nota, la nota queda visible para quien sugirió y para Owner/Co-admins en el historial de sugerencias.
- El participante puede editar su sugerencia solo mientras esté pendiente.
- Editar una sugerencia pendiente propia no requiere confirmación obligatoria.
- El participante puede eliminar su sugerencia solo mientras esté pendiente.
- Eliminar una sugerencia pendiente propia requiere confirmación obligatoria.
- No hay notificación de evento en MVP; el participante ve el estado de su sugerencia al entrar al evento.

### Historias relacionadas

- US-23 Sugerir un ítem.
- US-24 Editar una sugerencia pendiente.
- US-25 Aprobar o rechazar una sugerencia.

### Escenarios Gherkin

```gherkin
Feature: Sugerencias de ítems

Scenario: Participante sugiere un ítem
  Given que el evento está activo
  And el usuario es Participante aceptado
  When sugiere un ítem con nombre válido
  Then el sistema registra la sugerencia como pendiente
  And no la muestra en la lista oficial
  And la muestra en la sección de sugerencias del evento
```

```gherkin
Feature: Sugerencias de ítems

Scenario: Participante elimina su sugerencia pendiente
  Given que el usuario es Participante aceptado
  And tiene una sugerencia en estado pendiente
  When elimina su sugerencia
  Then el sistema pide confirmación obligatoria
  And si el participante confirma, elimina la sugerencia pendiente
  And la sugerencia deja de aparecer para revisión de Owner y Co-admins
```

```gherkin
Feature: Revisión de sugerencias

Scenario: Co-admin aprueba una sugerencia
  Given que existe una sugerencia pendiente
  And el usuario actual es Co-admin del evento
  When aprueba la sugerencia
  Then el sistema crea el ítem en la lista oficial
  And el ítem inicia con estado sin asignar
  And el ítem no muestra quién lo sugirió
  And la sugerencia queda marcada como aprobada
```

```gherkin
Feature: Revisión de sugerencias

Scenario: Owner modifica una sugerencia antes de aprobarla
  Given que existe una sugerencia pendiente
  And el usuario actual es Owner del evento
  When modifica nombre, cantidad o unidad de la sugerencia
  And aprueba la sugerencia modificada
  Then el sistema crea el ítem en la lista oficial con los datos modificados
  And la sugerencia queda marcada como aprobada
```

```gherkin
Feature: Rechazo de sugerencias

Scenario: Owner rechaza una sugerencia con nota
  Given que existe una sugerencia pendiente
  And el usuario actual es Owner del evento
  When rechaza la sugerencia con una nota
  Then el sistema pide confirmación obligatoria
  And si el Owner confirma, la sugerencia queda marcada como rechazada
  And la nota queda visible para quien sugirió el ítem
  And la nota queda visible para Owner y Co-admins en el historial de sugerencias
```

---

## 4.8 `Notifications`

### Responsabilidad

Centralizar futuras notificaciones de eventos por email.

### Estado MVP

`Notifications` queda fuera del MVP como módulo funcional activo.

En el MVP no habrá:

- Notificaciones in-app de evento.
- Emails de evento.
- Push notifications.
- Centro de notificaciones.
- Historial de notificaciones.

### Decisión post-MVP

Cuando las notificaciones de evento se implementen, el canal definido será **email**.

No se contemplan para esta fase:

- Push notifications.
- Centro de notificaciones in-app.
- Historial de notificaciones in-app.

### Lo que sí existe en MVP

Los únicos correos incluidos en el MVP pertenecen a `Auth`:

- Correo de verificación de cuenta.
- Correo de recuperación de contraseña.

### Eventos candidatos para email post-MVP

Estos eventos podrían evaluarse más adelante como emails de evento:

- Nueva solicitud de entrada al evento.
- Solicitud aceptada o rechazada.
- Nueva sugerencia de ítem.
- Sugerencia aprobada o rechazada.
- Ítem marcado como comprado.
- Evento cerrado o cancelado.

### Escenarios Gherkin post-MVP

```gherkin
Feature: Emails de evento post-MVP

Scenario: Owner recibe email por nueva solicitud de entrada
  Given que los emails de evento están habilitados
  And un usuario solicita entrar a un evento
  When el sistema registra la solicitud
  Then envía un email al Owner
  And envía un email a los Co-admins del evento
```

---

## 5. Dependencias entre módulos

| Módulo | Depende de | Motivo |
|---|---|---|
| `Dashboard` | `Auth`, `Events` | Necesita usuario autenticado y eventos relacionados. |
| `Events` | `Auth` | Todo evento requiere Owner autenticado. |
| `EventAccess` | `Auth`, `Events` | Solo usuarios con cuenta pueden solicitar entrada a eventos existentes. |
| `Items` | `Events`, `EventAccess` | Solo Owner de evento activo puede gestionar lista base. |
| `Assignments` | `Items`, `EventAccess` | Solo participantes aceptados pueden asignarse ítems existentes. |
| `Moderation` | `Items`, `EventAccess` | Solo participantes aceptados sugieren; Owner/Co-admin revisan. |
| `Notifications` | Todos | Post-MVP; reaccionará a eventos de negocio y enviará emails. |

---

## 6. Reglas transversales

### Roles

Los roles existen solo dentro de un evento:

- `Owner`
- `Co-admin`
- `Participante`

Un mismo usuario puede tener distintos roles en distintos eventos.

### Estados de evento

- `activo`
- `cerrado`
- `cancelado`

### Estados de acceso

- `pendiente`
- `aceptado`
- `rechazado`

### Estados calculados de ítem

- `sin_asignar`
- `parcialmente_cubierto`
- `cubierto`
- `parcialmente_comprado`
- `comprado`

### Estados de sugerencia

- `pendiente_aprobacion`
- `aprobada`
- `rechazada`

---

## 7. Pendientes de definición

No quedan pendientes abiertos en esta fase.

---

## 8. Acciones que requieren confirmación

### Requieren confirmación obligatoria

| Módulo | Acción | Quién confirma | Motivo |
|---|---|---|---|
| `Events` | Cerrar evento manualmente | Owner | Bloquea nuevas solicitudes y asignaciones. |
| `Events` | Reabrir evento cerrado | Owner | Vuelve a permitir nuevas solicitudes y asignaciones. |
| `Events` | Cancelar evento | Owner | Acción irreversible en MVP. |
| `Events` | Revocar Co-admin | Owner | Quita permisos administrativos. |
| `Events` | Remover participante | Owner | Retira participación del evento. |
| `EventAccess` | Salirse del evento | Participante/Co-admin | Retira participación y puede revocar rol Co-admin. |
| `EventAccess` | Rechazar solicitud de entrada | Owner/Co-admin | Bloquea nuevo intento de solicitud salvo corrección manual. |
| `Items` | Guardar cambio de cantidad en ítem con asignaciones | Owner | Puede afectar disponibilidad visible. |
| `Items` | Eliminar ítem | Owner | Elimina el ítem y sus asignaciones asociadas. |
| `Assignments` | Cancelar asignación propia | Participante | Libera cantidad previamente comprometida. |
| `Assignments` | Cancelar asignación ajena | Owner | Libera compromiso de otro participante. |
| `Assignments` | Marcar asignación como comprada | Participante/Owner/Co-admin | No puede desmarcarse en MVP. |
| `Moderation` | Eliminar sugerencia pendiente propia | Participante | Retira la sugerencia de revisión. |
| `Moderation` | Rechazar sugerencia | Owner/Co-admin | Cierra la sugerencia como rechazada. |

### No requieren confirmación obligatoria

| Módulo | Acción |
|---|---|
| `Auth` | Registrar cuenta |
| `Auth` | Reenviar correo de verificación |
| `Auth` | Solicitar recuperación de contraseña |
| `Events` | Crear evento |
| `Events` | Editar datos del evento |
| `Events` | Asignar Co-admin |
| `EventAccess` | Solicitar entrada |
| `EventAccess` | Aprobar solicitud de entrada |
| `Items` | Agregar ítem |
| `Items` | Editar ítem sin asignaciones |
| `Assignments` | Crear asignación |
| `Assignments` | Modificar asignación propia no comprada |
| `Moderation` | Crear sugerencia |
| `Moderation` | Editar sugerencia pendiente propia |
| `Moderation` | Aprobar sugerencia |

---

## 9. Próximo documento

Después de validar este mapa funcional, el siguiente paso será:

1. `DATA_MODEL.md` — esquema de datos derivado de estos módulos y reglas.
