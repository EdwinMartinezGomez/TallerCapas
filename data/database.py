import sqlite3
from pathlib import Path

DB_FILENAME = "tallercapas.db"

def _default_db_path():
    # Put DB in the project root (parent of this data folder)
    return str(Path(__file__).resolve().parent.parent / DB_FILENAME)

def get_db_path(path=None):
    return path or _default_db_path()

def get_connection(path=None):
    db_path = get_db_path(path)
    conn = sqlite3.connect(db_path)
    # enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(path=None):
    db_path = get_db_path(path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        identificacion TEXT NOT NULL UNIQUE,
        carrera TEXT,
        semestre INTEGER
    );
    """
    )
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        creditos INTEGER
    );
    """
    )
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_identificacion TEXT NOT NULL,
        curso_codigo TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(estudiante_identificacion) REFERENCES students(identificacion) ON DELETE CASCADE,
        FOREIGN KEY(curso_codigo) REFERENCES courses(codigo) ON DELETE CASCADE
    );
    """
    )
    # Users table for authentication
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    )

    # Optional: table for login attempts (keeps traceability)
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        success INTEGER,
        reason TEXT,
        occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    )
    conn.commit()
    conn.close()
