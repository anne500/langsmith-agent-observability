# 🔍 Project 6 · LangSmith Agent Observability

![Project overview and reading map](assets/readme-overview.svg)

**🟦 Learn AI · 🟩 Portfolio evidence · 🟪 PhD research**

A Windows PowerShell walkthrough for tracing a local LangChain agent running `qwen3.5:4b` through Ollama. LangSmith records the execution path and timing when cloud tracing is enabled.

<a id="explore-the-project"></a>

## 🧭 Explore the project

[🟦 Base tutorial](#base-tutorial) · [🧩 Contributions](#contributions) · [🗺️ Roadmap](#visual-roadmap) · [🏗️ Architecture](#architecture) · [🚀 Setup](#setup) · [🧪 Results & verification](#verified-runs) · [🗂️ Evidence & guides](#latency-results) · [🟪 Thesis connection](#thesis-connection) · [🎨 Visual standard](https://github.com/anne500/multi-agent-study-guide/blob/main/VISUAL_STYLE.md)

![Python](https://img.shields.io/badge/Python-Local-3776AB?logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20inference-334155)
![Project toolkit](https://img.shields.io/badge/LangSmith-Tracing-2563EB)

<a id="base-tutorial"></a>

## 🟦 Base tutorial

The baseline follows Darsh Shah’s [How to Trace and Monitor AI Agents with LangSmith](https://www.freecodecamp.org/news/how-to-trace-and-monitor-ai-agents-with-langsmith/). It runs a local Ollama agent with `current_time` and `word_count`, then uses LangSmith to inspect the model and tool calls. The verified baseline traces below cover a direct answer (Paris) and a tool call (Cedar, 6 words).

<a id="-extensions-added-in-project-6"></a>

<a id="contributions"></a>

## 🧩 Tutorial baseline and contributions

| Origin | Item | Scope or contribution | Verification |
| --- | --- | --- | --- |
| 🟦 Tutorial baseline | 📘 Local agent tracing | Observe direct-answer and tool-call paths in LangSmith. | [Verified runs](#verified-runs) |
| 🧩 Implemented extension | 🏷️ 1. Trace metadata | Implements run names, tags, model and app metadata, and a CI evidence condition label. | Run name and tags appeared on model runs. |
| 🧩 Implemented extension | ⏱️ 2. Latency comparison | Measures total latency and first model call time to first token. | [Six recorded traces](#latency-results) |
| 🧩 Implemented extension | 🧪 3. Controlled tool failure | Raises a controlled error and returns the CLI to the prompt. | Tool and top-level trace showed the error. A subsequent Paris prompt succeeded. |
| 🧩 Implemented extension | 🔎 4. CI diagnosis with and without evidence | Repeats the same MAPLE-207 question with the synthetic log available and withheld. | [Paired trace outcomes](#ci-evidence) |

The latency comparison includes setup runs and describes these six traces. The CI comparison uses one synthetic build and one run per condition.

<a id="visual-roadmap"></a>

### 🗺️ Learning roadmap

```mermaid
flowchart TD
    B["Baseline traces"] --> T["Tag and compare requests"]
    B --> F["Trace a controlled tool failure"]
    T --> C["Compare CI diagnosis conditions"]
    F --> C
    classDef baseline fill:#DBEAFE,stroke:#2563EB,color:#172554
    classDef analysis fill:#EDE9FE,stroke:#7C3AED,color:#3B0764
    classDef result fill:#DCFCE7,stroke:#15803D,color:#14532D
    class B baseline
    class T,F analysis
    class C result
```

<a id="-execution-paths"></a>

<a id="architecture"></a>

## 🧩 Architecture

```mermaid
flowchart TD
    Q["User prompt"] --> M["Ollama model"]
    M --> D{"Tool requested?"}
    D -->|"No"| A["Final answer"]
    D -->|"Yes"| T["Python tool"]
    T --> F["Ollama model with tool result"]
    F --> A
    M -.->|"When enabled"| L["LangSmith cloud trace"]
    T -.-> L
    F -.-> L
    classDef model fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef tool fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef result fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef decision fill:#fef3c7,stroke:#b45309,color:#451a03
    classDef store fill:#ccfbf1,stroke:#0f766e,color:#134e4a
    class D decision
    class L store
    class M,F model
    class T tool
    class A result
```

<a id="-run-locally"></a>

<a id="setup"></a>

## 🚀 Run locally

Use the project folder containing `trace_agent.py`. Start Ollama before running the agent.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install langchain langchain-ollama langsmith
ollama pull qwen3.5:4b

$env:LANGSMITH_TRACING = "false"
python .\trace_agent.py
```

At `You:`, enter either prompt from the verification table. Type `exit` to return to PowerShell.

## 🟪 Enable LangSmith Cloud tracing

In the LangSmith workspace, register an agent with ID `langsmith-agent-observability` and use its **Local** environment. Generate a LangSmith API key for that workspace and use the endpoint or workspace ID from the setup screen if specified. In the same PowerShell session, run:

```powershell
Remove-Item Env:LANGSMITH_PROJECT, Env:LANGCHAIN_PROJECT, Env:LANGCHAIN_SESSION -ErrorAction SilentlyContinue
$env:LANGSMITH_AGENT_ID = "langsmith-agent-observability"
$env:LANGSMITH_AGENT_ENVIRONMENT = "local"
$env:LANGSMITH_TRACING = "true"

$langsmithKey = Read-Host "Paste your LangSmith API key" -AsSecureString
$env:LANGSMITH_API_KEY = [pscredential]::new("langsmith", $langsmithKey).GetNetworkCredential().Password
Remove-Variable langsmithKey

python .\trace_agent.py
```

Paste the key at the masked prompt. Use sample inputs because cloud tracing sends request and response data to LangSmith. Ollama still runs inference locally. The tutorial was run on the Developer plan with Base retention. See [LangSmith pricing](https://www.langchain.com/pricing) and [LangSmith billing](https://docs.langchain.com/langsmith/billing).

<a id="-verified-runs"></a>

<a id="verified-runs"></a>

## 🧪 Verified runs

Observed in LangSmith on November 12, 2026 (Pacific time).

| Prompt | Trace path | Result | Total latency |
|---|---|---|---:|
| What is the capital of France? | One `ChatOllama` call, zero tool runs | Paris | 58.08 s |
| Count the words in "Cedar needs a CI smoke test." | `ChatOllama` → `word_count` → `ChatOllama` | Tool returned `6` | 21.63 s |

- **Paris:** LangSmith reported 57.99 s for the model call and 57.04 s to first token. It recorded 354 input tokens and 8 output tokens.
- **Cedar:** The two model calls took 19.00 s and 2.52 s. The tool duration displayed as 0.00 s at the UI's precision.

In **Local → Tracing**, open each top-level `LangGraph` run and expand the child runs. Select `word_count` to inspect the tool input and output. Select `ChatOllama` to inspect model timing. These timings represent one captured trace per path. A benchmark would require repeated runs under comparable conditions.

<a id="latency-results"></a>

### 📊 Observed latency by prompt

![Median total latency and time to first token for Paris and Cedar, three traces per prompt](docs/assets/trace-latency.svg)

Medians summarize three tagged traces per prompt, including setup runs. Time to first token refers to the first model call. The prompts differ in content and execution path, so the comparison does not isolate the effect of tool calls. [Recorded medians](docs/data/trace-latency.csv) · [Plotting code](scripts/plot_trace_latency.py). With Matplotlib installed, run `python scripts/plot_trace_latency.py` from the repository root to recreate the figure.

<a id="thesis-connection"></a>

<a id="ci-evidence"></a>

## 🟪 CI diagnosis with and without evidence

Both runs asked: `Why did build MAPLE-207 fail?`

| Condition | Lookup output | Verified agent behavior |
|---|---|---|
| Evidence available | `ERROR [signing] Signing certificate expired.` | Identified the expired certificate and quoted the exact log line. |
| Evidence withheld | `No CI log available for MAPLE-207.` | Reported insufficient evidence and left the cause undetermined. |

Both requests completed successfully. Each condition was tested once with
synthetic evidence. Inspect the `lookup_ci_log` child run and the final AI
message in LangSmith to verify the behavior.

To reproduce the pilot in PowerShell, set `$env:BRI_HIDE_CI_LOG = "0"` for the available condition or `"1"` for the withheld condition before starting `python .\trace_agent.py`. Ask the same question in each run. Afterward, use `Remove-Item Env:BRI_HIDE_CI_LOG` to restore the default.

<a id="-references"></a>

## 📚 Tutorial Acknowledgment and Attribution

Thanks to **Darsh Shah** for the **freeCodeCamp** tutorial that provided the local-agent tracing baseline.

- [freeCodeCamp tutorial by Darsh Shah](https://www.freecodecamp.org/news/how-to-trace-and-monitor-ai-agents-with-langsmith/)
- [LangSmith tracing for LangChain agents](https://docs.langchain.com/langsmith/trace-with-langchain)
