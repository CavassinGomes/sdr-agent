# ⚙️ SDR Agent Backend (FastAPI)

Backend minimalista em **FastAPI**, responsável pela orquestração de conversas com leads de pré-venda.

---

## ✨ Funcionalidades

- Sessão por identificador anônimo (com expiração automática)
- Upsert de leads no **MongoDB** (utilizado como armazenamento canônico antes do envio ao **Pipefy**)
- Integrações (stubs) para **OpenAI (Gemini)**, **Pipefy** e **provedores de calendário (Cal.com)**
- Endpoints principais:  
  - `/start-session`  
  - `/message`

---

## 🚀 Como executar

1. Crie um ambiente virtual e instale as dependências:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    .venv\Scripts\activate     # Windows
    pip install -r requirements.txt
    ```

2. Crie um arquivo `.env` (veja `config.py`) com suas **chaves de API** e **configurações de ambiente**.

3. Inicie o servidor:

    ```bash
    uvicorn app:app --reload --port 8000
    ```

---

## 🧩 Notas

- Os serviços **Pipefy** e **Calendar (Cal.com)** são implementados com **clientes HTTP (`httpx`)**.  
  Substitua as **URLs base** e os **payloads GraphQL** conforme necessário.  
  > Exemplo de URL do Cal.com: [`https://api.cal.com`](https://api.cal.com)

- O uso da API **OpenAI/Gemini** baseia-se no fluxo de *Chat Completions + Function Calling*;  
  ajuste o modelo e as chamadas de biblioteca de acordo com o SDK instalado.

---

## 🧑‍💻 Autor

**Lucas Cavassini Gomes**  
📍 [GitHub](https://github.com/CavassinGomes)
