"""
Main MCP server for micro:bit interaction.

This module provides the main MCP server that orchestrates communication
between MCP clients and micro:bit devices.
"""

import asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .microbit_client import MicrobitClient
from .protocol import format_display_command
from .tools import get_all_tools
from .tools.display import handle_display_tool
from .tools.sensors import handle_sensor_tool
from .tools.input import handle_input_tool


class MicrobitMCPServer:
    """MCP Server for micro:bit interaction."""

    def __init__(self, serial_port: str = "/dev/tty.usbmodem2114202"):
        """
        Initialize the micro:bit MCP server.

        Args:
            serial_port: Serial port path for micro:bit connection
        """
        self.app = Server("microbit-server")
        self.microbit_client = MicrobitClient(serial_port)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.app.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools."""
            return get_all_tools()

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls."""
            # Display tools
            if name in ["display_message", "display_image"]:
                return await handle_display_tool(name, arguments, self.microbit_client)

            # Sensor tools
            elif name in ["get_temperature"]:
                return await handle_sensor_tool(name, arguments, self.microbit_client)

            # Input tools
            elif name in ["wait_for_button_press"]:
                return await handle_input_tool(name, arguments, self.microbit_client)

            else:
                raise ValueError(f"Tool not found: {name}")

    async def setup(self) -> None:
        """Set up the server and establish micro:bit connection."""
        await self.microbit_client.setup_serial_connection()
        # Send initial display message to indicate MCP server is ready
        await self.microbit_client.send_command(format_display_command("MCP"))

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as streams:
            await self.app.run(
                streams[0], streams[1], self.app.create_initialization_options()
            )

    async def close(self) -> None:
        """Clean up resources."""
        await self.microbit_client.close()


async def main():
    """Main entry point for the micro:bit MCP server."""
    server = MicrobitMCPServer("/dev/tty.usbmodem2114202")

    try:
        await server.setup()
        await server.run()
    finally:
        await server.close()


def cli_main():
    """Synchronous entry point for CLI."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
