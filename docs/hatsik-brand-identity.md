# 🎨 Identidad Visual — Hatsik

> **Documento:** Brand Identity v1.0
> **Producto:** Hatsik — "dividir, compartir" (maya)
> **Fecha:** 2026-05-23
> **Estado:** Definición inicial

---

## 1. Esencia de marca

Hatsik es la app que hace lo que hace una buena anfitriona: ya organizó todo, tú solo llega y aporta lo tuyo. La marca debe sentirse **cálida, confiable y festiva** — como entrar a la cocina de alguien que ya tiene todo bajo control.

**Tres palabras que definen a Hatsik:**
- **Calidez** — no es fría ni corporativa, es como una reunión familiar
- **Claridad** — sabes de un vistazo qué falta y qué ya está cubierto
- **Alegría** — hay un convivio al final, eso se tiene que sentir

---

## 2. Paleta de colores

La paleta combina el rojo coral festivo con blanco limpio. El color fuerte va en los momentos de acción (botones, badges, íconos clave), el blanco da espacio para respirar.

### Colores principales

| Nombre | HEX | Uso |
|---|---|---|
| **Coral Hatsik** | `#E8432D` | Color principal — botones, logo, acentos |
| **Coral Suave** | `#F26B54` | Hover de botones, estados intermedios |
| **Coral Claro** | `#FDE8E4` | Fondos de tarjetas con acento, badges suaves |
| **Blanco** | `#FFFFFF` | Fondo general de todas las pantallas |
| **Gris Texto** | `#1A1A1A` | Texto principal, títulos |
| **Gris Medio** | `#6B7280` | Texto secundario, subtítulos, metadatos |
| **Gris Borde** | `#E5E7EB` | Bordes de tarjetas, divisores |

### Colores de estado (semáforo de ítems)

Estos colores reflejan el estado de cada ítem en la lista del evento:

| Estado | Color | HEX | Descripción visual |
|---|---|---|---|
| Sin asignar | Rojo suave | `#FCA5A5` | Alerta, necesita atención |
| Parcialmente cubierto | Naranja | `#FDBA74` | En progreso |
| Cubierto | Verde | `#86EFAC` | ¡Listo! |
| Parcialmente comprado | Azul | `#93C5FD` | Casi ahí |
| Comprado | Verde oscuro | `#4ADE80` | Completado |

> **Regla de oro:** El blanco es el rey del fondo. El coral solo aparece donde hay acción o información importante. Nunca fondo coral en pantallas completas.

---

## 3. Tipografía

La tipografía de Hatsik es **redonda, amigable y fácil de leer** — como las letras de Duolingo o Notion, nunca rígida ni corporativa.

### Fuentes recomendadas

#### Títulos y nombre de la app — **Nunito**
- Fuente: [Nunito](https://fonts.google.com/specimen/Nunito) (Google Fonts, gratis)
- Características: Extremadamente redonda, cálida, perfecta para headings
- Pesos a usar: **700 (Bold)** para títulos, **800 (ExtraBold)** para el logo
- Ejemplo: "Asado del sábado" en Nunito Bold se ve como escrito con cariño, no como un formulario de Excel

#### Cuerpo de texto — **Plus Jakarta Sans**
- Fuente: [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans) (Google Fonts, gratis)
- Características: Moderna, muy legible en pantallas pequeñas, ligeramente redonda
- Pesos a usar: **400 (Regular)** para párrafos, **600 (SemiBold)** para etiquetas y botones
- Ejemplo: "2 kg de carne · Parcialmente cubierto" se lee de un vistazo

### Jerarquía tipográfica

| Elemento | Fuente | Peso | Tamaño |
|---|---|---|---|
| Logo / Nombre app | Nunito | ExtraBold 800 | Grande |
| Título de pantalla | Nunito | Bold 700 | 24–28px |
| Nombre del evento | Nunito | Bold 700 | 20px |
| Nombre de ítem | Plus Jakarta Sans | SemiBold 600 | 16px |
| Cantidad / estado | Plus Jakarta Sans | Regular 400 | 14px |
| Texto pequeño / metadatos | Plus Jakarta Sans | Regular 400 | 12px |
| Botones | Plus Jakarta Sans | SemiBold 600 | 15px |

> **Tip:** Nunito solo para títulos, nombres y el logo. Todo lo demás en Plus Jakarta Sans. Esta combinación crea contraste sin perder coherencia.

---

## 4. Estilo visual de la interfaz

### 4.1 Filosofía general

La interfaz de Hatsik funciona como una **pizarra de cocina bien organizada**: fondo blanco limpio, los ítems están claros y separados, y el color aparece exactamente donde necesitas poner atención.

Piénsalo así: si la app de tu banco se siente como una oficina de gobierno, Hatsik debe sentirse como una nota adhesiva bien diseñada en el refrigerador.

### 4.2 Tarjetas de ítems

Cada ítem de la lista vive en una tarjeta con bordes redondeados (esquinas suaves, como un posit). La tarjeta muestra:
- Nombre del ítem en texto grande
- Barra de progreso de color según el estado
- Quién lo trae (nombre o foto pequeña)
- Botón de acción si el usuario puede apuntarse

Las tarjetas **no tienen sombras dramáticas** — solo un borde gris muy suave. El color viene del estado, no de efectos.

### 4.3 Botones

- **Botón principal (acción clave):** Fondo coral `#E8432D`, texto blanco, esquinas muy redondeadas (border-radius: 12px). Ej: "Apuntarme", "Crear evento"
- **Botón secundario:** Fondo blanco, borde coral, texto coral. Ej: "Ver detalles", "Cancelar"
- **Botón destructivo:** Fondo gris claro, texto gris oscuro. Ej: "Cancelar evento"

### 4.4 Íconos

Usar íconos de línea redondeada — la familia **Lucide Icons** o **Heroicons** (ambas gratuitas y open source). Nunca íconos de línea recta/agresiva. El estilo debe ser consistente con la tipografía redonda.

Ejemplos de íconos clave:
- ✅ Check redondeado para "comprado"
- 🛒 Carrito o bolsa para "asignado"
- 👥 Personas para participantes
- 📋 Lista para el evento
- 🔗 Link para compartir

### 4.5 Espaciado

Generoso. Las tarjetas tienen padding interno de al menos 16px. Entre tarjetas, 12px de separación. Los títulos de sección tienen 24px de margen superior. La app no debe sentirse apretada — hay espacio para respirar, como una mesa bien puesta.

### 4.6 Bordes redondeados

Todo tiene esquinas redondeadas. No hay nada cuadrado en Hatsik. Guía base:
- Tarjetas: `border-radius: 16px`
- Botones: `border-radius: 12px`
- Badges de estado: `border-radius: 999px` (completamente oval)
- Inputs / campos de texto: `border-radius: 10px`

---

## 5. Tono de voz (cómo habla la app)

El diseño visual y el lenguaje van de la mano. Hatsik habla como un amigo organizador, no como un sistema.

| ❌ Evitar | ✅ Preferir |
|---|---|
| "Error: ítem ya asignado" | "Alguien más ya se apuntó a esto" |
| "Solicitud enviada con éxito" | "¡Listo! El organizador ya verá tu solicitud" |
| "Usuario no autorizado" | "Solo el organizador puede hacer esto" |
| "Completar campos obligatorios" | "Falta el nombre del evento, ¿cómo se llama el convivio?" |
| "Evento cancelado" | "Este evento fue cancelado. Queda como historial." |

**Características del tono:**
- Directo pero amable — nunca robótico
- Celebra los logros pequeños ("¡La lista está completa! 🎉")
- Nunca culpa al usuario — los errores se explican en humano
- Usa segunda persona: "tu evento", "lo que llevas tú"

---

## 6. Logo — lineamientos

El logo de Hatsik debe evocar **dos personas compartiendo** — consistente con el significado maya del nombre. Inspiraciones conceptuales:

- Dos manos que se unen / comparten
- Una mesa con objetos distribuidos
- Una forma que se divide en partes iguales

**Estilo del logo (basado en Omnex como referencia):**
- Ícono geométrico bold con el concepto de compartir
- Wordmark en Nunito ExtraBold
- El ícono va en fondo coral `#E8432D` con forma cuadrada de esquinas redondeadas (como el de Omnex)
- El wordmark "hatsik" en minúsculas, en gris muy oscuro `#1A1A1A`

**Variaciones:**
- Logo completo: ícono + wordmark (para landing page, emails)
- Solo ícono: versión cuadrada coral (para app icon, favicon)
- Solo wordmark: en negro (para documentos, contextos monocromáticos)

---

## 7. Tipo de web / app

### Aplicación web responsiva

Hatsik es una aplicación web responsiva para desktop, tablet y pantallas pequeñas. La experiencia se define como web adaptativa y el layout se reorganiza según el ancho disponible sin perder jerarquía.

### Estructura de navegación

La navegación principal vive en una barra superior adaptativa:

- Desktop / tablet: logo + wordmark, links `Mis eventos` y `Crear evento`, menú de usuario con `Cerrar sesión`.
- Pantallas pequeñas: header compacto con logo y botón hamburguesa. El botón abre un drawer/menú con `Mis eventos`, `Crear evento` y `Cerrar sesión`.
- No hay navegación inferior.
- Notificaciones no se muestran en el MVP.
- No existe pantalla completa de perfil en el MVP.

### Pantallas clave y su atmósfera visual

| Pantalla | Atmósfera | Color dominante |
|---|---|---|
| Login / Registro | Limpia, acogedora, con el logo grande | Blanco + coral en botón |
| Lista de mis eventos | Como un tablero de notas, festivo | Blanco con tarjetas |
| Detalle del evento | Centro de operaciones claro | Blanco, estados de colores |
| Lista de ítems | Semáforo visual, muy escaneable | Colores de estado |
| Crear evento | Formulario amigable, paso a paso | Blanco limpio |
| Pantalla de espera (solicitud pendiente) | Tranquilizadora, no ansiosa | Blanco, tono cálido |

---

## 8. Resumen ejecutivo — cheat sheet

Para cualquier decisión de diseño futura, usar esta tabla como referencia rápida:

| Decisión | Respuesta Hatsik |
|---|---|
| **Color principal** | Coral `#E8432D` |
| **Fondo** | Blanco `#FFFFFF` |
| **Fuente títulos** | Nunito Bold / ExtraBold |
| **Fuente cuerpo** | Plus Jakarta Sans Regular / SemiBold |
| **Esquinas** | Siempre redondeadas |
| **Tono de voz** | Amigo organizador, directo y cálido |
| **Sensación general** | Cocina familiar bien organizada |
| **Referencia visual** | Omnex (estructura bold) + Duolingo (redondez) |
| **Lo que NO es** | Corporativo, frío, técnico, anguloso |

---

*Este documento es la base para UI_FLOWS.md y todos los componentes de frontend de Hatsik.*
