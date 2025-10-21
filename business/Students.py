# modelos.py
class Estudiante:
    def __init__(self, nombre, identificacion, carrera, semestre):
        self.nombre = nombre
        self.identificacion = identificacion
        self.carrera = carrera
        self.semestre = semestre

    def __str__(self):
        return f"{self.nombre} ({self.identificacion}) - {self.carrera}, Semestre {self.semestre}"