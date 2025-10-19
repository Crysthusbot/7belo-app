import React, { useEffect, useMemo, useState } from "react";
import { socket } from "./socket";
import "./theme.css";

export default function App() {
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [state, setState] = useState(null);

  useEffect(() => {
    const onCreated = ({ code }) => setCode(code);
    const onState = (s) => setState(s);
    socket.on("room_created", onCreated);
    socket.on("state", onState);
    return () => { socket.off("room_created", onCreated); socket.off("state", onState); };
  }, []);

  const createRoom = () => socket.emit("create_room", {});
  const joinRoom   = () => socket.emit("join_room", { code, name: name || "Jogador" });
  const start      = () => socket.emit("start_game", { code });
  const draw       = () => socket.emit("draw_card", { code });
  const endTurn    = () => socket.emit("end_turn", { code });

  const players = useMemo(()=>Object.entries(state?.players || {}), [state]);

  return (
    <div className="container">
      <h1>7belo (mínimo)</h1>
      <div className="row">
        <button className="button" onClick={createRoom}>Criar sala</button>
        <input className="input" placeholder="Código" value={code} onChange={e=>setCode(e.target.value)} />
        <input className="input" placeholder="Seu nome" value={name} onChange={e=>setName(e.target.value)} />
        <button className="button" onClick={joinRoom} disabled={!code}>Entrar</button>
      </div>
      <hr/>
      {state ? (
        <>
          <p><b>Sala:</b> {state.code} | <b>Turno de:</b> {state.current ?? "-"}</p>
          <p><b>Topo do descarte:</b> {state.discard_top ?? "-"}</p>
          <ul>
            {players.map(([sid,p])=>(
              <li key={sid}>{p.name} — cartas: {p.hand_count} {state.current===sid?"← turno":""}</li>
            ))}
          </ul>
          <div className="row">
            <button className="button" onClick={start}>Iniciar</button>
            <button className="button" onClick={draw}>Comprar</button>
            <button className="button" onClick={endTurn}>Encerrar turno</button>
          </div>
        </>
      ) : <p>Sem estado ainda.</p>}
    </div>
  );
}
