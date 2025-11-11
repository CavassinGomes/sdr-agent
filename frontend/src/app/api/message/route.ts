import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json();

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (response.status === 404) {
    let errorData = {};
        try {
            errorData = await response.json();
        } catch {}
    return new NextResponse(
            JSON.stringify({ 
                error: "Sessão expirada ou não encontrada.", 
                detail: (errorData as any).detail || "Session not found" 
            }),
            {
                status: 404,
                headers: { "Content-Type": "application/json" },
            }
        );
    }

  if (response.body) {
    return new NextResponse(response.body, {
      headers: { "Content-Type": "application/json" },
    });
  }

  const data = await response.json();
  console.log("Start Session Response:", data);
  return NextResponse.json(data);
}
