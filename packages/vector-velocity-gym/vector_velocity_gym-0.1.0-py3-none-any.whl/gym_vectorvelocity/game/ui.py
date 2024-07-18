import pygame
from .config import settings
class UI:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()  
        self.font = pygame.font.Font(None, 36) 

    def show_coins(self, highscore: int):
        """
        Displays the number of coins collected in the left upper corner.
        :param highscore: int, The number of coins collected.
        """
        text = self.font.render(f'Coins: {highscore}', True, (128, 0, 120))
        self.screen.blit(text, (10, 10)) 

    def show_highscore(self, coins):
        """
        Displays the highscore in the left upper corner.
        :param coins: int, The highscore.
        """
        text = self.font.render(f'High Score: {coins}', True, (184, 0, 184))
        self.screen.blit(text, (10, 50))

    def show_credits(self):
        """
        Displays the credits in the right lower corner.
        """
        text = pygame.font.SysFont(None, 18)
        text = text.render("Background: vecteezy.com", True, (118, 0, 118))
        self.screen.blit(text, (settings.SCREEN_WIDTH - 170, settings.SCREEN_HEIGHT - 30))

    def show_game_over(self, coins: int, score: int, callback: callable):
        """
        Displays the game over screen.
        :param coins: int, The number of coins collected.
        :param score: int, The score.
        :param callback: callable, The function to call when the game is over.
        """
        game_over_text = f"Game Over space cadet!\nScore: {score}\nCoins: {coins}\nPress R to restart"
        text_surf = self.font.render(game_over_text, True, (255, 255, 255))

        overlay_height = int(settings.SCREEN_HEIGHT * 0.2) 
        overlay = pygame.Surface((settings.SCREEN_WIDTH, overlay_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0)) 

        # Positioning the text box
        text_x = (settings.SCREEN_WIDTH - text_surf.get_width()) // 2
        text_y = (settings.SCREEN_HEIGHT - overlay_height) // 2 + (overlay_height - text_surf.get_height()) // 2

        self.screen.blit(overlay, (0, (settings.SCREEN_HEIGHT - overlay_height) // 2))
        self.screen.blit(text_surf, (text_x, text_y))

        # Update the display and wait for input
        pygame.display.flip()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    callback()
                    waiting_for_input = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting_for_input = False