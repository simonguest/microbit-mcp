import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

MICROBIT_PORT = "/dev/cu.usbmodem2114202"
MCP_SERVER_COMMAND = "uv"
MCP_SERVER_ARGS = ["run", "microbit-mcp", "-p", MICROBIT_PORT]


async def main():
    mcp_server = MCPServerStdio(
        params={"command": MCP_SERVER_COMMAND, "args": MCP_SERVER_ARGS}
    )

    await mcp_server.connect()

    agent = Agent(
        name="micro:bit agent",
        model="gpt-4o",
        instructions="You are a helpful assistant with access to a set of tools to control the micro:bit device.",
        mcp_servers=[mcp_server],
    )

    # Main prompt for the agent
    prompt = "Display the temperature from the micro:bit on the LED matrix"

    result = Runner.run_streamed(agent, prompt)

    async for event in result.stream_events():
        if event.type == "run_item_stream_event":
            if event.name == "tool_called":
                function_name = event.item.raw_item.name
                call_id = event.item.raw_item.call_id
                args = event.item.raw_item.arguments
                print(
                    f"\033[33mTool Called:\033[0m {function_name} with args {args} ({call_id})"
                )
            elif event.name == "tool_output":
                call_id = event.item.raw_item["call_id"]
                output = event.item.raw_item["output"]
                print(f"\033[33mTool Output:\033[0m {output} ({call_id})")
            elif event.name == "message_output_created":
                message = event.item.raw_item.content[0].text
                print(f"\033[33mMessage Output:\033[0m {message}")

    input("Press Enter to close the MCP Server...")
    await mcp_server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
