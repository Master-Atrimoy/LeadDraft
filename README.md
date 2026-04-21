# LeadDraft

**LeadDraft** is a clean first-step GenAI portfolio repo: a prompt-based rewriter for workplace messages.

It takes one rough note and turns it into:
- one polished primary rewrite
- a few controlled variations
- a concise subject line when needed

This repo is intentionally simple in scope. The goal is not to show a giant AI system yet. The goal is to show taste, packaging, and disciplined prompt design.

## What this repo demonstrates

- single-input workplace rewriting
- controlled prompt-based variations
- local Ollama integration
- model selection and model pull from the UI
- Hydra Compose API for config loading
- Pydantic validation for structured LLM output
- a clean Streamlit interface that does not feel like a starter template

## Product framing

This is **repo 1** in a larger GitHub progression.

Positioning:
> Prompt-based Rewriter

Purpose:
> Turn one rough workplace note into a polished draft plus a few controlled variations.

## Example use case

Input:

> We may miss the milestone because vendor credentials are still unstable and QA cannot complete regression yet. Need to update my manager without sounding dramatic.

Output:
- Primary rewrite
- Tighter version
- Softer version
- More direct version

## Tech stack

- Python 3.11+
- Streamlit
- Ollama
- Hydra Compose API
- Pydantic v2
- Requests

## Folder structure

```text
leaddraft/
├── assets/
│   └── theme.css
├── configs/
│   └── app.yaml
├── src/
│   └── leaddraft/
│       ├── core/
│       │   ├── config.py
│       │   └── prompts.py
│       ├── schemas/
│       │   └── rewrite.py
│       ├── services/
│       │   ├── ollama_client.py
│       │   └── rewriter.py
│       ├── ui/
│       │   └── theme.py
│       └── __init__.py
├── streamlit_app.py
├── requirements.txt
└── .gitignore
```

## Setup

```bash
python -m venv .venv
```

### Windows
```bash
.venv\Scripts\activate
```

### Linux / macOS
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run streamlit_app.py
```

Make sure Ollama is running locally at the configured endpoint, usually:

```text
http://localhost:11434
```

## Recommended models

- `llama3.2:3b`
- `qwen2.5:3b`
- `mistral:7b`

## Why this is a good first repo

A first repo should not try to prove everything.
It should prove one idea well.

BriefShift does that by staying focused on:
- one input
- one rewrite task
- controlled output variations
- clean UX
- clean repo hygiene

## Next evolution paths

Natural follow-ups after this repo:
- structured output generator
- ambiguity resolver
- prompt reliability pipeline
- production-grade multi-step AI system
