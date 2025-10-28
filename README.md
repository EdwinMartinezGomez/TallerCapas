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

## Arquitectura (modificada para autenticación)
Representación simple de capas (ASCII):

Presentation (CLI)
	↕ uses
Auth (AuthManager)  — autentica/autoriza, registra intentos
	↕ calls
Business (AcademicManager)
	↕ uses
Data (Repository* / SQLite)

- La capa de `Auth` actúa como puerta de entrada; la presentación solicita autenticación y delega operaciones autorizadas al `AcademicManager`.

## Errores y solución rápida
- ModuleNotFoundError al ejecutar `presentation/App.py` directamente:
	- Ejecuta la app siempre desde la raíz con `python run.py` o con `python -m presentation.App`.
- Si ves `AttributeError: 'AuthManager' object has no attribute 'login'`:
	- Asegúrate de que el archivo `auth/AuthManager.py` contiene la implementación actual (con `login`).
	- Ejecuta el test rápido para comprobar:
		```cmd
		python - <<EOF
		from auth import AuthManager
		a = AuthManager()
		import inspect
		print('has login:', hasattr(a, 'login'))
		EOF
		```
	- Si muestra `False`, reinicia el intérprete (cierra/abre el terminal) para evitar módulos en caché y vuelve a ejecutar.

## Pruebas y validación
- `data/auth_test.py` realiza:
	- Creación de admin si no existen usuarios.
	- Login correcto y login con contraseña incorrecta.
	- Muestra últimos registros de `login_attempts`.
- Recomendación: después de cambios, ejecutar este script y correr manualmente `run.py` para validar flujo interactivo.

## Buenas prácticas / mejoras sugeridas (siguientes pasos)
- Añadir confirmación de contraseña y validación mínima (p. ej. 8+ caracteres) al registro.
- Añadir bloqueo temporal tras N intentos fallidos (throttling) para endurecer seguridad.
- Mover las comprobaciones de autorización a la capa de negocio si quieres doble protección (defensa en profundidad).
- Añadir pruebas unitarias automáticas (pytest) que cubran:
	- Registro de usuarios, login correcto/fallido, creación de estudiantes/cursos, reglas de rol.
- Mejorar la UX del CLI (validaciones, mensajes más claros, menús).
- Añadir migraciones (ej. usar Alembic/SQLAlchemy) si la BD crece en complejidad.

## Contacto / notas finales
- El proyecto ya incluye la mayoría de la infraestructura para autenticación segura y trazabilidad de intentos.
- Si quieres, puedo:
	- Añadir confirmación/validación de contraseñas en el flujo de registro.
	- Implementar bloqueo por intentos fallidos y notificaciones.
	- Convertir la persistencia a SQLAlchemy para migraciones y testing más robusto.
	- Generar un diagrama gráfico (PNG/SVG) de la arquitectura y añadirlo al repo.

¿Quieres que actualice ahora el `README.md` directamente en el repositorio con este contenido y/o que implemente alguna de las mejoras sugeridas (por ejemplo: confirmación de contraseña en el registro)?

Instrucciones rápidas para la base de datos (SQLite)

- El proyecto ahora usa SQLite para persistir estudiantes, cursos y matriculas.
- El archivo de BD por defecto se crea en el directorio raíz con el nombre `tallercapas.db`.

Inicializar y probar:

1. Ejecuta la aplicación de presentación para crear la BD y probar el flujo:

```bash
python presentation\App.py
```

2. El primer uso crea las tablas automáticamente. Registra un estudiante, un curso y una matrícula para verificar.

Si quieres usar una ruta de BD personalizada, puedes modificar los constructores de los repositorios para pasar `db_path`.