from fastapi import FastAPI
from routes.chat_routes import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SDR Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router, prefix="/api")


@app.get('/')
async def root():
    return {"ok": True, "msg": "SDR Agent Backend running"}