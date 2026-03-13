import json
import os
import time
# LIBRERÍAS
from PIL import Image      
import requests            
from io import BytesIO     

# CONSTANTES
NOMBRE_FICHERO = "animes.txt"
API_URL = "https://api.jikan.moe/v4/anime"

# --- UTILIDADES VISUALES ---
def imprimir_encabezado_seccion(titulo):
    ancho = 80
    print("\n" + "╔" + "═" * (ancho - 2) + "╗")
    print(f"║ {titulo.center(ancho - 4)} ║")
    print("╚" + "═" * (ancho - 2) + "╝")

def carga_visual(texto):
    """Simula una pequeña carga para dar feedback visual"""
    print(f" ⏳ {texto}", end="", flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print(" ✅")

# --- LÓGICA DE DATOS (LOCAL) ---
def cargar_datos():
    if not os.path.exists(NOMBRE_FICHERO):
        return []
    try:
        with open(NOMBRE_FICHERO, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def guardar_datos(datos):
    try:
        with open(NOMBRE_FICHERO, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error al guardar los datos: {e}")

def generar_id(datos):
    if not datos:
        return 1
    return max(anime['id'] for anime in datos) + 1

# --- NUEVA LÓGICA: API JIKAN ---
def buscar_en_api(nombre_busqueda):
    """
    Busca el anime en Jikan API y devuelve un diccionario con los datos
    o None si falla.
    """
    params = {
        'q': nombre_busqueda,
        'limit': 1  # Solo queremos el primer resultado más relevante
    }
    
    try:
        respuesta = requests.get(API_URL, params=params)
        if respuesta.status_code == 200:
            datos_api = respuesta.json()
            if datos_api['data']:
                item = datos_api['data'][0]
                
                # Extraer datos con seguridad (por si vienen vacíos)
                titulo = item.get('title', 'Desconocido')
                
                # Jikan devuelve estudios, cogemos el primero
                estudios = item.get('studios', [])
                autor = estudios[0]['name'] if estudios else "Desconocido"
                
                # Año (extraer del string de fecha 'aired')
                fecha_completa = item.get('aired', {}).get('prop', {}).get('from', {})
                anio = fecha_completa.get('year')
                fecha = str(anio) if anio else "????"
                
                capitulos = item.get('episodes')
                if capitulos is None: capitulos = 0 # En emisión o desconocido
                
                imagen = item.get('images', {}).get('jpg', {}).get('large_image_url')
                
                return {
                    "nombre": titulo,
                    "autor": autor,
                    "fecha": fecha,
                    "capitulos": capitulos,
                    "imagen": imagen,
                    "sinopsis": item.get('synopsis', '')[:100] + "..." # Opcional
                }
        return None
    except Exception as e:
        print(f" [!] Error de conexión con la API: {e}")
        return None

# --- FUNCIONES PRINCIPALES ---

def guardar_anime():
    imprimir_encabezado_seccion("NUEVO ANIME (BÚSQUEDA AUTOMÁTICA)")
    datos = cargar_datos()
    
    print(" Escribe el nombre y lo buscaremos en la base de datos online.")
    busqueda = input(" » Nombre del anime a buscar: ")
    
    carga_visual("Consultando API de Jikan")
    
    resultado_api = buscar_en_api(busqueda)
    
    if resultado_api:
        print("\n" + "┌" + "─"*50 + "┐")
        print(f"│ HE ENCONTRADO ESTO:")
        print(f"│ 📺 Título:   {resultado_api['nombre']}")
        print(f"│ 🖌️  Estudio:  {resultado_api['autor']}")
        print(f"│ 📅 Año:      {resultado_api['fecha']}")
        print(f"│ 🎞️  Caps:     {resultado_api['capitulos']}")
        print("└" + "─"*50 + "┘")
        
        confirmar = input("\n » ¿Es este el anime correcto? (s/n): ").lower()
        
        if confirmar == 's':
            # Creamos el objeto final mezclando datos API + datos Local
            nuevo_anime = {
                "id": generar_id(datos),
                "nombre": resultado_api['nombre'],
                "autor": resultado_api['autor'],
                "fecha": resultado_api['fecha'],
                "capitulos": resultado_api['capitulos'],
                "imagen": resultado_api['imagen'],
                "puntuacion": None,
                "en_lista_espera": False
            }
            
            datos.append(nuevo_anime)
            guardar_datos(datos)
            print(f"\n ✅ ¡Guardado en 'animes.txt' con ID {nuevo_anime['id']}!")
        else:
            print(" ❌ Cancelado. Intenta ser más específico con el nombre.")
    else:
        print(" ❌ No se encontraron resultados en la API o hubo un error.")
        opcion_manual = input(" ¿Quieres introducirlo manualmente? (s/n): ").lower()
        if opcion_manual == 's':
            # Fallback manual por si la API falla
            nombre = input("   » Nombre: ")
            autor = input("   » Autor/Estudio: ")
            fecha = input("   » Año: ")
            try: capitulos = int(input("   » Capítulos: "))
            except: capitulos = 0
            imagen = input("   » URL Imagen: ")
            
            nuevo_anime = {
                "id": generar_id(datos),
                "nombre": nombre, "autor": autor, "fecha": fecha,
                "capitulos": capitulos, "imagen": imagen,
                "puntuacion": None, "en_lista_espera": False
            }
            datos.append(nuevo_anime)
            guardar_datos(datos)
            print(" ✅ Guardado manualmente.")

def ver_catalogo(datos_filtrados=None):
    if datos_filtrados is None:
        imprimir_encabezado_seccion("CATÁLOGO COMPLETO")
        datos = cargar_datos()
    else:
        datos = datos_filtrados

    if not datos:
        print("\n [!] No hay animes para mostrar.")
        return

    w_id, w_nom, w_aut, w_cap, w_fec, w_pun, w_est = 4, 25, 15, 6, 6, 6, 12
    linea_borde = f"+{'-'*(w_id+2)}+{'-'*(w_nom+2)}+{'-'*(w_aut+2)}+{'-'*(w_cap+2)}+{'-'*(w_fec+2)}+{'-'*(w_pun+2)}+{'-'*(w_est+2)}+"

    print(linea_borde)
    print(f"| {'ID':^{w_id}} | {'NOMBRE':^{w_nom}} | {'ESTUDIO':^{w_aut}} | {'CAPS':^{w_cap}} | {'AÑO':^{w_fec}} | {'PUNT':^{w_pun}} | {'ESTADO':^{w_est}} |")
    print(linea_borde)

    for anime in datos:
        if anime['puntuacion'] is not None:
            puntuacion_str = str(anime['puntuacion'])
            estado = "VISTO"
        else:
            puntuacion_str = "-"
            estado = "PENDIENTE"
        
        if anime.get('en_lista_espera'):
            estado = "EN ESPERA"

        print(f"| {anime['id']:^{w_id}} | {anime['nombre'][:w_nom]:<{w_nom}} | {anime['autor'][:w_aut]:<{w_aut}} | {str(anime['capitulos']):^{w_cap}} | {str(anime['fecha']):^{w_fec}} | {puntuacion_str:^{w_pun}} | {estado:^{w_est}} |")

    print(linea_borde)

def puntuar_anime():
    imprimir_encabezado_seccion("PUNTUAR ANIME")
    ver_catalogo()
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
        print(f"\n ✅ ¡Puntuación guardada!")
    else:
        print("\n ❌ ID no encontrado.")

def ver_lista_espera():
    imprimir_encabezado_seccion("TU LISTA DE ESPERA")
    datos = cargar_datos()
    en_espera = [anime for anime in datos if anime.get('en_lista_espera') is True]
    
    if not en_espera:
        print("\n (Tu lista de espera está vacía)")
    else:
        ver_catalogo(datos_filtrados=en_espera)

def gestionar_lista_espera():
    while True:
        print("\n")
        print("┌────────────────────────────────────────┐")
        print("│       GESTIÓN DE LISTA DE ESPERA       │")
        print("├────────────────────────────────────────┤")
        print("│  1. [+] Añadir a la lista              │")
        print("│  2. [-] Eliminar de la lista           │")
        print("│  3. [<-] Volver al menú principal      │")
        print("└────────────────────────────────────────┘")
        
        opcion = input(" » Elige una opción: ")

        if opcion == "3": break 
        
        datos = cargar_datos()
        if not datos: continue

        if opcion == "1":
            ver_catalogo(datos) 
            try:
                id_buscado = int(input("\n » ID del anime a AÑADIR: "))
                for anime in datos:
                    if anime['id'] == id_buscado:
                        anime['en_lista_espera'] = True
                        print(f" ✅ Añadido a espera.")
                        guardar_datos(datos)
                        break
            except ValueError: pass

        elif opcion == "2":
            en_espera = [a for a in datos if a.get('en_lista_espera')]
            if en_espera:
                ver_catalogo(en_espera)
                try:
                    id_buscado = int(input("\n » ID a ELIMINAR de la lista: "))
                    for anime in datos:
                        if anime['id'] == id_buscado and anime['en_lista_espera']:
                            anime['en_lista_espera'] = False
                            print(f" 🗑️  Eliminado de espera.")
                            guardar_datos(datos)
                            break
                except ValueError: pass
            else:
                print(" Lista vacía.")

def ver_portada_anime():
    imprimir_encabezado_seccion("VISOR DE PORTADAS")
    ver_catalogo()
    datos = cargar_datos()
    if not datos: return

    try:
        print("\n")
        id_buscado = int(input(" » Introduce el ID para ver su imagen: "))
    except ValueError: return

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
                headers = {'User-Agent': 'Mozilla/5.0'} # A veces necesario para APIs
                respuesta = requests.get(ruta, stream=True, headers=headers)
                respuesta.raise_for_status()
                img = Image.open(BytesIO(respuesta.content))
            else:
                if os.path.exists(ruta): img = Image.open(ruta)

            if img: img.show()
        except Exception as e:
            print(f" ❌ Error al abrir imagen: {e}")

def menu_principal():
    while True:
        print("\n")
        print(" ╔════════════════════════════════════════════════════╗")
        print(" ║          GESTOR DE ANIMES - VERSIÓN API            ║")
        print(" ╠════════════════════════════════════════════════════╣")
        print(" ║  1. 🌐  BUSCAR y Guardar (Automático con API)      ║")
        print(" ║  2. 📋  Ver catálogo completo                      ║")
        print(" ║  3. ⭐  Puntuar anime                              ║")
        print(" ║  4. 📌  Gestionar Lista de Espera                  ║")
        print(" ║  5. ⏳  Ver SOLO Lista de Espera                   ║")
        print(" ║  6. 🖼️   Ver portada de un anime                    ║")
        print(" ║  7. 🚪  Salir                                      ║")
        print(" ╚════════════════════════════════════════════════════╝")
        
        opcion = input("\n » Selecciona una opción: ")

        if opcion == "1": guardar_anime()
        elif opcion == "2": ver_catalogo()
        elif opcion == "3": puntuar_anime()
        elif opcion == "4": gestionar_lista_espera()
        elif opcion == "5": ver_lista_espera() 
        elif opcion == "6": ver_portada_anime()
        elif opcion == "7": break
        else: print(" Opción no válida.")

if __name__ == "__main__":
    menu_principal()