# capa_datos.py
from business import Students, Courses

class RepositoryStudents:
    def __init__(self):
        self.estudiantes = []

    def guardar(self, estudiante: Students):
        self.estudiantes.append(estudiante)

    def listar(self):
        return self.estudiantes

    def buscar(self, identificacion):
        for e in self.estudiantes:
            if e.identificacion == identificacion:
                return e
        return None

