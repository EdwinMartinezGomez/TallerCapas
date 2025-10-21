

class Curso:
    def __init__(self, codigo, nombre, creditos):
        self.codigo = codigo
        self.nombre = nombre
        self.creditos = creditos

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.creditos} créditos)"
