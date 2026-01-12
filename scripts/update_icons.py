"""
Script para actualizar todos los iconos de la aplicación desde LOGO.png.

Usa el logo ORIGINAL del usuario y solo cambia los colores para cada estado.
"""

from pathlib import Path
from PIL import Image, ImageColor, ImageFilter, ImageEnhance
import colorsys

# Colores según STATE_COLORS en tray.py
STATE_COLORS = {
    "idle": "#9e9e9e",       # Gris
    "recording": "#e53935",   # Rojo
    "transcribing": "#fb8c00", # Naranja
    "formatting": "#1e88e5",  # Azul
}

# Color verde original del logo (aproximado)
ORIGINAL_GREEN = (0, 230, 118)  # #00e676


def replace_green_with_color(image: Image.Image, target_color: str) -> Image.Image:
    """
    Reemplaza los píxeles verdes del logo con el color objetivo.
    Preserva la luminosidad y el canal alpha.
    """
    img = image.convert("RGBA")
    pixels = img.load()

    target_rgb = ImageColor.getcolor(target_color, "RGB")

    # Convertir target a HSV para preservar luminosidad
    target_h, target_s, target_v = colorsys.rgb_to_hsv(
        target_rgb[0]/255, target_rgb[1]/255, target_rgb[2]/255
    )

    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # Solo procesar píxeles con algo de transparencia (no el fondo negro puro)
            if a > 10:
                # Detectar verde: G es el canal dominante
                if g > 100 and g > r * 1.2 and g > b * 1.2:
                    # Calcular luminosidad original
                    orig_h, orig_s, orig_v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

                    # Usar el hue y saturación del target, pero preservar luminosidad original
                    new_r, new_g, new_b = colorsys.hsv_to_rgb(target_h, target_s, orig_v)

                    pixels[x, y] = (
                        int(new_r * 255),
                        int(new_g * 255),
                        int(new_b * 255),
                        a
                    )

    return img


def create_ico(source_image: Image.Image, output_path: Path):
    """
    Crea un archivo .ico con múltiples tamaños estándar de Windows.
    """
    sizes = [(16, 16), (20, 20), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []

    for size in sizes:
        # Redimensionar con alta calidad
        resized = source_image.copy()
        resized.thumbnail(size, Image.Resampling.LANCZOS)

        # Crear imagen del tamaño exacto (centrada si es necesario)
        final = Image.new("RGBA", size, (0, 0, 0, 0))
        offset = ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2)
        final.paste(resized, offset)

        icons.append(final)

    # Guardar como .ico multi-size
    icons[0].save(output_path, format='ICO', sizes=[img.size for img in icons], append_images=icons[1:])
    print(f"[OK] {output_path.name} - {len(sizes)} sizes")


def main():
    root = Path(__file__).parent.parent
    logo_path = root / "LOGO.png"
    icons_dir = root / "src" / "resources" / "icons"

    if not logo_path.exists():
        print(f"ERROR: {logo_path} no encontrado")
        return

    print(f"Cargando logo original: {logo_path}")
    logo = Image.open(logo_path).convert("RGBA")
    print(f"Tamano: {logo.size}")

    # 1. Crear app.ico (verde original)
    print("\n1. Generando app.ico (verde original)...")
    create_ico(logo, icons_dir / "app.ico")

    # 2. Crear variantes de colores para tray (64x64)
    print("\n2. Generando iconos de tray...")
    tray_size = (64, 64)

    for state, color in STATE_COLORS.items():
        print(f"   {state}.png ({color})...")

        # Cambiar color
        colored = replace_green_with_color(logo, color)

        # Redimensionar a 64x64
        colored.thumbnail(tray_size, Image.Resampling.LANCZOS)

        # Guardar
        colored.save(icons_dir / f"{state}.png", "PNG")
        print(f"   [OK] {state}.png")

    # 3. Crear idle_256.png
    print("\n3. Generando idle_256.png...")
    idle_large = replace_green_with_color(logo, STATE_COLORS["idle"])
    idle_large.thumbnail((256, 256), Image.Resampling.LANCZOS)
    idle_large.save(icons_dir / "idle_256.png", "PNG")
    print("   [OK] idle_256.png")

    print("\n[DONE] Iconos actualizados usando tu logo original!")
    print(f"\nArchivos en: {icons_dir}")


if __name__ == "__main__":
    main()
