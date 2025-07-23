# type: ignore
# main.py for micro:bit
from microbit import *

def send_status_event(message):
    """Send status event"""
    timestamp = running_time()
    # Format: STATUS|message|timestamp
    event_str = "STATUS|" + message + "|" + str(timestamp)
    print(event_str)

def process_command(cmd):
    """Process commands from MCP server"""
    global waiting_for_button, wait_button_type, wait_start_time, wait_timeout
    
    if cmd.startswith("MESSAGE:"):
        message = cmd[8:]
        display.scroll(message)
        send_status_event("displayed:" + message)
    if cmd.startswith("IMAGE:"):
        image = cmd[6:]
        display.show(Image(image))
        send_status_event("displayed:" + image)
    if cmd.startswith("TEMP:"):
        temp_celsius = temperature()
        timestamp = running_time()
        # Format: TEMP|temperature|timestamp
        temp_response = "TEMP|" + str(temp_celsius) + "|" + str(timestamp)
        print(temp_response)
    if cmd.startswith("WAIT_BUTTON:"):
        # Parse: WAIT_BUTTON:button:timeout
        parts = cmd.split(":")
        if len(parts) >= 3:
            wait_button_type = parts[1]  # "a", "b", or "any"
            wait_timeout = float(parts[2])
            waiting_for_button = True
            wait_start_time = running_time()
            send_status_event("waiting_for_button:" + wait_button_type)

def send_button_event(button, action):
    """Send button event"""
    timestamp = running_time()
    # Format: BUTTON|button|action|timestamp
    event_str = "BUTTON|" + button + "|" + action + "|" + str(timestamp)
    print(event_str)

def send_button_timeout():
    """Send button timeout event"""
    # Format: BUTTON_TIMEOUT|waited_for|timeout_duration
    event_str = "BUTTON_TIMEOUT|" + wait_button_type + "|" + str(wait_timeout)
    print(event_str)

# Global variables for button waiting
waiting_for_button = False
wait_button_type = ""
wait_start_time = 0
wait_timeout = 0

# Button state tracking
button_a_was_pressed = False
button_b_was_pressed = False

# Startup
display.show(Image.HAPPY)
sleep(1000)
display.clear()
send_status_event("ready")

# Main loop
input_buffer = ""

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
    
    # Button monitoring when waiting for button press
    if waiting_for_button:
        # Check for timeout
        current_time = running_time()
        if (current_time - wait_start_time) >= (wait_timeout * 1000):  # Convert to milliseconds
            waiting_for_button = False
            send_button_timeout()
        else:
            # Check button states
            button_a_pressed = button_a.is_pressed()
            button_b_pressed = button_b.is_pressed()
            
            # Detect button A press (edge detection)
            if button_a_pressed and not button_a_was_pressed:
                if wait_button_type == "a" or wait_button_type == "any":
                    waiting_for_button = False
                    send_button_event("a", "pressed")
            
            # Detect button B press (edge detection)
            if button_b_pressed and not button_b_was_pressed:
                if wait_button_type == "b" or wait_button_type == "any":
                    waiting_for_button = False
                    send_button_event("b", "pressed")
            
            # Update button state tracking
            button_a_was_pressed = button_a_pressed
            button_b_was_pressed = button_b_pressed
    else:
        # Reset button state tracking when not waiting
        button_a_was_pressed = button_a.is_pressed()
        button_b_was_pressed = button_b.is_pressed()
    
    sleep(50)
