import time
from network.network_handler import NetworkHandler
import socket
import tkinter as tk
import queue

class GameLogic:
    def __init__(self, game_state, ui):
        self.state = game_state
        self.ui = ui
        
    def set_single_player_mode(self):
        self.state.is_single_player = True
        self.ui.hide_multiplayer_elements()
        self.ui.start_button.config(state=tk.NORMAL)

    def set_host_mode(self):
        self.state.is_host = True
        self.state.is_single_player = False
        host_ip = socket.gethostbyname(socket.gethostname())
        self.state.network = NetworkHandler(True, host_ip, 12345)
        self.state.network.set_game(self)
        self.state.network.start()
        return host_ip

    def set_client_mode(self, host_ip):
        self.state.is_host = False
        self.state.is_single_player = False
        self.state.network = NetworkHandler(False, host_ip, 12345)
        self.state.network.set_game(self)
        self.state.network.connect(host_ip)
        self.state.network.start()

    def start_game(self):
        self.state.start_time = time.time()
        self.state.game_started = True
        self.start_timer()
        self.ui.root.focus_set()
        if not self.state.is_single_player and self.state.is_host:
            msg = {"type": "START", "start_time": self.state.start_time}
            self.state.network.send_message(msg)

    def start_timer(self):
        if self.state.game_started:
            elapsed = time.time() - self.state.start_time
            remaining = 60 - elapsed
            if remaining > 0:
                self.ui.update_timer_display(remaining)
                self.ui.root.after(1000, self.start_timer)
            else:
                self.end_game()

    def end_game(self):
        self.state.game_started = False
        if self.state.is_single_player:
            self.ui.show_result("", self.state.my_score, None)
        elif self.state.is_host:
            winner = self.determine_winner()
            msg = {"type": "END", "winner": winner}
            self.state.network.send_message(msg)
            self.ui.show_result(winner, self.state.my_score, self.state.opponent_score)

    def determine_winner(self):
        if self.state.my_score > self.state.opponent_score:
            return "Host"
        elif self.state.opponent_score > self.state.my_score:
            return "Client"
        else:
            return "平手"
    
    def on_key_press(self, event):
        if self.state.game_started:
            self.process_key_input(event)
    
    def process_key_input(self, event):
        text = self.text_content
        if self.state.my_progress < len(text):
            current_char = text[self.state.my_progress]
            if current_char == '\n':  # 當前字符是換行符
                if event.keysym == "Return":  # 玩家按下 Enter 鍵
                    self.state.my_progress += 1
                    self.state.my_score += 1
                    self.ui.update_progress(self.ui.my_text, self.state.my_progress)
                    self.ui.my_score_label.config(text=f"我的分數: {self.state.my_score}")
                    if not self.state.is_single_player:
                        msg = {"type": "PROGRESS", "index": self.state.my_progress, "score": self.state.my_score}
                        self.state.network.send_message(msg)
                else:
                    # 錯誤輸入，顯示紅色高亮提示
                    self.ui.my_text.tag_add("error", f"1.0 + {self.state.my_progress} chars", f"1.0 + {self.state.my_progress + 1} chars")
                    self.ui.my_text.tag_config("error", background="red")
                    self.ui.root.after(500, lambda: self.ui.my_text.tag_remove("error", 1.0, tk.END))
            else:  # 當前字符不是換行符
                if event.char == current_char:
                    self.state.my_progress += 1
                    self.state.my_score += 1
                    self.ui.update_progress(self.ui.my_text, self.state.my_progress)
                    self.ui.my_score_label.config(text=f"我的分數: {self.state.my_score}")
                    if not self.state.is_single_player:
                        msg = {"type": "PROGRESS", "index": self.state.my_progress, "score": self.state.my_score}
                        self.state.network.send_message(msg)
                else:
                    # 錯誤輸入，顯示紅色高亮提示
                    self.ui.my_text.tag_add("error", f"1.0 + {self.state.my_progress} chars", f"1.0 + {self.state.my_progress + 1} chars")
                    self.ui.my_text.tag_config("error", background="red")
                    self.ui.root.after(500, lambda: self.ui.my_text.tag_remove("error", 1.0, tk.END))
    
    def process_queue(self):
        if not self.state.is_single_player:
            try:
                while True:
                    msg = self.state.queue.get_nowait()
                    self.handle_message(msg)
            except queue.Empty:
                pass
        self.ui.root.after(100, self.process_queue)

    def handle_message(self, msg):
        if msg["type"] == "CLIENT_JOINED":
            self.ui.messagebox.showinfo("Client 已加入", "Client 已加入房間")
            self.ui.start_button.config(state=tk.NORMAL)
        elif msg["type"] == "START":
            self.state.start_time = msg["start_time"]
            self.state.game_started = True
            self.start_timer()
            self.ui.root.focus_set()
        elif msg["type"] == "PROGRESS":
            self.state.opponent_progress = msg["index"]
            self.state.opponent_score = msg["score"]
            self.ui.update_progress(self.ui.opponent_text, self.state.opponent_progress)
            self.ui.opponent_score_label.config(text=f"對手分數: {self.state.opponent_score}")
        elif msg["type"] == "END":
            self.state.game_started = False
            self.ui.show_result(msg["winner"])
            self.ui.root.unbind("<KeyPress>")
        elif msg["type"] == "LOAD_TEXT":
            # 客戶端接收文本並更新顯示區域
            self.text_content = msg["text"]
            self.ui.my_text.config(state=tk.NORMAL)
            self.ui.my_text.delete(1.0, tk.END)
            self.ui.my_text.insert(tk.END, self.text_content)
            self.ui.my_text.config(state=tk.DISABLED)
            self.ui.opponent_text.config(state=tk.NORMAL)
            self.ui.opponent_text.delete(1.0, tk.END)
            self.ui.opponent_text.insert(tk.END, self.text_content)
            self.ui.opponent_text.config(state=tk.DISABLED)
    
    def load_text(self):
        file_path = self.ui.filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_content = file.read()
                self.ui.my_text.config(state=tk.NORMAL)
                self.ui.my_text.delete(1.0, tk.END)
                self.ui.my_text.insert(tk.END, self.text_content)
                self.ui.my_text.config(state=tk.DISABLED)
                if not self.state.is_single_player:
                    self.ui.opponent_text.config(state=tk.NORMAL)
                    self.ui.opponent_text.delete(1.0, tk.END)
                    self.ui.opponent_text.insert(tk.END, self.text_content)
                    self.ui.opponent_text.config(state=tk.DISABLED)
                    # 如果是主機，發送文本內容給客戶端
                    if self.state.is_host:
                        msg = {"type": "LOAD_TEXT", "text": self.text_content}
                        self.state.network.send_message(msg)
                if self.state.is_host or self.state.is_single_player:
                    self.ui.start_button.config(state=tk.NORMAL)

    def connect_to_host(self):
        host_ip = self.state.ip_entry.get()
        self.network = NetworkHandler(False, host_ip, 12345)
        self.network.connect(host_ip)
        self.network.start()
        self.ui.ip_frame.pack_forget()