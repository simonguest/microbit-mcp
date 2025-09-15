"""
Main MCP server for micro:bit interaction.

This module provides the main MCP server that orchestrates communication
between MCP clients and micro:bit devices.
"""

import argparse
import asyncio
import sys
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
import serial.tools.list_ports

from .microbit_client import MicrobitClient
from .tools import get_all_tools
from .tools.display import handle_display_tool
from .tools.sensors import handle_sensor_tool
from .tools.input import handle_input_tool
from .tools.music import handle_music_tool


class MicrobitMCPServer:
    """MCP Server for micro:bit interaction."""

    def __init__(self, serial_port: str = "/dev/cu.usbmodem211102"):
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

            # Music tools
            elif name in ["play_music"]:
                return await handle_music_tool(name, arguments, self.microbit_client)

            else:
                raise ValueError(f"Tool not found: {name}")

    async def setup(self) -> None:
        """Set up the server and establish micro:bit connection."""
        await self.microbit_client.setup_serial_connection()

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as streams:
            await self.app.run(
                streams[0], streams[1], self.app.create_initialization_options()
            )

    async def close(self) -> None:
        """Clean up resources."""
        await self.microbit_client.close()


def list_serial_ports():
    """List all available serial ports with micro:bit detection."""
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No serial ports found.")
        return
    
    # Try to identify likely micro:bit devices
    microbit_ports = []
    for port in ports:
        description = port.description.lower()
        device = port.device.lower()
        
        # Check for micro:bit specific identifiers
        if any(keyword in description for keyword in 
               ['microbit', 'micro:bit', 'daplink', 'mbed']):
            microbit_ports.append(port)
        # Also check for common USB serial patterns that micro:bit uses
        elif 'usb' in device and 'modem' in device:
            microbit_ports.append(port)
    
    print("Available Serial Ports:")
    print("=" * 50)
    
    if microbit_ports:
        print("\nLikely micro:bit devices:")
        for port in microbit_ports:
            print(f"  {port.device} - {port.description}")
            if port.hwid:
                print(f"    Hardware ID: {port.hwid}")
    
    print(f"\nAll serial ports ({len(ports)} found):")
    for port in ports:
        marker = " ⭐" if port in microbit_ports else ""
        print(f"  {port.device} - {port.description}{marker}")
    
    if microbit_ports:
        print(f"\nRecommended: Use {microbit_ports[0].device} for your micro:bit")
    else:
        print("\nNo micro:bit devices detected. Make sure your micro:bit is:")
        print("  - Connected via USB")
        print("  - Powered on")
        print("  - Has the correct firmware flashed")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP Server for the micro:bit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use default port
  %(prog)s -p /dev/tty.usbmodem1234  # Use specific port
  %(prog)s --list-ports              # List available ports
        """
    )
    
    parser.add_argument(
        "-p", "--port",
        default="/dev/cu.usbmodem2114202",
        help="Serial port for micro:bit connection (default: %(default)s)"
    )
    
    parser.add_argument(
        "--list-ports",
        action="store_true",
        help="List available serial ports and exit"
    )
    
    return parser.parse_args()


async def main(serial_port: str = "/dev/cu.usbmodem2114202"):
    """Main entry point for the micro:bit MCP server."""
    server = MicrobitMCPServer(serial_port)

    try:
        await server.setup()
        await server.run()
    finally:
        await server.close()


def cli_main():
    """Synchronous entry point for CLI."""
    args = parse_arguments()
    
    if args.list_ports:
        list_serial_ports()
        sys.exit(0)
    
    asyncio.run(main(args.port))


if __name__ == "__main__":
    cli_main()
