import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import json
import threading
import queue
import time

# 網路通訊處理類
class NetworkHandler:
    def __init__(self, is_host, host_ip, port):
        self.is_host = is_host
        self.host_ip = host_ip
        self.port = port
        self.queue = queue.Queue()
        self.client_socket = None
        self.server_socket = None
        if is_host:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host_ip, port))
            self.server_socket.listen(1)
        else:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host_ip, port))

    def start(self):
        if self.is_host:
            threading.Thread(target=self.accept_client).start()
        else:
            threading.Thread(target=self.receive_messages).start()

    def accept_client(self):
        self.client_socket, addr = self.server_socket.accept()
        print("Client connected")
        self.queue.put({"type": "CLIENT_JOINED"})
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                msg = json.loads(data.decode())
                self.queue.put(msg)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self, msg):
        data = json.dumps(msg).encode()
        if self.is_host and self.client_socket:
            self.client_socket.send(data)
        elif not self.is_host:
            self.client_socket.send(data)

# 打字遊戲主類
class TypingGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("英文打字遊戲 - 多人版")
        self.root.geometry("800x600")
        self.is_host = None
        self.network = None
        self.queue = queue.Queue()
        self.game_started = False
        self.start_time = None
        self.host_progress = 0
        self.client_progress = 0
        self.host_score = 0
        self.client_score = 0
        self.text_content = ""
        self.setup_ui()

    def setup_ui(self):
        # 模式選擇
        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(pady=20)
        tk.Label(self.mode_frame, text="選擇模式：").pack(side=tk.LEFT)
        tk.Button(self.mode_frame, text="建立房間 (Host)", command=self.set_host_mode).pack(side=tk.LEFT, padx=10)
        tk.Button(self.mode_frame, text="加入房間 (Client)", command=self.set_client_mode).pack(side=tk.LEFT, padx=10)

        # IP 相關介面
        self.ip_frame = tk.Frame(self.root)
        self.ip_label = tk.Label(self.ip_frame, text="")
        self.ip_label.pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(self.ip_frame)
        self.connect_button = tk.Button(self.ip_frame, text="連接", command=self.connect_to_host)

        # 開始按鈕
        self.start_button = tk.Button(self.root, text="開始遊戲", command=self.start_game, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        # 文本顯示區域
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.host_text = tk.Text(self.text_frame, wrap=tk.WORD, font=("Courier", 12), state=tk.DISABLED, height=10)
        self.host_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.client_text = tk.Text(self.text_frame, wrap=tk.WORD, font=("Courier", 12), state=tk.DISABLED, height=10)
        self.client_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # 分數和時間顯示
        self.score_frame = tk.Frame(self.root)
        self.score_frame.pack(pady=5)
        self.host_score_label = tk.Label(self.score_frame, text="Host 分數: 0")
        self.host_score_label.pack(side=tk.LEFT, padx=20)
        self.client_score_label = tk.Label(self.score_frame, text="Client 分數: 0")
        self.client_score_label.pack(side=tk.LEFT, padx=20)
        self.timer_label = tk.Label(self.score_frame, text="剩餘時間: 60")
        self.timer_label.pack(side=tk.LEFT, padx=20)

        # 加載文本按鈕
        self.load_button = tk.Button(self.root, text="加載文本", command=self.load_text)
        self.load_button.pack(pady=5)

        self.root.bind("<KeyPress>", self.on_key_press)
        self.process_queue()

    def set_host_mode(self):
        self.is_host = True
        self.mode_frame.pack_forget()
        self.ip_frame.pack(pady=10)
        host_ip = socket.gethostbyname(socket.gethostname())
        self.ip_label.config(text=f"你的內網 IP: {host_ip}\n請查詢公網 IP (例如透過 whatismyip.com) 並分享給 Client。\n請在路由器上設置端口轉發到 {host_ip}:12345")
        self.network = NetworkHandler(True, host_ip, 12345)
        self.network.start()

    def set_client_mode(self):
        self.is_host = False
        self.mode_frame.pack_forget()
        self.ip_frame.pack(pady=10)
        self.ip_label.config(text="輸入 Host IP 地址:")
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        self.connect_button.pack(side=tk.LEFT, padx=5)

    def connect_to_host(self):
        host_ip = self.ip_entry.get()
        if host_ip:
            self.network = NetworkHandler(False, host_ip, 12345)
            self.network.start()
            self.ip_frame.pack_forget()
            messagebox.showinfo("連接成功", "已連接到 Host")

    def load_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_content = file.read()
                self.host_text.config(state=tk.NORMAL)
                self.host_text.delete(1.0, tk.END)
                self.host_text.insert(tk.END, self.text_content)
                self.host_text.config(state=tk.DISABLED)
                self.client_text.config(state=tk.NORMAL)
                self.client_text.delete(1.0, tk.END)
                self.client_text.insert(tk.END, self.text_content)
                self.client_text.config(state=tk.DISABLED)
                if self.is_host:
                    self.start_button.config(state=tk.NORMAL)

    def start_game(self):
        if self.is_host:
            self.start_time = time.time()
            msg = {"type": "START", "start_time": self.start_time}
            self.network.send_message(msg)
            self.game_started = True
            self.start_timer()
            self.root.focus_set()

    def start_timer(self):
        if self.game_started:
            elapsed = time.time() - self.start_time
            remaining = 60 - elapsed
            if remaining > 0:
                self.timer_label.config(text=f"剩餘時間: {int(remaining)}")
                self.root.after(1000, self.start_timer)
            else:
                self.end_game()

    def end_game(self):
        self.game_started = False
        if self.is_host:
            if self.host_score > self.client_score:
                winner = "Host"
            elif self.client_score > self.host_score:
                winner = "Client"
            else:
                winner = "平手"
            msg = {"type": "END", "winner": winner}
            self.network.send_message(msg)
            self.show_result(winner)
        self.root.unbind("<KeyPress>")

    def show_result(self, winner):
        messagebox.showinfo("遊戲結束", f"獲勝者: {winner}")

    def on_key_press(self, event):
        if self.game_started:
            text = self.text_content
            if self.is_host:
                if event.char == text[self.host_progress]:
                    self.host_progress += 1
                    self.host_score += 1
                    self.update_progress(self.host_text, self.host_progress)
                    self.host_score_label.config(text=f"Host 分數: {self.host_score}")
                    msg = {"type": "PROGRESS", "index": self.host_progress, "score": self.host_score}
                    self.network.send_message(msg)
            else:
                if event.char == text[self.client_progress]:
                    self.client_progress += 1
                    self.client_score += 1
                    self.update_progress(self.client_text, self.client_progress)
                    self.client_score_label.config(text=f"Client 分數: {self.client_score}")
                    msg = {"type": "PROGRESS", "index": self.client_progress, "score": self.client_score}
                    self.network.send_message(msg)

    def update_progress(self, text_widget, index):
        text_widget.tag_remove("current", 1.0, tk.END)
        if index < len(self.text_content):
            text_widget.tag_add("current", f"1.0 + {index} chars", f"1.0 + {index + 1} chars")
            text_widget.tag_config("current", background="yellow")

    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                self.handle_message(msg)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def handle_message(self, msg):
        if msg["type"] == "CLIENT_JOINED":
            messagebox.showinfo("Client 已加入", "Client 已加入房間")
            self.start_button.config(state=tk.NORMAL)
        elif msg["type"] == "START":
            self.start_time = msg["start_time"]
            self.game_started = True
            self.start_timer()
            self.root.focus_set()
        elif msg["type"] == "PROGRESS":
            if self.is_host:
                self.client_progress = msg["index"]
                self.client_score = msg["score"]
                self.update_progress(self.client_text, self.client_progress)
                self.client_score_label.config(text=f"Client 分數: {self.client_score}")
            else:
                self.host_progress = msg["index"]
                self.host_score = msg["score"]
                self.update_progress(self.host_text, self.host_progress)
                self.host_score_label.config(text=f"Host 分數: {self.host_score}")
        elif msg["type"] == "END":
            self.game_started = False
            self.show_result(msg["winner"])
            self.root.unbind("<KeyPress>")

if __name__ == "__main__":
    game = TypingGame()
    game.root.mainloop()