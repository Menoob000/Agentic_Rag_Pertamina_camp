"""
RKS Agent — Interactive CLI runner
===================================
Run with:
    python main.py

Two interrupt() nodes pause the graph mid-execution:
  - upload_boq  : graph pauses waiting for a PDF path (or "skip")
  - review_rks  : graph pauses waiting for approval / revision instructions

When paused, snapshot.interrupts[0].value contains the question the node
asked via interrupt(message). We print that before reading user input.

For clarify_rks (not an interrupt node), the agent emits an AIMessage
asking for one field at a time, then returns to __end__. The outer loop
picks up the next user message normally.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from agent import graph

# Nodes that use interrupt() — need Command(resume=...) to continue
INTERRUPT_NODES = {"upload_boq", "review_rks"}

# Human-readable prompt labels shown before input() per context
PROMPT_LABELS = {
    "upload_boq":  "📂 Path file / skip",
    "review_rks":  "✍️  Keputusan Anda   ",
    "clarify":     "📝 Jawaban Anda     ",
    "default":     "Anda               ",
}


def run():
    config = {"configurable": {"thread_id": "session-1"}}

    print("=" * 60)
    print("  RKS Assistant — PT Pertamina")
    print("  Ketik 'exit' atau 'quit' untuk keluar.")
    print("=" * 60)
    print()

    while True:
        # ── Detect if we're mid-clarification (state already has rks_fields) ──
        snapshot = graph.get_state(config)
        in_clarification = (
            snapshot.values.get("rks_fields")
            and snapshot.values.get("source_used") in ("document_maker", "document_maker_clarify")
        ) if snapshot.values else False

        prompt_label = PROMPT_LABELS["clarify"] if in_clarification else PROMPT_LABELS["default"]

        # ── Get user input ──────────────────────────────────────
        try:
            user_input = input(f"{prompt_label}: ").strip()
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

        _print_last_ai(state)

        # ── Handle interrupt() pauses ─────────────────────────────
        _handle_interrupts(config)


def _handle_interrupts(config: dict):
    """
    After each graph.invoke(), check if the graph paused at an interrupt() call.
    - Print the interrupt message (the question the node asked).
    - Show a context-specific input prompt.
    - Resume with Command(resume=user_input).
    - Loop until the graph reaches __end__ or no more interrupts.
    """
    while True:
        snapshot = graph.get_state(config)

        # Check if paused at one of our interrupt nodes
        paused_at = set(snapshot.next) & INTERRUPT_NODES if snapshot.next else set()
        if not paused_at:
            break

        # Print the question the node asked via interrupt(message)
        if snapshot.interrupts:
            question = snapshot.interrupts[0].value
            print(f"\nAgent: {question}\n")

        # Show a descriptive prompt so the user knows what type of input is needed
        node_name = next(iter(paused_at))
        prompt_label = PROMPT_LABELS.get(node_name, PROMPT_LABELS["default"])

        try:
            user_input = input(f"{prompt_label}: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        try:
            state = graph.invoke(
                Command(resume=user_input),
                config=config,
            )
        except Exception as e:
            print(f"[Error] {e}\n")
            break

        _print_last_ai(state)


def _print_last_ai(state: dict):
    """Print the last AI message from the graph state."""
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.__class__.__name__ in ("AIMessage", "ChatMessage"):
            print(f"\nAgent: {msg.content}\n")
            return
    if messages:
        last = messages[-1]
        content = last.content if hasattr(last, "content") else str(last)
        print(f"\nAgent: {content}\n")


if __name__ == "__main__":
    run()
