from langchain_openai import ChatOpenAI
import config
import requests
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import StateGraph, START
from typing import Any, Dict, List, Optional, Annotated, TypedDict
from langgraph.graph.message import BaseMessage
from operator import add
from langchain_core.messages import SystemMessage, HumanMessage

from RAG.tools import rag_tools


def main():
    llm = ChatOpenAI(
        base_url=config.REMOTE_LLM_URL,
        api_key="ollama",
        model=config.LLM_MODEL_NAME,
        temperature=0,
        timeout=600,
        streaming=True,
        default_headers={"ngrok-skip-browser-warning": "true"},
    )

    AGENT_SYSTEM_PROMPT = (
        "Kamu adalah asisten AI yang ahli dalam membuat dokumen RKS (Rencana Kerja dan Syarat-Syarat) "
        "untuk Pertamina. Kamu memiliki akses ke knowledge base berisi dokumen-dokumen RKS referensi.\n\n"
        "ALUR KERJA:\n"
        "1. TANYA JAWAB UMUM: Ketika user bertanya tentang proyek, sistem, atau detail teknis, "
        "gunakan tool `search_knowledge_base` untuk mencari informasi dari knowledge base.\n\n"
        "2. GENERATE RKS: Ketika user meminta membuat/generate RKS baru, gunakan tool "
        "`generate_rks_document`. Setelah draft di-generate, tampilkan ringkasan struktur dan "
        "tanyakan apakah ada revisi yang diinginkan.\n\n"
        "3. REVISI: Ketika user meminta perubahan pada bab tertentu dari draft RKS, gunakan tool "
        "`revise_rks_section` dengan nomor bab (I, II, III, dst) dan instruksi revisi.\n\n"
        "4. EXPORT: Ketika user sudah puas dan meminta export/simpan/unduh ke .docx, gunakan tool "
        "`export_rks_to_docx` untuk finalisasi dokumen.\n\n"
        "PENTING:\n"
        "- Selalu ground jawaban pada knowledge base\n"
        "- Gunakan Bahasa Indonesia dalam semua respons\n"
        "- Setelah generate draft, selalu tanyakan apakah ada revisi"
    )

    class AgentState(TypedDict):
        messages: Annotated[List[BaseMessage], add]

    llm_with_tools = llm.bind_tools(rag_tools)
    tools = ToolNode(rag_tools)

    def assistant(state: AgentState):
        """The assistant function that processes the agent's state and generates a response."""
        messages = state["messages"] + [SystemMessage(content=AGENT_SYSTEM_PROMPT)]
        response = llm_with_tools.invoke(messages)
        return {'messages': [response]}

    graph = StateGraph(AgentState)

    graph.add_node('assistant', assistant)
    graph.add_node('tools', tools)

    graph.add_edge(START, 'assistant')
    graph.add_conditional_edges('assistant', tools_condition)
    graph.add_edge('tools', 'assistant')
    workflow = graph.compile()

    print("\n=======================================================")
    print("🤖 RAG Agent Siap! Ketik pertanyaan Anda (atau 'exit' / 'quit' untuk keluar).")
    print("=======================================================\n")

    history = []
    while True:
        try:
            user_input = input("\nAnda: ")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in ["exit", "quit", "q"]:
                print("Terima kasih! Sampai jumpa.")
                break

            history.append(HumanMessage(content=user_input))
            print("🤖 AI sedang berpikir dan mencari dokumen relevan...")

            ai_message = workflow.invoke({'messages': history})
            latest_response = ai_message['messages'][-1].content

            # Simpan balasan AI ke riwayat
            history = ai_message['messages']
            print(f"\nAI: {latest_response}")

        except KeyboardInterrupt:
            print("\nProgram dihentikan.")
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"\n[⚠️ Koneksi Error]: Server LLM tidak dapat dijangkau.")
            print(f"   Pastikan tunnel ngrok aktif dan URL di config.py sudah benar.")
            print(f"   Detail: {str(e)[:150]}")
            # Hapus pesan terakhir dari history agar user bisa coba lagi
            if history and len(history) > 0:
                history.pop()
        except Exception as e:
            error_msg = str(e)
            if "ERR_NGROK" in error_msg or "ngrok" in error_msg.lower() or "endpoint" in error_msg.lower():
                print(f"\n[⚠️ Ngrok Offline]: Tunnel ngrok sudah tidak aktif (kedaluwarsa/mati).")
                print(f"   Langkah perbaikan:")
                print(f"   1. Jalankan ulang server LLM + ngrok di Kaggle/Colab")
                print(f"   2. Salin URL ngrok baru ke config.py")
                print(f"   3. Restart agent ini")
                # Hapus pesan terakhir dari history agar user bisa coba lagi
                if history and len(history) > 0:
                    history.pop()
            else:
                print(f"\n[Error]: {e}")

if __name__ == "__main__":
    main()
