# SDR Agent Backend (FastAPI)

Minimal FastAPI backend implementing the conversation-orchestration for pre-sales leads.

## Features

- Session-per-anonymous-id with timeout
- Lead upsert to MongoDB (used as canonical storage before Pipefy)
- Integrations (stubs) for OpenAI function calling, Pipefy, and Calendar providers
- Endpoints: /start-session, /message

## How to run

1. Create a virtualenv and install requirements:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. Create a `.env` file (see `config.py`) with your API keys and settings.

3. Start server:

    ```bash
    uvicorn app:app --reload --port 8000
    ```

## Notes

- Pipefy and Calendar services are implemented with HTTP clients (httpx). Replace base URLs and the GraphQL payloads as needed.
- The OpenAI usage shown relies on the Chat Completions + functions workflow; adjust model and library calls to match your installed OpenAI SDK.
"""
