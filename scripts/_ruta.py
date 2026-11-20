"""Permite ejecutar los scripts desde la raíz del proyecto: python scripts/archivo.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
