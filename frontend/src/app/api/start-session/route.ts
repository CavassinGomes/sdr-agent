import { NextResponse } from "next/server";

export async function POST(request: Request) {
    const body = await request.json();

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/start-session`, {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });

    if (response.body) {
        return new NextResponse(response.body, {
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        });
    }

    const data = await response.json();
    return NextResponse.json(data);
}