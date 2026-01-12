# Actualización de Iconos - Whisper Cheap

Este directorio contiene scripts para regenerar todos los iconos de la aplicación.

## Scripts disponibles

### `update_icons_optimized.py` ⭐ **RECOMENDADO**
Genera iconos **optimizados para system tray** con diseño simplificado que se ve nítido incluso en 16x16 píxeles.

### `update_icons.py`
Convierte el logo original (LOGO.png) cambiando solo los colores. Puede verse pixelado en tamaños pequeños.

## Archivos generados

A partir de `LOGO.png` (micrófono verde sobre fondo negro), se generan:

### System Tray Icons (64x64 PNG)
- **idle.png** - Gris (#9e9e9e): cuando la app está inactiva
- **recording.png** - Rojo (#e53935): cuando está grabando
- **transcribing.png** - Naranja (#fb8c00): cuando está transcribiendo
- **formatting.png** - Azul (#1e88e5): cuando está formateando con LLM

### Application Icon
- **app.ico** - Multi-size ICO (16x16 hasta 256x256): usado por el ejecutable y el instalador
- **idle_256.png** - Versión grande (256x256) del estado idle

## Uso

Para regenerar todos los iconos (usa el script optimizado):

```bash
python scripts/update_icons_optimized.py
```

Si prefieres usar el logo original sin simplificar:

```bash
python scripts/update_icons.py
```

## Dónde se usan los iconos

### System Tray (src/ui/tray.py)
- Carga iconos desde `src/resources/icons/{estado}.png`
- Se redimensionan automáticamente si son muy grandes
- Fallback a iconos generados programáticamente si faltan archivos

### Ejecutable y Instalador
- **build_config.spec:148** - Define el icono del .exe
- **installer/WhisperCheap.iss:17** - Define el icono del instalador

## Cómo funcionan los scripts

### update_icons_optimized.py (Recomendado)
1. **Dibuja un micrófono simplificado** programáticamente usando PIL/Pillow
2. **Optimiza para cada tamaño**:
   - 16x16 a 32x32: diseño ultra-simple con líneas gruesas
   - 64x64+: diseño más detallado con rejilla interna
3. **Genera versiones para cada color** según el estado
4. **Crea app.ico multi-size** con 8 tamaños optimizados
5. **Resultado**: Iconos nítidos que se ven bien en cualquier tamaño

### update_icons.py (Alternativa)
1. **Carga LOGO.png** (800x800 píxeles)
2. **Detecta píxeles verdes** del micrófono
3. **Reemplaza el verde** con el color del estado
4. **Redimensiona** a 64x64, 256x256, y multi-size para .ico
5. **Limitación**: Los detalles finos se pierden en tamaños pequeños

## Verificación

Para verificar que los iconos funcionan:

1. **Ejecutar la app**:
   ```bash
   python -m src.main
   ```

2. **Verificar el tray icon**:
   - Debería aparecer un micrófono GRIS en la bandeja del sistema
   - Al grabar, cambia a ROJO
   - Al transcribir, cambia a NARANJA
   - Al formatear con LLM, cambia a AZUL

3. **Verificar el .exe después de compilar**:
   ```bash
   pyinstaller build_config.spec
   ```
   - El archivo `dist/WhisperCheap/WhisperCheap.exe` debe tener el icono del micrófono
   - Verificar en el Explorador de Windows que el icono se ve correctamente

## Notas técnicas

- **Formato**: PNG para tray (con canal alpha), ICO para Windows
- **Detección de color**: Detecta píxeles donde G > 150 y G > R*1.3 y G > B*1.3
- **Preservación de alpha**: El fondo negro y el canal alpha se mantienen intactos
- **Resampling**: LANCZOS para mejor calidad al redimensionar
