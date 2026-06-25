from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

from .tools import query_casper_blockchain, _get_tools_description
from .mcp_client import list_tools

NETWORK = "testnet"

SYSTEM_PROMPT = """You are Casper Agentic Bot, an AI assistant for the Casper blockchain ({network}).

You have access to the Casper MCP Server with these tools (87 total):

{tools_description}

Rules:
1. For greetings or non-blockchain questions, answer directly without calling tools.
2. For blockchain queries, ALWAYS call query_casper_blockchain with the correct tool_name and JSON arguments.
3. Convert motes to CSPR: 1 CSPR = 1,000,000,000 motes.
4. Format data cleanly and concisely.
5. Never make up data — use the tool.
6. If a tool errors, explain it helpfully.

Examples:
- "Network status?" → query_casper_blockchain(tool_name="GetNetworkStatus")
- "Latest blocks" → query_casper_blockchain(tool_name="GetLatestBlocks", arguments={{"limit": 5}})
- "Account 01abc..." → query_casper_blockchain(tool_name="GetAccountInfo", arguments={{"account_hash": "01abc..."}})
"""


async def build_agent():
    tools_desc = await _get_tools_description()
    system_prompt = SYSTEM_PROMPT.format(network=NETWORK, tools_description=tools_desc)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    tools = [query_casper_blockchain]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SystemMessage(content=system_prompt),
        version="v2",
    )
    return agent


async def run_agent(user_input: str):
    agent = await build_agent()
    result = await agent.ainvoke({"messages": [("human", user_input)]})
    messages = result.get("messages", [])
    # Return the last AI message content
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "ai" and msg.content:
            return msg.content
    return "I couldn't process that request."
