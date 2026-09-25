// src/api/websocket.js
class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
  }

connect(endpoint) {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const cleanEndpoint = endpoint.replace(/^\/+|\/+$/g, '');
    const wsUrl = `ws://localhost:8000/ws/chat/${cleanEndpoint}/`;   

    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log('[WS] Connected to:', wsUrl);
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (this.listeners['message']) {
          this.listeners['message'](data);
        }
      } catch (err) {
        console.error('[WS Error] Failed to parse JSON:', err);
      }
    };

    this.socket.onerror = (err) => console.error('[WS Error]', err);
    this.socket.onclose = () => console.log('[WS] Disconnected');
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }

  on(event, callback) {
    this.listeners[event] = callback;
  }

  off(event) {
    delete this.listeners[event];
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default new WebSocketService();