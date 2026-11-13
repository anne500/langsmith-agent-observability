from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


@tool
def current_time() -> str:
    """Return the current local date and time."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


@tool
def word_count(text: str) -> int:
    """Count the words in text by splitting on whitespace."""
    return len(text.split())


def main() -> None:
    agent = create_agent(
        model=ChatOllama(model="qwen3.5:4b", temperature=0, reasoning=False),
        tools=[current_time, word_count],
        system_prompt=(
            "Use current_time for requests about the current local date or time. "
            "Use word_count when asked to count words. "
            "Answer directly when neither tool is needed."
        ),
    )

    print("Local agent ready. Type exit to quit.")
    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue

        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )

        for message in result["messages"]:
            if isinstance(message, AIMessage):
                for call in message.tool_calls:
                    print(f"[tool call] {call['name']} {call['args']}")

        print(f"Answer: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    main()