from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import socketio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Socket.IO (pode ficar vazio por enquanto)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

@app.get("/")
async def root():
    return {"ok": True, "dica": "use /health ou /docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}
