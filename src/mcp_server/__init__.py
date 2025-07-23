"""
Micro:bit MCP Server Package.

This package provides an MCP (Model Context Protocol) server for interacting
with micro:bit devices over serial connections.
"""

from .server import MicrobitMCPServer
from .microbit_client import MicrobitClient
from .protocol import Commands, Responses

__version__ = "0.1.0"
__all__ = ["MicrobitMCPServer", "MicrobitClient", "Commands", "Responses"]
