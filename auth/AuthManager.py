import os
import hashlib
import hmac
import binascii
import logging
from pathlib import Path

from data.RepositoryUsers import RepositoryUsers
from business.User import User

LOG_FILE = str(Path(__file__).resolve().parent.parent / "auth.log")

# Configure logging for auth events (file + console)
logger = logging.getLogger("tallercapas.auth")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)
"""
AuthManager implementation (single coherent class).

We expose the class `AuthService` here and keep a package-level alias in
`auth.__init__` so the rest of the code can continue importing `AuthManager`.
"""
import os
import hashlib
import hmac
import binascii
import logging
from pathlib import Path

from data.RepositoryUsers import RepositoryUsers
from business.User import User

LOG_FILE = str(Path(__file__).resolve().parent.parent / "auth.log")

# Configure logging for auth events (file + console)
logger = logging.getLogger("tallercapas.auth")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)


def _generate_salt(length=16):
    return binascii.hexlify(os.urandom(length)).decode()


def _hash_password(password: str, salt: str, iterations: int = 100_000):
    # PBKDF2-HMAC-SHA256
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"{iterations}${salt}${binascii.hexlify(dk).decode()}"


def _verify_password(stored_hash: str, password: str) -> bool:
    try:
        parts = stored_hash.split("$")
        iterations = int(parts[0])
        salt = parts[1]
        expected = parts[2]
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
        return hmac.compare_digest(binascii.hexlify(dk).decode(), expected)
    except Exception:
        return False


class AuthService:
    """Authentication manager: register/login/logout/role checks and thin wrappers.

    Methods:
    - any_users_exist()
    - register_user(username, password, role)
    - login(username, password) -> (bool, User|str)
    - logout()
    - is_authenticated(), has_role(role)
    - require_authentication()
    - registrar_* wrappers that call AcademicManager when authenticated
    """

    def __init__(self, db_path=None):
        self.repo = RepositoryUsers(db_path)
        self.current_user = None
        # lazy import to avoid circular imports at module import time
        from business.AcademicManager import AcademicManager

        self.manager = AcademicManager()

    def any_users_exist(self):
        return self.repo.any_users_exist()

    def register_user(self, username: str, password: str, role: str = "user"):
        if self.repo.get_by_username(username):
            return False, "El usuario ya existe."
        salt = _generate_salt()
        password_hash = _hash_password(password, salt)
        try:
            self.repo.create(username, password_hash, salt, role)
            logger.info(f"Usuario registrado: {username} rol={role}")
            return True, "Usuario registrado correctamente."
        except Exception as e:
            logger.exception("Error al registrar usuario")
            return False, str(e)

    def login(self, username: str, password: str):
        record = self.repo.get_by_username(username)
        if not record:
            logger.warning(f"Login fallido: usuario no encontrado '{username}'")
            self.repo.log_login_attempt(username, False, "usuario_no_encontrado")
            return False, "Usuario no encontrado."

        stored_hash = record.get("password_hash")
        if _verify_password(stored_hash, password):
            self.current_user = User(username, record.get("role"))
            logger.info(f"Login exitoso: {username}")
            self.repo.log_login_attempt(username, True, "ok")
            return True, self.current_user
        else:
            logger.warning(f"Login fallido: credenciales incorrectas '{username}'")
            self.repo.log_login_attempt(username, False, "credenciales_incorrectas")
            return False, "Credenciales incorrectas."

    def logout(self):
        if self.current_user:
            logger.info(f"Logout: {self.current_user.username}")
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None

    def has_role(self, role: str):
        return self.current_user is not None and self.current_user.role == role

    def require_authentication(self):
        if not self.is_authenticated():
            return False, 'Usuario no autenticado'
        return True, None

    # Wrapper methods that enforce authentication/authorization before calling business
    def registrar_estudiante(self, nombre, identificacion, carrera, semestre):
        ok, msg = self.require_authentication()
        if not ok:
            return '❌ Acceso denegado. Inicie sesión.'
        return self.manager.registrar_estudiante(nombre, identificacion, carrera, semestre)

    def registrar_curso(self, codigo, nombre, creditos):
        ok, msg = self.require_authentication()
        if not ok:
            return '❌ Acceso denegado. Inicie sesión.'
        if not self.has_role('admin'):
            return '❌ Acceso denegado. Se requiere rol admin.'
        return self.manager.registrar_curso(codigo, nombre, creditos)

    def matricular_estudiante(self, identificacion, codigo_curso):
        ok, msg = self.require_authentication()
        if not ok:
            return '❌ Acceso denegado. Inicie sesión.'
        return self.manager.matricular_estudiante(identificacion, codigo_curso)

    def listar_estudiantes(self):
        ok, msg = self.require_authentication()
        if not ok:
            return []
        return self.manager.listar_estudiantes()

    def listar_cursos(self):
        ok, msg = self.require_authentication()
        if not ok:
            return []
        return self.manager.listar_cursos()

    def listar_matriculas(self):
        ok, msg = self.require_authentication()
        if not ok:
            return []
        return self.manager.listar_matriculas()



def _generate_salt(length=16):
    return binascii.hexlify(os.urandom(length)).decode()


def _hash_password(password: str, salt: str, iterations: int = 100_000):
    # PBKDF2-HMAC-SHA256
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"{iterations}${salt}${binascii.hexlify(dk).decode()}"


def _verify_password(stored_hash: str, password: str) -> bool:
    try:
        parts = stored_hash.split("$")
        iterations = int(parts[0])
        salt = parts[1]
        expected = parts[2]
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
        return hmac.compare_digest(binascii.hexlify(dk).decode(), expected)
    except Exception:
        return False


class AuthManager:
    """Authentication manager: register/login/logout/role checks.

    Responsibilities:
    - Register users (stores salted PBKDF2 hash)
    - Authenticate credentials and set current_user (business.User)
    - Expose is_authenticated() and has_role() for presentation to enforce authorization
    - Log attempts to DB via RepositoryUsers and to file/console for traceability
    """

    def __init__(self, db_path=None):
        self.repo = RepositoryUsers(db_path)
        self.current_user = None

    def any_users_exist(self):
        return self.repo.any_users_exist()

    def register_user(self, username: str, password: str, role: str = "user"):
        if self.repo.get_by_username(username):
            return False, "El usuario ya existe."
        salt = _generate_salt()
        password_hash = _hash_password(password, salt)
        try:
            self.repo.create(username, password_hash, salt, role)
            logger.info(f"Usuario registrado: {username} rol={role}")
            return True, "Usuario registrado correctamente."
        except Exception as e:
            logger.exception("Error al registrar usuario")
            return False, str(e)

    def login(self, username: str, password: str):
        record = self.repo.get_by_username(username)
        if not record:
            logger.warning(f"Login fallido: usuario no encontrado '{username}'")
            self.repo.log_login_attempt(username, False, "usuario_no_encontrado")
            return False, "Usuario no encontrado."

        stored_hash = record.get("password_hash")
        if _verify_password(stored_hash, password):
            self.current_user = User(username, record.get("role"))
            logger.info(f"Login exitoso: {username}")
            self.repo.log_login_attempt(username, True, "ok")
            return True, self.current_user
        else:
            logger.warning(f"Login fallido: credenciales incorrectas '{username}'")
            self.repo.log_login_attempt(username, False, "credenciales_incorrectas")
            return False, "Credenciales incorrectas."

    def logout(self):
        if self.current_user:
            logger.info(f"Logout: {self.current_user.username}")
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None

    def has_role(self, role: str):
        return self.current_user is not None and self.current_user.role == role

    def require_role(self, role: str):
        if not self.is_authenticated():
            raise PermissionError("Usuario no autenticado")
        if not self.has_role(role):
            raise PermissionError(f"Acceso denegado. Se requiere rol: {role}")
import os
import hashlib
import hmac
import binascii
import logging
from pathlib import Path

from data.RepositoryUsers import RepositoryUsers
from business.User import User

LOG_FILE = str(Path(__file__).resolve().parent.parent / "auth.log")

# Configure logging for auth events (file + console)
logger = logging.getLogger("tallercapas.auth")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)


def _generate_salt(length=16):
    return binascii.hexlify(os.urandom(length)).decode()


def _hash_password(password: str, salt: str, iterations: int = 100_000):
    # PBKDF2-HMAC-SHA256
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"{iterations}${salt}${binascii.hexlify(dk).decode()}"


def _verify_password(stored_hash: str, password: str) -> bool:
    try:
        parts = stored_hash.split("$")
        iterations = int(parts[0])
        salt = parts[1]
        expected = parts[2]
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
        return hmac.compare_digest(binascii.hexlify(dk).decode(), expected)
    except Exception:
        return False


class AuthManager:
    def __init__(self, db_path=None):
        self.repo = RepositoryUsers(db_path)
        self.current_user = None

    def register_user(self, username: str, password: str, role: str = "user"):
        # If no users exist, allow creation without restrictions (bootstrap admin)
        if self.repo.get_by_username(username):
            return False, "El usuario ya existe."
        salt = _generate_salt()
        password_hash = _hash_password(password, salt)
        try:
            self.repo.create(username, password_hash, salt, role)
            logger.info(f"Usuario registrado: {username} rol={role}")
            return True, "Usuario registrado correctamente."
        except Exception as e:
            logger.exception("Error al registrar usuario")
            return False, str(e)



    def registrar_curso(self, codigo, nombre, creditos):
        ok, msg = self.require_authentication()
        if not ok:
            return '❌ Acceso denegado. Inicie sesión.'
        # authorization: only admin role allowed to register courses
        if not self.has_role('admin'):
            return '❌ Acceso denegado. Se requiere rol admin.'
        return self.manager.registrar_curso(codigo, nombre, creditos)

    def matricular_estudiante(self, identificacion, codigo_curso):
        ok, msg = self.require_authentication()
        if not ok:
            return '❌ Acceso denegado. Inicie sesión.'
        return self.manager.matricular_estudiante(identificacion, codigo_curso)

    def listar_estudiantes(self):
        ok, msg = self.require_authentication()
        if not ok:
            return []
        return self.manager.listar_estudiantes()

    def listar_cursos(self):
        ok, msg = self.require_authentication()
        if not ok:
            return []
        return self.manager.listar_cursos()

    def listar_matriculas(self):
        ok, msg = self.require_authentication()
        if not ok:
            return []
        return self.manager.listar_matriculas()
