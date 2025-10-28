# TallerCapas

Sistema académico sencillo con separación de capas (presentación / negocio / datos) y una capa de autenticación añadida. Permite registrar estudiantes, cursos y matrículas, además de gestionar usuarios del sistema con control por roles.

## Resumen
- Lenguaje: Python 3.x
- Persistencia: SQLite (archivo `tallercapas.db` en la raíz del proyecto)
- Capas:
	- `presentation/` — Interfaz de línea de comandos (`App.py`, arranque via `run.py`)
	- `business/` — Lógica de negocio (`AcademicManager.py`, modelos en `Students.py`, `Courses.py`, `User.py`)
	- `data/` — Repositorios y acceso a BD (`RepositoryStudents.py`, `RepositoryCourses.py`, `RepositoryEnRoll.py`, `RepositoryUsers.py`, `database.py`)
	- `auth/` — Capa de autenticación y autorización (`AuthManager.py`)

## Características implementadas
- Registro y listado de estudiantes y cursos.
- Matriculación de estudiantes en cursos.
- Persistencia con SQLite (tablas: `students`, `courses`, `enrollments`, `users`, `login_attempts`).
- Registro de usuarios del sistema (username, contraseña hasheada, role).
- Inicio de sesión con credenciales.
- Control por rol: solo usuarios con `role == 'admin'` pueden registrar cursos o crear usuarios desde el menú principal.
- Registro de intentos de inicio de sesión (tabla `login_attempts` + archivo de log `auth.log`).
- Contraseñas almacenadas con PBKDF2-HMAC-SHA256 + salt + iteraciones (no texto plano).
- Primer usuario (bootstrap) puede crearse como `admin` desde el flujo de autenticación cuando la BD está vacía.

## Archivos clave (lo añadido/modificado)
- `run.py` — Launcher desde la raíz (ejecuta la app correctamente con importaciones de paquete).
- `presentation/App.py` — Interfaz CLI, ahora exige autenticación; permite registro desde el login.
- `business/AcademicManager.py` — Lógica de negocio (usa repositorios).
- `business/Students.py`, `business/Courses.py`, `business/User.py` — Modelos.
- `data/database.py` — Inicializa la BD y crea tablas si no existen.
- `data/RepositoryStudents.py`, `data/RepositoryCourses.py`, `data/RepositoryEnRoll.py` — Repositorios migrados a SQLite.
- `data/RepositoryUsers.py` — Repositorio para usuarios y registro de intentos.
- `data/auth_test.py` — Script de pruebas de autenticación (crea admin si no existen usuarios, prueba login correcto/fallido y muestra últimos intentos).
- `auth/AuthManager.py` — Registro/login, control de sesión, wrappers de autorización.
- `auth/auth.log` (creado en tiempo de ejecución) — Registro de eventos de autenticación.
- `tallercapas.db` — (se crea en la raíz cuando se ejecuta la app por primera vez).

## Cómo ejecutar (Windows, cmd)
1. Abre un terminal en la raíz del proyecto (la carpeta que contiene `run.py`).
2. Ejecuta la aplicación:
	 ```cmd
	 python run.py
	 ```
	 - Al iniciar verás el menú de autenticación:
		 - `2` Registrarse — si la BD no tiene usuarios el primer usuario se creará como `admin`.
		 - `1` Iniciar sesión — una vez registrado, accede con esas credenciales.
3. Desde el menú principal (después de iniciar sesión) puedes:
	 - Registrar estudiantes, cursos (solo admin), matricular, listar, etc.

## Comandos útiles para pruebas rápidas
- Ejecutar script de pruebas de autenticación (crea admin si no hay usuarios, prueba login correcto/fallido y muestra últimos intentos):
	```cmd
	python data\auth_test.py
	```
- Ejecutar prueba de inserción/listado básica de estudiantes/cursos/matrículas:
	```cmd
	python data\db_test.py
	```
- Eliminar/resetear la base de datos:
	- Cierra la aplicación y borra `tallercapas.db` en la raíz del proyecto.
	- Al ejecutar la app de nuevo se recreará con las tablas.

## Detalles de seguridad implementados
- Confidencialidad: 
	- Las contraseñas se guardan con PBKDF2-HMAC-SHA256 con salt y 100000 iteraciones.
	- En BD se almacena un valor con formato `iterations$salt$hexhash`.
- Autorización:
	- Verificación de roles expuesta a la presentación vía `AuthManager.has_role`.
	- Política actual: la presentación (UI) verifica `has_role('admin')` antes de permitir registrar cursos o crear usuarios desde el menú principal.
	- (Nota) La autorización se gestiona en la capa de autenticación/presentación tal como pediste; la capa de negocio sigue siendo sin estado en cuanto a roles.
- Trazabilidad:
	- Todos los intentos de login (éxito/fracaso) se registran en la tabla `login_attempts` y en `auth.log`.
	- `auth.log` se encuentra en la raíz del proyecto y contiene entradas con timestamp.

## Arquitectura 
Representación simple de capas (ASCII):

Presentation (CLI)
	↕ uses
Auth (AuthManager)  — autentica/autoriza, registra intentos
	↕ calls
Business (AcademicManager)
	↕ uses
Data (Repository* / SQLite)

- La capa de `Auth` actúa como puerta de entrada; la presentación solicita autenticación y delega operaciones autorizadas al `AcademicManager`.
