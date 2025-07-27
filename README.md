# microbit-mcp

An MCP (Model Context Protocol) server for the micro:bit that enables LLMs to interact with micro:bit devices.

## Features

### Tools
- **display_message**: Display text messages on the micro:bit LED matrix
- **display_image**: Display custom images on the micro:bit LED matrix using a 5x5 grid format
- **wait_for_button_press**: Wait for a button press on the micro:bit with optional button selection and timeout
- **get_temperature**: Return the real-time reading from the micro:bit's built-in temperature sensor

## Setup

1. Flash the `src/microbit/main.py` program to your micro:bit
2. Connect the micro:bit via USB
3. Run the MCP server: `uv run microbit-mcp`
4. Configure your MCP client to connect to this server

### Command Line Options

The MCP server supports several command-line options for configuration:

```bash
# Use default port (recommended for most users)
uv run microbit-mcp

# Specify a custom serial port
uv run microbit-mcp --port /dev/tty.usbmodem1234
uv run microbit-mcp -p COM3  # Windows example

# List available serial ports to find your micro:bit
uv run microbit-mcp --list-ports

# Show help and usage information
uv run microbit-mcp --help
```

#### Finding Your micro:bit Port

If you're unsure which port your micro:bit is using, run:

```bash
uv run microbit-mcp --list-ports
```

This will show all available serial ports and highlight likely micro:bit devices. The output will look something like:

```
Available Serial Ports:

Likely micro:bit devices:
  /dev/cu.usbmodem2114202 - "BBC micro:bit CMSIS-DAP"
    Hardware ID: USB VID:PID=0D28:0204

All serial ports (3 found):
  /dev/cu.usbmodem2114202 - "BBC micro:bit CMSIS-DAP" ⭐
  /dev/cu.Bluetooth-Incoming-Port - Bluetooth-Incoming-Port
  /dev/cu.usbserial-A1B2C3D4 - USB Serial Device

Recommended: Use /dev/cu.usbmodem2114202 for your micro:bit
```

The ⭐ symbol indicates ports that are likely micro:bit devices.

## Button Press Tool

The `wait_for_button_press` tool allows you to wait for button presses on the micro:bit with flexible configuration options.

### Parameters (all optional)
- **button** (optional): Which specific button to wait for
  - `"a"` - Wait only for button A
  - `"b"` - Wait only for button B
  - If not specified, waits for any button press
- **timeout** (optional): Maximum time to wait in seconds (default: 10.0)

### Usage Examples

**Wait for any button with default timeout:**
```json
{}
```

**Wait for any button with custom timeout:**
```json
{
  "timeout": 5.0
}
```

**Wait for specific button A:**
```json
{
  "button": "a"
}
```

**Wait for button B with custom timeout:**
```json
{
  "button": "b",
  "timeout": 3.0
}
```

### Response Format

**Success response:**
```json
{
  "button_pressed": "a",
  "timeout": false,
  "timestamp": 12345,
  "waited_for": "any"
}
```

**Timeout response:**
```json
{
  "button_pressed": null,
  "timeout": true,
  "timestamp": null,
  "waited_for": "any",
  "timeout_duration": 10.0
}
```

## Communication Protocol

The server communicates with the micro:bit using simple text commands over serial:

- `MESSAGE:<text>` - Display text message
- `IMAGE:<pattern>` - Display image pattern (e.g., "00300:03630:36963:03630:00300")
- `TEMP:` - Request temperature reading
- `WAIT_BUTTON:<button>:<timeout>` - Wait for button press (e.g., "WAIT_BUTTON:a:10" or "WAIT_BUTTON:any:5")

The micro:bit responds with status events and data in the format:
- `STATUS|<message>|<timestamp>` - General status updates
- `TEMP|<celsius>|<timestamp>` - Temperature response
- `BUTTON|<button>|<action>|<timestamp>` - Button press event (e.g., "BUTTON|a|pressed|12345")
- `BUTTON_TIMEOUT|<waited_for>|<timeout_duration>` - Button wait timeout

## Using the MCP Inspector

To test/debug the server, you can also use the MCP Inspector. To launch the inspector:

1. Run `npx @modelcontextprotocol/inspector` (recommend LTS-version of Node)
2. The inspector will launch in a new browser window.
3. Set transport type to STDIO, command is the full path to your uv binary (e.g., `/Users/yourname/.local/bin/uv`), arguments is `--directory /full-path-to-the-mcp-server run microbit-mcp`
4. Click on the Connect button to connect and inspect the MCP server.

## Project Structure

The project is organized as follows:

```
microbit-mcp/
├── src/
│   ├── mcp_server/             # Main MCP server package
│   │   ├── server.py           # Main server entry point
│   │   ├── microbit_client.py  # Serial communication with micro:bit
│   │   ├── protocol.py         # Command/response protocol definitions
│   │   └── tools/              # MCP tools organized by category
│   │       ├── display.py      # Display-related tools
│   │       ├── sensors.py      # Sensor-related tools
│   │       └── input.py        # Input-related tools
│   ├── microbit/               # Micro:bit firmware
│   │   ├── main.py            # Firmware to flash to micro:bit
│   │   └── README.md          # Micro:bit setup instructions
│   └── examples/               # Usage examples
└── README.md                   # This file
```
