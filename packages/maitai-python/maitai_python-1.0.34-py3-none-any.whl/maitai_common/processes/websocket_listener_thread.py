import threading

import websocket

from maitai_common.processes.io_thread import IOThread


class WebsocketListenerThread(IOThread):
    def __init__(self, path, type, key=None):
        super(WebsocketListenerThread, self).__init__(interval=60)
        self.child_name = f'{self.__class__.__name__}'
        self.messages = []
        self.ws_url = f'{path}?type={type}'
        if key:
            self.ws_url += f'&key={key}'
        self.ws = None
        self.ws_threads = []
        self.closing_ws = False  # Add a shutdown flag
        self.connection_established_event = threading.Event()  # Add an event attribute

    def connect_to_websocket(self):
        self.connection_established_event.clear()  # Clear the event before attempting a new connection
        if self.run_thread and not self.closing_ws:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self.on_message,
                on_close=self.on_close,
                on_error=self.on_error,
                on_open=self.on_open
            )
            # Starting a new thread to handle the WebSocket connection
            ws_thread = threading.Thread(target=self.ws.run_forever, name="WebsocketThread")
            ws_thread.start()
            tmp = [ws_thread]
            for t in self.ws_threads:
                if t.is_alive():
                    tmp.append(t)
            self.ws_threads = tmp

    def on_message(self, ws, message):
        print(f'Received message: {message}')
        self.messages.append(message)

    def on_close(self, ws):
        print("WebSocket connection closed. Reconnecting...")
        self.connect_to_websocket()

    def on_open(self, ws):
        self.connection_established_event.set()  # Set the event when connection is open
        if not self.run_thread or self.closing_ws:
            ws.close()
            if self.ws:
                self.ws.close()

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}. Reconnecting...")
        self.connect_to_websocket()

    def initialize(self):
        self.connect_to_websocket()

        super(WebsocketListenerThread, self).initialize()

    def terminate(self):
        self.closing_ws = True  # Indicate that shutdown is in progress
        if self.ws:
            self.ws.close()
        for i, ws_thread in enumerate(self.ws_threads):
            if ws_thread.is_alive():
                ws_thread.join(timeout=1)
        super(WebsocketListenerThread, self).terminate()

    def clear(self):
        self.messages = []

    def process(self):
        if self.run_thread:
            old_ws = self.ws
            # Temporarily override the on_close to prevent reconnection
            old_on_close = old_ws.on_close
            old_ws.on_close = lambda *args, **kwargs: None

            try:
                # Try to establish a new connection
                self.connect_to_websocket()
                # Wait for the on_open callback to set the event
                self.connection_established_event.wait()
                # If successful, close the old connection
                old_ws.close()
            except Exception as e:
                # If new connection fails, keep the old connection
                old_ws.on_close = old_on_close
                self.ws = old_ws

            super(WebsocketListenerThread, self).process()
