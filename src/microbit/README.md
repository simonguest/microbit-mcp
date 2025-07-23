# Micro:bit Firmware for MCP Server

This directory contains the firmware that needs to be flashed to your micro:bit device to enable communication with the MCP server.

## Setup Instructions

1. **Flash the firmware**: Copy the contents of `main.py` to your micro:bit device
   - You can use the [micro:bit Python editor](https://python.microbit.org/) online
   - Or use a local development environment like Mu or Thonny
   - Or copy the file directly to the micro:bit when it appears as a USB drive

2. **Connect via USB**: Connect your micro:bit to your computer using a USB cable

3. **Verify connection**: The micro:bit should show a happy face on startup, then clear the display and show "ready" status

## Communication Protocol

The micro:bit firmware implements a simple text-based protocol over serial (UART) communication at 115200 baud.

### Commands Received from MCP Server

The micro:bit listens for these commands from the MCP server:

- **`MESSAGE:<text>`** - Display a scrolling text message on the LED matrix
- **`IMAGE:<pattern>`** - Display a custom image on the LED matrix
  - Pattern format: 5 rows of 5 digits (0-9) separated by colons
  - Example: `00300:03630:36963:03630:00300` displays a star
- **`TEMP:`** - Request a temperature reading from the built-in sensor
- **`WAIT_BUTTON:<button>:<timeout>`** - Wait for a button press
  - `<button>`: "a", "b", or "any"
  - `<timeout>`: Maximum wait time in seconds

### Responses Sent to MCP Server

The micro:bit sends these response formats back to the MCP server:

- **`STATUS|<message>|<timestamp>`** - General status updates
  - Example: `STATUS|ready|1234` when firmware starts
  - Example: `STATUS|displayed:Hello|5678` after displaying a message

- **`TEMP|<celsius>|<timestamp>`** - Temperature reading response
  - Example: `TEMP|23|9012` for 23°C at timestamp 9012

- **`BUTTON|<button>|<action>|<timestamp>`** - Button press event
  - Example: `BUTTON|a|pressed|3456` when button A is pressed

- **`BUTTON_TIMEOUT|<waited_for>|<timeout_duration>`** - Button wait timeout
  - Example: `BUTTON_TIMEOUT|a|10.0` when waiting for button A times out after 10 seconds
