@echo off
title Descargador de Musica MP3
color 0A
echo.
echo ============================================================
echo    DESCARGADOR DE MUSICA MP3
echo ============================================================
echo.
echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python NO esta instalado.
    echo  Descargalo de: https://www.python.org/downloads/
    echo  Marca la opcion Add Python to PATH al instalar.
    echo.
    pause
    exit /b 1
)
echo  [OK] Python detectado.
echo.
echo [2/3] Instalando librerias necesarias...
echo  (La primera vez puede tardar varios minutos, por favor espera)
echo  Podras ver el progreso de cada descarga a continuacion:
echo.
pip install -r "%~dp0requirements.txt" --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo  ERROR: No se pudieron instalar las librerias.
    echo  Verifica tu conexion a internet e intenta de nuevo.
    pause
    exit /b 1
)
echo.
echo  [OK] Librerias listas.
echo.
echo [3/3] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if not errorlevel 1 goto LANZAR
if exist "%~dp0ffmpeg\bin\ffmpeg.exe" (
    set PATH=%~dp0ffmpeg\bin;%PATH%
    goto LANZAR
)
echo  Descargando FFmpeg (solo ocurre una vez)...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol='Tls12'; Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile '%~dp0ffmpeg_temp.zip' -UseBasicParsing}"
if not exist "%~dp0ffmpeg_temp.zip" (
    echo  AVISO: No se pudo descargar FFmpeg.
    goto LANZAR
)
powershell -Command "Expand-Archive -Path '%~dp0ffmpeg_temp.zip' -DestinationPath '%~dp0ffmpeg_ext' -Force" >nul 2>&1
for /d %%i in ("%~dp0ffmpeg_ext\ffmpeg-*") do move "%%i" "%~dp0ffmpeg" >nul 2>&1
del "%~dp0ffmpeg_temp.zip" >nul 2>&1
rmdir "%~dp0ffmpeg_ext" >nul 2>&1
if exist "%~dp0ffmpeg\bin\ffmpeg.exe" (
    set PATH=%~dp0ffmpeg\bin;%PATH%
    echo  [OK] FFmpeg instalado.
) else (
    echo  AVISO: FFmpeg no se instalo. La conversion podria fallar.
)
:LANZAR
cd /d "%~dp0"
echo.
echo ============================================================
echo  Todo listo. Iniciando la aplicacion...
echo  Se abrira una pestana en tu navegador.
echo  Para CERRAR la app cierra esta ventana.
echo ============================================================
echo.
streamlit run app.py
if errorlevel 1 (
    echo.
    echo  ERROR: La aplicacion no pudo iniciarse.
    echo  Revisa el mensaje de error que aparece arriba.
)
echo.
pause