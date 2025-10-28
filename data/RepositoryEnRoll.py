from .database import get_connection, init_db

class RepositoryEnroll:
    def __init__(self, db_path=None):
        self.db_path = db_path
        init_db(self.db_path)

    def guardar(self, estudiante_id, curso_codigo):
        conn = get_connection(self.db_path)
        with conn:
            conn.execute(
                "INSERT INTO enrollments (estudiante_identificacion, curso_codigo) VALUES (?,?)",
                (estudiante_id, curso_codigo),
            )
        conn.close()

    def listar(self):
        conn = get_connection(self.db_path)
        rows = conn.execute(
            "SELECT estudiante_identificacion, curso_codigo, created_at FROM enrollments"
        ).fetchall()
        conn.close()
        return rows