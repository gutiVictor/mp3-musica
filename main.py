import pandas as pd
import yt_dlp
import os
import sys

# Configuración de yt-dlp para descargar como MP3
YTDL_OPTS = {
    'format': 'bestaudio/best',
    'extract_audio': True,
    'audio_format': 'mp3',
    'audio_quality': '192K',
    'outtmpl': 'descargas/%(title)s.%(ext)s', # Guarda en la subcarpeta 'descargas'
    'noplaylist': True,
    'quiet': False
}

def descargar_cancion(nombre_cancion):
    print(f"\nBuscando y descargando: {nombre_cancion}...")
    try:
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            # ytsearch1 busca el término y obtiene el primer resultado
            ydl.extract_info(f"ytsearch1:{nombre_cancion}", download=True)
        print(f"¡Descarga completada: {nombre_cancion}!")
    except Exception as e:
        print(f"Error al descargar '{nombre_cancion}': {e}")

def crear_excel_ejemplo(nombre_archivo):
    print(f"Creando un archivo de Excel de ejemplo: {nombre_archivo}...")
    df = pd.DataFrame({'Cancion': ['Bohemian Rhapsody Queen', 'Billie Jean Michael Jackson']})
    df.to_excel(nombre_archivo, index=False)
    print("Archivo de ejemplo creado. Por favor, edítalo con tus canciones y vuelve a ejecutar el programa.")

def principal():
    archivo_excel = 'canciones.xlsx'

    # Crea carpeta descargas si no existe
    if not os.path.exists('descargas'):
        os.makedirs('descargas')

    # Si no existe el archivo excel, crea uno de ejemplo y detiene el programa
    if not os.path.exists(archivo_excel):
        print(f"No se encontró el archivo '{archivo_excel}'.")
        crear_excel_ejemplo(archivo_excel)
        return

    try:
        df = pd.read_excel(archivo_excel)
        
        # Validar si tiene la columna correcta
        if 'Cancion' not in df.columns:
            print("El archivo Excel debe tener una columna llamada 'Cancion' en la primera fila.")
            return

        lista_canciones = df['Cancion'].dropna().tolist()
        
        print(f"Se encontraron {len(lista_canciones)} canciones en la lista.")
        
        for cancion in lista_canciones:
            descargar_cancion(str(cancion))
            
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    principal()
