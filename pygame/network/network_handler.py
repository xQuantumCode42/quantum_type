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
