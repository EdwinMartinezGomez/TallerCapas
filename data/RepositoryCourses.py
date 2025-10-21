from business import Courses

class RepositoryCourses:
    def __init__(self):
        self.cursos = []

    def guardar(self, curso: Courses):
        self.cursos.append(curso)

    def listar(self):
        return self.cursos

    def buscar(self, codigo):
        for c in self.cursos:
            if c.codigo == codigo:
                return c
        return None

