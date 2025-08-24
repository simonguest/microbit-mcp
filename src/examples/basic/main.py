import gradio as gr
from gradio import ChatMessage

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

MICROBIT_PORT = "/dev/cu.usbmodem102"
MCP_SERVER_COMMAND = "uv"
MCP_SERVER_ARGS = ["run", "microbit-mcp", "-p", MICROBIT_PORT]

mcp_server = MCPServerStdio(
    params={"command": MCP_SERVER_COMMAND, "args": MCP_SERVER_ARGS}
)

agent = Agent(
    name="micro:bit agent",
    model="gpt-4o",
    instructions="You are a helpful assistant with access to a set of tools to control the micro:bit device.",
    mcp_servers=[mcp_server],
)

async def chat_with_agent(user_msg: str, history: list):
    if mcp_server.session is None:
        await mcp_server.connect()
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    messages.append({"role": "user", "content": user_msg})
    responses = []
    reply_created = False
    active_agent = None

    result = Runner.run_streamed(agent, messages)
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            if event.data.type == "response.output_text.delta":
                if not reply_created:
                    responses.append(ChatMessage(role="assistant", content=""))
                    reply_created = True
                responses[-1].content += event.data.delta
        elif event.type == "agent_updated_stream_event":
            active_agent = event.new_agent.name
            responses.append(
                ChatMessage(
                    content=event.new_agent.name,
                    metadata={"title": "Agent Now Running", "id": active_agent},
                )
            )
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                if event.item.raw_item.type == "file_search_call":
                    responses.append(
                        ChatMessage(
                            content=f"Query used: {event.item.raw_item.queries}",
                            metadata={
                                "title": "File Search Completed",
                                "parent_id": active_agent,
                            },
                        )
                    )
                else:
                    tool_name = getattr(event.item.raw_item, "name", "unknown_tool")
                    tool_args = getattr(event.item.raw_item, "arguments", {})
                    responses.append(
                        ChatMessage(
                            content=f"Calling tool {tool_name} with arguments {tool_args}",
                            metadata={"title": "Tool Call", "parent_id": active_agent},
                        )
                    )
            if event.item.type == "tool_call_output_item":
                responses.append(
                    ChatMessage(
                        content=f"Tool output: '{event.item.raw_item['output']}'",
                        metadata={"title": "Tool Output", "parent_id": active_agent},
                    )
                )
            if event.item.type == "handoff_call_item":
                responses.append(
                    ChatMessage(
                        content=f"Name: {event.item.raw_item.name}",
                        metadata={
                            "title": "Handing Off Request",
                            "parent_id": active_agent,
                        },
                    )
                )
        yield responses

demo = gr.ChatInterface(
    chat_with_agent,
    title="micro:bit MCP",
    theme=gr.themes.Soft(
        primary_hue="red", secondary_hue="slate", font=[gr.themes.GoogleFont("Inter")]
    ),
    examples=[
        "Can you display a 'heart' on the display?",
    ],
    submit_btn=True,
    flagging_mode="manual",
    flagging_options=["Like", "Spam", "Inappropriate", "Other"],
    type="messages",
    save_history=False,
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)