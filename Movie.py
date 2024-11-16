import os
import cv2
from dotenv import load_dotenv
from ImageManager import PlaceImage, PlaceText, overlay_images_and_text
from Meter import Meter, MeterType
import omdb_api


class Movie:
    def __init__(self, name, year, box_office, poster_path, tomatometer:float, popcornmeter:float, credit:str):
        load_dotenv(override=True)
        self.title = name
        self.role = credit
        self.year = PlaceText(
            text=year,
            x=int(os.environ.get('YEAR_X', 0)),
            y=int(os.environ.get('YEAR_Y', 0)),
            scale=float(os.environ.get('YEAR_SCALE', 2.4)),
            color=eval(os.environ.get('TEXT_COLOR_BLACK')),
            font=os.environ.get('FONT_PATH', cv2.FONT_HERSHEY_SIMPLEX),
            thickness=int(os.environ.get('YEAR_THICKNESS', 6))
        )
        self.box_office = PlaceText(
            text=box_office,
            x=int(os.environ.get('BOX_OFFICE_X', 0)),
            y=int(os.environ.get('BOX_OFFICE_Y', 0)),
            scale=float(os.environ.get('BOX_OFFICE_SCALE', 1.0)),
            color=eval(os.environ.get('TEXT_COLOR_GREEN')),
            font=os.environ.get('FONT_PATH', cv2.FONT_HERSHEY_SIMPLEX),
            thickness=int(os.environ.get('BOX_OFFICE_THICKNESS', 2))
        )
        self.poster = PlaceImage(poster_path, 
                               x=os.environ.get('POSTER_X'), 
                               y=os.environ.get('POSTER_Y'),
                               width=os.environ.get('POSTER_WIDTH'), 
                               height=os.environ.get('POSTER_HEIGHT'))
        self.tomato_meter = Meter(MeterType.TOMATO, tomatometer)
        self.popcorn_meter = Meter(MeterType.POPCORN, popcornmeter)
        self.box_office.text = self.convert_box_office_to_readable()
    def get_tomato_meter_Image_tuple(self):
        return self.tomato_meter.get_image_tuple()
    def get_popcorn_meter_Image_tuple(self):
        return self.popcorn_meter.get_image_tuple()
    def get_tomato_meter_Text_tuple(self):
        return self.tomato_meter.get_text_tuple()
    def get_popcorn_meter_Text_tuple(self):
        return self.popcorn_meter.get_text_tuple()
    def convert_box_office_to_readable(self):
        try:
            value = float(str(self.box_office.text).replace('$', '').replace(',', ''))
            if value >= 1_000_000_000:
                return f"${value/1_000_000_000:.1f}B"
            elif value >= 1_000_000:
                return f"${value/1_000_000:.1f}M"
            elif value >= 1_000:
                return f"${value/1_000:.1f}K"
            else:
                return f"${value:.0f}"
        except (ValueError, TypeError):
            return self.box_office.text
    def get_movie_image(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            background_image = os.path.join(current_dir, "icons", "film_strip.png")
            # Load background image
            background = cv2.imread(background_image)
            if background is None:
                raise ValueError(f"Could not load background image from {background_image}")
            self.poster.image_path = omdb_api.get_poster_url_from_omdb(self.title)
         # Get image and text tuples from movie
            images = [
                self.poster.get_tuple(),  # Movie poster image
                self.get_tomato_meter_Image_tuple(),  # Tomato meter icon
                self.get_popcorn_meter_Image_tuple()   # Popcorn meter icon
            ]
            
            texts = [
                self.year.get_tuple(),         # Year text
                self.box_office.get_tuple(),   # Box office text
                self.get_tomato_meter_Text_tuple(),  # Tomato score text
                self.get_popcorn_meter_Text_tuple()   # Popcorn score text
            ]
            
        # Overlay movie content onto background
            result = overlay_images_and_text(background, images, texts)
        
            return result
