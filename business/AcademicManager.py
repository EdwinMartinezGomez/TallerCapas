# capa_negocio.py
from business import Students, Courses
from data import RepositoryStudents, RepositoryCourses, RepositoryEnRoll

class AcademicManager:
    def __init__(self):
        self.repo_estudiantes = RepositoryStudents()
        self.repo_cursos = RepositoryCourses()
        self.repo_matriculas = RepositoryEnRoll()

    def registrar_estudiante(self, nombre, identificacion, carrera, semestre):
        if self.repo_estudiantes.buscar(identificacion):
            return "⚠️ El estudiante ya existe."
        est = Students(nombre, identificacion, carrera, semestre)
        self.repo_estudiantes.guardar(est)
        return "✅ Estudiante registrado con éxito."

    def registrar_curso(self, codigo, nombre, creditos):
        if self.repo_cursos.buscar(codigo):
            return "⚠️ El curso ya existe."
        curso = Courses(codigo, nombre, creditos)
        self.repo_cursos.guardar(curso)
        return "✅ Curso registrado con éxito."

    def matricular_estudiante(self, identificacion, codigo_curso):
        est = self.repo_estudiantes.buscar(identificacion)
        if not est:
            return "❌ Estudiante no encontrado."
        curso = self.repo_cursos.buscar(codigo_curso)
        if not curso:
            return "❌ Curso no encontrado."
        self.repo_matriculas.guardar(identificacion, codigo_curso)
        return "✅ Matrícula registrada correctamente."

    def listar_estudiantes(self):
        return self.repo_estudiantes.listar()

    def listar_cursos(self):
        return self.repo_cursos.listar()

    def listar_matriculas(self):
        return self.repo_matriculas.listar()
