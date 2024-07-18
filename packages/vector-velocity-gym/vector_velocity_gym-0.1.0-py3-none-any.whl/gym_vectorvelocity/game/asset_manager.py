import pygame 
from .config import settings
from .config.settings import save_setting
import os

class AssetManager: 
    """
    This class manages the assets of the game and initializes them on start.
    """
    def __init__(self): 
        self.is_audio_available = pygame.mixer.get_init()
        self.assets = {}

        if self.is_audio_available: 
            pygame.mixer.init()

        self._load_assets()

    def _load_assets(self): 
        """
        Load all assets from the settings file and store them in the assets dictionary.
        """
        self.assets['background'] = pygame.image.load(settings.BACKGROUND_ASSET_PATH)
        self.assets['background'] = pygame.transform.scale(self.assets['background'], (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.assets["player"] = pygame.image.load(settings.PLAYER_ASSET_PATH)
        self.assets["obstacles"] = []

        if self.is_audio_available:
            self.assets['bgmusic'] = pygame.mixer.Sound(settings.SOUNDS_ASSET_PATH + "bgmusic.wav")
            self.assets['bgmusic'].set_volume(settings.MUSIC_VOLUME)

        obstacles = os.listdir(settings.OBSTACLE_ASSET_PATH)
        for obstacle in obstacles: 
            self.assets["obstacles"].append(pygame.image.load(settings.OBSTACLE_ASSET_PATH + obstacle)) 


    def get_asset(self, key: str): 
        """
        retrieve an asset from the assets dictionary by key.
        """
        return self.assets[key]
    
    def set_audio_volume(self, volume: float, save_to_settings:bool=False): 
        """
        Set the volume of the games background music.
        :param volume: float between 0.0 and 1.0
        :param save_to_settings: bool, if True the volume will be saved to the settings file.
        """
        if volume > 1.0 or volume < 0.0: 
            raise ValueError("Volume must be between 0.0 and 1.0")
        if self.is_audio_available: 
            self.assets['bgmusic'].set_volume(volume)
            if save_to_settings: 
                settings.MUSIC_VOLUME = volume
                save_setting('MUSIC_VOLUME', volume)
