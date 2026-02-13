# Intranet - Portal de Comisiones

Aplicacion web interna construida con Django para gestionar ventas, comisiones e incidencias en equipos comerciales.

## Contenido
1. [Resumen funcional](#resumen-funcional)
2. [Stack tecnologico](#stack-tecnologico)
3. [Arquitectura del proyecto](#arquitectura-del-proyecto)
4. [Modelo de datos](#modelo-de-datos)
5. [Puesta en marcha local](#puesta-en-marcha-local)
6. [Datos demo reproducibles (seed)](#datos-demo-reproducibles-seed)
7. [Configuracion y entornos](#configuracion-y-entornos)
8. [Flujos por rol](#flujos-por-rol)
9. [Rutas principales](#rutas-principales)
10. [Calidad, estado actual y limitaciones](#calidad-estado-actual-y-limitaciones)
11. [Contribucion](#contribucion)
12. [Licencia](#licencia)

## Resumen funcional
El sistema permite:

- Visualizar ventas personales y su comision aprobada.
- Registrar incidencias asociadas a una venta concreta o de tipo general.
- Consultar historial de incidencias con filtros y detalle navegable.
- Gestionar perfiles comerciales con jerarquia organizativa.
- Ofrecer vistas de gerencia para comisiones e incidencias (estado parcial, ver limitaciones).

## Stack tecnologico
- Python 3.14 (verificado en desarrollo).
- Django 6.0.2.
- SQLite como base de datos por defecto.
- Plantillas Django (server-side rendering), CSS y recursos estaticos.
- Pillow para gestion de imagenes de perfil.

Dependencias exactas en `requirements.txt`.

## Arquitectura del proyecto
Estructura principal:

```text
.
|- intranet/                  # Proyecto Django (settings, urls, asgi/wsgi)
|  |- settings/               # Configuracion modular (base/local/production)
|- comisiones/                # App de negocio (modelos, vistas, urls, admin)
|- templates/                 # Plantillas HTML
|- static/                    # CSS e imagenes
|- media/                     # Archivos subidos (foto de perfil)
|- manage.py
```

Puntos clave de arquitectura:

- Autenticacion con el sistema de usuarios y grupos nativo de Django.
- Un `Perfil` por usuario (creado automaticamente mediante señal `post_save`).
- Jerarquia organizativa en `Perfil`: vendedor -> jefe de ventas -> gerente -> director comercial.
- Separacion de settings por entorno (`intranet/settings/`).

## Modelo de datos
Entidades principales:

- `Venta`: informacion comercial por operacion (matricula, IDV, cliente, tipo de venta, etc.).
- `Comision`: importe y estado de comision asociados a una `Venta`.
- `Incidencia`: reporte funcional por usuario, con relacion N:M contra `Venta` (o general).
- `Perfil`: extension del usuario con sede, foto y cadena jerarquica.

Relaciones relevantes:

- `Venta.usuario` -> `auth.User`.
- `Comision.venta` -> `Venta`.
- `Incidencia.reportado_por` -> `auth.User`.
- `Incidencia.ventas` -> `Venta` (ManyToMany).
- `Perfil.user` -> `auth.User` (OneToOne).

## Puesta en marcha local
### Opcion rapida en Windows (script .bat)
Si estas en Windows, puedes preparar y arrancar el proyecto con:

```powershell
.\iniciar_intranet.bat
```

El script `iniciar_intranet.bat` hace este flujo automaticamente:

1. Verifica `python` en `PATH`.
2. Usa `venv` (o `.venv` si existe); si no existe ninguno, crea `venv`.
3. Activa el entorno virtual.
4. Instala dependencias de `requirements.txt`.
5. Aplica migraciones.
6. Ejecuta `python manage.py seed` si la BD esta vacia.
7. Pregunta si quieres crear superusuario.
8. Abre `http://127.0.0.1:8000/` y ejecuta el servidor.

Para forzar seed en cualquier momento:

```powershell
set SEED=1
.\iniciar_intranet.bat
```

### Opcion manual (Windows/Linux/macOS)
#### 1) Clonar y entrar al proyecto
```bash
git clone <url-del-repositorio>
cd intranet
```

#### 2) Crear entorno virtual
Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3) Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4) Aplicar migraciones
```bash
python manage.py migrate
```

#### 5) Crear usuario administrador
```bash
python manage.py createsuperuser
```

#### 6) Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

Acceso local:

- Aplicacion: `http://127.0.0.1:8000/`
- Admin Django: `http://127.0.0.1:8000/admin/`

## Datos demo reproducibles (seed)
Este proyecto incluye un management command para poblar datos de ejemplo sin depender de subir SQLite al repositorio.

Comando base:

```bash
python manage.py seed
```

Opciones disponibles:

- `--n-ventas`: numero de ventas demo a crear (default: `30`).
- `--n-incidencias`: numero de incidencias demo a crear (default: `10`).
- `--reset`: borra ventas/comisiones/incidencias y regenera datos demo.

Ejemplos:

```bash
python manage.py seed --n-ventas 50 --n-incidencias 20
python manage.py seed --reset
```

Comportamiento de idempotencia:

- Si ya existen ventas o incidencias, `seed` no duplica datos y se omite.
- Si quieres regenerar desde cero, usa `--reset`.

Datos demo creados:

- Grupos de permisos (`Vendedor`, `Jefe de ventas`, `Gerente`, `Director Comercial`).
- Usuarios demo con perfiles y jerarquia organizativa.
- Ventas y comisiones con fechas recientes e importes plausibles.
- Incidencias asociadas a ventas (o generales).

Credenciales demo por defecto:

- Usuario: `vendedor_1_demo`
- Password: `Demo12345!`

Notas de repositorio:

- `db.sqlite3` y `*.sqlite3` estan excluidos en `.gitignore`.
- Cada clon puede reconstruir su BD local con migraciones + seed.

## Configuracion y entornos
Configuracion activa:

- `manage.py` usa `DJANGO_SETTINGS_MODULE=intranet.settings`.
- `intranet/settings/__init__.py` importa `local.py` por defecto.

Archivos de settings:

- `intranet/settings/base.py`: configuracion comun.
- `intranet/settings/local.py`: DEBUG activo y hosts locales.
- `intranet/settings/production.py`: plantilla comentada (pendiente de completar).

Recomendaciones para produccion:

- Mover `SECRET_KEY` a variable de entorno.
- Desactivar `DEBUG`.
- Definir `ALLOWED_HOSTS` reales.
- Activar cookies seguras y HTTPS.

## Flujos por rol
El sistema usa grupos de Django para comportamiento por rol:

- `Vendedor` y `Jefe de ventas`:
  - Redireccion tras login a perfil o ventas.
  - Acceso a `mis_ventas`, `mis_incidencias`, `registrar_incidencia`, `mi_perfil`.
- `Gerente` y `Director Comercial`:
  - Flujo orientado a vistas de gerencia.
  - Existe implementacion de vistas y plantillas, con una limitacion actual en routing (ver abajo).

## Rutas principales
- `/` -> login.
- `/accounts/login/` -> login.
- `/accounts/logout/` -> logout.
- `/redirigir/` -> redireccion segun rol.
- `/comisiones/mis_ventas/` -> ventas del usuario.
- `/comisiones/mis_incidencias/` -> incidencias del usuario.
- `/comisiones/registrar_incidencia/` -> alta de incidencia.
- `/comisiones/mis_incidencias/<id>/` -> detalle incidencia personal.
- `/comisiones/mi_perfil/` -> perfil del usuario.
- `/comisiones/incidencias/` -> incidencias para gerencia.

## Calidad, estado actual y limitaciones
Verificaciones ejecutadas:

- `python manage.py check` -> sin incidencias del sistema.
- `python manage.py test` -> 0 tests detectados.

Limitaciones detectadas en el estado actual:

1. Ruta de comisiones de gerencia no expuesta:
   - `comisiones_gerencia` existe en vistas/plantillas, pero su `path(...)` esta comentado en `comisiones/urls.py`.
   - Se referencia ese nombre de ruta desde plantillas y redireccion por rol.
2. Vistas de gerencia parcialmente mockeadas:
   - `incidencias_gerencia` usa datos estaticos en `comisiones/mock_data.py`.
3. Datos de perfil parcialmente hardcodeados:
   - `mi_perfil` muestra campos de ejemplo (DNI, telefono, organigrama) no persistidos en base de datos.
4. Cobertura automatizada:
   - No hay tests implementados actualmente.
5. Seguridad para entorno productivo:
   - `SECRET_KEY` y `DEBUG` estan definidos para desarrollo en settings base/local.

## Contribucion
Normas y flujo de trabajo en:

- `./.github/CONTRIBUTING.md`
- `./.github/pull_request_template.md`

Resumen:

- Trabajar siempre en ramas (`feature/*`, `fix/*`, `refactor/*`, `hotfix/*`).
- Abrir Pull Request hacia `main`.
- Revisar manualmente cualquier cambio asistido por IA antes de merge.

## Licencia
Distribuido bajo licencia MIT. Ver `LICENSE`.
