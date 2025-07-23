"""
MCP tools for micro:bit interaction.

This package contains all the MCP tools that can be used to interact
with the micro:bit device.
"""

from .display import get_display_tools
from .sensors import get_sensor_tools
from .input import get_input_tools

def get_all_tools():
    """Get all available micro:bit MCP tools."""
    tools = []
    tools.extend(get_display_tools())
    tools.extend(get_sensor_tools())
    tools.extend(get_input_tools())
    return tools
