import os
import numerize
from numerize import numerize as n

def numerize_value(value):
    print(f"Debug - Original value: {value}")
    print(f"Debug - Type of value: {type(value)}")
    
    try:
        if not value or value == "N/A":
            return "N/A"
            
        cleaned_value = str(value).replace("$", "").replace(",", "")
        print(f"Debug - Cleaned value: {cleaned_value}")
        
        try:
            float_value = float(cleaned_value)
            print(f"Debug - Float value: {float_value}")
            result = n(float_value, 1)
            print(f"Debug - Numerized result: {result}")
            return result
        except ValueError as ve:
            print(f"Debug - ValueError: {ve}")
            return value
            
    except Exception as e:
        print(f"Debug - Exception: {e}")
        return str(value)

class noDB_actor:
    def __init__(self, name, age, birthdate, oscar_wins, oscar_nominations, movies):
        self.name = name
        self.age = age
        self.birthdate = birthdate
        self.oscar_wins = oscar_wins
        self.oscar_nominations = oscar_nominations
        self.movies = movies

    def get_highest_tomatometer_movie(self):
        return max(self.movies, key=lambda x: x.tomatometer)
    def get_highest_popcornmeter_movie(self):
        return max(self.movies, key=lambda x: x.popcornmeter)
    def get_highest_grossing_movie(self):
        return max(self.movies, key=lambda x: x.box_office)
    def get_lowest_tomatometer_movie(self):
        return min(self.movies, key=lambda x: x.tomatometer)
    def get_lowest_popcornmeter_movie(self):
        return min(self.movies, key=lambda x: x.popcornmeter)
    def get_total_box_office(self):
        return sum(movie.box_office for movie in self.movies)
    def get_average_tomatometer(self):
        return round(sum(movie.tomatometer for movie in self.movies) / len(self.movies))
    def get_average_popcornmeter(self):
        return round(sum(movie.popcornmeter for movie in self.movies) / len(self.movies))
    def get_main_image_path(self):
        name_ = self.name.replace(" ", "_")
        return os.path.join(self.name, f"{name_}.jpg")
    def NumerizeTotalBoxOffice(self):
        return numerize_value(self.get_total_box_office())
    def get_summary_movies(self):
        return [self.get_highest_tomatometer_movie(), self.get_highest_popcornmeter_movie(),self.get_highest_grossing_movie(),self.get_lowest_tomatometer_movie(),self.get_lowest_popcornmeter_movie()]
class noDB_movie:
    def __init__(self, title, year, tomatometer, popcornmeter, box_office, role):
        self.title = title
        self.year = year
        self.tomatometer = tomatometer
        self.popcornmeter = popcornmeter
        self.box_office = box_office
        self.role = role
    def NumerizeBoxOffice(self):
        return numerize_value(self.box_office)
from enum import Enum
import os
import cv2

from HelperMethods import overlay_images_and_text
from image_models import PlaceImage

class PlaceImage:
    def __init__(self, image_path, x_pos, y_pos, width, height):
        self.image_path = image_path
        self.x = x_pos
        self.y = y_pos
        self.width = width
        self.height = height
    def get_tuple(self):
        # Returns (image_path, x_pos, y_pos, width, height) for movie poster
        return (self.image_path, self.x, self.y, self.width, self.height)
# Define the enum
class MeterType(Enum):
    TOMATO = 1
    POPCORN = 2

# Simplify the Meter class for testing
class Meter:
    def __init__(self, meter_type, score):
        # Print debug info
        print(f"Debug - Received meter_type: {meter_type}")
        print(f"Debug - Type of meter_type: {type(meter_type)}")
        print(f"Debug - MeterType.TOMATO: {MeterType.TOMATO}")
        print(f"Debug - Type of MeterType.TOMATO: {type(MeterType.TOMATO)}")
        print(f"Debug - Are they equal? {meter_type == MeterType.TOMATO}")
        
        self.meter_type = meter_type
        self.score = score
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if meter_type == MeterType.TOMATO:
            self.image_path = os.path.join(current_dir, "icons", "FreshTomato.png")
            self.x = 156  # X position of tomato meter icon
        else:
            self.image_path = os.path.join(current_dir, "icons", "FreshPopcorn.png")
            self.x = 626  # X position of popcorn meter icon
            
        self.y = 1510  # Y position of meter icons
        self.width = 300  # Width of meter icons
        self.height = 300  # Height of meter icons
    
    def get_image_tuple(self):
        # Returns (image_path, x_pos, y_pos, width, height) for meter icon
        return (self.image_path, self.x, self.y, self.width, self.height)
    
    def get_text_tuple(self):
        # Format score text
        text = f"{self.score}%"
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "RozhaOne-Regular.ttf")
        font = cv2.FONT_HERSHEY_SIMPLEX # Fallback to default font if custom font fails
        try:
            font = cv2.freetype.createFreeType2()
            font.loadFontData(font_path, 0)
        except:
            print(f"Warning: Could not load custom font from {font_path}")
        y_pos = 1890
        scale = 4
        thickness = 15
        if self.meter_type == MeterType.TOMATO:
            x_pos = 200
        else:
            x_pos = 670
        return (text, x_pos, y_pos, scale, (255,255,255), font, thickness)



class Movie:
    def __init__(self, title: str, poster_path: str, tmeter: Meter, pmeter: Meter, year: str, box_office: str):
        self.title = title
        self.poster = Poster(poster_path, 156, 144, 770, 1365)   
        self.tmeter = tmeter
        self.pmeter = pmeter
        self.year = year
        self.box_office = box_office
        
    def get_poster_tuple(self):
        # Returns poster image tuple from Poster class
        return self.poster.get_poster_tuple()

    def get_year_tuple(self):
        # Returns (text, x_pos, y_pos, scale, color, font, thickness) for year text
        return (self.year, 170, 100, 2.4, (0,0,0), cv2.FONT_HERSHEY_SIMPLEX, 6)

    def get_box_office_tuple(self):
        # Returns (text, x_pos, y_pos, scale, color, font, thickness) for box office text
        return (f"${self.box_office}", 696, 100, 2.0, (0,0,0), cv2.FONT_HERSHEY_SIMPLEX, 6)
        
    def get_tmeter_tuple(self):
        # Returns tomato meter image tuple from Meter class
        return self.tmeter.get_image_tuple()
        
    def get_pmeter_tuple(self):
        # Returns popcorn meter image tuple from Meter class
        return self.pmeter.get_image_tuple()
        
    def get_tmeter_text_tuple(self):
        # Returns tomato score text tuple from Meter class
        return self.tmeter.get_text_tuple()
        
    def get_pmeter_text_tuple(self):
        # Returns popcorn score text tuple from Meter class
        return self.pmeter.get_text_tuple()
        
    def get_movie_image(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            background_image = os.path.join(current_dir, "icons", "film_strip.png")
            # Load background image
            background = cv2.imread(background_image)
            if background is None:
                raise ValueError(f"Could not load background image from {background_image}")
                
            # Get image and text tuples from movie
            images = [
                self.get_poster_tuple(),  # Movie poster image
                self.get_tmeter_tuple(),  # Tomato meter icon
                self.get_pmeter_tuple()   # Popcorn meter icon
            ]
            
            texts = [
                self.get_year_tuple(),         # Year text
                self.get_box_office_tuple(),   # Box office text
                self.get_tmeter_text_tuple(),  # Tomato score text
                self.get_pmeter_text_tuple()   # Popcorn score text
            ]
            
        # Overlay movie content onto background
            result = overlay_images_and_text(background, images, texts)
        
            return result
def convert_to_movie_object(movie: noDB_movie,current_dir: str):
    Tmeter = Meter(MeterType.TOMATO, movie.tomatometer)
    Pmeter = Meter(MeterType.POPCORN, movie.popcornmeter)
    poster_path = os.path.join(current_dir, f"{movie.title.replace(' ', '_')}.jpg")
    return Movie(movie.title, poster_path, Tmeter, Pmeter, movie.year, movie.box_office)
