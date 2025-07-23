"""
Micro:bit serial communication client.

This module handles all serial communication with the micro:bit device,
including connection management and protocol handling.
"""

import asyncio
import serial_asyncio
from typing import Optional, Tuple

from .protocol import (
    Responses,
    parse_temperature_response,
    parse_button_response,
    parse_button_timeout_response
)


class MicrobitClient:
    """Client for communicating with micro:bit over serial connection."""
    
    def __init__(self, serial_port: str = "/dev/tty.usbmodem2114202"):
        """
        Initialize the micro:bit client.
        
        Args:
            serial_port: Serial port path for micro:bit connection
        """
        self.serial_port = serial_port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
    
    async def setup_serial_connection(self) -> None:
        """
        Establish serial connection to the micro:bit.
        
        Raises:
            Exception: If connection fails
        """
        try:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.serial_port, 
                baudrate=115200
            )
            print(f"Connected to micro:bit on {self.serial_port}")
        except Exception as e:
            print(f"Failed to connect to micro:bit: {e}")
            raise
    
    async def send_command(self, command: str) -> None:
        """
        Send a command to the micro:bit.
        
        Args:
            command: Command string to send
            
        Raises:
            Exception: If no connection is established
        """
        if not self.writer:
            raise Exception("Serial connection not established")
        
        self.writer.write(f"{command}\n".encode())
        await self.writer.drain()
    
    async def read_temperature_response(self) -> dict:
        """
        Read and parse temperature response from micro:bit.
        
        Returns:
            Dictionary with temperature data
            
        Raises:
            Exception: If no connection is established
        """
        if not self.reader:
            raise Exception("Serial connection not established")
        
        while True:
            line = await self.reader.readline()
            if line:
                response = line.decode('utf-8').strip()
                if response.startswith(Responses.TEMP):
                    return parse_temperature_response(response)
    
    async def read_button_response(self, expected_button: str) -> dict:
        """
        Read and parse button response from micro:bit.
        
        Args:
            expected_button: The button we're waiting for ("a", "b", or "any")
            
        Returns:
            Dictionary with button press data
            
        Raises:
            Exception: If no connection is established
        """
        if not self.reader:
            raise Exception("Serial connection not established")
        
        while True:
            line = await self.reader.readline()
            if line:
                response = line.decode('utf-8').strip()
                
                if response.startswith(Responses.BUTTON):
                    button_data = parse_button_response(response)
                    button_pressed = button_data["button"]
                    action = button_data["action"]
                    
                    # Check if this is the button we're waiting for
                    if (expected_button == "any" or 
                        expected_button == button_pressed) and action == "pressed":
                        return {
                            "button_pressed": button_pressed,
                            "timeout": False,
                            "timestamp": button_data["timestamp"],
                            "waited_for": expected_button
                        }
                
                elif response.startswith(Responses.BUTTON_TIMEOUT):
                    timeout_data = parse_button_timeout_response(response)
                    return {
                        "button_pressed": None,
                        "timeout": True,
                        "timestamp": None,
                        "waited_for": timeout_data["waited_for"],
                        "timeout_duration": timeout_data["timeout_duration"]
                    }
    
    async def get_temperature(self) -> dict:
        """
        Request and get temperature reading from micro:bit.
        
        Returns:
            Dictionary with temperature data
            
        Raises:
            Exception: If connection fails or timeout occurs
        """
        if not self.reader or not self.writer:
            raise Exception("Serial connection not established")
        
        # Send temperature request
        await self.send_command("TEMP:")
        
        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(
                self.read_temperature_response(), 
                timeout=5.0
            )
            return response
        except asyncio.TimeoutError:
            raise Exception("Timeout waiting for temperature response from micro:bit")
    
    async def wait_for_button_press(self, button: str, timeout: float) -> dict:
        """
        Wait for a button press on the micro:bit.
        
        Args:
            button: Button to wait for ("a", "b", or "any")
            timeout: Maximum time to wait in seconds
            
        Returns:
            Dictionary with button press result
            
        Raises:
            Exception: If connection fails
        """
        if not self.reader or not self.writer:
            raise Exception("Serial connection not established")
        
        # Send button wait request
        await self.send_command(f"WAIT_BUTTON:{button}:{timeout}")
        
        # Wait for response with timeout (add 1 second buffer)
        try:
            response = await asyncio.wait_for(
                self.read_button_response(button), 
                timeout=timeout + 1.0
            )
            return response
        except asyncio.TimeoutError:
            return {
                "button_pressed": None,
                "timeout": True,
                "timestamp": None,
                "waited_for": button,
                "timeout_duration": timeout
            }
    
    def is_connected(self) -> bool:
        """Check if serial connection is established."""
        return self.reader is not None and self.writer is not None
    
    async def close(self) -> None:
        """Close the serial connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None
            self.reader = None
