from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import socketio
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random

@dataclass
class Player:  name: str; hand: List[str] = field(default_factory=list)
@dataclass
class Room:
    code: str
    players: Dict[str, Player] = field(default_factory=dict)
    current: Optional[str] = None
    discard: List[str] = field(default_factory=list)
    started: bool = False

rooms: Dict[str, Room] = {}

def deck():
    ranks = ["A","2","3","4","5","6","7","Q","J","K","10","9","8"]
    suits = ["♠","♥","♦","♣"]
    return [f"{r}{s}" for r in ranks for s in suits]

def public_state(r: Room):
    return {
        "code": r.code,
        "players": {sid: {"name": p.name, "hand_count": len(p.hand)} for sid,p in r.players.items()},
        "discard_top": r.discard[-1] if r.discard else None,
        "current": r.current,
        "started": r.started,
    }

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], allow_credentials=True
)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

@app.get("/health")
async def health(): return {"status": "ok"}

async def broadcast(code: str):
    r = rooms.get(code)
    if r: await sio.emit("state", public_state(r), room=code)

@sio.event
async def connect(sid, environ): print("connect", sid)

@sio.event
async def disconnect(sid):
    for r in rooms.values():
        if sid in r.players:
            del r.players[sid]
            if r.current == sid:
                r.current = next(iter(r.players.keys()), None)
            await broadcast(r.code)

@sio.event
async def create_room(sid, data):
    code = str(random.randint(1000, 9999))
    rooms[code] = Room(code=code)
    await sio.enter_room(sid, code)
    await sio.emit("room_created", {"code": code}, to=sid)
    await broadcast(code)

@sio.event
async def join_room(sid, data):
    code = data.get("code"); name = (data.get("name") or "Jogador").strip()
    r = rooms.get(code); 
    if not r: return
    r.players[sid] = Player(name=name)
    if not r.current: r.current = sid
    await sio.enter_room(sid, code)
    await broadcast(code)

@sio.event
async def start_game(sid, data):
    code = data.get("code"); r = rooms.get(code)
    if not r or r.started: return
    cards = deck(); random.shuffle(cards)
    for _ in range(5):
        for p in r.players.values(): p.hand.append(cards.pop())
    r.discard.append(cards.pop()); r.started = True
    await broadcast(code)

@sio.event
async def draw_card(sid, data):
    code = data.get("code"); r = rooms.get(code)
    if not r or r.current != sid: return
    cards = deck(); random.shuffle(cards)
    r.players[sid].hand.append(cards.pop())
    await broadcast(code)

@sio.event
async def end_turn(sid, data):
    code = data.get("code"); r = rooms.get(code)
    if not r or r.current != sid: return
    sids = list(r.players.keys())
    if sid in sids:
        i = (sids.index(sid) + 1) % len(sids)
        r.current = sids[i]
        await broadcast(code)
