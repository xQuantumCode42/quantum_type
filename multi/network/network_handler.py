import socket
import json
import threading

class NetworkHandler:
    def __init__(self, is_host, ip, port):
        self.is_host = is_host
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.running = True

    def start(self):
        if self.is_host:
            self.sock.bind((self.ip, self.port))
            self.sock.listen(1)
            threading.Thread(target=self.accept_clients, daemon=True).start()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def accept_clients(self):
        while self.running:
            conn, addr = self.sock.accept()
            self.clients.append(conn)
            msg = {"type": "CLIENT_JOINED"}
            conn.send(json.dumps(msg).encode())

    def receive_messages(self):
        while self.running:
            if self.is_host:
                for client in self.clients[:]:
                    try:
                        data = client.recv(1024).decode()
                        if data:
                            msg = json.loads(data)
                            game.queue.put(msg)
                            for c in self.clients:
                                c.send(json.dumps(msg).encode())
                    except:
                        self.clients.remove(client)
            else:
                try:
                    data = self.sock.recv(1024).decode()
                    if data:
                        msg = json.loads(data)
                        game.queue.put(msg)
                except:
                    self.running = False

    def send_message(self, msg):
        if self.is_host:
            for client in self.clients:
                client.send(json.dumps(msg).encode())
        else:
            self.sock.send(json.dumps(msg).encode())

    def connect(self, host_ip):
        self.sock.connect((host_ip, self.port))
