# 🤖 SDR-Agent

O **SDR-Agent** é uma aplicação fullstack desenvolvida para automatizar e registrar conversas com leads e clientes.  
Seu objetivo é centralizar interações, integrando diferentes serviços e armazenando o histórico de mensagens de forma persistente.

---

## 🧩 Estrutura do Projeto

sdr-agent/
├── backend/ # API desenvolvida em FastAPI
├── frontend/ # Interface web em Next.js
└── README.md # Documentação principal

---

## 🚀 Tecnologias Utilizadas

### 🖥️ **Frontend**

- [Next.js 15+](https://nextjs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [Shadcn/UI](https://ui.shadcn.com/)
- Integração com a API via `fetch` e endpoints REST

### ⚙️ **Backend**

- [Python 3.12+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [MongoDB (Atlas)](https://www.mongodb.com/atlas)
- [Pydantic](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/)

---

## 🔗 Integrações Externas

O SDR-Agent realiza integrações com três principais serviços externos:

| Serviço | Descrição |
|----------|------------|
| **Cal.com** | Gerencia agendamentos de reuniões com leads captados. |
| **Pipefy** | Armazena e organiza as informações dos leads coletadas nas conversas. |
| **Google Gemini API** | Responsável pelo processamento e geração de respostas inteligentes durante as conversas. |

Essas integrações permitem que o sistema atue como um **assistente SDR** (Sales Development Representative) automatizado, captando, respondendo e qualificando leads de forma eficiente.

---

## 🧠 Fluxo de Funcionamento

1. O usuário acessa a interface web e inicia uma conversa.
2. O frontend cria uma **sessão** com o backend.
3. As mensagens são enviadas e armazenadas no MongoDB.
4. O backend processa a entrada do usuário e aciona o **Gemini API** para gerar a resposta e depois salva no MongoDB atraves da sessao e email.
5. Dados relevantes da conversa são enviados ao **Pipefy** e **Cal.com** para registro e agendamento.

---

## 🛠️ Passo a Passo para Rodar o Projeto

### 🔹 Clonar o repositório

```bash
git clone https://github.com/CavassinGomes/sdr-agent.git
cd sdr-agent
.
├── backend
│   ├── app.py
│   ├── config.py
│   ├── database
│   │   ├── connection.py
│   │   └── __init__.py
│   ├── models
│   │   ├── db.py
│   │   ├── __init__.py
│   │   ├── lead.py
│   │   └── __pycache__
│   ├── __pycache__
│   │   ├── app.cpython-310.pyc
│   │   └── config.cpython-310.pyc
│   ├── pytest.ini
│   ├── readme.md
│   ├── requirements.txt
│   ├── routes
│   │   ├── chat_routes.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── services
│   │   ├── ai_service.py
│   │   ├── calendar_service.py
│   │   ├── __init__.py
│   │   ├── pipefy_service.py
│   │   └── __pycache__
│   ├── tests
│   │   ├── __pycache__
│   │   ├── test_calendar_service.py
│   │   ├── test_chat_flow.py
│   │   └── test_pipefy_service.py
│   ├── utils
│   │   ├── __pycache__
│   │   └── session_manager.py
│   └── venv
│       ├── bin
│       ├── include
│       ├── lib
│       ├── lib64 -> lib
│       └── pyvenv.cfg
├── estrutura.txt
├── frontend
│   ├── components.json
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── next-env.d.ts
│   ├── node_modules
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── postcss.config.mjs
│   ├── public
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── robot-ai-svgrepo-com.svg
│   │   └── window.svg
│   ├── README.md
│   ├── src
│   │   ├── app
│   │   ├── components
│   │   └── lib
│   ├── tailwind.config.js
│   └── tsconfig.json
└── README.md

```

## Execução dos modulos

- Intruções detalhadas em:
    - [📂 Back-end](backend/README.md)
    - [📂 Front-end](frontend/README.md)


