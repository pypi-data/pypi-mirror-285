import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

SETTINGS_FILE = os.path.join(current_dir, "settings.json")
DEFAULTS_FILE = os.path.join(current_dir, "defaults.json")

# root path is current directory ../../
root_path = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))

with open(DEFAULTS_FILE, 'r') as f:
    defaults = json.load(f)

if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(defaults, f, indent=4)

with open(SETTINGS_FILE, 'r') as f:
    settings = json.load(f)

for key, value in defaults.items():
    if key not in settings:
        settings[key] = value

with open(SETTINGS_FILE, 'w') as f:
    json.dump(settings, f, indent=4)

def save_setting(key, value):
    settings[key] = value
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# Apply settings to variables
SCREEN_WIDTH = settings['SCREEN_WIDTH']
SCREEN_HEIGHT = settings['SCREEN_HEIGHT']
FRAME_RATE = settings['FRAME_RATE']
CAPTION = settings['CAPTION']
MUSIC_VOLUME = settings['MUSIC_VOLUME']

# level settings
LEVEL_WIDTH_PERCENTAGE = settings['LEVEL_WIDTH_PERCENTAGE']
LEVEL_HEIGHT_PERCENTAGE = settings['LEVEL_HEIGHT_PERCENTAGE']
LEVEL_WIDTH = int(SCREEN_WIDTH * LEVEL_WIDTH_PERCENTAGE)
LEVEL_HEIGHT = SCREEN_HEIGHT * 2
LEVEL_X = (SCREEN_WIDTH - LEVEL_WIDTH) // 2
LEVEL_Y = -LEVEL_HEIGHT / 2 
PLAYER_Y = settings['PLAYER_Y']

LANE_POSITIONS = [LEVEL_X + 100, LEVEL_X + LEVEL_WIDTH // 2, LEVEL_X + LEVEL_WIDTH - 190]

# asset settings
OBSTACLE_ASSET_PATH = os.path.join(root_path, settings['OBSTACLE_ASSET_PATH'])
SOUNDS_ASSET_PATH = os.path.join(root_path, settings['SOUNDS_ASSET_PATH'])
PLAYER_ASSET_PATH = os.path.join(root_path, settings['PLAYER_ASSET_PATH'])
BACKGROUND_ASSET_PATH = os.path.join(root_path, settings['BACKGROUND_ASSET_PATH'])


# difficulty settings
MAXIMUM_SPEED = settings['MAXIMUM_SPEED']
COIN_SPEEDUP_FACTOR = settings['COIN_SPEEDUP_FACTOR']
SCORE_SPEEDUP_FACTOR = settings['SCORE_SPEEDUP_FACTOR']
DIFFICULTY_INCREASE_FACTOR = settings['DIFFICULTY_INCREASE_FACTOR']

MAXIMUM_OBSTACLE_SPAWN_COUNT = settings['MAXIMUM_OBSTACLE_SPAWN_COUNT']
MAINIMUM_OBSTACLE_SPAWN_RATE = settings['MAINIMUM_OBSTACLE_SPAWN_RATE']
COIN_SPAWN_RATE_MULTIPLIER = settings['COIN_SPAWN_RATE_MULTIPLIER']

OBSTACLE_SPAWN_RATE_DECREASE = settings['OBSTACLE_SPAWN_RATE_DECREASE']
OBSTACLE_Y_OFFSET_DECREASE = settings['OBSTACLE_Y_OFFSET_DECREASE']
COIN_Y_OFFSET_DECREASE = settings['COIN_Y_OFFSET_DECREASE']
