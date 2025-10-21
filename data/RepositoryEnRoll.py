class RepositoryEnroll:
    def __init__(self):
        self.matriculas = []

    def guardar(self, estudiante_id, curso_codigo):
        self.matriculas.append((estudiante_id, curso_codigo))

    def listar(self):
        return self.matriculas