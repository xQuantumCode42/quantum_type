import tkinter as tk
from tkinter import filedialog, messagebox


class GameUI:
    def __init__(self):
        self.game_logic = None
        self.root = tk.Tk()
        self.root.title("英文打字遊戲")
        self.root.geometry("800x600")
        self.messagebox = messagebox
        self.filedialog = filedialog
        self.countdown_label = None
        self.is_fullscreen = False  # 添加全螢幕狀態追蹤
        
        # 綁定 F11 切換全螢幕
        self.root.bind("<F11>", self.toggle_fullscreen)
        # 綁定 Escape 退出全螢幕
        self.root.bind("<Escape>", self.exit_fullscreen)

    def set_game_logic(self, game_logic):
        self.game_logic = game_logic

    def setup_ui(self):
        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(side=tk.TOP, pady=20)
        tk.Label(self.mode_frame, text="選擇模式：").pack(side=tk.LEFT)
        tk.Button(
            self.mode_frame,
            text="建立房間 (Host)",
            command=self.game_logic.set_host_mode,
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            self.mode_frame, text="加入房間 (Client)", command=self.show_client_ip_entry
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            self.mode_frame,
            text="單人模式",
            command=self.game_logic.set_single_player_mode,
        ).pack(side=tk.LEFT, padx=10)

        # IP frames for client and host
        self.ip_frame = tk.Frame(self.root)
        self.ip_label = tk.Label(self.ip_frame, text="輸入主機IP:")
        self.ip_label.pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(self.ip_frame)
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        self.connect_button = tk.Button(
            self.ip_frame, text="連接", command=self.game_logic.connect_to_host
        )
        self.connect_button.pack(side=tk.LEFT, padx=5)

        # Host info frame (new)
        self.host_frame = tk.Frame(self.root)
        self.host_ip_label = tk.Label(
            self.host_frame, text="", font=("Arial", 12, "bold")
        )
        self.host_ip_label.pack(pady=10)
        self.host_status_label = tk.Label(
            self.host_frame, text="等待客戶端連接...", fg="blue"
        )
        self.host_status_label.pack(pady=5)

        self.basic_frame = tk.Frame(self.root)
        self.basic_frame.pack(pady=20)
        self.start_button = tk.Button(
            self.basic_frame,
            text="開始遊戲",
            command=self.game_logic.start_game,
            state=tk.DISABLED,
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.back_button = tk.Button(
            self.basic_frame,
            text="回主選單",
            command=self.game_logic.back_to_home,
            state=tk.DISABLED,
        )
        self.back_button.pack(side=tk.LEFT, padx=10)

        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.my_text = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Courier", 12),
            state=tk.DISABLED,
            height=10,
        )
        self.my_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.opponent_text = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Courier", 12),
            state=tk.DISABLED,
            height=10,
        )
        self.opponent_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.score_frame = tk.Frame(self.root)
        self.score_frame.pack(pady=5)
        self.my_score_label = tk.Label(self.score_frame, text="我的分數: 0")
        self.my_score_label.pack(side=tk.LEFT, padx=20)
        self.opponent_score_label = tk.Label(self.score_frame, text="對手分數: 0")
        self.opponent_score_label.pack(side=tk.LEFT, padx=20)
        self.timer_label = tk.Label(self.score_frame, text="剩餘時間: 60")
        self.timer_label.pack(side=tk.LEFT, padx=20)
        self.countdown_label = tk.Label(
            self.root, text="", font=("Arial", 48, "bold"), fg="red"
        )

        self.load_button = tk.Button(
            self.root, text="加載文本", command=self.game_logic.load_text
        )
        self.load_button.pack(pady=5)

        self.root.bind("<KeyPress>", self.game_logic.on_key_press)
        self.game_logic.process_queue()

    def show_client_ip_entry(self):
        """Show the IP entry frame for client mode"""
        self.back_button.config(state=tk.NORMAL)
        self.mode_frame.pack_forget()
        self.host_frame.pack_forget()  # Hide host frame if visible
        self.ip_frame.pack(pady=20)
        self.ip_entry.focus_set()

    def display_host_info(self, host_ip):
        """Display host information"""
        self.ip_frame.pack_forget()  # Hide client frame if visible
        self.host_frame.pack(pady=20)
        self.host_ip_label.config(text=f"房間IP地址: {host_ip}")
        self.host_status_label.config(text="等待客戶端連接...")

    def update_progress(self, text_widget, index):
        text_widget.tag_remove("current", 1.0, tk.END)
        if index < len(self.game_logic.text_content):
            text_widget.tag_add(
                "current", f"1.0 + {index} chars", f"1.0 + {index + 1} chars"
            )
            text_widget.tag_config("current", background="yellow")

    def show_error_highlight(self, text_widget, index):
        text_widget.tag_add("error", f"1.0 + {index} chars", f"1.0 + {index + 1} chars")
        text_widget.tag_config("error", background="red")
        self.root.after(500, lambda: text_widget.tag_remove("error", 1.0, tk.END))

    def update_timer_display(self, remaining):
        self.timer_label.config(text=f"剩餘時間: {int(remaining)}")

    def update_score_display(self, my_score, opponent_score=None):
        self.my_score_label.config(text=f"我的分數: {my_score}")
        if opponent_score is not None:
            self.opponent_score_label.config(text=f"對手分數: {opponent_score}")

    def show_result(self, winner, my_score=None, opponent_score=None):
        if my_score is not None and opponent_score is not None:
            messagebox.showinfo(
                "遊戲結束",
                f"勝者: {winner}\n我的分數: {my_score}\n對手分數: {opponent_score}",
            )
        else:
            messagebox.showinfo("遊戲結束", f"勝者: {winner}")

    def hide_multiplayer_elements(self):
        self.mode_frame.pack_forget()
        self.ip_frame.pack_forget()
        self.host_frame.pack_forget()
        self.opponent_text.pack_forget()
        self.opponent_score_label.pack_forget()

    def connect_to_host(self):
        """Called after successful connection to host"""
        # Hide IP entry frame
        self.ip_frame.pack_forget()
        # Show connection success message
        self.host_frame.pack(pady=20)
        self.host_ip_label.config(text="已連接到主機")
        self.host_status_label.config(text="等待主機開始遊戲...", fg="green")

        # Ensure opponent UI elements are visible
        if not self.opponent_text.winfo_ismapped():
            self.opponent_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        if not self.opponent_score_label.winfo_ismapped():
            self.opponent_score_label.pack(side=tk.LEFT, padx=20)

    def show_countdown(self, count):
        # 顯示倒計時數字
        self.countdown_label.config(text=str(count))
        self.countdown_label.place(relx=0.5, rely=0.5, anchor="center")

        # 如果是最後一個數字，設置一秒後隱藏
        if count == 1:
            self.root.after(1000, self.hide_countdown)

    def hide_countdown(self):
        # 隱藏倒計時標籤
        self.countdown_label.place_forget()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            # 恢復到固定大小
            self.root.geometry("800x600")
        return "break"  # 防止事件繼續傳播

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.root.geometry("800x600")
        return "break"  # 防止事件繼續傳播
