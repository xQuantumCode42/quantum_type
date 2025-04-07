import tkinter as tk
from tkinter import filedialog

class TypingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("英文打字遊戲")
        self.score = 0
        self.index = 0  # 追蹤目前打到哪個字元
        self.text = ""

        # 建立用來顯示文章的文字區域
        self.text_display = tk.Text(root, width=60, height=15, font=("Helvetica", 14))
        self.text_display.pack(pady=10)

        # 建立用來顯示分數的 Label
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Helvetica", 14))
        self.score_label.pack(pady=5)

        # 綁定鍵盤事件
        self.root.bind("<Key>", self.key_pressed)

        # 讀取文章內容
        self.load_text()

    def load_text(self):
        # 使用檔案選擇對話框讓使用者選取 txt 檔案
        file_path = filedialog.askopenfilename(title="選取文字檔", filetypes=(("Text Files", "*.txt"),))
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.text = f.read()
            # 將內容顯示在文字區域中
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, self.text)
            # 標示第一個字元
            self.highlight_current_letter()
            # 設定主視窗取得焦點，確保鍵盤事件可以觸發
            self.root.focus_set()

    def highlight_current_letter(self):
        # 移除先前的標示
        self.text_display.tag_remove("highlight", "1.0", tk.END)
        # 根據目前 index 計算出文字區域中的位置
        pos = f"1.0 + {self.index} chars"
        # 為目前字元加上標示 tag
        self.text_display.tag_add("highlight", pos, f"{pos} +1c")
        self.text_display.tag_config("highlight", background="yellow")

    def key_pressed(self, event):
        # 若已完成所有文字，則不再處理
        if self.index >= len(self.text):
            return

        current_char = self.text[self.index]
        # 檢查使用者輸入是否與目前字元一致
        if event.char == current_char:
            self.index += 1
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.highlight_current_letter()
        else:
            # 可在此處加入錯誤提示或扣分的邏輯
            pass

if __name__ == "__main__":
    root = tk.Tk()
    game = TypingGame(root)
    root.mainloop()
