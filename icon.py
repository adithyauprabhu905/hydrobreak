"""Procedural icon generation so the project ships with zero binary assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def _draw_droplet(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = size / 2
    tip_y = size * 0.08
    base_y = size * 0.92
    radius = size * 0.34

    # Teardrop: a triangle-ish tip blended into a circle base.
    points = [
        (cx, tip_y),
        (cx - radius * 0.95, base_y - radius * 0.65),
        (cx + radius * 0.95, base_y - radius * 0.65),
    ]
    draw.polygon(points, fill=(64, 170, 235, 255))
    draw.ellipse(
        (cx - radius, base_y - 2 * radius, cx + radius, base_y),
        fill=(64, 170, 235, 255),
    )

    # Soft highlight for a "cute" glossy look.
    hl_r = size * 0.09
    draw.ellipse(
        (cx - hl_r * 1.8, base_y - radius * 1.4, cx - hl_r * 0.2, base_y - radius * 1.4 + hl_r * 1.6),
        fill=(255, 255, 255, 140),
    )

    # Simple smiling face.
    eye_r = size * 0.03
    eye_y = base_y - radius * 0.75
    draw.ellipse((cx - radius * 0.35 - eye_r, eye_y - eye_r, cx - radius * 0.35 + eye_r, eye_y + eye_r),
                 fill=(20, 60, 90, 255))
    draw.ellipse((cx + radius * 0.35 - eye_r, eye_y - eye_r, cx + radius * 0.35 + eye_r, eye_y + eye_r),
                 fill=(20, 60, 90, 255))
    smile_bbox = (cx - radius * 0.28, eye_y + eye_r * 0.5, cx + radius * 0.28, eye_y + radius * 0.55)
    draw.arc(smile_bbox, start=20, end=160, fill=(20, 60, 90, 255), width=max(1, size // 40))

    return img


def build_icon(dest: Path) -> Path:
    """Creates a multi-resolution .ico file at dest and returns its path."""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    base = _draw_droplet(256)
    frames = [base.resize((s, s), Image.LANCZOS) for s in sizes]
    dest.parent.mkdir(parents=True, exist_ok=True)
    base.save(dest, format="ICO", sizes=[(s, s) for s in sizes])
    return dest


def build_tray_image(size: int = 64):
    """Returns a PIL.Image suitable for pystray (in-memory, no disk write)."""
    return _draw_droplet(size)


if __name__ == "__main__":
    out = Path(__file__).parent / "assets" / "icon.ico"
    build_icon(out)
    print(f"Icon written to {out}")
