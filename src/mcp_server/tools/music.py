"""
Music tools for micro:bit MCP server.

This module contains tools for playing music on the micro:bit.
"""

import mcp.types as types
from ..protocol import format_music_command


def get_music_tools() -> list[types.Tool]:
    """Get all music-related MCP tools."""
    return [
        types.Tool(
            name="play_music",
            description="Play music on the micro:bit using an array of notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "notes": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """Array of note strings in micro:bit format. 
                        Examples: ["C4:4", "D4:4", "E4:2"] where format is "NOTE:DURATION".
                        Notes: C, D, E, F, G, A, B with optional # for sharp (e.g., C#)
                        Octaves: 0-8 (4 is middle octave)
                        Durations: 1=whole note, 2=half note, 4=quarter note, 8=eighth note, etc.
                        Use "R" for rests, e.g., "R:4" for quarter rest."""
                    }
                },
                "required": ["notes"]
            }
        )
    ]


async def handle_music_tool(name: str, arguments: dict, microbit_client) -> list[types.TextContent]:
    """
    Handle music tool calls.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        microbit_client: MicrobitClient instance
        
    Returns:
        List of TextContent responses
    """
    if name == "play_music":
        notes = arguments.get("notes", [])
        if not notes:
            return [types.TextContent(type="text", text="Error: No notes provided")]
        
        # Validate notes format (basic validation)
        for note in notes:
            if not isinstance(note, str):
                return [types.TextContent(type="text", text=f"Error: Invalid note format - all notes must be strings")]
        
        command = format_music_command(notes)
        await microbit_client.send_command(command)
        
        # Wait for completion status from micro:bit
        # The micro:bit will send a status response when music finishes playing
        return [types.TextContent(type="text", text=f"Playing {len(notes)} notes on micro:bit")]
    
    else:
        raise ValueError(f"Unknown music tool: {name}")
