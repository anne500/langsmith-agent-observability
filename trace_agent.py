import os
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

class DemoToolError(RuntimeError):
    """An intentional failure used to verify tracing."""


@tool
def fail_demo() -> str:
    """Run the controlled failure test when explicitly requested."""
    raise DemoToolError("Simulated CI evidence lookup failure")


@tool
def lookup_ci_log(build_id: str) -> str:
    """Look up synthetic CI evidence for a build ID."""
    build_id = build_id.strip().upper()
    if build_id == "MAPLE-207" and os.getenv("BRI_HIDE_CI_LOG") != "1":
        return "ERROR [signing] Signing certificate expired."
    return f"No CI log available for {build_id}."

def main() -> None:
    model_name = "qwen3.5:4b"
    agent = create_agent(
        model=ChatOllama(model=model_name, temperature=0, reasoning=False),
        tools=[current_time, word_count, fail_demo, lookup_ci_log],
        system_prompt=(
            "Use current_time for requests about the current local date or time. "
            "Use word_count when asked to count words. "
            "Use fail_demo only when the controlled failure test is requested. "
            "For CI build diagnosis, call lookup_ci_log with the build ID. "
            "Base the diagnosis only on the returned evidence and quote the exact "
            "log line that supports it. If no log is available, say that there is "
            "insufficient evidence to determine the cause. "
            "For other questions, answer directly."
        ),
    )

    print("Local agent ready. Type exit to quit.")
    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue

        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": question}]},
                config={
                    "run_name": "local-ollama-agent",
                    "tags": ["project-6", "ollama"],
                    "metadata": {
                        "model": model_name,
                        "app_version": "bri-evidence-v1", #"failure-demo-v1",
			"ci_evidence": (
                            "missing" if os.getenv("BRI_HIDE_CI_LOG") == "1"
                            else "available"
                        ),
                    },
                },
            )
        except DemoToolError as error:
            print(f"Controlled tool failure: {error}")
            continue
        
        for message in result["messages"]:
            if isinstance(message, AIMessage):
                for call in message.tool_calls:
                    print(f"[tool call] {call['name']} {call['args']}")

        print(f"Answer: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    main()