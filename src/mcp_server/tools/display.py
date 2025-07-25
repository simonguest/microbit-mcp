"""
Display tools for micro:bit MCP server.

This module contains tools for controlling the micro:bit LED matrix display.
"""

import mcp.types as types
from ..protocol import format_message_command, format_image_command


def get_display_tools() -> list[types.Tool]:
    """Get all display-related MCP tools."""
    return [
        types.Tool(
            name="display_message",
            description="Display a text message on micro:bit LED matrix",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to display"
                    }
                },
                "required": ["message"]
            }
        ),
        types.Tool(
            name="display_image",
            description="Display an image on the micro:bit LED matrix.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": """A sequence of 5 numbers (0-9), with a colon delimeter for each of the 5 rows in the matrix. 
                        e.g., 00300:03630:36963:03630:00300 is a star
                        """
                    }
                },
                "required": ["image"]
            }
        )
    ]


async def handle_display_tool(name: str, arguments: dict, microbit_client) -> list[types.TextContent]:
    """
    Handle display tool calls.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        microbit_client: MicrobitClient instance
        
    Returns:
        List of TextContent responses
    """
    if name == "display_message":
        message = arguments.get("message", "")
        command = format_message_command(message)
        await microbit_client.send_command(command)
        return [types.TextContent(type="text", text=f"Displayed: {message}")]
    
    elif name == "display_image":
        image = arguments.get("image", "")
        command = format_image_command(image)
        await microbit_client.send_command(command)
        return [types.TextContent(type="text", text="Displayed image")]
    
    else:
        raise ValueError(f"Unknown display tool: {name}")
