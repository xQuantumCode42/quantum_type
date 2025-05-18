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
        pygame.display.set_caption("Quantum Type")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.countdown_font = pygame.font.SysFont("Arial", 48, bold=True)

        # Colors
        self.bg_color = (30, 30, 30)  # Dark background
        self.text_color = (255, 255, 255)  # White text
        self.button_color = (70, 130, 180)  # Steel blue
        self.button_hover_color = (100, 149, 237)  # Cornflower blue
        self.error_color = (255, 0, 0)  # Red for errors
        self.highlight_color = (255, 255, 0)  # Yellow for current char

        # UI states
        self.current_screen = "main_menu"  # main_menu, client_ip, host, game
        self.ip_input = ""
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

        # Button rectangles
        self.buttons = []
        self.setup_buttons()

        # Text input for IP
        self.ip_input_active = False

        # Error highlight timers
        self.error_highlights = []

    def setup_buttons(self):
        """Initialize buttons for main menu"""
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = 300
        self.buttons = [
            {
                "text": "建立房間 (Host)",
                "rect": pygame.Rect(300, start_y, button_width, button_height),
                # "action": self.game_logic.set_host_mode,
            },
            {
                "text": "加入房間 (Client)",
                "rect": pygame.Rect(
                    300, start_y + button_height + spacing, button_width, button_height
                ),
                # "action": self.show_client_ip_entry,
            },
            {
                "text": "單人模式",
                "rect": pygame.Rect(
                    300,
                    start_y + 2 * (button_height + spacing),
                    button_width,
                    button_height,
                ),
                # "action": self.game_logic.set_single_player_mode,
            },
        ]

    def run(self):
        """Main game loop"""
        while True:
            self.screen.fill(self.bg_color)
            mouse_pos = pygame.mouse.get_pos()
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        self.exit_fullscreen()
                    elif self.current_screen == "client_ip" and self.ip_input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.ip_input = self.ip_input[:-1]
                        elif event.key == pygame.K_RETURN:
                            self.game_logic.ip_input = (
                                self.ip_input
                            )  # Pass to game logic
                            self.game_logic.connect_to_host()
                        else:
                            self.ip_input += event.unicode
                    else:
                        self.game_logic.on_key_press(
                            event
                        )  # Pass key events to game logic
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            button["action"]()

            if self.current_screen == "main_menu":
                title = self.title_font.render("英文打字遊戲", True, self.text_color)
                self.screen.blit(
                    title, (self.screen_width // 2 - title.get_width() // 2, 100)
                )
                for button in self.buttons:
                    color = (
                        self.button_hover_color
                        if button["rect"].collidepoint(mouse_pos)
                        else self.button_color
                    )
                    pygame.draw.rect(
                        self.screen, color, button["rect"], border_radius=10
                    )
                    text = self.font.render(button["text"], True, self.text_color)
                    self.screen.blit(
                        text, (button["rect"].x + 10, button["rect"].y + 10)
                    )

            pygame.display.flip()
            self.clock.tick(60)
