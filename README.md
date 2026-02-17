# 🧠 LLM Code Style Reviewer

An AI-powered GitHub Action that performs static and LLM-based code
review for Pull Requests.

This action:

-   Detects changed files in a PR\
-   Runs configurable static checks\
-   Sends code to an LLM provider (currently OpenAI) for deeper
    analysis\
-   Outputs structured review feedback in GitHub Actions logs

------------------------------------------------------------------------

## 🚀 Features

-   🔍 Automatic PR diff detection\
-   📏 Rule-based static checks (configurable via YAML)\
-   🤖 LLM-powered semantic code review\
-   🐳 Docker-based isolated execution\
-   ⚙️ Modular architecture (static → LLM → pipeline)\
-   🔌 Extendable provider system (supports multiple AI backends)

------------------------------------------------------------------------

## 📚 Supported Language

-   Java (static + LLM review)

------------------------------------------------------------------------

## 🔧 Installation

Create a workflow file:

`.github/workflows/llm-review.yml`

``` yaml
name: LLM Code Review

on:
  pull_request:

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run LLM Code Reviewer
        uses: varuuuun/llm-code-style-reviewer@v1
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

------------------------------------------------------------------------

## 🔐 Required Secret

Add your OpenAI API key:

Settings → Secrets and variables → Actions → Repository secrets

-   Name: `OPENAI_API_KEY`
-   Value: your-api-key

------------------------------------------------------------------------

## 🧠 How It Works

1.  Detects PR base branch automatically\

2.  Fetches base branch\

3.  Runs:

        git diff origin/<base>...HEAD

4.  Filters changed `.java` files\

5.  Runs static rule checks\

6.  Sends content to LLM provider for structured review\

7.  Prints warnings in workflow logs

------------------------------------------------------------------------

## ⚙️ Configuration

### Static Rules

Located at:

    data/coding_standard/rules.yaml

### LLM Rules

Located at:

    src/rules/llm_rules.yaml

### Local Config (For Local Testing)

    config.yaml

-   Used for local testing when GitHub Secrets are not available\
-   Stores API keys locally\
-   Committed version contains placeholder values only\
-   Not used inside GitHub Actions (Actions use repository secrets)

------------------------------------------------------------------------

## 🔌 Provider Architecture

`providers.py` makes the project extendable to additional AI providers.

-   Currently supported: **OpenAI**
-   To support another provider (e.g., Anthropic, Azure OpenAI),
    implement a new provider class inside `providers.py`
-   The architecture allows extension without modifying core pipeline
    logic

------------------------------------------------------------------------

## 🏗 Architecture

    Docker Action
    ├── action.yaml
    ├── Dockerfile
    ├── scripts/
    │   ├── run_action.py
    │   └── run.py
    ├── src/
    │   ├── analysis/
    │   ├── reviewer/
    │   ├── llm/
    │   └── rules/
    ├── data/
    ├── config.yaml
    ├── requirements.txt
    └── README.md

Pipeline Flow:

Static Checks → LLM Review → Aggregated Output

------------------------------------------------------------------------

## ❗ Failure Behavior

-   Static and LLM warnings are printed\
-   Workflow exits with non-zero only if script errors occur\
-   Future versions may support strict mode

------------------------------------------------------------------------

## 🔐 Privacy & Cost Notice

This action sends changed Java files to an external LLM provider.

Ensure:

-   You are comfortable sending code externally\
-   You understand API usage may incur cost

------------------------------------------------------------------------

## 🧪 Local Testing

1. Add your OpenAI API key to `config.yaml`:

``` yaml
provider: openai
openai:
  model: gpt-4
  api_key: your-api-key-here
```

2. Run the reviewer on a file:

``` bash
python scripts.run /path/to/your/file.java
```

------------------------------------------------------------------------

## 📈 Roadmap

-   [ ] Strict mode (fail on violations)\
-   [ ] Inline PR comments via GitHub API\
-   [ ] Multi-language support\
-   [ ] Configurable severity levels\
-   [ ] Additional LLM providers

------------------------------------------------------------------------

## 📜 License

MIT License

------------------------------------------------------------------------

Built by Varun
