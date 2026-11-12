"""Run the CRUD scenarios using LangChain and the remote MCP tools."""
import asyncio

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from rich.console import Console
from rich.panel import Panel

from backend.config import Settings
from backend.client.scenarios import Scenario, scenarios_list

console = Console()


async def build_agent(settings: Settings):
    client = MultiServerMCPClient({
        "items": {"url": settings.mcp_host_url, "transport": settings.mcp_transport}
    })
    tools = await client.get_tools()
    kwargs = {}
    if settings.openai_api_key:
        kwargs["api_key"] = settings.openai_api_key.get_secret_value()
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    model = init_chat_model(settings.llm_model, **kwargs)
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You manage inventory using the provided MCP tools. Always call tools "
            "to read or change items; never invent results or item IDs. "
            "Only perform changes explicitly requested by the user."
        ),
    )


async def run_scenario(agent, scenario: Scenario, messages: list):
    result = await agent.ainvoke({
        "messages": [*messages, {"role": "user", "content": scenario.prompt}]
    })
    return result["messages"]


async def main():
    settings = Settings()
    console.print(f"MCP host: {settings.mcp_host_url}")
    agent = await build_agent(settings)
    messages = []
    for scenario in scenarios_list:
        console.rule(f"Scenario: {scenario.name}")
        console.print(Panel(scenario.prompt, title="Prompt"))
        with console.status("Running…"):
            messages = await run_scenario(agent, scenario, messages)
        console.print(Panel(str(messages[-1].content), title="Agent"))


if __name__ == "__main__":
    asyncio.run(main())
