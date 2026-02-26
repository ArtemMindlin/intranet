# Intranet - Portal de Comisiones

Aplicacion interna en Django para gestion comercial: ventas, comisiones, incidencias, perfil de usuario y boletines.

## Contenido

1. Resumen funcional
2. Stack tecnico
3. Estructura del proyecto
4. Modelo de datos
5. Autenticacion (login por DNI)
6. Puesta en marcha local
7. Datos demo (seed)
8. Configuracion de email
9. Rutas principales
10. Estado actual y limitaciones

## Resumen funcional

El sistema permite:

- Login con DNI + contrasena.
- Vista `Mis Ventas` con filtros mensuales, ordenacion y detalle comercial.
- Vista `Mis Incidencias` con filtros, detalle y navegacion entre incidencias.
- Registro de nuevas incidencias (generales o asociadas a matriculas del vendedor).
- Perfil de usuario con datos personales y estructura organizativa.
- Modulo `Boletin` y secciones relacionadas (`Normativas`, `Manuales`, `Avisos sin leer`, `Vehiculos en uso`).
- Registro de lectura de boletines al confirmar descarga.
- Vistas de gerencia para comisiones e incidencias.

## Stack tecnico

- Python 3.14
- Django 6.0.2
- SQLite (por defecto en local)
- Plantillas Django + CSS + JS vanilla
- Pillow (imagenes de perfil)

Dependencias: `requirements.txt`.

## Estructura del proyecto

```text
.
|- intranet/
|  |- settings/
|  |  |- base.py
|  |  |- local.py
|  |  |- production.py
|  |  |- __init__.py        # actualmente importa local.py
|  |- urls.py
|- comisiones/
|  |- models.py
|  |- views.py
|  |- forms.py
|  |- auth_backends.py
|  |- admin.py
|  |- urls.py
|  |- management/commands/seed.py
|- templates/
|  |- registration/login.html
|  |- comisiones/*.html
|- static/
|  |- css/*.css
|  |- js/*.js
|  |- img/
|- media/
|- manage.py
```

## Modelo de datos

Modelos principales (`comisiones/models.py`):

- `Venta`
  - Relacionada con `auth.User` (`usuario`)
  - Campos de venta (matricula, idv, tipo, cliente, fecha, etc.)
- `Comision`
  - FK a `Venta`
  - Campos economicos + estado
- `Incidencia`
  - `reportado_por` (User)
  - N:M con `Venta` (`ventas`)
  - Permite incidencias generales (`es_general=True`)
- `Perfil`
  - OneToOne con `auth.User`
  - `dni`, `telefono`, `area`, `concesionario`, `sede`
  - Jerarquia: `jefe_ventas`, `gerente`, `director_comercial`
  - `foto_perfil`
- `Boletin`
  - titulo, fecha, marca, tipo, archivo, activo
- `LecturaBoletin`
  - FK a `Boletin` + FK a `User`
  - marca de lectura (unique por boletin/usuario)

## Autenticacion (login por DNI)

El login se hace por **DNI** (no por username):

- Formulario: `comisiones/forms.py` -> `LoginPorDNIForm`
- Backend de autenticacion: `comisiones/auth_backends.py` -> `DNIAutenticacionBackend`
- Configuracion en settings: `AUTHENTICATION_BACKENDS` en `intranet/settings/base.py`
- Vistas de login: `intranet/urls.py` usando `LoginView(authentication_form=LoginPorDNIForm)`

Importante:

- El usuario debe tener `Perfil.dni` informado para poder iniciar sesion.

## Puesta en marcha local

### Opcion rapida (Windows)

```powershell
.\iniciar_intranet.bat
```

Hace: entorno virtual, dependencias, migraciones, seed opcional, arranque del servidor.

### Opcion manual

1. Crear y activar entorno virtual

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

3. Migrar base de datos

```powershell
python manage.py migrate
```

4. Ejecutar servidor

```powershell
python manage.py runserver
```

Accesos:

- App: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## Datos demo (seed)

Comando:

```powershell
python manage.py seed
```

Opciones:

- `--n-ventas` (default 30)
- `--n-incidencias` (default 10)
- `--reset` (borra y regenera datos demo)

Ejemplos:

```powershell
python manage.py seed --reset
python manage.py seed --n-ventas 50 --n-incidencias 20
```

El seed crea:

- Grupos: `Vendedor`, `Jefe de ventas`, `Gerente`, `Director Comercial`
- Usuarios demo + perfiles con DNI, telefono, area, concesionario, sede y jerarquia
- Ventas + comisiones
- Incidencias
- Boletines + lecturas demo

Credenciales demo:

- DNI vendedor 1: `70000005E`
- Password: `Demo12345!`

(Tambien existen `70000006F`, `70000007G`, etc. segun usuarios seed).

## Configuracion de email

En local se usa `intranet/settings/local.py`.

Configuracion actual:

- SMTP host: `mail.grupomarcos.com`
- Puerto: `25`
- Sin TLS/SSL
- From por defecto: `noresponder@grupomarcos.com`
- Destino incidencias: `INCIDENCIAS_EMAIL_TO` (actualmente correo de pruebas)

La funcion de envio se ejecuta al registrar incidencia:

- `comisiones/views.py` -> `_enviar_correo_nueva_incidencia`

## Rutas principales

- `/` -> login
- `/accounts/login/` -> login
- `/accounts/logout/` -> logout
- `/redirigir/` -> redireccion por rol
- `/comisiones/` -> comisiones gerencia
- `/comisiones/mis_ventas/`
- `/comisiones/mis_incidencias/`
- `/comisiones/mis_incidencias/<id>/`
- `/comisiones/registrar_incidencia/`
- `/comisiones/mi_perfil/`
- `/comisiones/boletin/`
- `/comisiones/mis_comunicaciones/`
- `/comisiones/normativas/`
- `/comisiones/manuales/`
- `/comisiones/avisos_sin_leer/`
- `/comisiones/vehiculos_en_uso/`
- `/comisiones/incidencias/` (gerencia)

## Estado actual y limitaciones

- `python manage.py check` pasa sin errores.
- `comisiones/tests.py` existe pero no hay suite de tests implementada.
- `intranet/settings/production.py` esta como plantilla (pendiente de completar para despliegue real).
- Para login por DNI, si un perfil no tiene DNI informado, ese usuario no podra autenticarse.

