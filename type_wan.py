import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import json
import threading
import queue
import time

# 網路通訊處理類（保持不變）
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

# 打字遊戲主類
class TypingGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("英文打字遊戲")
        self.root.geometry("800x600")
        self.is_host = None
        self.is_single_player = False  # 新增單人模式標誌
        self.network = None
        self.queue = queue.Queue()
        self.game_started = False
        self.start_time = None
        self.my_progress = 0
        self.my_score = 0
        self.opponent_progress = 0
        self.opponent_score = 0
        self.text_content = ""
        self.setup_ui()

    def setup_ui(self):
        # 模式選擇
        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(pady=20)
        tk.Label(self.mode_frame, text="選擇模式：").pack(side=tk.LEFT)
        tk.Button(self.mode_frame, text="建立房間 (Host)", command=self.set_host_mode).pack(side=tk.LEFT, padx=10)
        tk.Button(self.mode_frame, text="加入房間 (Client)", command=self.set_client_mode).pack(side=tk.LEFT, padx=10)
        tk.Button(self.mode_frame, text="單人模式", command=self.set_single_player_mode).pack(side=tk.LEFT, padx=10)

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
        self.my_text = tk.Text(self.text_frame, wrap=tk.WORD, font=("Courier", 12), state=tk.DISABLED, height=10)
        self.my_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.opponent_text = tk.Text(self.text_frame, wrap=tk.WORD, font=("Courier", 12), state=tk.DISABLED, height=10)
        self.opponent_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # 分數和時間顯示
        self.score_frame = tk.Frame(self.root)
        self.score_frame.pack(pady=5)
        self.my_score_label = tk.Label(self.score_frame, text="我的分數: 0")
        self.my_score_label.pack(side=tk.LEFT, padx=20)
        self.opponent_score_label = tk.Label(self.score_frame, text="對手分數: 0")
        self.opponent_score_label.pack(side=tk.LEFT, padx=20)
        self.timer_label = tk.Label(self.score_frame, text="剩餘時間: 60")
        self.timer_label.pack(side=tk.LEFT, padx=20)

        # 加載文本按鈕
        self.load_button = tk.Button(self.root, text="加載文本", command=self.load_text)
        self.load_button.pack(pady=5)

        self.root.bind("<KeyPress>", self.on_key_press)
        self.process_queue()

    def set_single_player_mode(self):
        self.is_single_player = True
        self.mode_frame.pack_forget()
        self.ip_frame.pack_forget()  # 隱藏 IP 相關介面
        self.start_button.config(state=tk.NORMAL)  # 直接啟用開始按鈕
        self.opponent_text.pack_forget()  # 隱藏對手文本框
        self.opponent_score_label.pack_forget()  # 隱藏對手分數

    def set_host_mode(self):
        self.is_host = True
        self.is_single_player = False
        self.mode_frame.pack_forget()
        self.ip_frame.pack(pady=10)
        host_ip = socket.gethostbyname(socket.gethostname())
        self.ip_label.config(text=f"你的 IP 地址: {host_ip}")
        self.network = NetworkHandler(True, host_ip, 12345)
        self.network.start()

    def set_client_mode(self):
        self.is_host = False
        self.is_single_player = False
        self.mode_frame.pack_forget()
        self.ip_frame.pack(pady=10)
        self.ip_label.config(text="輸入 Host IP 地址:")
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        self.connect_button.pack(side=tk.LEFT, padx=5)

    def connect_to_host(self):
        host_ip = self.ip_entry.get()
        self.network = NetworkHandler(False, host_ip, 12345)
        self.network.connect(host_ip)
        self.network.start()
        self.ip_frame.pack_forget()

    def load_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_content = file.read()
                self.my_text.config(state=tk.NORMAL)
                self.my_text.delete(1.0, tk.END)
                self.my_text.insert(tk.END, self.text_content)
                self.my_text.config(state=tk.DISABLED)
                if not self.is_single_player:
                    self.opponent_text.config(state=tk.NORMAL)
                    self.opponent_text.delete(1.0, tk.END)
                    self.opponent_text.insert(tk.END, self.text_content)
                    self.opponent_text.config(state=tk.DISABLED)
                    # 如果是主機，發送文本內容給客戶端
                    if self.is_host:
                        msg = {"type": "LOAD_TEXT", "text": self.text_content}
                        self.network.send_message(msg)
                if self.is_host or self.is_single_player:
                    self.start_button.config(state=tk.NORMAL)

    def start_game(self):
        self.start_time = time.time()
        self.game_started = True
        self.start_timer()
        self.root.focus_set()
        if not self.is_single_player and self.is_host:
            msg = {"type": "START", "start_time": self.start_time}
            self.network.send_message(msg)

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
        if self.is_single_player:
            messagebox.showinfo("遊戲結束", f"你的分數: {self.my_score}")
        elif self.is_host:
            if self.my_score > self.opponent_score:
                winner = "Host"
            elif self.opponent_score > self.my_score:
                winner = "Client"
            else:
                winner = "平手"
            msg = {"type": "END", "winner": winner}
            self.network.send_message(msg)
            self.show_result(winner)
        self.root.unbind("<KeyPress>")

    def on_key_press(self, event):
        if self.game_started:
            text = self.text_content
            if self.my_progress < len(text):
                current_char = text[self.my_progress]
                if current_char == '\n':  # 當前字符是換行符
                    if event.keysym == "Return":  # 玩家按下 Enter 鍵
                        self.my_progress += 1
                        self.my_score += 1
                        self.update_progress(self.my_text, self.my_progress)
                        self.my_score_label.config(text=f"我的分數: {self.my_score}")
                        if not self.is_single_player:
                            msg = {"type": "PROGRESS", "index": self.my_progress, "score": self.my_score}
                            self.network.send_message(msg)
                    else:
                        # 錯誤輸入，顯示紅色高亮提示
                        self.my_text.tag_add("error", f"1.0 + {self.my_progress} chars", f"1.0 + {self.my_progress + 1} chars")
                        self.my_text.tag_config("error", background="red")
                        self.root.after(500, lambda: self.my_text.tag_remove("error", 1.0, tk.END))
                else:  # 當前字符不是換行符
                    if event.char == current_char:
                        self.my_progress += 1
                        self.my_score += 1
                        self.update_progress(self.my_text, self.my_progress)
                        self.my_score_label.config(text=f"我的分數: {self.my_score}")
                        if not self.is_single_player:
                            msg = {"type": "PROGRESS", "index": self.my_progress, "score": self.my_score}
                            self.network.send_message(msg)
                    else:
                        # 錯誤輸入，顯示紅色高亮提示
                        self.my_text.tag_add("error", f"1.0 + {self.my_progress} chars", f"1.0 + {self.my_progress + 1} chars")
                        self.my_text.tag_config("error", background="red")
                        self.root.after(500, lambda: self.my_text.tag_remove("error", 1.0, tk.END))

    def update_progress(self, text_widget, index):
        text_widget.tag_remove("current", 1.0, tk.END)
        if index < len(self.text_content):
            text_widget.tag_add("current", f"1.0 + {index} chars", f"1.0 + {index + 1} chars")
            text_widget.tag_config("current", background="yellow")

    def process_queue(self):
        if not self.is_single_player:
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
            self.opponent_progress = msg["index"]
            self.opponent_score = msg["score"]
            self.update_progress(self.opponent_text, self.opponent_progress)
            self.opponent_score_label.config(text=f"對手分數: {self.opponent_score}")
        elif msg["type"] == "END":
            self.game_started = False
            self.show_result(msg["winner"])
            self.root.unbind("<KeyPress>")
        elif msg["type"] == "LOAD_TEXT":
            # 客戶端接收文本並更新顯示區域
            self.text_content = msg["text"]
            self.my_text.config(state=tk.NORMAL)
            self.my_text.delete(1.0, tk.END)
            self.my_text.insert(tk.END, self.text_content)
            self.my_text.config(state=tk.DISABLED)
            self.opponent_text.config(state=tk.NORMAL)
            self.opponent_text.delete(1.0, tk.END)
            self.opponent_text.insert(tk.END, self.text_content)
            self.opponent_text.config(state=tk.DISABLED)

    def show_result(self, winner):
        messagebox.showinfo("遊戲結束", f"勝者: {winner}\n我的分數: {self.my_score}\n對手分數: {self.opponent_score}")

if __name__ == "__main__":
    game = TypingGame()
    game.root.mainloop()