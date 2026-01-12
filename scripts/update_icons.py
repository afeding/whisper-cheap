"""
Script para actualizar todos los iconos de la aplicación desde LOGO.png.

Genera:
- app.ico (múltiples tamaños para Windows)
- idle.png (gris)
- recording.png (rojo)
- transcribing.png (naranja)
- formatting.png (azul)
- idle_256.png (versión grande)
"""

from pathlib import Path
from PIL import Image, ImageColor

# Colores según STATE_COLORS en tray.py
STATE_COLORS = {
    "idle": "#9e9e9e",
    "recording": "#e53935",
    "transcribing": "#fb8c00",
    "formatting": "#1e88e5",
}

def change_color_of_green_pixels(image: Image.Image, target_color: str) -> Image.Image:
    """
    Cambia todos los píxeles verdes del logo al color objetivo.
    Mantiene el canal alpha intacto.
    """
    img = image.convert("RGBA")
    data = img.getdata()

    target_rgb = ImageColor.getcolor(target_color, "RGB")
    new_data = []

    for item in data:
        r, g, b, a = item

        # Detectar píxeles verdes (el micrófono)
        # Verde brillante aproximadamente: más green que red/blue
        if g > 150 and g > r * 1.3 and g > b * 1.3:
            # Reemplazar con el color objetivo, manteniendo alpha
            new_data.append((target_rgb[0], target_rgb[1], target_rgb[2], a))
        else:
            # Mantener píxel original (fondo negro)
            new_data.append(item)

    img.putdata(new_data)
    return img


def create_ico(source_image: Image.Image, output_path: Path):
    """
    Crea un archivo .ico con múltiples tamaños estándar de Windows.
    """
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []

    for size in sizes:
        resized = source_image.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)

    # Guardar como .ico multi-size
    icons[0].save(output_path, format='ICO', sizes=[img.size for img in icons], append_images=icons[1:])
    print(f"[OK] Created {output_path.name} with {len(sizes)} sizes")


def main():
    # Paths
    root = Path(__file__).parent.parent
    logo_path = root / "LOGO.png"
    icons_dir = root / "src" / "resources" / "icons"

    if not logo_path.exists():
        print(f"ERROR: {logo_path} no encontrado")
        return

    print(f"Cargando {logo_path}...")
    logo = Image.open(logo_path).convert("RGBA")
    print(f"Tamaño original: {logo.size}")

    # 1. Crear app.ico (mantiene el verde original)
    print("\n1. Generando app.ico...")
    create_ico(logo, icons_dir / "app.ico")

    # 2. Crear variantes de colores para tray
    print("\n2. Generando iconos de tray con variantes de color...")

    # Tamaño para iconos de tray (64x64 recomendado, el tray.py redimensiona si es necesario)
    tray_size = (64, 64)

    for state, color in STATE_COLORS.items():
        print(f"   Generando {state}.png ({color})...")

        # Cambiar color del micrófono
        colored_logo = change_color_of_green_pixels(logo, color)

        # Redimensionar a tamaño de tray
        colored_logo_small = colored_logo.resize(tray_size, Image.Resampling.LANCZOS)

        # Guardar
        output_path = icons_dir / f"{state}.png"
        colored_logo_small.save(output_path, "PNG")
        print(f"   [OK] Guardado {output_path.name}")

    # 3. Crear idle_256.png (versión grande del idle)
    print("\n3. Generando idle_256.png...")
    idle_large = change_color_of_green_pixels(logo, STATE_COLORS["idle"])
    idle_large = idle_large.resize((256, 256), Image.Resampling.LANCZOS)
    idle_large.save(icons_dir / "idle_256.png", "PNG")
    print("   [OK] Guardado idle_256.png")

    print("\n[SUCCESS] Todos los iconos actualizados exitosamente!")
    print(f"\nIconos generados en: {icons_dir}")
    print("   - app.ico (multi-size .ico para Windows)")
    print("   - idle.png (gris)")
    print("   - recording.png (rojo)")
    print("   - transcribing.png (naranja)")
    print("   - formatting.png (azul)")
    print("   - idle_256.png (versión grande)")


if __name__ == "__main__":
    main()
