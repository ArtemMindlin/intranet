# 🤝 Guía de Contribución — GM Neologic

Este documento describe las normas básicas de trabajo dentro del repositorio para mantener un flujo de desarrollo claro, seguro y consistente entre todos los miembros del equipo.

---

# 🌿 Estrategia de ramas (Branching Strategy)

La rama `main` representa siempre la versión estable del proyecto.

Tipos de ramas permitidas:

* **main** → siempre estable y lista para producción.
* **feature/*** → nuevas funcionalidades.
* **fix/*** → correcciones de errores.
* **refactor/*** → mejoras internas sin cambios funcionales.
* **hotfix/*** → correcciones urgentes en producción.

---

# 🏷️ Convenciones de naming

Ejemplos válidos:

```
feature/login-auditoria
fix/permisos-roles
refactor/estructura-settings
hotfix/error-sqlserver
```

Reglas generales:

* Usar siempre minúsculas.
* Separar palabras con guiones (`-`).
* Evitar nombres genéricos como `test`, `cambios`, `update`.
* El nombre debe describir claramente el objetivo del cambio.

---

# 👨‍💻 Cómo crear una nueva rama

Desde la terminal o VS Code:

```
git checkout -b feature/nombre-cambio
```

Trabaja siempre en ramas separadas.
Nunca realizar cambios directamente sobre `main`.

---

# 🔄 Flujo de Pull Requests

Proceso estándar de trabajo:

1. Crear una nueva rama siguiendo las convenciones.
2. Realizar los cambios necesarios.
3. Crear una Pull Request hacia `main`.
4. Revisar el código (code review).
5. Hacer merge únicamente tras aprobación.

---

# 🤖 Uso de IA y herramientas asistidas

Si se utilizan herramientas como Codex o asistentes de IA:

* Todos los cambios deben revisarse manualmente antes del merge.
* No realizar commits automáticos sin verificación.
* Mantener la coherencia con el estilo del proyecto.

---

# ✅ Buenas prácticas generales

* Mantener commits claros y descriptivos.
* Evitar subir credenciales o información sensible.
* Seguir la estructura del proyecto Django existente.
* Priorizar cambios pequeños y revisables.
