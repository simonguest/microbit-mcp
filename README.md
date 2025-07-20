# microbit-mcp

An MCP (Model Context Protocol) server for the micro:bit that enables LLMs to interact with micro:bit devices.

## Features

### Tools
- **display_message**: Display text messages on the micro:bit LED matrix
- **display_image**: Display custom images on the micro:bit LED matrix using a 5x5 grid format

### Resources
- **microbit://temperature**: Real-time temperature readings from the micro:bit's built-in temperature sensor

## Setup

1. Flash the `main.py` program to your micro:bit
2. Connect the micro:bit via USB
3. Run the MCP server: `python server.py`
4. Configure your MCP client to connect to this server

## Temperature Resource

The temperature resource provides real-time temperature data in JSON format:

```json
{
  "temperature_celsius": 25,
  "timestamp": 1234567890
}
```

Each request to the temperature resource triggers a fresh reading from the micro:bit's sensor, ensuring current data.

## Communication Protocol

The server communicates with the micro:bit using simple text commands over serial:

- `MESSAGE:<text>` - Display text message
- `IMAGE:<pattern>` - Display image pattern (e.g., "00300:03630:36963:03630:00300")
- `TEMP:` - Request temperature reading

The micro:bit responds with status events and data in the format:
- `STATUS|<message>|<timestamp>` - General status updates
- `TEMP|<celsius>|<timestamp>` - Temperature response
