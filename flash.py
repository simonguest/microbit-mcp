# type: ignore
# flash.py for micro:bit
from microbit import *

def send_status_event(message):
    """Send status event"""
    timestamp = running_time()
    # Format: STATUS|message|timestamp
    event_str = "STATUS|" + message + "|" + str(timestamp)
    print(event_str)

def process_command(cmd):
    """Process commands from MCP server"""
    if cmd.startswith("MESSAGE:"):
        message = cmd[8:]
        display.scroll(message)
        send_status_event("displayed:" + message)
    if cmd.startswith("IMAGE:"):
        image = cmd[6:]
        display.show(Image(image))
        send_status_event("displayed:" + image)

# Startup
display.show(Image.HAPPY)
sleep(1000)
display.clear()
send_status_event("ready")

# Main loop
input_buffer = ""
both_pressed = False

while True:
    # Handle commands
    if uart.any():
        char = uart.read(1)
        if char:
            if char == b'\n':
                if input_buffer:
                    process_command(input_buffer.strip())
                    input_buffer = ""
            else:
                input_buffer += char.decode('utf-8', 'ignore')
    
    sleep(50)