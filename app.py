import streamlit as st
import pandas as pd
import yt_dlp
import os
import shutil
import io

# Configuración de página
st.set_page_config(page_title="Descargador MP3", page_icon="🎵", layout="centered")

# Estilos CSS personalizados para que parezca una app Premium
st.markdown("""
<style>
    div.stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #ff2b2b;
        box-shadow: 0 4px 8px rgba(255, 75, 75, 0.3);
    }
    .main-header {
        text-align: center;
        color: #1f1f1f;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-top: 0px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🎵 Descargador de Música MP3</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Busca y descarga canciones de YouTube en la mejor calidad de audio.</p>", unsafe_allow_html=True)

# Crear carpeta temporal de descargas
if not os.path.exists('descargas'):
    os.makedirs('descargas')

# Función robusta de descarga
def descargar_cancion(nombre_cancion):
    YTDL_OPTS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'descargas/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            # Buscar y descargar directamente
            info = ydl.extract_info(f"ytsearch1:{nombre_cancion}", download=True)
            
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
            else:
                entry = info
                
            titulo = entry.get('title', nombre_cancion)
            
            # Obtener la ruta final del archivo procesado si yt-dlp lo reporta
            ruta_final = None
            if 'requested_downloads' in entry and len(entry['requested_downloads']) > 0:
                ruta_final = entry['requested_downloads'][0]['filepath']
            else:
                target = ydl.prepare_filename(entry)
                ruta_final = os.path.splitext(target)[0] + '.mp3'
            
            return titulo, ruta_final, None
    except Exception as e:
        return None, None, str(e)


# Pestañas de la aplicación
tab1, tab2 = st.tabs(["🎧 Descarga Individual", "📁 Descarga por Lote (Excel)"])

# --- TAB 1: INDIVIDUAL ---
with tab1:
    st.subheader("Buscar una sola canción")
    st.markdown("Ingresa el nombre de la canción o del artista, la buscaremos por ti y te daremos el archivo MP3 listo para guardar en tu PC.")
    
    cancion_individual = st.text_input("Ingresa tu búsqueda aquí:")
    
    if st.button("Buscar y Descargar Canción"):
        if cancion_individual.strip():
            with st.spinner(f"Buscando el mejor audio para '{cancion_individual}'..."):
                titulo, ruta_mp3, error = descargar_cancion(cancion_individual.strip())
                
            if error:
                st.error(f"Ocurrió un error: {error}")
            elif ruta_mp3 and os.path.exists(ruta_mp3):
                st.success(f"¡Audio procesado con éxito: {titulo}!")
                # Guardar en el estado para que el botón no desaparezca
                st.session_state['archivo_listo'] = ruta_mp3
            else:
                st.error("No se pudo extraer el archivo de audio. Intenta con otra búsqueda.")
        else:
            st.warning("Por favor, ingresa un nombre válido para buscar.")

    # Mostrar botón de descarga si hay un archivo listo en sesión
    if 'archivo_listo' in st.session_state and os.path.exists(st.session_state['archivo_listo']):
        with open(st.session_state['archivo_listo'], "rb") as file:
            st.download_button(
                label="💾 Guardar archivo MP3 ahora",
                data=file,
                file_name=os.path.basename(st.session_state['archivo_listo']),
                mime="audio/mpeg"
            )

# --- TAB 2: LOTE ---
with tab2:
    st.subheader("Descargar múltiples canciones a la vez")
    st.markdown("Sube tu archivo de Excel (`.xlsx`) con una columna llamada **'Cancion'** en la primera fila. Nosotros haremos el resto.")
    
    # Generador de archivo de ejemplo en memoria
    ejemplo_df = pd.DataFrame({'Cancion': ['Bohemian Rhapsody Queen', 'Billie Jean Michael Jackson']})
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        ejemplo_df.to_excel(writer, index=False)
    
    # Botón de ejemplo
    st.download_button(
        label="📄 Descargar Excel de Ejemplo",
        data=buffer.getvalue(),
        file_name="ejemplo_canciones.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.write("---")
    
    # Carga de archivo
    archivo_subido = st.file_uploader("Sube tu archivo Excel aquí", type=["xlsx", "xls"])
    
    if archivo_subido is not None:
        try:
            df = pd.read_excel(archivo_subido)
            if 'Cancion' not in df.columns:
                st.error("⚠️ El archivo no tiene la columna 'Cancion'. Revisa el Excel de ejemplo.")
            else:
                lista_canciones = df['Cancion'].dropna().tolist()
                st.info(f"✅ Se han detectado {len(lista_canciones)} canciones en tu lista.")
                
                # Usamos session_state para que el botón de ZIP no desaparezca
                if 'descargado_lote' not in st.session_state:
                    st.session_state.descargado_lote = False
                
                if st.button("▶️ Iniciar Descarga de Todas las Canciones"):
                    barra = st.progress(0)
                    estado = st.empty()
                    archivos_exitosos = 0
                    
                    for i, cancion in enumerate(lista_canciones):
                        estado.text(f"Descargando ({i+1}/{len(lista_canciones)}): {cancion} ...")
                        titulo, ruta_mp3, error = descargar_cancion(str(cancion))
                        
                        if ruta_mp3 and os.path.exists(ruta_mp3):
                            archivos_exitosos += 1
                            
                        # Actualizar barra
                        barra.progress((i + 1) / len(lista_canciones))
                        
                    estado.text("¡Proceso finalizado!")
                    st.success(f"🎉 Se descargaron {archivos_exitosos} de {len(lista_canciones)} canciones con éxito.")
                    
                    if archivos_exitosos > 0:
                        st.session_state.descargado_lote = True
                    
                if st.session_state.get('descargado_lote', False):
                    st.write("Tus canciones están listas. Hemos creado un archivo Comprimido (ZIP) con todas ellas.")
                    
                    # Generar ZIP
                    shutil.make_archive("CANCIONES_DESCARGADAS", 'zip', "descargas")
                    
                    if os.path.exists("CANCIONES_DESCARGADAS.zip"):
                        file_size = os.path.getsize("CANCIONES_DESCARGADAS.zip") / (1024 * 1024)
                        
                        with open("CANCIONES_DESCARGADAS.zip", "rb") as fp:
                            st.download_button(
                                label=f"📦 Descargar todas las canciones juntas (ZIP - {file_size:.1f} MB)",
                                data=fp,
                                file_name="Canciones_Escuchadas.zip",
                                mime="application/zip"
                            )
        except Exception as e:
            st.error(f"Error procesando tu archivo: {e}")
