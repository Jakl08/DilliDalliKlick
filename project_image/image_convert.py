from pathlib import Path
from typing import cast

from PIL import Image
from PIL.Image import Image as PillowImage


BASE_DIR = Path(__file__).parent
DESTINATION_PATH = BASE_DIR / "generated"
PNG_SIZES = (1024, 512, 256, 128, 64, 32)
ICO_SIZES = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
ICNS_SIZES = [(1024, 1024), (512, 512), (256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]


def resolve_source_image() -> Path:
	for candidate in ("original.png", "origin.png"):
		path = BASE_DIR / candidate
		if path.exists():
			return path
	raise FileNotFoundError("No source image found. Expected original.png or origin.png in project_image/.")


def export_pngs(image: PillowImage, output_dir: Path) -> None:
	for size in PNG_SIZES:
		target_size: tuple[int, int] = (size, size)
		resized = cast(PillowImage, image.resize(target_size, Image.Resampling.LANCZOS))
		resized.save(output_dir / f"dalli_klick_icon_{size}.png", format="PNG")

	image.save(output_dir / "dalli_klick_icon.png", format="PNG")


def export_ico(image: PillowImage, output_dir: Path) -> None:
	image.save(output_dir / "dalli_klick_icon.ico", format="ICO", sizes=ICO_SIZES)


def export_icns(image: PillowImage, output_dir: Path) -> None:
	try:
		image.save(output_dir / "dalli_klick_icon.icns", format="ICNS", sizes=ICNS_SIZES)
	except OSError as exc:
		print(f"Skipped ICNS export: {exc}")


def main() -> None:
	source_image_path = resolve_source_image()
	DESTINATION_PATH.mkdir(exist_ok=True)

	with Image.open(source_image_path) as img:
		image = img.convert("RGBA")
		export_pngs(image, DESTINATION_PATH)
		export_ico(image, DESTINATION_PATH)
		export_icns(image, DESTINATION_PATH)

	print(f"Generated icon files in: {DESTINATION_PATH}")


if __name__ == "__main__":
	main()