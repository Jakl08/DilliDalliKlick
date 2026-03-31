# DilliDalliKlick

DilliDalliKlick is a desktop photo-reveal game inspired by the "Dalli Klick" format.
It is built with PyQt6 and lets you create photobooks, import images, and play rounds where
an image is gradually uncovered tile by tile.

The interface language is currently German.

## Features

- Photobook management
- Create and delete photobooks
- Add photos by selecting a folder or importing individual files
- Remove single photos from a photobook
- Game setup per round
- Choose photobook, number of photos, and board size (columns x rows)
- Two reveal modes:
	- Click mode: reveal random tiles manually
	- Timer mode: reveal random tiles automatically by interval
- Multi-photo sessions with progress tracking
- Theme support with multiple color schemes
- Local JSON persistence of your photobooks

## Supported Image Formats

The app scans/imports files with these extensions:

- .jpg
- .jpeg
- .png
- .gif
- .bmp
- .webp
- .svg

## Requirements

- Python 3.10+ (recommended)
- Windows, macOS, or Linux

Python dependencies are listed in `requirements.txt`:

- PyQt6
- Pillow

## Installation

```bash
python -m venv .venv
```

Activate the environment:

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

From the project root:

```bash
python main.py
```

## Typical Workflow

1. Start the app.
2. Open "Fotobücher verwalten".
3. Create a new photobook.
4. Add photos (directory or single-file import).
5. Go back and open "Spiel starten".
6. Configure game options and start.
7. Reveal tiles until the photo is complete, then continue with the next photo.

## Data Storage

Photobook metadata is stored as JSON in a user data directory:

- Windows: `%APPDATA%/DilliDalliKlick/data.json`
- macOS: `~/Library/Application Support/DilliDalliKlick/data.json`
- Linux: `${XDG_DATA_HOME:-~/.local/share}/DilliDalliKlick/data.json`

## Build a Windows Executable (PyInstaller)

This repository includes `DilliDalliKlick.spec`.

Install PyInstaller if needed:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller DilliDalliKlick.spec
```

## Project Structure

```text
main.py                      # Application entry point and main window stack
dillidalliklick/
	constants/                 # Strings, theme system, color schemes
	logic/                     # Non-UI game/settings/photobook logic
	screens/                   # PyQt windows/screens
	store.py                   # Persistent JSON store
project_image/generated/     # Generated icon/assets used by the app
```

## Notes

- The UI text is German (for example: "Fotobücher", "Spiel starten").
- Theme selection is runtime-only in the current implementation.
- Invalid or unreadable image files are skipped or reported in-game.

## License

This project is licensed under **Creative Commons Attribution-NonCommercial (CC BY-NC)**.

License details:

- https://creativecommons.org/share-your-work/cclicenses/
