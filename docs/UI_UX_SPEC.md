# UI_UX_SPEC.md — Hatsik

> Especificación puente entre el alcance funcional y la interfaz de Hatsik.

## 1. Objetivo

Definir cómo se traduce el alcance de producto en navegación, pantallas, componentes y tokens base de UI.

Este documento se deriva de:

| Fuente | Aporta |
|---|---|
| `docs/PRODUCT_OVERVIEW.md` | Problema, propuesta de valor, roles, flujo principal y alcance MVP. |
| `docs/MODULES_SPEC.md` | Módulos funcionales, reglas de negocio y exclusiones del MVP. |
| `docs/hatsik-brand-identity.md` | Paleta, tipografía, tono visual y lineamientos de marca. |

## 2. Principios de UI/UX

| Principio | Decisión |
|---|---|
| Aplicación web responsiva | Hatsik se diseña como web app adaptable. |
| Navegación principal simple | MVP con una sola barra superior adaptativa; no sidebar ni navegación inferior. |
| Máxima escaneabilidad | Estados, roles y progresos siempre visibles de un vistazo. |
| Sin ruido innecesario | Notificaciones ocultas por completo en MVP. |
| Logout accesible | Cerrar sesión vive en un menú simple de usuario; no hay pantalla completa de perfil en MVP. |
| Un flujo, una pantalla | Las tareas operativas principales viven en el detalle del evento con secciones claras. |

## 3. Alcance funcional reflejado en UI

| Módulo | Superficie UI | Estado MVP |
|---|---|---|
| `Auth` | Login, registro, verificación pendiente, recuperación y reseteo de contraseña. | Incluido |
| `Dashboard` | Pantalla `Mis eventos`. | Incluido |
| `Events` | Crear, editar, cerrar, reabrir, cancelar, compartir link/QR. | Incluido |
| `EventAccess` | Ficha del evento y solicitudes de entrada. | Incluido |
| `Items` | Lista de ítems dentro del detalle del evento. | Incluido |
| `Assignments` | Apuntar, modificar, cancelar y marcar como comprado. | Incluido |
| `Moderation` | Sugerencias pendientes y revisión. | Incluido |
| `Notifications` | Centro de notificaciones, badges y historial. | Fuera del MVP |

## 4. Mapa de navegación

### 4.1 Flujo principal

`Login / Registro` → `Verificación pendiente` (si aplica) → `Mis eventos` → `Detalle del evento` → `Crear / Editar evento`

### 4.2 Flujo de acceso a evento por link o QR

`Link / QR` → `Ficha del evento` → `Solicitud enviada` → `Detalle del evento` (cuando la solicitud queda `aceptada`)

### 4.3 Navegación global

| Contexto | Navegación |
|---|---|
| Desktop / tablet | Logo + wordmark, links `Mis eventos` y `Crear evento`, menú de usuario con `Cerrar sesión`. |
| Pantallas pequeñas | Header compacto con logo y botón hamburguesa; abre drawer/menú con `Mis eventos`, `Crear evento` y `Cerrar sesión`. |
| Fuera de alcance MVP | No hay notificaciones, no hay pantalla de perfil completa, no hay navegación inferior. |

## 5. Pantallas y componentes clave

| Pantalla | Objetivo | Componentes clave |
|---|---|---|
| `Login` | Acceder a la cuenta. | Logo, email, contraseña, CTA primaria, link a registro, link a recuperación. |
| `Registro` | Crear cuenta nueva. | Nombre de pantalla, email, contraseña, ayuda de requisitos, CTA primaria, link a login. |
| `Verificación pendiente` | Bloquear uso funcional hasta verificar email. | Mensaje de estado, CTA para reenviar correo, estado de rate limit, logout. |
| `Recuperación de contraseña` | Solicitar link de reseteo. | Email, CTA primaria, mensaje genérico de respuesta. |
| `Restablecer contraseña` | Definir nueva contraseña. | Nueva contraseña, confirmación, ayuda de requisitos, CTA primaria. |
| `Mis eventos` | Ver eventos propios y participaciones. | Header global, tarjetas de evento, roles visibles, estados `activo/cerrado/cancelado`, CTA `Crear evento`. |
| `Ficha del evento` | Ver datos del evento y solicitar entrada. | Nombre, descripción, fecha, estado de acceso, CTA `Solicitar entrada`, mensaje de acceso restringido. |
| `Detalle del evento` | Operar el evento. | Cabecera del evento, progreso, acciones del owner, solicitudes pendientes, lista de ítems, sugerencias, participantes/co-admins, acciones destructivas. |
| `Crear evento` | Crear un nuevo evento. | Formulario de nombre, fecha, descripción opcional, fecha límite opcional, CTA primaria. |
| `Editar evento` | Ajustar datos del evento. | Mismo formulario base que crear evento en modo edición. |

### 5.1 Detalle del evento: estructura interna

| Sección | Contenido |
|---|---|
| Cabecera | Nombre del evento, fecha, estado, rol del usuario, acciones de compartir. |
| Resumen | Progreso general, conteos clave, estado actual de la lista. |
| Solicitudes pendientes | Badge de conteo, lista de solicitudes, aceptar/rechazar. |
| Lista de ítems | Tarjetas por ítem con estado, responsables y acciones de asignación. |
| Sugerencias | Pendientes, aprobadas y rechazadas con estado visible. |
| Participantes y co-admins | Roles visibles, gestión por el owner. |
| Acciones de evento | Editar, cerrar, reabrir, cancelar, según permisos. |

### 5.2 Componentes operativos por pantalla

| Pantalla | Formularios | Listas / tablas | Indicadores / gráficas |
|---|---|---|---|
| `Login` | Email, contraseña. | No aplica. | No aplica. |
| `Registro` | Nombre de pantalla, email, contraseña. | No aplica. | Validación visual de contraseña. |
| `Verificación pendiente` | Reenvío de correo. | No aplica. | Countdown de 60 segundos para rate limit. |
| `Mis eventos` | No aplica. | Tarjetas de eventos. | Badges de rol y estado. |
| `Crear evento` | Datos base del evento. | No aplica. | No aplica. |
| `Editar evento` | Datos base del evento. | No aplica. | Estado actual del evento. |
| `Ficha del evento` | Solicitud de entrada. | No aplica. | Estado de acceso: pendiente, rechazado o bloqueado. |
| `Detalle del evento` | Ítem, asignación, sugerencia, edición de evento. | Ítems, solicitudes, sugerencias, participantes. | Barra de progreso general y barras por ítem. |

### 5.3 Tarjetas y filas clave

| Componente | Contenido mínimo | Acciones |
|---|---|---|
| Tarjeta de evento | Nombre, fecha, rol del usuario, estado del evento. | Ver evento. |
| Tarjeta de ítem | Nombre, cantidad total/asignada/pendiente, estado visual, participantes asignados. | Apuntarme, modificar, cancelar, marcar comprado, editar/eliminar si Owner. |
| Fila de solicitud | Nombre, email, fecha de solicitud. | Aceptar, rechazar. |
| Tarjeta de sugerencia | Nombre, cantidad/unidad, estado, autor cuando aplique. | Editar/eliminar propia, aprobar/rechazar/modificar si Owner o Co-admin. |
| Fila de participante | Nombre, email, rol dentro del evento. | Asignar co-admin, revocar co-admin, remover. |

### 5.4 Confirmaciones obligatorias en UI

Las confirmaciones deben usarse solo para acciones riesgosas definidas en `MODULES_SPEC.md`.

| Módulo | Acción | Patrón UI |
|---|---|---|
| `Events` | Cerrar, reabrir o cancelar evento. | Modal de confirmación. |
| `Events` | Revocar co-admin o remover participante. | Modal de confirmación. |
| `EventAccess` | Salirse del evento o rechazar solicitud. | Modal de confirmación. |
| `Items` | Eliminar ítem o guardar cambio de cantidad con asignaciones. | Modal con advertencia contextual. |
| `Assignments` | Cancelar asignación propia/ajena o marcar comprado. | Modal de confirmación. |
| `Moderation` | Eliminar sugerencia pendiente propia o rechazar sugerencia. | Modal de confirmación. |

## 6. Decisiones de UX propuestas donde faltan detalles

| Tema | Decisión propuesta | Estado |
|---|---|---|
| Drawer móvil | Abrir desde el header como panel lateral superpuesto, con cierre al tocar fuera o elegir una opción. | Propuesta |
| Crear / editar evento | Reutilizar un solo formulario base con modo `crear` / `editar`. | Propuesta |
| Detalle del evento | Resolver el detalle con secciones apiladas en la misma pantalla, no con subpantallas separadas en MVP. | Propuesta |

## 7. Tokens base de diseño

### 7.1 Color

| Token | Valor | Uso |
|---|---|---|
| `--color-primary` | `#E8432D` | Botones principales, acentos, logo. |
| `--color-primary-hover` | `#F26B54` | Hover y estados activos de acción. |
| `--color-primary-soft` | `#FDE8E4` | Fondos suaves, badges y chips. |
| `--color-bg` | `#FFFFFF` | Fondo general. |
| `--color-surface` | `#FFFFFF` | Tarjetas y superficies. |
| `--color-text` | `#1A1A1A` | Texto principal. |
| `--color-text-muted` | `#6B7280` | Metadatos y texto secundario. |
| `--color-border` | `#E5E7EB` | Bordes y divisores. |
| `--color-state-empty` | `#FCA5A5` | Ítems sin asignar. |
| `--color-state-partial` | `#FDBA74` | Ítems parcialmente cubiertos. |
| `--color-state-covered` | `#86EFAC` | Ítems cubiertos. |
| `--color-state-partial-bought` | `#93C5FD` | Ítems parcialmente comprados. |
| `--color-state-bought` | `#4ADE80` | Ítems comprados. |

### 7.2 Tipografía

| Token | Valor | Uso |
|---|---|---|
| `--font-heading` | `Nunito` | Títulos, logo, nombre de evento. |
| `--font-body` | `Plus Jakarta Sans` | Cuerpo, etiquetas, botones. |
| `--font-weight-bold` | `700` | Títulos de pantalla y nombres clave. |
| `--font-weight-semibold` | `600` | Botones, labels, estados. |
| `--font-weight-regular` | `400` | Texto corrido y metadatos. |

### 7.3 Espaciado, forma y elevación

| Token | Valor | Uso |
|---|---|---|
| `--space-1` | `4px` | Ajustes mínimos. |
| `--space-2` | `8px` | Separación compacta. |
| `--space-3` | `12px` | Separación entre elementos relacionados. |
| `--space-4` | `16px` | Padding base de tarjetas y formularios. |
| `--space-6` | `24px` | Separación de secciones. |
| `--radius-card` | `16px` | Tarjetas. |
| `--radius-button` | `12px` | Botones. |
| `--radius-input` | `10px` | Inputs. |
| `--radius-pill` | `999px` | Badges y chips. |
| `--shadow-none` | `none` | Base visual plana. |
| `--shadow-soft` | `0 1px 2px rgba(0,0,0,0.04)` | Elevación mínima cuando haga falta. |

### 7.4 Motion

| Token | Valor | Uso |
|---|---|---|
| `--motion-fast` | `120ms` | Hover y feedback inmediato. |
| `--motion-base` | `180ms` | Transiciones estándar. |
| `--motion-slow` | `240ms` | Drawer y cambios de sección. |

### 7.5 Estados de botones

| Variante | Base | Hover / active | Disabled | Uso |
|---|---|---|---|---|
| Primario | Fondo `--color-primary`, texto blanco. | Fondo `--color-primary-hover`. | Opacidad reducida, sin interacción. | Crear evento, guardar, apuntarme. |
| Secundario | Fondo blanco, borde coral, texto coral. | Fondo `--color-primary-soft`. | Opacidad reducida. | Copiar link, volver, acciones alternativas. |
| Terciario | Fondo transparente, texto gris o coral. | Fondo gris/coral suave. | Opacidad reducida. | Acciones de baja prioridad. |
| Destructivo | Fondo suave, texto de advertencia. | Mayor contraste del fondo. | Opacidad reducida. | Cancelar evento, eliminar ítem, remover participante. |

### 7.6 Estados de formularios

| Estado | Regla visual |
|---|---|
| Default | Borde `--color-border`, label visible. |
| Focus | Anillo visible en coral suave. |
| Error | Mensaje debajo del campo; no depender solo del color. |
| Success | Mensaje breve y cálido cuando aporte claridad. |
| Disabled | Fondo suave, texto muted, sin interacción. |
| Loading | Mantener layout estable; no cambiar ancho de botones. |

## 8. Resumen operativo

| Decisión | Regla |
|---|---|
| Navegación principal | Header adaptativo único. |
| Mobile | Drawer desde hamburger. |
| Notificaciones | No existen en MVP. |
| Perfil | No hay pantalla completa de perfil. |
| Logout | Vive en el menú de usuario. |
| Base visual | Blanco + coral, redondeado, limpio y escaneable. |
