from business.Students import Estudiante
from .database import get_connection, init_db

class RepositoryStudents:
    def __init__(self, db_path=None):
        self.db_path = db_path
        init_db(self.db_path)

    def guardar(self, estudiante: Estudiante):
        conn = get_connection(self.db_path)
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO students (nombre, identificacion, carrera, semestre) VALUES (?,?,?,?)",
                (estudiante.nombre, estudiante.identificacion, estudiante.carrera, estudiante.semestre),
            )
        conn.close()

    def listar(self):
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        rows = cur.execute("SELECT nombre, identificacion, carrera, semestre FROM students").fetchall()
        conn.close()
        return [Estudiante(*row) for row in rows]

    def buscar(self, identificacion):
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        row = cur.execute(
            "SELECT nombre, identificacion, carrera, semestre FROM students WHERE identificacion = ?",
            (identificacion,),
        ).fetchone()
        conn.close()
        if row:
            return Estudiante(*row)
        return None

