import { io } from "socket.io-client";

const HTTP_BASE = import.meta.env.VITE_API_BASE; // https://xxxxx-8000.app.github.dev
const WS_BASE = HTTP_BASE.replace(/^http/i, "ws"); // vira wss://... em https

export const socket = io(WS_BASE, {
  path: "/socket.io",
  transports: ["websocket"],
});
