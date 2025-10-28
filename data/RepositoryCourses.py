from business.Courses import Curso
from .database import get_connection, init_db

class RepositoryCourses:
    def __init__(self, db_path=None):
        self.db_path = db_path
        init_db(self.db_path)

    def guardar(self, curso: Curso):
        conn = get_connection(self.db_path)
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO courses (codigo, nombre, creditos) VALUES (?,?,?)",
                (curso.codigo, curso.nombre, curso.creditos),
            )
        conn.close()

    def listar(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT codigo, nombre, creditos FROM courses").fetchall()
        conn.close()
        return [Curso(*row) for row in rows]

    def buscar(self, codigo):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT codigo, nombre, creditos FROM courses WHERE codigo = ?", (codigo,)
        ).fetchone()
        conn.close()
        if row:
            return Curso(*row)
        return None

