"""
Script para generar iconos optimizados para system tray.

Para iconos pequeños (16x16, 32x32), crea versiones simplificadas
del micrófono que se ven mejor en baja resolución.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageColor

# Colores según STATE_COLORS en tray.py
STATE_COLORS = {
    "idle": "#9e9e9e",
    "recording": "#e53935",
    "transcribing": "#fb8c00",
    "formatting": "#1e88e5",
}


def draw_simple_microphone(size: int, color: str, bg_color: str = "#0f0f0f") -> Image.Image:
    """
    Dibuja un micrófono simplificado optimizado para tamaños pequeños.

    Args:
        size: Tamaño del icono (cuadrado)
        color: Color del micrófono (hex)
        bg_color: Color de fondo (hex, default negro)

    Returns:
        Imagen PIL con el micrófono dibujado
    """
    img = Image.new("RGBA", (size, size), ImageColor.getcolor(bg_color, "RGBA"))
    draw = ImageDraw.Draw(img)

    # Calcular dimensiones basadas en el tamaño
    # Dejamos 15% de margen en cada lado
    margin = int(size * 0.15)
    mic_width = size - (margin * 2)
    mic_height = size - (margin * 2)

    # Color del micrófono
    mic_color = ImageColor.getcolor(color, "RGB")

    # Centro del canvas
    cx = size / 2
    cy = size / 2

    if size <= 32:
        # Para iconos pequeños: diseño ultra-simplificado
        # Cápsula superior del micrófono (rectángulo + semicírculo arriba)
        capsule_width = int(mic_width * 0.5)
        capsule_height = int(mic_height * 0.55)
        capsule_x = cx - capsule_width / 2
        capsule_y = margin

        # Dibujar cápsula (rectángulo redondeado)
        draw.rounded_rectangle(
            [capsule_x, capsule_y, capsule_x + capsule_width, capsule_y + capsule_height],
            radius=int(capsule_width / 2),
            fill=mic_color,
            outline=None
        )

        # Base del micrófono (línea vertical corta)
        base_y_start = capsule_y + capsule_height + 1
        base_y_end = size - margin - 1
        base_thickness = max(2, int(capsule_width * 0.3))

        draw.line(
            [(cx, base_y_start), (cx, base_y_end)],
            fill=mic_color,
            width=base_thickness
        )

        # Base inferior (línea horizontal)
        base_width = int(capsule_width * 1.2)
        draw.line(
            [(cx - base_width/2, base_y_end), (cx + base_width/2, base_y_end)],
            fill=mic_color,
            width=base_thickness
        )
    else:
        # Para iconos grandes (64x64+): diseño más detallado
        # Cápsula superior
        capsule_width = int(mic_width * 0.45)
        capsule_height = int(mic_height * 0.5)
        capsule_x = cx - capsule_width / 2
        capsule_y = margin + 2

        # Dibujar cápsula con más detalle
        draw.rounded_rectangle(
            [capsule_x, capsule_y, capsule_x + capsule_width, capsule_y + capsule_height],
            radius=int(capsule_width / 2),
            fill=mic_color,
            outline=None
        )

        # Líneas internas de la cápsula (rejilla del micrófono)
        num_lines = 3
        line_spacing = capsule_height / (num_lines + 1)
        for i in range(1, num_lines + 1):
            y = capsule_y + line_spacing * i
            line_margin = int(capsule_width * 0.15)
            draw.line(
                [(capsule_x + line_margin, y), (capsule_x + capsule_width - line_margin, y)],
                fill=bg_color,
                width=1
            )

        # Arco de soporte (forma de "U" debajo de la cápsula)
        arc_width = int(capsule_width * 1.3)
        arc_height = int(capsule_height * 0.8)
        arc_x = cx - arc_width / 2
        arc_y = capsule_y + capsule_height + 2
        arc_thickness = max(2, int(capsule_width * 0.15))

        # Dibujar arco usando arco de elipse (solo la parte inferior)
        draw.arc(
            [arc_x, arc_y, arc_x + arc_width, arc_y + arc_height],
            start=0,
            end=180,
            fill=mic_color,
            width=arc_thickness
        )

        # Base del micrófono (línea vertical)
        base_y_start = arc_y + arc_height / 2
        base_y_end = size - margin - 3
        base_thickness = arc_thickness

        draw.line(
            [(cx, base_y_start), (cx, base_y_end)],
            fill=mic_color,
            width=base_thickness
        )

        # Base inferior (línea horizontal)
        base_width = int(arc_width * 0.8)
        draw.line(
            [(cx - base_width/2, base_y_end), (cx + base_width/2, base_y_end)],
            fill=mic_color,
            width=base_thickness
        )

    return img


def create_ico_optimized(output_path: Path, colors: dict):
    """
    Crea un archivo .ico multi-size con versiones optimizadas para cada tamaño.
    Usa el color verde para el .ico principal.
    """
    # Para .ico, usamos verde (color original)
    green_color = "#00e676"  # Verde del logo original

    sizes = [(16, 16), (20, 20), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []

    for size in sizes:
        # Crear icono optimizado para este tamaño específico
        img = draw_simple_microphone(size[0], green_color)
        icons.append(img)

    # Guardar como .ico multi-size
    icons[0].save(output_path, format='ICO', sizes=[img.size for img in icons], append_images=icons[1:])
    print(f"[OK] Created {output_path.name} with {len(sizes)} optimized sizes")


def main():
    # Paths
    root = Path(__file__).parent.parent
    icons_dir = root / "src" / "resources" / "icons"

    print("Generando iconos optimizados para system tray...")
    print("(Diseñados específicamente para verse bien en 16x16 y 32x32)\n")

    # 1. Crear app.ico con versiones optimizadas
    print("1. Generando app.ico multi-size...")
    create_ico_optimized(icons_dir / "app.ico", STATE_COLORS)

    # 2. Crear variantes de colores para tray
    print("\n2. Generando iconos de tray con diseño simplificado...")

    # Para el tray, usar 64x64 (Windows redimensiona automáticamente según el DPI)
    # Pero con diseño optimizado que se ve bien incluso al redimensionar a 16x16
    tray_size = 64

    for state, color in STATE_COLORS.items():
        print(f"   Generando {state}.png ({color})...")

        # Crear icono simplificado
        img = draw_simple_microphone(tray_size, color)

        # Guardar
        output_path = icons_dir / f"{state}.png"
        img.save(output_path, "PNG")
        print(f"   [OK] Guardado {output_path.name}")

    # 3. Crear idle_256.png (versión grande)
    print("\n3. Generando idle_256.png...")
    idle_large = draw_simple_microphone(256, STATE_COLORS["idle"])
    idle_large.save(icons_dir / "idle_256.png", "PNG")
    print("   [OK] Guardado idle_256.png")

    print("\n" + "="*60)
    print("[SUCCESS] Iconos optimizados generados exitosamente!")
    print("="*60)
    print(f"\nIconos generados en: {icons_dir}")
    print("\nCaracterísticas:")
    print("  - Diseño simplificado para verse bien en 16x16 y 32x32")
    print("  - Líneas más gruesas para mejor visibilidad")
    print("  - Sin detalles finos que se pierdan al redimensionar")
    print("  - Optimizado para system tray de Windows")
    print("\nIconos generados:")
    print("  - app.ico (multi-size .ico)")
    print("  - idle.png (gris)")
    print("  - recording.png (rojo)")
    print("  - transcribing.png (naranja)")
    print("  - formatting.png (azul)")
    print("  - idle_256.png (versión grande)")
    print("\nPróximo paso: Ejecuta la app para ver los iconos en el tray!")
    print("  python -m src.main")


if __name__ == "__main__":
    main()
