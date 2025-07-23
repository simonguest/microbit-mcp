"""
Input tools for micro:bit MCP server.

This module contains tools for handling input from the micro:bit (buttons, etc.).
"""

import json
import mcp.types as types


def get_input_tools() -> list[types.Tool]:
    """Get all input-related MCP tools."""
    return [
        types.Tool(
            name="wait_for_button_press",
            description="Wait for a button press on the micro:bit",
            inputSchema={
                "type": "object",
                "properties": {
                    "button": {
                        "type": "string",
                        "enum": ["a", "b"],
                        "description": "Which specific button to wait for. If not specified, waits for any button press."
                    },
                    "timeout": {
                        "type": "number",
                        "default": 10.0,
                        "description": "Maximum time to wait in seconds"
                    }
                },
                "required": []
            }
        )
    ]


async def handle_input_tool(name: str, arguments: dict, microbit_client) -> list[types.TextContent]:
    """
    Handle input tool calls.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        microbit_client: MicrobitClient instance
        
    Returns:
        List of TextContent responses
    """
    if name == "wait_for_button_press":
        button = arguments.get("button", "any")
        timeout = arguments.get("timeout", 10.0)
        result = await microbit_client.wait_for_button_press(button, timeout)
        return [types.TextContent(type="text", text=json.dumps(result))]
    
    else:
        raise ValueError(f"Unknown input tool: {name}")
