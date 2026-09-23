from langchain_openrouter import ChatOpenRouter
from typing import Literal
from langchain.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph.message import BaseMessage
from langchain_tavily import TavilySearch
from typing import List, Dict, Any, TypedDict, Optional, Annotated
from operator import add
from langchain_core.documents import Document

from dotenv import load_dotenv

load_dotenv()

def main():

    @tool
    def search(query: str):
        """Call to surf the web."""
        tavily_search_tool = TavilySearch()
        return tavily_search_tool.invoke(query)

    tools = [search]

    model = ChatOpenRouter(
        model="deepseek/deepseek-v4.1-flash",
        temperature=0,
    )

    # def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    #     messages = state['messages']
    #     last_message = messages[-1]
    #     if last_message.tool_calls:
    #         return "tools"
    #     return "__end__"

    class AgentState(TypedDict): 
        messages : Annotated[List[BaseMessage], add]

    llm_with_tools = model.bind_tools(tools)
    def call_model(state: AgentState):
        messages = state['messages']
        system = f"""You are an intelligent agent that will use the tools provided to you \n" \
        "to help the user get their answer as factualy as possible. " \
        "You are provided the following tools : " \
        "{tools}"""

        message = [SystemMessage(system)] + messages 
        # Invoking `model` will automatically infer the correct tracing context
        response = llm_with_tools.invoke(message)
        return {"messages": [response]}

    tool_node = ToolNode(tools)    
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_edge("__start__", "agent")
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
    )
    workflow.add_edge("tools", 'agent')

    app = workflow.compile()

    final_state = app.invoke(
        {"messages": [HumanMessage(content="Who won the latest world cup")]},
        config={"configurable": {"thread_id": 42}}
    )

    print(final_state["messages"][-1].content)

if __name__ == "__main__":
    main()
