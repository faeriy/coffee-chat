
const API_WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

export function createWebSocket(path: string): WebSocket {
    const url = `${API_WS_URL}${path}`;
    return new WebSocket(url);
}

export function connectWebSocket(
    path: string,
    onMessage: (data: string) => void,
    onOpen?: () => void,
    onClose?: () => void
): WebSocket {
    const ws = createWebSocket(path);
    ws.onmessage = (event) => onMessage(event.data);
    ws.onopen = () => onOpen?.();
    ws.onclose = () => onClose?.();
    return ws;
}
