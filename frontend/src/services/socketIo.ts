import {io, Socket} from 'socket.io-client';

const API_URL = import.meta.env.VITE_API_URL;

let socket: Socket | null = null;

export function getSocket(): Socket {
    if (!socket) socket = io(API_URL);
    return socket;
}

export function connectSocket(onMessage: (msg: string) => void) {
    const s = getSocket();
    s.on('message', onMessage);
}

export function sendMessage(message: string) {
    getSocket().emit('message', message);
}

export function disconnectSocket() {
    socket?.disconnect();
    socket = null;
}
