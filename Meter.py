
from enum import Enum
import os
import cv2
from ImageManager import PlaceImage, PlaceText
from config import DEFAULT_FONT, TEXT_COLOR_WHITE


class MeterType(Enum):
    TOMATO = 1
    POPCORN = 2
class Meter:
    def __init__(self, meter_type, score):
        self.meter_type = meter_type
        self.score = self.parse_score(score)
        is_tomato = self.meter_type == MeterType.TOMATO
        self.x = os.environ.get('TOMATO_METER_X') if is_tomato else os.environ.get('POPCORN_METER_X')
    def parse_score(self, score):
        try:
            return float(score)
        except (ValueError, TypeError):
            print(f"Warning: Invalid score value '{score}'. Using 0 instead.")
            return 0

    def get_image_tuple(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        is_tomato = self.meter_type == MeterType.TOMATO
        is_fresh = self.score >= 60
        
        # Build icon filename and position based on type and freshness
        icon_type = "Tomato" if is_tomato else "Popcorn"
        freshness = "Fresh" if is_fresh else "Rotten"
        self.image_path = os.path.join(current_dir, "icons", f"{freshness}{icon_type}.png")
        
        self.y = os.environ.get('METER_Y')
        self.width = os.environ.get('METER_WIDTH')
        self.height = os.environ.get('METER_HEIGHT')
        return PlaceImage(self.image_path, self.x, self.y, self.width, self.height).get_tuple()
    def get_text_tuple(self):
        text = f"{self.score}%"
        
        # Try to load custom font, fall back to default if needed
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "RozhaOne-Regular.ttf")
        font = eval(DEFAULT_FONT) # Fallback to default font if custom font fails
        try:
            font = cv2.freetype.createFreeType2()
            font.loadFontData(font_path, 0)
        except:
            print(f"Warning: Could not load custom font from {font_path}")
            
        # Position score text below corresponding meter
        # Center text below the meter image
        # Get text size to center it properly
        text_size = cv2.getTextSize(str(text), font, float(os.environ.get('SCORE_SCALE')), int(os.environ.get('SCORE_THICKNESS')))[0]
        x_pos = (int(self.x) + int(self.width) // 2) - (text_size[0] // 2)
        y_pos = int(os.environ.get('SCORE_Y'))
        return PlaceText(str(text), x_pos, y_pos, 
                        scale=float(os.environ.get('SCORE_SCALE')), 
                        color=TEXT_COLOR_WHITE, 
                        font=font, 
                        thickness=int(os.environ.get('SCORE_THICKNESS'))).get_tuple()

