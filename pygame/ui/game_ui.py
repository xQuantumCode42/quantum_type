import pygame
import sys
import os
from pygame import font

class GameUI:
    def __init__(self):
        self.game_logic = None
        self.screen_width = 800
        self.screen_height = 600
        self.is_fullscreen = False
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("英文打字遊戲")
        self.clock = pygame.time.Clock()
        
        # 字體設置
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.countdown_font = pygame.font.SysFont("Arial", 48, bold=True)

        # 顏色定義
        self.bg_color = (30, 30, 30)  # 深色背景
        self.text_color = (255, 255, 255)  # 白色文字
        self.button_color = (70, 130, 180)  # 鋼藍色按鈕
        self.button_hover_color = (100, 149, 237)  # 懸停時的淺藍色
        self.error_color = (255, 0, 0)  # 錯誤提示紅色
        self.highlight_color = (255, 255, 0)  # 當前字符黃色高亮
        self.progress_color = (0, 255, 0)  # 進度條綠色

        try:
            self.font = pygame.font.SysFont("microsoftyaheimicrosoftyaheiui", 24)
            self.title_font = pygame.font.SysFont("microsoftyaheimicrosoftyaheiui", 36, bold=True)
            self.countdown_font = pygame.font.SysFont("microsoftyaheimicrosoftyaheiui", 48, bold=True)
        except:
            # 如果找不到微軟雅黑，嘗試使用其他中文字體
            try:
                self.font = pygame.font.SysFont("simsun", 24)
                self.title_font = pygame.font.SysFont("simsun", 36, bold=True)
                self.countdown_font = pygame.font.SysFont("simsun", 48, bold=True)
            except:
                # 如果都找不到，使用系統默認字體
                self.font = pygame.font.Font(None, 24)
                self.title_font = pygame.font.Font(None, 36)
                self.countdown_font = pygame.font.Font(None, 48)

        # UI 狀態
        self.current_screen = "main_menu"  # main_menu, client_ip, host, game
        self.ip_input = ""
        self.ip_input_active = False
        self.host_ip = ""
        self.host_status = "等待客戶端連接..."
        self.my_score = 0
        self.opponent_score = 0
        self.timer = 60
        self.countdown = None
        self.my_text_content = ""
        self.opponent_text_content = ""
        self.my_progress = 0
        self.opponent_progress = 0
        self.error_highlights = []

        # 按鈕設置
        self.buttons = []
        self.setup_buttons()

    def setup_buttons(self):
        """初始化主選單按鈕"""
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = 300
        
        self.buttons = [
            {
                "text": "建立房間 (Host)",
                "rect": pygame.Rect((self.screen_width - button_width) // 2, start_y, button_width, button_height),
                "action": lambda: self.game_logic.set_host_mode() if self.game_logic else None,
            },
            {
                "text": "加入房間 (Client)",
                "rect": pygame.Rect((self.screen_width - button_width) // 2, start_y + button_height + spacing, button_width, button_height),
                "action": lambda: self.show_client_ip_entry() if self.game_logic else None,
            },
            {
                "text": "單人模式",
                "rect": pygame.Rect((self.screen_width - button_width) // 2, start_y + 2 * (button_height + spacing), button_width, button_height),
                "action": lambda: self.game_logic.set_single_player_mode() if self.game_logic else None,
            },
        ]

    def show_client_ip_entry(self):
        """顯示客戶端IP輸入界面"""
        self.current_screen = "client_ip"
        self.ip_input_active = True
        self.ip_input = ""

    def display_host_info(self, host_ip):
        """顯示主機信息"""
        self.current_screen = "host"
        self.host_ip = host_ip
        self.host_status = "等待客戶端連接..."

    def render_main_menu(self):
        """渲染主選單"""
        # 渲染標題
        title = self.title_font.render("英文打字遊戲", True, self.text_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)

        # 渲染按鈕
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            color = self.button_hover_color if button["rect"].collidepoint(mouse_pos) else self.button_color
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=10)
            text = self.font.render(button["text"], True, self.text_color)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)

    def render_client_ip_screen(self):
        """渲染客戶端IP輸入界面"""
        # 渲染標題
        title = self.font.render("輸入主機IP:", True, self.text_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(title, title_rect)

        # 渲染IP輸入框
        input_rect = pygame.Rect((self.screen_width - 300) // 2, 250, 300, 40)
        pygame.draw.rect(self.screen, self.text_color, input_rect, 2)
        ip_surface = self.font.render(self.ip_input, True, self.text_color)
        self.screen.blit(ip_surface, (input_rect.x + 5, input_rect.y + 5))

    def render_host_screen(self):
        """渲染主機等待界面"""
        # 渲染IP信息
        ip_text = self.font.render(f"房間IP地址: {self.host_ip}", True, self.text_color)
        ip_rect = ip_text.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(ip_text, ip_rect)

        # 渲染狀態信息
        status_text = self.font.render(self.host_status, True, self.text_color)
        status_rect = status_text.get_rect(center=(self.screen_width // 2, 250))
        self.screen.blit(status_text, status_rect)

    def render_game_screen(self):
        """渲染遊戲界面"""
        # 渲染計時器
        timer_text = self.font.render(f"剩餘時間: {int(self.timer)}", True, self.text_color)
        self.screen.blit(timer_text, (20, 20))

        # 渲染分數
        score_text = self.font.render(f"我的分數: {self.my_score}", True, self.text_color)
        self.screen.blit(score_text, (20, 60))

        if not self.game_logic.game_state.is_single_player:
            opponent_score = self.font.render(f"對手分數: {self.opponent_score}", True, self.text_color)
            self.screen.blit(opponent_score, (20, 100))

        # 渲染文本區域
        text_y = self.screen_height // 2 - 100
        if self.my_text_content:
            text_surface = self.font.render(self.my_text_content, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, text_y))
            self.screen.blit(text_surface, text_rect)

            # 渲染當前字符高亮
            x = text_rect.x
            for i, char in enumerate(self.my_text_content):
                char_surface = self.font.render(char, True, 
                                              self.highlight_color if i == len(self.my_text_content) - 1 
                                              else self.text_color)
                self.screen.blit(char_surface, (x, text_rect.y))
                x += char_surface.get_width()

        # 渲染進度條
        progress_width = 600
        progress_height = 20
        progress_x = (self.screen_width - progress_width) // 2
        progress_y = self.screen_height - 100

        # 背景進度條
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (progress_x, progress_y, progress_width, progress_height))
        # 當前進度
        progress_fill = int(progress_width * (self.my_progress / 100))
        if progress_fill > 0:
            pygame.draw.rect(self.screen, self.progress_color,
                           (progress_x, progress_y, progress_fill, progress_height))

        # 對手進度條（多人模式）
        if not self.game_logic.game_state.is_single_player:
            opponent_progress_y = progress_y - 30
            pygame.draw.rect(self.screen, (100, 100, 100),
                            (progress_x, opponent_progress_y, progress_width, progress_height))
            opponent_progress_fill = int(progress_width * (self.opponent_progress / 100))
            if opponent_progress_fill > 0:
                pygame.draw.rect(self.screen, (200, 100, 100),
                               (progress_x, opponent_progress_y, opponent_progress_fill, progress_height))

    def show_countdown(self, count):
        """顯示倒計時"""
        countdown_text = self.countdown_font.render(str(count), True, self.text_color)
        countdown_rect = countdown_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(countdown_text, countdown_rect)

    def run(self):
        """主遊戲循環"""
        while True:
            self.screen.fill(self.bg_color)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        if self.is_fullscreen:
                            self.exit_fullscreen()
                        elif self.current_screen != "main_menu":
                            self.current_screen = "main_menu"
                    elif self.current_screen == "client_ip" and self.ip_input_active:
                        if event.key == pygame.K_RETURN:
                            if self.game_logic:
                                self.game_logic.ip_input = self.ip_input
                                self.game_logic.connect_to_host()
                        elif event.key == pygame.K_BACKSPACE:
                            self.ip_input = self.ip_input[:-1]
                        else:
                            self.ip_input += event.unicode
                    elif self.current_screen == "game":
                        self.game_logic.on_key_press(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.current_screen == "main_menu":
                        for button in self.buttons:
                            if button["rect"].collidepoint(mouse_pos):
                                button["action"]()

            # 根據當前界面渲染不同內容
            if self.current_screen == "main_menu":
                self.render_main_menu()
            elif self.current_screen == "client_ip":
                self.render_client_ip_screen()
            elif self.current_screen == "host":
                self.render_host_screen()
            elif self.current_screen == "game":
                self.render_game_screen()

            if self.countdown is not None:
                self.show_countdown(self.countdown)

            pygame.display.flip()
            self.clock.tick(60)

    def toggle_fullscreen(self):
        """切換全螢幕"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def exit_fullscreen(self):
        """退出全螢幕"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))