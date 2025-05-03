import time
from network.network_handler import NetworkHandler
import socket
import tkinter as tk
import queue
import tkinter.filedialog as filedialog

class GameLogic:
    def __init__(self, game_state, ui):
        self.state = game_state
        self.ui = ui
        self.text_content = ""
        
    def set_single_player_mode(self):
        self.state.is_single_player = True
        self.ui.hide_multiplayer_elements()
        self.ui.start_button.config(state=tk.NORMAL)

    def set_host_mode(self):
        self.state.is_host = True
        self.state.is_single_player = False
        
        # Get local IP address instead of possibly getting WAN IP
        try:
            # This trick gets the IP used to connect to local network
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google's DNS server
            host_ip = s.getsockname()[0]
            s.close()
        except:
            # Fallback if the above method fails
            host_ip = socket.gethostbyname(socket.gethostname())
        
        self.state.network = NetworkHandler(True, host_ip, 12345)
        self.state.network.set_game(self)
        self.state.network.start()
        # Show host information in UI
        self.ui.mode_frame.pack_forget()
        self.ui.display_host_info(host_ip)
        return host_ip

    def set_client_mode(self, host_ip):
        self.state.is_host = False
        self.state.is_single_player = False
        self.state.network = NetworkHandler(False, host_ip, 12345)
        self.state.network.set_game(self)
        self.state.network.connect(host_ip)
        self.state.network.start()

    def start_game(self):
        if not self.state.is_single_player:
            # 開始倒計時而不是直接開始遊戲
            self.start_countdown()
        else:
            self.start_actual_game()

    def start_countdown(self):
        if self.state.is_host:
            # 主機發送倒計時開始的消息
            msg = {
                "type": "COUNTDOWN_START",
                "time": time.time()
            }
            self.state.network.send_message(msg)
        self.countdown(3)  # 從3開始倒計時

    def countdown(self, count):
        if count > 0:
            # 顯示當前倒計時數字
            self.ui.show_countdown(count)
            # 一秒後顯示下一個數字
            self.ui.root.after(1000, lambda: self.countdown(count - 1))
        else:
            # 倒計時結束，開始遊戲
            self.start_actual_game()

    def start_actual_game(self):
        self.state.start_time = time.time()
        self.state.game_started = True
        self.start_timer()
        self.ui.root.focus_set()
        self.highlight_current_character()
        if not self.state.is_single_player and self.state.is_host:
            msg = {
                "type": "START",
                "start_time": self.state.start_time,
                "text": self.state.text_content
            }
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
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return
        
        text = self.text_content
        if self.state.my_progress < len(text):
            current_char = text[self.state.my_progress]
            
            if current_char == '\n':  # 當前字符是換行符
                if event.keysym == "Return":  # 玩家按下 Enter 鍵
                    self.state.my_progress += 1
                    self.state.my_score += 1
                    self.ui.update_progress(self.ui.my_text, self.state.my_progress)
                    self.ui.my_score_label.config(text=f"我的分數: {self.state.my_score}")
                    self.highlight_current_character()
                    if not self.state.is_single_player:
                        msg = {"type": "PROGRESS", "index": self.state.my_progress, "score": self.state.my_score}
                        self.state.network.send_message(msg)
                else:
                    # 錯誤輸入，顯示紅色高亮提示
                    self.ui.my_text.tag_add("error", f"1.0 + {self.state.my_progress} chars", f"1.0 + {self.state.my_progress + 1} chars")
                    self.ui.my_text.tag_config("error", background="red")
                    self.ui.root.after(500, lambda: self.ui.my_text.tag_remove("error", 1.0, tk.END))
                    self.ui.root.after(501, self.highlight_current_character)
            else:  # 當前字符不是換行符
                if event.char == current_char:
                    self.state.my_progress += 1
                    self.state.my_score += 1
                    self.ui.update_progress(self.ui.my_text, self.state.my_progress)
                    self.ui.my_score_label.config(text=f"我的分數: {self.state.my_score}")
                    self.highlight_current_character()
                    if not self.state.is_single_player:
                        msg = {"type": "PROGRESS", "index": self.state.my_progress, "score": self.state.my_score}
                        self.state.network.send_message(msg)
                else:
                    # 錯誤輸入，顯示紅色高亮提示
                    self.ui.my_text.tag_add("error", f"1.0 + {self.state.my_progress} chars", f"1.0 + {self.state.my_progress + 1} chars")
                    self.ui.my_text.tag_config("error", background="red")
                    self.ui.root.after(500, lambda: self.ui.my_text.tag_remove("error", 1.0, tk.END))
                    self.ui.root.after(501, self.highlight_current_character)
    
    def process_queue(self):
        if not self.state.is_single_player:
            try:
                while True:
                    msg = self.state.queue.get_nowait()
                    print(f"Processing message: {msg['type']}")  # Debug print
                    self.handle_message(msg)
            except queue.Empty:
                pass
        self.ui.root.after(100, self.process_queue)

    def handle_message(self, msg):
        if msg["type"] == "CLIENT_JOINED":
            self.ui.messagebox.showinfo("Client 已加入", "Client 已加入房間")
            self.ui.start_button.config(state=tk.NORMAL)
            if self.state.is_host:
                self.ui.host_status_label.config(text="客戶端已連接，可以開始遊戲", fg="green")
        elif msg["type"] == "CLIENT_CONNECTED":
            # Host receives confirmation from client
            if self.state.is_host:
                self.ui.messagebox.showinfo("客戶端已連接", "客戶端已成功連接到房間")
                self.ui.host_status_label.config(text="客戶端已連接，可以開始遊戲", fg="green")
                self.ui.start_button.config(state=tk.NORMAL)
        elif msg["type"] == "START":
            self.state.start_time = msg["start_time"]
            self.state.game_started = True
            # Make sure opponent text is visible for client
            if not self.state.is_host:
                # Ensure client UI is properly set up
                self.ui.opponent_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
                self.ui.opponent_score_label.pack(side=tk.LEFT, padx=20)
                # Set initial highlight for client
                self.highlight_current_character()
            self.start_timer()
            self.ui.root.focus_set()
            self.ui.root.bind("<KeyPress>", self.on_key_press)
        elif msg["type"] == "PROGRESS":
            self.state.opponent_progress = msg["index"]
            self.state.opponent_score = msg["score"]
            self.ui.update_progress(self.ui.opponent_text, self.state.opponent_progress)
            self.ui.opponent_score_label.config(text=f"對手分數: {self.state.opponent_score}")
        elif msg["type"] == "END":
            self.state.game_started = False
            self.ui.show_result(msg["winner"])
            self.ui.root.unbind("<KeyPress>")
        # Handle chunked text messages
        elif msg["type"] == "TEXT_CHUNKS":
            # Initialize for receiving chunks
            try:
                chunk_count = msg["count"]
                self.state.text_chunks = [""] * chunk_count
                self.state.received_chunks = 0
                self.state.total_chunks = chunk_count
                print(f"Expecting {chunk_count} text chunks")
                # Prepare text widgets for incoming text
                self.ui.my_text.config(state=tk.NORMAL)
                self.ui.my_text.delete(1.0, tk.END)
                self.ui.opponent_text.config(state=tk.NORMAL)
                self.ui.opponent_text.delete(1.0, tk.END)
                
                # Show progress message
                if not self.state.is_host:
                    self.ui.host_status_label.config(text=f"正在接收文本 (0/{chunk_count})", fg="blue")
            except Exception as e:
                print(f"Error initializing text chunks: {str(e)}")
        
        elif msg["type"] == "TEXT_CHUNK":
            try:
                # Store the received chunk
                index = msg["index"]
                chunk = msg["chunk"]
                
                # Check if we have the text_chunks list initialized
                if not hasattr(self.state, 'text_chunks') or not self.state.text_chunks:
                    print("Text chunks not initialized, creating new list")
                    if hasattr(self.state, 'total_chunks') and self.state.total_chunks > 0:
                        self.state.text_chunks = [""] * self.state.total_chunks
                    else:
                        self.state.text_chunks = [""] * 10  # Default size
                        self.state.total_chunks = 10
                    self.state.received_chunks = 0
                
                # Ensure index is within range
                if index < len(self.state.text_chunks):
                    self.state.text_chunks[index] = chunk
                    self.state.received_chunks += 1
                    print(f"Received chunk {index+1}/{self.state.total_chunks}")
                    
                    # Update progress
                    if not self.state.is_host:
                        self.ui.host_status_label.config(text=f"正在接收文本 ({self.state.received_chunks}/{self.state.total_chunks})", fg="blue")
                else:
                    print(f"Chunk index {index} out of range (max: {len(self.state.text_chunks)-1})")
            except Exception as e:
                print(f"Error processing text chunk: {str(e)}")
        
        elif msg["type"] == "TEXT_COMPLETE":
            try:
                # All chunks received, combine them
                if hasattr(self.state, 'text_chunks') and self.state.text_chunks:
                    self.text_content = "".join(self.state.text_chunks)
                    print(f"Text complete, total size: {len(self.text_content)}")
                    
                    # Update the UI
                    self.ui.my_text.config(state=tk.NORMAL)
                    self.ui.my_text.delete(1.0, tk.END)
                    self.ui.my_text.insert(tk.END, self.text_content)
                    self.ui.my_text.config(state=tk.DISABLED)
                    
                    # Make sure opponent text is visible for client
                    self.ui.opponent_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
                    self.ui.opponent_score_label.pack(side=tk.LEFT, padx=20)
                    
                    self.ui.opponent_text.config(state=tk.NORMAL)
                    self.ui.opponent_text.delete(1.0, tk.END)
                    self.ui.opponent_text.insert(tk.END, self.text_content)
                    self.ui.opponent_text.config(state=tk.DISABLED)
                    
                    # Reset progress counter
                    self.state.my_progress = 0
                    self.highlight_current_character()
                    
                    # Show notification for client
                    if not self.state.is_host:
                        self.ui.messagebox.showinfo("文本已加載", "主機已加載文本，等待遊戲開始")
                        self.ui.host_status_label.config(text="主機已加載文本，等待遊戲開始", fg="blue")
                else:
                    print("Error: text_chunks not initialized or empty")
            except Exception as e:
                print(f"Error processing text complete: {str(e)}")
                
        elif msg["type"] == "LOAD_TEXT":
            # 客戶端接收文本並更新顯示區域
            self.text_content = msg["text"]
            self.ui.my_text.config(state=tk.NORMAL)
            self.ui.my_text.delete(1.0, tk.END)
            self.ui.my_text.insert(tk.END, self.text_content)
            self.ui.my_text.config(state=tk.DISABLED)
            
            # Make sure opponent text is visible for client
            self.ui.opponent_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.ui.opponent_score_label.pack(side=tk.LEFT, padx=20)
            
            self.ui.opponent_text.config(state=tk.NORMAL)
            self.ui.opponent_text.delete(1.0, tk.END)
            self.ui.opponent_text.insert(tk.END, self.text_content)
            self.ui.opponent_text.config(state=tk.DISABLED)
            
            # Reset progress counter
            self.state.my_progress = 0
            self.highlight_current_character()
            
            # Show notification for client
            if not self.state.is_host:
                self.ui.messagebox.showinfo("文本已加載", "主機已加載文本，等待遊戲開始")
                self.ui.host_status_label.config(text="主機已加載文本，等待遊戲開始", fg="blue")
        elif msg["type"] == "COUNTDOWN_START":
            # 客戶端收到倒計時開始的消息
            self.countdown(3)

    def load_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_content = file.read()
                    print(f"Loaded text file with {len(self.text_content)} characters")
                    
                    # Update host's text display
                    self.ui.my_text.config(state=tk.NORMAL)
                    self.ui.my_text.delete(1.0, tk.END)
                    self.ui.my_text.insert(tk.END, self.text_content)
                    self.ui.my_text.config(state=tk.DISABLED)
                    self.state.my_progress = 0
                    self.highlight_current_character()
                    
                    if not self.state.is_single_player:
                        # Update host's opponent display
                        self.ui.opponent_text.config(state=tk.NORMAL)
                        self.ui.opponent_text.delete(1.0, tk.END)
                        self.ui.opponent_text.insert(tk.END, self.text_content)
                        self.ui.opponent_text.config(state=tk.DISABLED)
                        
                        # If host, send text to client
                        if self.state.is_host:
                            print(f"Host sending text to client, length: {len(self.text_content)}")
                            msg = {"type": "LOAD_TEXT", "text": self.text_content}
                            self.state.network.send_message(msg)
                            # Show confirmation message
                            self.ui.messagebox.showinfo("文本已加載", "文本已加載，等待開始遊戲")
                    
                    # Enable start button
                    if self.state.is_host or self.state.is_single_player:
                        self.ui.start_button.config(state=tk.NORMAL)
            except Exception as e:
                print(f"Error loading text file: {str(e)}")
                self.ui.messagebox.showerror("錯誤", f"無法加載文本文件: {str(e)}")

    def connect_to_host(self):
        host_ip = self.ui.ip_entry.get()
        if not host_ip:
            self.ui.messagebox.showerror("錯誤", "請輸入主機IP地址")
            return
            
        # Set client mode first
        self.state.is_host = False
        self.state.is_single_player = False
        
        # Then create network connection
        try:
            self.state.network = NetworkHandler(False, host_ip, 12345)
            self.state.network.set_game(self)
            self.state.network.connect(host_ip)
            self.state.network.start()
            
            # Update UI to show successful connection
            self.ui.connect_to_host()
            
            # Send a message to host to confirm connection
            msg = {"type": "CLIENT_CONNECTED"}
            self.state.network.send_message(msg)
        except Exception as e:
            self.ui.messagebox.showerror("連接錯誤", f"無法連接到主機: {str(e)}")

    def highlight_current_character(self):
        """Highlight the current character position with yellow background"""
        if hasattr(self, 'text_content') and self.text_content and self.state.my_progress < len(self.text_content):
            # Remove any previous highlight
            self.ui.my_text.tag_remove("current", "1.0", tk.END)
            # Add highlight for current character
            self.ui.my_text.tag_add("current", f"1.0 + {self.state.my_progress} chars", f"1.0 + {self.state.my_progress + 1} chars")
            self.ui.my_text.tag_config("current", background="yellow")