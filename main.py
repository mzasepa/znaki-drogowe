#!/usr/bin/env python3
"""Entry point for the Znaki Drogowe application."""

from nicegui import ui
from src.ui.app import init_app

init_app()

ui.run(
    title="Znaki Drogowe",
    port=8080,
    reload=False,
    show=True,
    storage_secret="znaki-drogowe-secret",
)
