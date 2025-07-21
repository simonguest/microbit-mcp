import asyncio
import json
import serial_asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

class MicrobitMCPServer:
  def __init__(self, serial_port="/dev/tty.usbmodem2114202"):
    self.app = Server("microbit-server")
    self.serial_port = serial_port
  
    @self.app.list_tools()
    async def list_tools() -> list[types.Tool]:
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
                  }
               }
            ),
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

    @self.app.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> list[types.TextContent]:
      if name == "display_message":
        message = arguments.get("message", "")
        await self.send_to_microbit(f"MESSAGE:{message}")
        return [types.TextContent(type="text", text=f"Displayed: {message}")]
      if name == "display_image":
        image = arguments.get("image", "")
        await self.send_to_microbit(f"IMAGE:{image}")
        return [types.TextContent(type="text", text=f"Displayed image")]
      if name == "wait_for_button_press":
        button = arguments.get("button", "any")
        timeout = arguments.get("timeout", 10.0)
        result = await self.wait_for_button_press(button, timeout)
        return [types.TextContent(type="text", text=json.dumps(result))]
      raise ValueError(f"Tool not found: {name}")

    @self.app.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri="microbit://temperature",
                name="Temperature",
                description="Current temperature reading from micro:bit sensor",
                mimeType="application/json"
            )
        ]

    @self.app.read_resource()
    async def read_resource(uri: str) -> str:
        if str(uri) == "microbit://temperature":
          temperature_data = await self.get_temperature()
          return json.dumps(temperature_data)
        raise ValueError(f"Resource not found: {uri}")
  
  # micro:bit specific functions
  async def setup_serial_connection(self):
      try:
          self.reader, self.writer = await serial_asyncio.open_serial_connection(
              url=self.serial_port, 
              baudrate=115200
          )
          print(f"Connected to micro:bit on {self.serial_port}")
                    
      except Exception as e:
          print(f"Failed to connect to micro:bit: {e}")

  async def send_to_microbit(self, command):
    if self.writer:
        self.writer.write(f"{command}\n".encode())
        await self.writer.drain()

  async def get_temperature(self):
    """Request temperature reading from micro:bit"""
    if not self.reader or not self.writer:
        raise Exception("Serial connection not established")
    
    # Send temperature request
    await self.send_to_microbit("TEMP:")
    
    # Wait for response with timeout
    try:
        response = await asyncio.wait_for(self.read_temperature_response(), timeout=5.0)
        return response
    except asyncio.TimeoutError:
        raise Exception("Timeout waiting for temperature response from micro:bit")

  async def read_temperature_response(self):
    """Read and parse temperature response from micro:bit"""
    while True:
        line = await self.reader.readline()
        if line:
            response = line.decode('utf-8').strip()
            if response.startswith("TEMP|"):
                # Parse: TEMP|temperature|timestamp
                parts = response.split("|")
                if len(parts) >= 3:
                    temperature_celsius = int(parts[1])
                    timestamp = int(parts[2])
                    return {
                        "temperature_celsius": temperature_celsius,
                        "timestamp": timestamp
                    }
        # Continue reading if not a temperature response

  async def wait_for_button_press(self, button, timeout):
    """Wait for a button press on the micro:bit"""
    if not self.reader or not self.writer:
        raise Exception("Serial connection not established")
    
    # Send button wait request
    await self.send_to_microbit(f"WAIT_BUTTON:{button}:{timeout}")
    
    # Wait for response with timeout
    try:
        response = await asyncio.wait_for(self.read_button_response(button), timeout=timeout + 1.0)
        return response
    except asyncio.TimeoutError:
        return {
            "button_pressed": None,
            "timeout": True,
            "timestamp": None,
            "waited_for": button,
            "timeout_duration": timeout
        }

  async def read_button_response(self, expected_button):
    """Read and parse button response from micro:bit"""
    while True:
        line = await self.reader.readline()
        if line:
            response = line.decode('utf-8').strip()
            if response.startswith("BUTTON|"):
                # Parse: BUTTON|button|action|timestamp
                parts = response.split("|")
                if len(parts) >= 4:
                    button_pressed = parts[1]
                    action = parts[2]
                    timestamp = int(parts[3])
                    
                    # Check if this is the button we're waiting for
                    if (expected_button == "any" or 
                        expected_button == button_pressed) and action == "pressed":
                        return {
                            "button_pressed": button_pressed,
                            "timeout": False,
                            "timestamp": timestamp,
                            "waited_for": expected_button
                        }
            elif response.startswith("BUTTON_TIMEOUT|"):
                # Parse: BUTTON_TIMEOUT|waited_for|timeout_duration
                parts = response.split("|")
                if len(parts) >= 3:
                    return {
                        "button_pressed": None,
                        "timeout": True,
                        "timestamp": None,
                        "waited_for": parts[1],
                        "timeout_duration": float(parts[2])
                    }
        # Continue reading if not a button response

async def main():
    microbit_server = MicrobitMCPServer("/dev/tty.usbmodem2114202")
    await microbit_server.setup_serial_connection()
    await microbit_server.send_to_microbit(f"DISPLAY:MCP")
    
    async with stdio_server() as streams:
        await microbit_server.app.run(
            streams[0],
            streams[1],
            microbit_server.app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
