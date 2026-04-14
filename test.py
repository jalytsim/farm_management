from datetime import date
from PIL import Image, ImageDraw, ImageFont
import ctypes
import os

# =======================
# CONFIGURATION
# =======================
GOAL_DATE = date(2026, 12, 31)   # <-- CHANGE ICI ta date objectif
BACKGROUND_COLOR = (15, 15, 20)
TEXT_COLOR = (255, 255, 255)
IMAGE_SIZE = (1920, 1080)

OUTPUT_PATH = r"C:\LifeCalendar\wallpaper.png"

# =======================
# CALCUL
# =======================
today = date.today()
days_left = (GOAL_DATE - today).days

text = f"{days_left} jours restants\njusqu'à ton objectif"

# =======================
# IMAGE
# =======================
img = Image.new("RGB", IMAGE_SIZE, BACKGROUND_COLOR)
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 80)
except:
    font = ImageFont.load_default()

text_width, text_height = draw.multiline_textsize(text, font=font)
x = (IMAGE_SIZE[0] - text_width) // 2
y = (IMAGE_SIZE[1] - text_height) // 2

draw.multiline_text((x, y), text, fill=TEXT_COLOR, font=font, align="center")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
img.save(OUTPUT_PATH)

# =======================
# APPLIQUER LE FOND D'ÉCRAN
# =======================
ctypes.windll.user32.SystemParametersInfoW(
    20, 0, OUTPUT_PATH, 3
)
