# 🖥️ SDR Agent Frontend (Next.js)

Frontend desenvolvido em **Next.js + TypeScript**, responsável pela interface de interação com o usuário e comunicação com o backend FastAPI.  
Este módulo implementa a camada visual do agente SDR, permitindo iniciar e gerenciar sessões de conversa com leads.

---

## ✨ Funcionalidades

- Interface de chat interativo com histórico de mensagens  
- Criação e gerenciamento de sessões de conversa  
- Comunicação com o backend via **API REST**  
- Renderização reativa e estilização moderna com **TailwindCSS**  
- Estrutura modular de componentes em React  
- Controle de sessão (iniciar/encerrar conversa)

---

## ⚙️ Tecnologias

- [Next.js 15+](https://nextjs.org/)
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [Shadcn/UI](https://ui.shadcn.com/)
- [Lucide React](https://lucide.dev/)
- Comunicação via **Fetch API**

---

## 🔌 Integração com o Backend

O frontend se comunica com a API FastAPI por meio de rotas internas do Next.js, funcionando como um **proxy**.  
Isso evita erros de *CORS* e facilita a comunicação entre módulos durante o desenvolvimento.

| Função | Rota interna (Next.js) | Endpoint Backend |
|--------|--------------------------|------------------|
| Criar sessão | `/api/start-session` | `/start-session` |
| Enviar mensagem | `/api/send-message` | `/message` |

---

## ⚙️ Configuração do Ambiente

Crie um arquivo `.env.local` na pasta `frontend/` com:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Como executar

- Instale as dependencias
  - pnpm install
    ou
  - npm install
  
- Inicie o servidor de desenvolvimento:
  - pnpm dev
    ou
  - npm run dev

- Acesse a aplicação:
  - 🌐 localhost:3000

## 🧩 Notas

- A comunicação com o backend é totalmente assíncrona e baseada em fetch + JSON.
- Caso utilize ambientes diferentes (ex.: produção/staging), atualize a variável NEXT_PUBLIC_API_URL.
- O projeto foi configurado para funcionar com Node.js 20+ e Next.js 15+.
