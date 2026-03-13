import json
import os
# LIBRERÍAS NUEVAS NECESARIAS
from PIL import Image      # Para manipular y mostrar la imagen
import requests            # Para descargar la imagen si es una URL
from io import BytesIO     # Para convertir la descarga en algo que PIL pueda leer

# CONSTANTES
NOMBRE_FICHERO = "animes.txt"

# --- UTILIDADES VISUALES ---
def limpiar_pantalla():
    """Limpia la consola según el sistema operativo (opcional, ayuda a la visualización)."""
    # Si prefieres ver el historial, comenta la siguiente línea:
    # os.system('cls' if os.name == 'nt' else 'clear') 
    pass 

def imprimir_encabezado_seccion(titulo):
    """Imprime un título bonito y centrado con bordes."""
    ancho = 80
    print("\n" + "╔" + "═" * (ancho - 2) + "╗")
    print(f"║ {titulo.center(ancho - 4)} ║")
    print("╚" + "═" * (ancho - 2) + "╝")

def imprimir_separador(ancho=80):
    print("─" * ancho)

# --- LÓGICA DE DATOS ---

def cargar_datos():
    """ Lee el fichero de texto y convierte JSON a lista. """
    if not os.path.exists(NOMBRE_FICHERO):
        return []
    try:
        with open(NOMBRE_FICHERO, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def guardar_datos(datos):
    """ Escribe la lista en formato JSON. """
    try:
        with open(NOMBRE_FICHERO, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error al guardar los datos: {e}")

def generar_id(datos):
    if not datos:
        return 1
    return max(anime['id'] for anime in datos) + 1

# --- FUNCIONES PRINCIPALES ---

def guardar_anime():
    imprimir_encabezado_seccion("NUEVO ANIME")
    datos = cargar_datos()
    
    print("Por favor, introduce los datos del nuevo registro:")
    imprimir_separador(50)
    
    nombre = input("   » Nombre del anime: ")
    autor = input("   » Nombre del autor: ")
    fecha = input("   » Fecha de lanzamiento (ej. 2023): ")
    
    while True:
        try:
            capitulos = int(input("   » Cantidad de capítulos: "))
            break
        except ValueError:
            print("   [!] Por favor, introduce un número entero.")

    print("\n   [Nota] Puedes poner una URL (http...) o una ruta local.")
    imagen = input("   » URL o Ruta de la imagen: ")

    nuevo_anime = {
        "id": generar_id(datos),
        "nombre": nombre,
        "autor": autor,
        "fecha": fecha,
        "capitulos": capitulos,
        "imagen": imagen,
        "puntuacion": None,
        "en_lista_espera": False
    }

    datos.append(nuevo_anime)
    guardar_datos(datos)
    print("\n" + "═"*50)
    print(f" ✅ ¡'{nombre}' guardado correctamente (ID: {nuevo_anime['id']})!")
    print("═"*50)

def ver_catalogo(datos_filtrados=None):
    """ 
    Muestra la tabla. Si se le pasa 'datos_filtrados', muestra esos.
    Si no, carga todos los datos del archivo.
    """
    
    # Si no nos pasan una lista específica, cargamos todo
    if datos_filtrados is None:
        imprimir_encabezado_seccion("CATÁLOGO COMPLETO")
        datos = cargar_datos()
    else:
        # Si ya viene filtrado (ej. lista de espera), no imprimimos el encabezado grande aquí
        datos = datos_filtrados

    if not datos:
        print("\n [!] No hay animes para mostrar en esta lista.")
        return

    # DEFINICIÓN DE ANCHOS DE COLUMNA PARA LA TABLA
    w_id, w_nom, w_aut, w_cap, w_fec, w_pun, w_est = 4, 25, 15, 6, 6, 6, 12
    
    # LÍNEAS SEPARADORAS
    linea_borde = f"+{'-'*(w_id+2)}+{'-'*(w_nom+2)}+{'-'*(w_aut+2)}+{'-'*(w_cap+2)}+{'-'*(w_fec+2)}+{'-'*(w_pun+2)}+{'-'*(w_est+2)}+"

    # IMPRIMIR CABECERA DE TABLA
    print(linea_borde)
    print(f"| {'ID':^{w_id}} | {'NOMBRE':^{w_nom}} | {'AUTOR':^{w_aut}} | {'CAPS':^{w_cap}} | {'FECHA':^{w_fec}} | {'PUNT':^{w_pun}} | {'ESTADO':^{w_est}} |")
    print(linea_borde)

    for anime in datos:
        # Lógica de estado y puntuación
        if anime['puntuacion'] is not None:
            puntuacion_str = str(anime['puntuacion'])
            estado = "VISTO"
        else:
            puntuacion_str = "-"
            estado = "PENDIENTE"
        
        # Añadir indicador visual si está en lista de espera
        if anime.get('en_lista_espera'):
            estado = "EN ESPERA"

        # IMPRIMIR FILA CON FORMATO FIJO
        # Se recortan textos largos con [:w_nom] para no romper la tabla
        print(f"| {anime['id']:^{w_id}} | {anime['nombre'][:w_nom]:<{w_nom}} | {anime['autor'][:w_aut]:<{w_aut}} | {str(anime['capitulos']):^{w_cap}} | {str(anime['fecha']):^{w_fec}} | {puntuacion_str:^{w_pun}} | {estado:^{w_est}} |")

    # CIERRE DE TABLA
    print(linea_borde)

def puntuar_anime():
    imprimir_encabezado_seccion("PUNTUAR ANIME")
    ver_catalogo() # Muestra la tabla primero
    datos = cargar_datos()
    if not datos: return

    try:
        print("\n")
        id_buscado = int(input(" » Introduce el ID del anime a puntuar: "))
    except ValueError:
        print(" [!] El ID debe ser un número.")
        return

    encontrado = False
    for anime in datos:
        if anime['id'] == id_buscado:
            print(f"   Seleccionado: {anime['nombre']}")
            while True:
                try:
                    nota = float(input(f"   » ¿Qué nota le das? (1-10): "))
                    if 1 <= nota <= 10:
                        anime['puntuacion'] = nota
                        encontrado = True
                        break
                    else:
                        print("   [!] La nota debe estar entre 1 y 10.")
                except ValueError:
                    print("   [!] Introduce un número válido.")
            break
    

    if encontrado:
        guardar_datos(datos)
        print(f"\n ✅ ¡Puntuación guardada! '{anime['nombre']}' ahora tiene un {anime['puntuacion']}.")
    else:
        print("\n ❌ No se encontró ningún anime con ese ID.")

# --- NUEVA FUNCIÓN: VER SOLO LISTA DE ESPERA ---
def ver_lista_espera():
    imprimir_encabezado_seccion("TU LISTA DE ESPERA")
    datos = cargar_datos()
    # Filtramos solo los que tienen en_lista_espera = True
    en_espera = [anime for anime in datos if anime.get('en_lista_espera') is True]
    
    if not en_espera:
        print("\n (Tu lista de espera está vacía)")
    else:
        # Reutilizamos la lógica de impresión pasándole la lista filtrada
        ver_catalogo(datos_filtrados=en_espera)

# --- FUNCIÓN MODIFICADA: MINI MENÚ AÑADIR/ELIMINAR ---
def gestionar_lista_espera():
    while True:
        # Caja del sub-menú
        print("\n")
        print("┌────────────────────────────────────────┐")
        print("│       GESTIÓN DE LISTA DE ESPERA       │")
        print("├────────────────────────────────────────┤")
        print("│  1. [+] Añadir a la lista              │")
        print("│  2. [-] Eliminar de la lista           │")
        print("│  3. [<-] Volver al menú principal      │")
        print("└────────────────────────────────────────┘")
        
        opcion = input(" » Elige una opción: ")

        if opcion == "3":
            break # Sale del bucle y vuelve al menú principal
        
        datos = cargar_datos()
        if not datos:
            print(" [!] No hay animes registrados para gestionar.")
            continue

        if opcion == "1":
            print("\n --- SELECCIONA PARA AÑADIR ---")
            ver_catalogo(datos) # Mostramos todo para que elija
            try:
                id_buscado = int(input("\n » ID del anime a AÑADIR: "))
                encontrado = False
                for anime in datos:
                    if anime['id'] == id_buscado:
                        anime['en_lista_espera'] = True
                        print(f" ✅ '{anime['nombre']}' AÑADIDO a la lista de espera.")
                        encontrado = True
                        break
                if encontrado:
                    guardar_datos(datos)
                else:
                    print(" [!] ID no encontrado.")
            except ValueError:
                print(" [!] Error: El ID debe ser un número.")

        elif opcion == "2":
            print("\n --- SELECCIONA PARA ELIMINAR ---")
            # Mostramos solo la lista de espera para facilitar la visión
            en_espera = [a for a in datos if a.get('en_lista_espera')]
            if not en_espera:
                print(" [!] La lista de espera ya está vacía.")
            else:
                ver_catalogo(en_espera)
                try:
                    id_buscado = int(input("\n » ID del anime a ELIMINAR de la lista: "))
                    encontrado = False
                    for anime in datos:
                        if anime['id'] == id_buscado:
                            if anime['en_lista_espera']:
                                anime['en_lista_espera'] = False
                                print(f" 🗑️  '{anime['nombre']}' ELIMINADO de la lista de espera.")
                                encontrado = True
                            else:
                                print(" [!] Ese anime no estaba en la lista de espera.")
                            break
                    if encontrado:
                        guardar_datos(datos)
                    else:
                        print(" [!] ID no encontrado.")
                except ValueError:
                    print(" [!] Error: El ID debe ser un número.")
        else:
            print(" [!] Opción no válida.")

def ver_portada_anime():
    imprimir_encabezado_seccion("VISOR DE PORTADAS")
    ver_catalogo()
    datos = cargar_datos()
    if not datos: return

    try:
        print("\n")
        id_buscado = int(input(" » Introduce el ID para ver su imagen: "))
    except ValueError:
        print(" [!] El ID debe ser numérico.")
        return

    anime_encontrado = None
    for anime in datos:
        if anime['id'] == id_buscado:
            anime_encontrado = anime
            break
    
    if anime_encontrado:
        ruta = anime_encontrado['imagen']
        print(f" Cargando imagen de: {anime_encontrado['nombre']}...")
        
        try:
            img = None
            if ruta.startswith("http"):
                respuesta = requests.get(ruta, stream=True)
                respuesta.raise_for_status()
                img = Image.open(BytesIO(respuesta.content))
            else:
                if os.path.exists(ruta):
                    img = Image.open(ruta)
                else:
                    print(" ❌ Error: El archivo no existe en esa ruta.")
                    return

            if img:
                print(" >> Abriendo visor de imágenes...")
                img.show()
                
        except Exception as e:
            print(f" ❌ Error al abrir la imagen: {e}")
            print("    Asegúrate de que la URL es directa a una imagen (.jpg / .png)")

    else:
        print(" ❌ ID no encontrado.")

def menu_principal():
    while True:
        print("\n" + "="*150)
        print("\t  /$$$$$$            /$$                               /$$      /$$                                                           ")
        print("\t /$$__  $$          |__/                              | $$$    /$$$                                                            ")
        print("\t| $$  \ $$ /$$$$$$$  /$$ /$$$$$$/$$$$   /$$$$$$       | $$$$  /$$$$  /$$$$$$  /$$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$ ")
        print("\t| $$$$$$$$| $$__  $$| $$| $$_  $$_  $$ /$$__  $$      | $$ $$/$$ $$ |____  $$| $$__  $$ |____  $$ /$$__  $$ /$$__  $$ /$$__  $$")
        print("\t| $$__  $$| $$  \ $$| $$| $$ \ $$ \ $$| $$$$$$$$      | $$  $$$| $$  /$$$$$$$| $$  \ $$  /$$$$$$$| $$  \ $$| $$$$$$$$| $$  \__/")
        print("\t| $$  | $$| $$  | $$| $$| $$ | $$ | $$| $$_____/      | $$\  $ | $$ /$$__  $$| $$  | $$ /$$__  $$| $$  | $$| $$_____/| $$      ")
        print("\t| $$  | $$| $$  | $$| $$| $$ | $$ | $$|  $$$$$$$      | $$ \/  | $$|  $$$$$$$| $$  | $$|  $$$$$$$|  $$$$$$/|  $$$$$$$| $$      ")
        print("\t|__/  |__/|__/  |__/|__/|__/ |__/ |__/ \_______/      |__/     |__/ \_______/|__/  |__/ \_______/ \____  $$ \_______/|__/      ")  
        print("\t                                                                                                  /$$  \ $$                    ") 
        print("\t                                                                                                 |  $$$$$$/                    ")
        print("\t                                                                                                  \______/                     ")
        print("="*150) 
        
        # MENU ENCUADRADO
        print(" ╔════════════════════════════════════════════════════╗")
        print(" ║                 MENÚ PRINCIPAL                     ║")
        print(" ╠════════════════════════════════════════════════════╣")
        print(" ║  1. 💾  Guardar nuevo anime                        ║")
        print(" ║  2. 📋  Ver catálogo completo                      ║")
        print(" ║  3. ⭐  Puntuar anime                              ║")
        print(" ║  4. 📌  Gestionar Lista de Espera (Añadir/Borrar)  ║")
        print(" ║  5. ⏳  Ver SOLO Lista de Espera                   ║")
        print(" ║  6. 🖼️   Ver portada de un anime                    ║")
        print(" ║  7. 🚪  Salir                                      ║")
        print(" ╚════════════════════════════════════════════════════╝")
        
        opcion = input("\n » Selecciona una opción: ")

        if opcion == "1":
            guardar_anime()
        elif opcion == "2":
            ver_catalogo()
        elif opcion == "3":
            puntuar_anime()
        elif opcion == "4":
            gestionar_lista_espera() # Ahora lleva al sub-menú
        elif opcion == "5":
            ver_lista_espera()       # Nueva función
        elif opcion == "6":
            ver_portada_anime()
        elif opcion == "7":
            print("\n ¡Sayonara! Cerrando gestor... 👋")
            break
        else:
            print(" [!] Opción no válida, intenta de nuevo.")
        
        input("\nPresiona ENTER para continuar...") # Pausa para leer antes de redibujar menú

if __name__ == "__main__":
    menu_principal()


