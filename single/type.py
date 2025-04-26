import tkinter as tk
from tkinter import filedialog

# 創建主窗口
root = tk.Tk()
root.title("英文打字遊戲")
root.geometry("1000x700+250+100")  # 設置窗口大小


# 創建文本顯示區域
text_display = tk.Text(root, wrap=tk.WORD, font=("Courier", 12), state=tk.DISABLED)
text_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# 創建分數標籤
score_label = tk.Label(root, text="分數: 0", font=("Arial", 12))
score_label.pack(pady=5)

# 初始化全局變數
score = 0  # 分數
current_index = 0  # 當前字母索引
text_content = ""  # 存儲文本內容

# 載入文本檔案的函數
def load_text():
    global current_index, score, text_content
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
            # 啟用 Text 控件以插入內容
            text_display.config(state=tk.NORMAL)
            text_display.delete(1.0, tk.END)  # 清空現有內容
            text_display.insert(tk.END, text_content)  # 插入新內容
            text_display.config(state=tk.DISABLED)  # 禁用編輯
            # 重置遊戲狀態
            current_index = 0
            score = 0
            score_label.config(text="分數: 0")
            highlight_current_char()

# 高亮當前字母的函數
def highlight_current_char():
    text_display.tag_remove("current", 1.0, tk.END)  # 移除之前的高亮
    if current_index < len(text_content):
        text_display.tag_add("current", f"1.0 + {current_index} chars", f"1.0 + {current_index + 1} chars")
        text_display.tag_config("current", background="yellow")  # 設置高亮顏色

# 處理鍵盤輸入的函數
def on_key_press(event):
    global current_index, score
    if current_index < len(text_content):
        current_char = text_content[current_index]
        # 處理換行符
        if current_char == '\n':
            if event.keysym == "Return":  # 用戶按下 Enter
                current_index += 1
                score += 1
                score_label.config(text=f"分數: {score}")
                highlight_current_char()
            else:
                text_display.tag_add("error", f"1.0 + {current_index} chars", f"1.0 + {current_index + 1} chars")
                text_display.tag_config("error", background="red")
                root.after(500, lambda: text_display.tag_remove("error", 1.0, tk.END))
        else:
            if event.char == current_char:  # 輸入正確
                current_index += 1
                score += 1
                score_label.config(text=f"分數: {score}")
                highlight_current_char()
            else:  # 輸入錯誤
                text_display.tag_add("error", f"1.0 + {current_index} chars", f"1.0 + {current_index + 1} chars")
                text_display.tag_config("error", background="red")
                root.after(500, lambda: text_display.tag_remove("error", 1.0, tk.END))

# 綁定鍵盤事件並設置焦點
root.bind("<KeyPress>", on_key_press)
root.focus_set()

# 創建載入按鈕
load_button = tk.Button(root, text="加載文本", command=load_text, font=("Arial", 12))
load_button.pack(pady=5)

# 啟動主循環
root.mainloop()