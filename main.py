"""
RKS Agent — Interactive CLI runner
===================================
Run with:
    python main.py

Uses the compiled graph from agent.py with MemorySaver so state
(including rks_fields and rks_draft_json) persists across turns.

The interrupt() in `review_rks` is handled here: after the graph
pauses, we read the user's next input and resume with Command(resume=...).
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from agent import graph


def run():
    config = {"configurable": {"thread_id": "session-1"}}

    print("=" * 60)
    print(" RKS Assistant — PT Pertamina")
    print(" Ketik 'exit' atau 'quit' untuk keluar.")
    print("=" * 60)
    print()

    while True:
        # ── Get user input ──────────────────────────────────────
        try:
            user_input = input("Anda: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Agent] Sampai jumpa!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "keluar"}:
            print("[Agent] Sampai jumpa!")
            break

        # ── Invoke graph ─────────────────────────────────────────
        try:
            state = graph.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
            )
        except Exception as e:
            print(f"[Error] {e}\n")
            continue

        # ── Print the last AI message ────────────────────────────
        _print_last_ai(state)

        # ── Handle interrupt (review_rks pause) ──────────────────
        # Check if the graph is paused at an interrupt node
        snapshot = graph.get_state(config)
        if snapshot.next and "review_rks" in snapshot.next:
            # Graph is waiting for human approval — loop to read input
            while True:
                try:
                    review_input = input("Anda: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not review_input:
                    continue

                # Resume the graph with the user's decision
                try:
                    state = graph.invoke(
                        Command(resume=review_input),
                        config=config,
                    )
                except Exception as e:
                    print(f"[Error] {e}\n")
                    break

                _print_last_ai(state)

                # Check if we're paused again (e.g. revision requested → re-generated → paused again)
                snapshot = graph.get_state(config)
                if not (snapshot.next and "review_rks" in snapshot.next):
                    break


def _print_last_ai(state: dict):
    """Print the last AI message from the graph state."""
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.__class__.__name__ in ("AIMessage", "ChatMessage"):
            print(f"\nAgent: {msg.content}\n")
            return
    # Fallback: print the very last message regardless of type
    if messages:
        last = messages[-1]
        content = last.content if hasattr(last, "content") else str(last)
        print(f"\nAgent: {content}\n")


if __name__ == "__main__":
    run()
