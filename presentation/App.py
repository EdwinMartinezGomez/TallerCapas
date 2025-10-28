from auth import AuthManager
from business.AcademicManager import AcademicManager
from data.RepositoryUsers import RepositoryUsers


def mostrar_menu():
    print("\n=== SISTEMA ACADÉMICO UPTC ===")
    print("1. Registrar estudiante")
    print("2. Registrar curso")
    print("3. Matricular estudiante")
    print("4. Listar estudiantes")
    print("5. Listar cursos")
    print("6. Listar matrículas")
    print("7. Registrar usuario (solo admin)")
    print("0. Salir")


def main():
    auth = AuthManager()
    am = AcademicManager()
    repo_users = RepositoryUsers()

    print("Bienvenido.")

    # Login / Register menu
    while True:
        print("\n--- Autenticación ---")
        print("1) Iniciar sesión")
        print("2) Registrarse")
        print("0) Salir")
        opt = input("Seleccione una opción: ")
        if opt == "0":
            print("Saliendo...")
            return
        if opt == "1":
            username = input("Usuario: ")
            password = input("Contraseña: ")
            ok, result = auth.login(username, password)
            if ok:
                print(f"Bienvenido {result.username} (rol={result.role})")
                break
            else:
                print(result)
                continue
        if opt == "2":
            username = input("Nuevo usuario: ")
            password = input("Contraseña: ")
            # If no users exist allow creating admin; otherwise self-register as 'user'
            if not repo_users.any_users_exist():
                print("No existen usuarios en el sistema. Este usuario será creado como admin (bootstrap).")
                role = 'admin'
            else:
                print("Se creará un usuario con rol 'user'. Si necesita un admin, pida a un admin existente que lo cree.")
                role = 'user'
            okc, msgc = auth.register_user(username, password, role=role)
            print(msgc)
            if okc:
                print("Ahora puede iniciar sesión con estas credenciales.")
            continue
        print("Opción inválida.")

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre: ")
            identificacion = input("Identificación: ")
            carrera = input("Carrera: ")
            semestre = input("Semestre: ")
            print(am.registrar_estudiante(nombre, identificacion, carrera, semestre))

        elif opcion == "2":
            codigo = input("Código del curso: ")
            nombre = input("Nombre del curso: ")
            creditos = input("Créditos: ")
            # Only admins can register courses (authorization enforced by auth layer)
            if not auth.has_role('admin'):
                print('Acceso denegado. Se requiere rol admin para registrar cursos.')
            else:
                print(am.registrar_curso(codigo, nombre, creditos))

        elif opcion == "3":
            id_est = input("Identificación del estudiante: ")
            cod_curso = input("Código del curso: ")
            print(am.matricular_estudiante(id_est, cod_curso))

        elif opcion == "4":
            print("\n Estudiantes:")
            for e in am.listar_estudiantes():
                print(f" - {e}")

        elif opcion == "5":
            print("\n Cursos:")
            for c in am.listar_cursos():
                print(f" - {c}")

        elif opcion == "6":
            print("\n Matrículas:")
            for m in am.listar_matriculas():
                print(f" - Estudiante ID: {m[0]}, Curso: {m[1]}")

        elif opcion == "7":
            usuario = input("Nuevo usuario: ")
            clave = input("Contraseña: ")
            role = input("Rol (admin/user): ")
            if not auth.has_role('admin'):
                print('Acceso denegado. Se requiere rol admin para registrar usuarios.')
            else:
                ok, msg = auth.register_user(usuario, clave, role=role)
                print(msg)

        elif opcion == "0":
            print(" Saliendo del sistema...")
            break

        else:
            print(" Opción no válida.")


if __name__ == "__main__":
    main()
