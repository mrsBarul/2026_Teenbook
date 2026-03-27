"""Совместимый входной файл для автоматической простановки кросс-ссылок.

Запускает основной скрипт insert_crosslinks.py из папки scripts/.
"""
from pathlib import Path
import runpy

SCRIPT = Path(__file__).parent / "scripts" / "insert_crosslinks.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
