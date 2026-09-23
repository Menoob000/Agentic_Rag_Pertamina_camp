from langgraph.graph import  StateGraph
from langgraph.graph.message import add_messages 
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_openrouter import ChatOpenRouter
from typing import List, Dict, Any, TypedDict, Optional, Annotated, Literal
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from docling_core.types.doc import DoclingDocument
from dotenv import load_dotenv
from RAG.vector_store import  Vector_Store
from langchain_core.documents import Document
from pydantic import BaseModel, Field
load_dotenv()


class AgentState(TypedDict): 
    messages : Annotated[List[BaseMessage], add_messages]
    refined_query : str
    supporting_docs : Optional[DoclingDocument]
    kb_context : List[Document]
    source_used : str


class RouteDecision(BaseModel):
    route: Literal["kb", "direct", "document_maker"] = Field(
        description="Use kb for questions needing RKS docs; direct for greetings/simple chat, document_maker if asked to generate a document."
    )


class EvidenceGrade(BaseModel):
    grade: Literal["good", "weak"] = Field(
        description="good means evidence can answer the question; weak means not enough evidence."
    )

llm = ChatOpenRouter(
        model="deepseek/deepseek-v4.1-flash",
        temperature=0,
    )

router_llm = llm.with_structured_output(RouteDecision, method="json_mode")

@tool
def retrieval_tool(state : AgentState) -> AgentState: 
    query = state["messages"][-1].content
    print(query)
    retriever = Vector_Store._retriever_()
    retrieved_context = retriever.invoke(query)
    return {'kb_context' : retrieved_context}

def route_question(state:AgentState): 
    question = state['messages'][-1]
    print(question)

    decision = router_llm.invoke(f'''
You are a router for an Agentic RAG assistant.

Route to "kb" if the user asks about:
- RKS (Rencana Kerja dan Syarat)
- Struktur RKS

Route to "document_maker" also if you are asked to generate a document.

Route to "direct" only for greetings, thanks, or very simple conversation.

Question:
{question}

Return your response as valid JSON.
Example:
{{"route": "kb"}}
''')

    print("[Router]", decision.route)

    return {
        # "current_query": question,
        "source_used": decision.route,
    }

def route_after_router(state: AgentState) -> Literal["retrieve_kb", "direct_answer", "document_maker"]:
    if state["source_used"] == "kb":
        return "retrieve_kb"
    elif state['source_used'] == 'document_maker':
        return "document_maker"
    return "direct_answer"

tools = [retrieval_tool]
llm_with_tools = llm.bind_tools(tools)

def doc_maker(state: AgentState): 
    messages = state['messages']
    query = state['messages'][-1].content
    prompt = """
        Generate draft RKS (Rencana Kerja dan Syarat-Syarat) secara utuh berdasarkan knowledge base.

        Gunakan konteks berikut ini sebagai acuan untuk struktur dokumen : 
        {context}

        Apabila dokument tersebut masih belum cukup bagi anda untuk memahami struktur dokumen yang diinginkan,
        lakukan tool_call untuk memanggil tool retrieval dan menambah context dokumen.

        Struktur dan konten diekstrak secara dinamis dari dokumen RKS sejenis.
        AI secara otomatis menentukan judul pekerjaan, level risiko CSMS, 
        nama unit perusahaan, dan struktur bab yang sesuai jenis pekerjaan.
        Gunakan tool ini ketika user meminta untuk membuat/generate RKS baru.
        
        Berikut adalah query dari user sejauh ini: 
        {query}
        """
    response = llm_with_tools.invoke(prompt.format(context=state['kb_context'] ,query=messages))

