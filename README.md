# Multi-Agent Service Request System

A modular 7-agent pipeline designed to intelligently process multilingual service requests end-to-end.

## Architecture

Each agent is self-contained, with its own logic, prompts, and data schemas. Agents are coordinated via a central orchestrator (coming soon).

```text
agents/
├── language_parser/     # Agent 1: Parse multilingual requests & extract slots
├── agent_2/            # (Coming soon)
├── agent_3/            # (Coming soon)
├── agent_4/            # (Coming soon)
├── agent_5/            # (Coming soon)
├── agent_6/            # (Coming soon)
└── agent_7/            # (Coming soon)
```

## Agents

| # | Agent | Goal | Model |
|---|-------|------|-------|
| 1 | `language_parser` | Parse multilingual service requests and extract slots | Gemini 2.0 Flash |
| 2 | TBD | TBD | TBD |
| 3 | TBD | TBD | TBD |
| 4 | TBD | TBD | TBD |
| 5 | TBD | TBD | TBD |
| 6 | TBD | TBD | TBD |
| 7 | TBD | TBD | TBD |

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd <repo-dir>
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env  # Windows
# Then edit .env and fill in your GEMINI_API_KEY
```

Get your API key from: https://aistudio.google.com/app/apikey

### 5. Run

```bash
python main.py
```

## Project Structure

```text
/
├── agents/                     # All agent implementations
│   ├── base.py                 # Base class shared by all agents
│   └── language_parser/        # Agent 1
│       ├── agent.py            # Core agent logic
│       ├── prompts.py          # System prompt & templates
│       └── schemas.py          # Pydantic slot schemas
├── core/                       # Shared utilities
│   ├── config.py               # Loads environment variables
│   └── llm_client.py           # Centralised Gemini client
├── tests/                      # Tests
│   └── agents/
│       └── test_language_parser.py
├── main.py                     # Entry point / demo runner
├── .env.example                # Example environment config
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```
