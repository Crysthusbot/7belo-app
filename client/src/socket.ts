// client/src/socket.ts
import { io, Socket } from "socket.io-client";

// Pega a URL base do backend do .env
const HTTP_BASE = import.meta.env.VITE_API_BASE;

// Converte http(s) -> ws(s)
const WS_BASE = HTTP_BASE.replace(/^http/i, "ws");

// Importante: path '/socket.io' (padrão do python-socketio)
// e forçamos 'websocket' para evitar long polling
export const socket: Socket = io(WS_BASE, {
  path: "/socket.io",
  transports: ["websocket"],
  withCredentials: true,
});
