/**
 * WebSocketHandler class to manage WebSocket connections.
 */
export class WebSocketHandler {
    /**
     * Creates an instance of WebSocketHandler.
     * @param {string} url - The WebSocket server URL.
     * @param {function} onMessageCallback - The callback function to handle incoming messages.
     */
    constructor(url, onMessageCallback) {
        // Initialize WebSocket connection
        this.ws = new WebSocket(url);

        // Add an event listener for incoming messages
        this.ws.addEventListener('message', (event) => {
            if (onMessageCallback) {
                onMessageCallback(event.data);
            }
        });
    }

    /**
     * Sends a message through the WebSocket connection.
     * @param {string | Blob} message - The message to be sent.
     */
    sendMessage(message) {
        // Check if the WebSocket connection is open before sending the message
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            console.error('WebSocket is not open. Cannot send message');
        }
    }

    /**
     * Closes the WebSocket connection.
     */
    close() {
        // Check if the WebSocket instance exists before attempting to close it
        if (this.ws) {
            this.ws.close();
        }
    }
}
