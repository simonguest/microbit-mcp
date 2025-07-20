import asyncio
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
            )
        ]

    @self.app.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> list[types.TextContent]:
      if name == "display_message":
        message = arguments.get("message", "")
        await self.send_to_microbit(f"DISPLAY:{message}")
        return [types.TextContent(type="text", text=f"Displayed: {message}")]
      if name == "display_image":
        image = arguments.get("image", "")
        await self.send_to_microbit(f"IMAGE:{image}")
        return [types.TextContent(type="text", text=f"Displayed image")]
      raise ValueError(f"Tool not found: {name}")
  
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