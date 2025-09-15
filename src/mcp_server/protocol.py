"""
Protocol definitions for micro:bit MCP server communication.

This module defines the command and response formats used for serial
communication between the MCP server and the micro:bit device.
"""

import unicodedata

# Command formats sent to micro:bit
class Commands:
    MESSAGE = "MESSAGE:"
    IMAGE = "IMAGE:"
    TEMP = "TEMP:"
    WAIT_BUTTON = "WAIT_BUTTON:"
    DISPLAY = "DISPLAY:"
    MUSIC = "MUSIC:"

# Response formats received from micro:bit
class Responses:
    STATUS = "STATUS|"
    TEMP = "TEMP|"
    BUTTON = "BUTTON|"
    BUTTON_TIMEOUT = "BUTTON_TIMEOUT|"

def parse_temperature_response(response: str) -> dict:
    """
    Parse temperature response from micro:bit.
    
    Format: TEMP|temperature|timestamp
    
    Args:
        response: Raw response string from micro:bit
        
    Returns:
        Dictionary with temperature_celsius and timestamp
    """
    if not response.startswith(Responses.TEMP):
        raise ValueError(f"Invalid temperature response: {response}")
    
    parts = response.split("|")
    if len(parts) < 3:
        raise ValueError(f"Malformed temperature response: {response}")
    
    return {
        "temperature_celsius": int(parts[1]),
        "timestamp": int(parts[2])
    }

def parse_button_response(response: str) -> dict:
    """
    Parse button response from micro:bit.
    
    Format: BUTTON|button|action|timestamp
    
    Args:
        response: Raw response string from micro:bit
        
    Returns:
        Dictionary with button, action, and timestamp
    """
    if not response.startswith(Responses.BUTTON):
        raise ValueError(f"Invalid button response: {response}")
    
    parts = response.split("|")
    if len(parts) < 4:
        raise ValueError(f"Malformed button response: {response}")
    
    return {
        "button": parts[1],
        "action": parts[2],
        "timestamp": int(parts[3])
    }

def parse_button_timeout_response(response: str) -> dict:
    """
    Parse button timeout response from micro:bit.
    
    Format: BUTTON_TIMEOUT|waited_for|timeout_duration
    
    Args:
        response: Raw response string from micro:bit
        
    Returns:
        Dictionary with waited_for and timeout_duration
    """
    if not response.startswith(Responses.BUTTON_TIMEOUT):
        raise ValueError(f"Invalid button timeout response: {response}")
    
    parts = response.split("|")
    if len(parts) < 3:
        raise ValueError(f"Malformed button timeout response: {response}")
    
    return {
        "waited_for": parts[1],
        "timeout_duration": float(parts[2])
    }

def format_message_command(message: str) -> str:
    """Format a message command for the micro:bit."""
    # Try to transliterate unicode to ASCII equivalents, then filter
    try:
        # Normalize and transliterate unicode characters
        ascii_message = unicodedata.normalize('NFKD', message)
        ascii_message = ascii_message.encode('ascii', 'ignore').decode('ascii')
    except Exception:
        # Fallback to simple ASCII filtering
        ascii_message = ''.join(char for char in message if ord(char) < 128)
    
    # Truncate if too long (200 character limit)
    if len(ascii_message) > 200:
        ascii_message = ascii_message[:200]
    
    return f"{Commands.MESSAGE}{ascii_message}"

def format_image_command(image: str) -> str:
    """Format an image command for the micro:bit."""
    return f"{Commands.IMAGE}{image}"

def format_temperature_command() -> str:
    """Format a temperature request command for the micro:bit."""
    return Commands.TEMP

def format_button_wait_command(button: str, timeout: float) -> str:
    """Format a button wait command for the micro:bit."""
    return f"{Commands.WAIT_BUTTON}{button}:{timeout}"

def format_music_command(notes: list) -> str:
    """Format a music command for the micro:bit."""
    # Join notes with comma separator
    notes_str = ",".join(notes)
    return f"{Commands.MUSIC}{notes_str}"
