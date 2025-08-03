#Importación de librerías
from dataclasses import dataclass
import re

#Definicion de clase de datos @dataclass
@dataclass
class usuario:
    nombre_completo: str
    edad: int
    direccion: str
    correo: str
    telefono: int

#Creacion de lista para guardar usuarios registrados
usuarios_registrados: list [usuario] = []

#Creación de funcion de menú
def menu_principal():
    print("\n---Menú Principal---")
    print("1. Registrar nuevo usuario ")
    print("2. Ver usuarios registrados ")
    print("3. Salir \n")

#Función para validar correo electrónico 
def correo_valido(correo: str) -> bool:
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

#Función para registrar usuarios
def registar_usuario ():
    print("\n---Registro de usuario---")

    nombre = input("Nombre completo: ")
    
    while True:
        try:
            edad = int(input("Edad: "))
            break
        except ValueError:
            print("Por favor, ingrese números enteros para la edad.")

    direccion = input("Dirección: ")

    while True:
        correo = input("Correo electrónico: ")
        if correo_valido(correo):
            break
        else:
            print("Correo no válido. Asegúrate de que tenga el formato correcto.")

    while True:
        try:
            telefono = int(input("Telefono: "))
            break
        except ValueError:
            print("Por favor, ingrese numeros enteros.")

    nuevo_usuario = usuario(nombre, edad, direccion, correo, telefono)

    usuarios_registrados.append(nuevo_usuario)

    print("Usuario registrado exitosamente.")

#Función para mostrar usuarios registrados
def mostrar_usuarios():
    print("\n--- Usuarios Registrados ---")

    if not usuarios_registrados:
        print("No hay usuarios registrados todavía.")
    else:
        for i, usuario in enumerate(usuarios_registrados, start=1):
            print(f"\nUsuario #{i}")
            print(f"Nombre completo: {usuario.nombre_completo}")
            print(f"Edad: {usuario.edad}")
            print(f"Dirección: {usuario.direccion}")
            print(f"Correo: {usuario.correo}")
            print(f"Telefono: {usuario.telefono}")

#Bucle principal del programa
while True:
    menu_principal()

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        registar_usuario()
    elif opcion == "2":
        mostrar_usuarios()
    elif opcion == "3":
        print("Saliendo del sistema de registro...")
        break
    else:   
        print("Opción no válida. Intente nuevamente.")