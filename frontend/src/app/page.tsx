'use client';

import { useEffect, useRef, useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent,CardDescription, CardFooter, CardHeader,CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { LogOut } from "lucide-react";

interface Message {
  role: "user" | "ai";
  content: string;
}

interface AIResponse {
  session_id: string;
  messages: string;
  reply: string;
}

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const savedSessionId = sessionStorage.getItem("sessionId");
    if (savedSessionId) setSessionId(savedSessionId);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function startSession() {
    setLoading(true);
    try {
      const res = await fetch("/api/start-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "iniciar" }), 
      });

      const data: AIResponse = await res.json();

      if (data.session_id) {
        setSessionId(data.session_id);
        sessionStorage.setItem("sessionId", data.session_id);
        setMessages([{ role: "ai", content: data.reply || data.messages }]);
      }
    } catch (error) {
      console.error("Erro ao iniciar sessão:", error);
      setMessages([{ role: "ai", content: "Erro ao iniciar sessão 😢" }]);
    } finally {
      setLoading(false);
    }
  }

  function endSession() {
    sessionStorage.removeItem("sessionId");
    setSessionId(null);
    setMessages([]);
  }

  async function sendMessage() {
    if (!input.trim() || !sessionId) return;

    const newUserMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, newUserMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: input }),
      });

      if (!res.ok) {
        if (res.status === 404) {
          setMessages((prev) => [
          ...prev,
          {
            role: "ai",
            content: "⚠️ Sua sessão expirou ou não foi encontrada. Redirecionando...",
          },
        ]);

        setTimeout(() => {
          setSessionId(null);
          setMessages([]);
        }, 2500);
          return;
        } else {
          throw new Error(`Erro HTTP ${res.status}`);
        }
      }

      const data: AIResponse = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: data.reply || data.messages },
      ]);
    } catch (error) {
      console.error("Erro:", error);
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: "Erro ao enviar mensagem 😢" },
      ]);
      alert("Erro ao enviar mensagem. Por favor, tente novamente.");
      setSessionId(null);
    } finally {
      setLoading(false);
    }
  }

  if (!sessionId) {
    return (
      <div className="flex min-h-screen bg-slate-50 items-center justify-center">
        <Card className="w-full sm:w-[400px] p-8 text-center">
          <CardHeader>
            <CardTitle className="text-xl font-bold">Bem-vindo à Selly-AI 🤖</CardTitle>
            <CardDescription>Converse com a assistente virtual inteligente</CardDescription>
          </CardHeader>
          <CardContent>
            <Avatar className="mx-auto mb-4">
              <AvatarFallback>SA</AvatarFallback>
              <AvatarImage src="/robot-ai-svgrepo-com.svg" />
            </Avatar>
            <p className="text-slate-600 mb-6">
              Clique no botão abaixo para iniciar uma nova conversa
            </p>
            <Button onClick={startSession} disabled={loading} className="w-full">
              {loading ? "Iniciando..." : "Iniciar conversa com Selly"}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50 items-center justify-center ">
      <Card className="w-full sm:w-[440px] h-[90vh] sm:h-[700px] min-h-full grid grid-rows-[min-content_1fr_min-content]">
        <CardHeader className="flex flex-row items-center justify-between p-4 pb-2">
          <div>
            <CardTitle className="text-lg sm:text-xl">Chat Selly-AI</CardTitle>
            <CardDescription className="text-sm text-slate-500">
              Converse com a assistente virtual
            </CardDescription>
          </div>
          
          <Button
            variant="ghost"
            size="icon" 
            className="text-shadow-black hover:bg-red-50 rounded-full"
            onClick={endSession}
            aria-label="Encerrar Sessão" 
            title="Encerrar Sessão"
          >
            <LogOut className="h-5 w-5" /> 
          </Button>
        </CardHeader>

        <CardContent className="space-y-4 overflow-y-auto"
          role="log"
          aria-live="polite"
        >
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 text-slate-600 text-small ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.role === "ai" && (
                <Avatar>
                  <AvatarFallback>SA</AvatarFallback>
                  <AvatarImage src="/robot-ai-svgrepo-com.svg" />
                </Avatar>
              )}
              <p
                className={`leading-relaxed whitespace-pre-wrap max-w-[80%] ${
                  msg.role === "user"
                    ? "text-right bg-blue-50 p-2 rounded-2xl"
                    : ""
                }`}
              >
                <span className="block font-bold text-slate-800">
                  {msg.role === "user" ? "Você" : "Selly-AI"}
                </span>
                {msg.content}
              </p>
              {msg.role === "user" && (
                <Avatar>
                  <AvatarFallback>YOU</AvatarFallback>
                  <AvatarImage src="https://github.com/cavassingomes.png" />
                </Avatar>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 text-slate-600 text-small" role="status" aria-live="assertive">
              <Avatar>
                <AvatarFallback>SA</AvatarFallback>
                <AvatarImage src="/robot-ai-svgrepo-com.svg" />
              </Avatar>
              <p className="animate-pulse text-slate-400">Digitando...</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </CardContent>

        <CardFooter className="space-x-2">
          <Input
            placeholder="Como posso te ajudar?"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <Button type="button" onClick={sendMessage} disabled={loading}>
            {loading ? "Enviando..." : "Enviar"}
          </Button>
          <div className="flex items-center">
            
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
