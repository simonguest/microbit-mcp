"""
Sensor tools for micro:bit MCP server.

This module contains tools for reading sensor data from the micro:bit.
"""

import json
import mcp.types as types


def get_sensor_tools() -> list[types.Tool]:
    """Get all sensor-related MCP tools."""
    return [
        types.Tool(
            name="get_temperature",
            description="Get the current temperature reading from the micro:bit sensor",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


async def handle_sensor_tool(name: str, arguments: dict, microbit_client) -> list[types.TextContent]:
    """
    Handle sensor tool calls.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        microbit_client: MicrobitClient instance
        
    Returns:
        List of TextContent responses
    """
    if name == "get_temperature":
        temperature_data = await microbit_client.get_temperature()
        return [types.TextContent(type="text", text=json.dumps(temperature_data))]
    
    else:
        raise ValueError(f"Unknown sensor tool: {name}")
