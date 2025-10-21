# capa_presentacion.py
# Capa de Presentación: interacción con el usuario

from business import AcademicManager

def mostrar_menu():
    print("\n=== SISTEMA ACADÉMICO UPTC ===")
    print("1. Registrar estudiante")
    print("2. Registrar curso")
    print("3. Matricular estudiante")
    print("4. Listar estudiantes")
    print("5. Listar cursos")
    print("6. Listar matrículas")
    print("7. Buscar estudiante por identificación")
    print("0. Salir")

def main():
    gestor = AcademicManager()
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre: ")
            identificacion = input("Identificación: ")
            carrera = input("Carrera: ")
            semestre = input("Semestre: ")
            print(gestor.registrar_estudiante(nombre, identificacion, carrera, semestre))

        elif opcion == "2":
            codigo = input("Código del curso: ")
            nombre = input("Nombre del curso: ")
            creditos = int(input("Créditos: "))
            print(gestor.registrar_curso(codigo, nombre, creditos))

        elif opcion == "3":
            id_est = input("Identificación del estudiante: ")
            cod_curso = input("Código del curso: ")
            print(gestor.matricular_estudiante(id_est, cod_curso))

        elif opcion == "4":
            print("\n Estudiantes registrados:")
            for e in gestor.listar_estudiantes():
                print(e)

        elif opcion == "5":
            print("\n Cursos registrados:")
            for c in gestor.listar_cursos():
                print(c)

        elif opcion == "6":
            print("\n Matrículas registradas:")
            for m in gestor.listar_matriculas():
                print(m)

        elif opcion == "7":
            id_est = input("Ingrese identificación: ")
            est = gestor.buscar_estudiante(id_est)
            print(est if est else "❌ No encontrado.")

        elif opcion == "0":
            print("👋 Saliendo del sistema...")
            break

        else:
            print("Opción no válida, intente nuevamente.")

if __name__ == "__main__":
    main()
