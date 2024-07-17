"""Qt related modules.

This module contains Modules that are Qt related, and help to integrate
ArkitektNext with Qt applications.

The main component is the MagicBar, which is a widget that can be added
to any Qt application. It will then allow the user to configure and connect
to ArkitektNext, and configure settings.
"""
from .magic_bar import MagicBar
from .builder import build_arkitekt_next_qt_app

__all__ = ["MagicBar", "build_arkitekt_next_qt_app"]