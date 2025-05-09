import socket
import json
import threading
import time


class NetworkHandler:
    def __init__(self, is_host, ip, port):
        self.is_host = is_host
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Set additional socket options for better reliability
        if hasattr(socket, "SO_KEEPALIVE"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # Set socket timeout to prevent blocking indefinitely
        self.sock.settimeout(5.0)  # 5 second timeout

        self.clients = []
        self.running = True
        self.game = None

        print(
            f"NetworkHandler initialized as {'host' if is_host else 'client'} with IP {ip} and port {port}"
        )

    def set_game(self, game):
        self.game = game

    def start(self):
        if self.is_host:
            try:
                self.sock.bind((self.ip, self.port))
                self.sock.listen(1)
                threading.Thread(target=self.accept_clients, daemon=True).start()
            except OSError as e:
                self.port = self.port + 1
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((self.ip, self.port))
                self.sock.listen(1)
                threading.Thread(target=self.accept_clients, daemon=True).start()
                if self.game and hasattr(self.game, "ui"):
                    self.game.ui.messagebox.showinfo(
                        "Port Changed", f"Using port {self.port} instead"
                    )
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def accept_clients(self):
        while self.running:
            try:
                conn, addr = self.sock.accept()
                self.clients.append(conn)
                msg = {"type": "CLIENT_JOINED"}
                # Use the new message format with length header
                self._send_raw_message_to_client(msg, conn)

                # Also notify the host that a client has joined
                if self.game and hasattr(self.game.state, "queue"):
                    self.game.state.queue.put(msg)
            except Exception as e:
                print(f"Error in accept_clients: {str(e)}")
                time.sleep(0.1)
                continue

    def _send_raw_message_to_client(self, msg, client_socket):
        """Send a message to a specific client using the length header protocol"""
        try:
            msg_str = json.dumps(msg)
            msg_bytes = msg_str.encode()

            # Add message length header (4 bytes)
            header = len(msg_bytes).to_bytes(4, byteorder="big")
            print(
                f"Sending direct message: {msg['type']}, size: {len(msg_bytes)} bytes"
            )

            # Send header first
            client_socket.send(header)

            # Then send actual message
            total_sent = 0
            while total_sent < len(msg_bytes):
                sent = client_socket.send(msg_bytes[total_sent:])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent
            print(f"Sent {total_sent} bytes directly to client")
        except Exception as e:
            print(f"Error in _send_raw_message_to_client: {str(e)}")
            pass

    def receive_messages(self):
        while self.running:
            if self.is_host:
                if not self.clients:
                    # No clients connected yet, just wait
                    time.sleep(0.1)
                    continue

                for client in self.clients[:]:
                    try:
                        # Read complete messages using length header
                        try:
                            # Get message length (4 bytes)
                            client.setblocking(1)  # Use blocking mode for headers
                            header_data = b""
                            while len(header_data) < 4:
                                chunk = client.recv(4 - len(header_data))
                                if not chunk:
                                    break
                                header_data += chunk

                            if len(header_data) == 4:
                                # Got complete header
                                msg_len = int.from_bytes(header_data, byteorder="big")
                                print(f"Host receiving message of {msg_len} bytes")

                                # Now receive the full message
                                data = b""
                                while len(data) < msg_len:
                                    chunk = client.recv(min(4096, msg_len - len(data)))
                                    if not chunk:
                                        break
                                    data += chunk

                                if len(data) == msg_len:
                                    # Successfully received complete message
                                    try:
                                        msg = json.loads(data.decode())
                                        print(f"Host received message: {msg['type']}")
                                        self.game.state.queue.put(msg)
                                        # Echo message to all other clients if needed
                                        for c in self.clients:
                                            if c != client:  # Don't echo back to sender
                                                self._send_raw_message_to_client(msg, c)
                                    except json.JSONDecodeError as e:
                                        print(
                                            f"Host JSON decode error: {str(e)}, data length: {len(data)}"
                                        )
                        except socket.error as se:
                            # No data or socket error
                            pass
                    except Exception as e:
                        print(f"Host error with client: {str(e)}")
                        try:
                            self.clients.remove(client)
                        except:
                            pass
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
            else:
                try:
                    # Read complete messages with length headers for clients
                    try:
                        # Get message length (4 bytes)
                        self.sock.setblocking(1)  # Use blocking mode for receiving
                        header_data = b""
                        while len(header_data) < 4:
                            try:
                                chunk = self.sock.recv(4 - len(header_data))
                                if not chunk:
                                    time.sleep(0.1)
                                    continue
                                header_data += chunk
                            except socket.error:
                                time.sleep(0.1)
                                continue

                        if len(header_data) == 4:
                            # Got complete header
                            msg_len = int.from_bytes(header_data, byteorder="big")
                            print(f"Client receiving message of {msg_len} bytes")

                            # Now receive the full message
                            data = b""
                            while len(data) < msg_len:
                                try:
                                    chunk = self.sock.recv(
                                        min(4096, msg_len - len(data))
                                    )
                                    if not chunk:
                                        break
                                    data += chunk
                                except socket.error:
                                    time.sleep(0.1)
                                    continue

                            if len(data) == msg_len:
                                # Successfully received complete message
                                try:
                                    msg = json.loads(data.decode())
                                    print(f"Client received message: {msg['type']}")
                                    self.game.state.queue.put(msg)
                                except json.JSONDecodeError as e:
                                    print(
                                        f"Client JSON decode error: {str(e)}, data length: {len(data)}"
                                    )
                    except socket.error:
                        # No data available
                        time.sleep(0.1)
                except Exception as e:
                    print(f"Client receive error: {str(e)}")
                    self.running = False
                time.sleep(0.01)  # Small sleep to prevent CPU hogging

    def send_message(self, msg):
        try:
            # Special handling for large text messages
            if msg["type"] == "LOAD_TEXT" and len(msg["text"]) > 4000:
                print(f"Sending large text in chunks, total size: {len(msg['text'])}")
                # Split the text into chunks
                text = msg["text"]
                chunk_size = 4000
                chunks = [
                    text[i : i + chunk_size] for i in range(0, len(text), chunk_size)
                ]

                # Send number of chunks first
                chunk_info = {"type": "TEXT_CHUNKS", "count": len(chunks)}
                self._send_raw_message(chunk_info)

                # Send each chunk
                for i, chunk in enumerate(chunks):
                    chunk_msg = {"type": "TEXT_CHUNK", "index": i, "chunk": chunk}
                    self._send_raw_message(chunk_msg)
                    time.sleep(0.1)  # Give some time between chunks

                # Send completion message
                self._send_raw_message({"type": "TEXT_COMPLETE"})
                return

            # Regular message sending
            self._send_raw_message(msg)
        except Exception as e:
            print(f"Error in send_message: {str(e)}")
            pass

    def _send_raw_message(self, msg):
        try:
            msg_str = json.dumps(msg)
            msg_bytes = msg_str.encode()

            # Add message length header (4 bytes) for complete message delivery
            header = len(msg_bytes).to_bytes(4, byteorder="big")
            print(f"Sending message: {msg['type']}, size: {len(msg_bytes)} bytes")

            if self.is_host:
                for client in self.clients[:]:  # Use a copy of the list
                    try:
                        self._send_raw_message_to_client(msg, client)
                    except Exception as e:
                        print(f"Error sending to client: {str(e)}")
                        try:
                            self.clients.remove(client)
                        except:
                            pass
            else:
                # Send header first
                self.sock.send(header)
                # Then send actual message
                total_sent = 0
                while total_sent < len(msg_bytes):
                    sent = self.sock.send(msg_bytes[total_sent:])
                    if sent == 0:
                        raise RuntimeError("Socket connection broken")
                    total_sent += sent
                print(f"Client sent {total_sent} bytes to host")
        except Exception as e:
            print(f"Error in _send_raw_message: {str(e)}")
            pass

    def connect(self, host_ip):
        try:
            print(f"Attempting to connect to host at {host_ip}:{self.port}")
            self.sock.settimeout(5.0)  # Set 5 second timeout for connection
            self.sock.connect((host_ip, self.port))
            print(f"Connected to host at {host_ip}:{self.port}")

            # Reset timeout after connection for data transfer
            self.sock.settimeout(None)
        except ConnectionRefusedError:
            print(f"Connection refused at port {self.port}, trying next port")
            self.port += 1
            self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                print(f"Attempting to connect to host at {host_ip}:{self.port}")
                self.sock.connect((host_ip, self.port))
                print(f"Connected to host at {host_ip}:{self.port}")
                # Reset timeout after connection for data transfer
                self.sock.settimeout(None)
            except Exception as e:
                print(f"Failed to connect with second port: {str(e)}")
                if self.game and hasattr(self.game, "ui"):
                    self.game.ui.messagebox.showerror(
                        "Connection Error", "Could not connect to host"
                    )
                self.running = False
        except Exception as e:
            print(f"Connection error: {str(e)}")
            if self.game and hasattr(self.game, "ui"):
                self.game.ui.messagebox.showerror(
                    "Connection Error", f"Could not connect to host: {str(e)}"
                )
            self.running = False
    
    def stop(self):
        if self.running:
            self.running = False
            if self.sock:
                self.sock.close()
