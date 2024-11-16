from datetime import datetime
import os
import time
from unicodedata import numeric

import cv2
from dotenv import load_dotenv
from HelperMethods import get_float_from_box_office
import HelperMethods
from ImageManager import PlaceImage, PlaceText, overlay_images_and_text
from Meter import Meter, MeterType
from Movie import Movie
from RottenTomatoesScraper import scrape_actor_data2, get_actor_birthdate
import Wikipedia_scraper
import omdb_api
from numerize import numerize

class Actor:
    def __init__(self, name, birthdate,oscar_wins,oscar_nominations,headshot_path,movies):
        load_dotenv(override=True)
        self.movies = movies
        self.name = name
        self.birthdate = PlaceText(text=f"({birthdate})",             
                                   x=int(os.environ.get('BIRTHDATE_X', 0)),
                                   y=int(os.environ.get('BIRTHDATE_Y', 0)),
                                   scale=float(os.environ.get('BIRTHDATE_SCALE', 2.4)),
                                   color=eval(os.environ.get('TEXT_COLOR_BLACK')),
                                   font=os.environ.get('FONT_PATH', cv2.FONT_HERSHEY_SIMPLEX),
                                   thickness=int(os.environ.get('BIRTHDATE_THICKNESS', 6)))
        # Calculate age from birthdate
        self.age = PlaceText(text=self.get_age(),
                             x=int(os.environ.get('AGE_X', 0)),
                             y=int(os.environ.get('AGE_Y', 0)),
                             scale=float(os.environ.get('AGE_SCALE', 1)),
                             color=eval(os.environ.get('TEXT_COLOR_BLACK')),
                             font=os.environ.get('FONT_PATH', cv2.FONT_HERSHEY_SIMPLEX),
                             thickness=int(os.environ.get('AGE_THICKNESS', 2)))
        self.box_office = PlaceText(text=self.get_total_box_office(readable=True), 
                            x=int(os.environ.get('BOX_OFFICE_X', 0)),
                            y=int(os.environ.get('BOX_OFFICE_Y', 0)),
                            scale=float(os.environ.get('ACTOR_BOX_OFFICE_SCALE', 1)),
                            color=eval(os.environ.get('TEXT_COLOR_GREEN')),
                            font=os.environ.get('FONT_PATH', cv2.FONT_HERSHEY_SIMPLEX),
                            thickness=int(os.environ.get('ACTOR_BOX_OFFICE_THICKNESS', 2)))
        self.movies = movies 
        self.tomato_meter = Meter(MeterType.TOMATO, self.get_average_tomato_score())
        self.popcorn_meter = Meter(MeterType.POPCORN, self.get_average_popcorn_score())
        self.oscar_wins = oscar_wins
        self.oscar_nominations = oscar_nominations
        self.headshot = PlaceImage(headshot_path,                                
                            x=os.environ.get('POSTER_X'), 
                            y=os.environ.get('POSTER_Y'),
                            width=os.environ.get('POSTER_WIDTH'), 
                            height=os.environ.get('POSTER_HEIGHT'))
        
    def get_average_tomato_score(self):
        valid_scores = [movie.tomato_meter.score for movie in self.movies if isinstance(movie.tomato_meter.score, (int, float))]
        return round(sum(valid_scores) / len(valid_scores),1) if valid_scores else 0
    def get_average_popcorn_score(self):
        valid_scores = [movie.popcorn_meter.score for movie in self.movies if isinstance(movie.popcorn_meter.score, (int, float))]
        return round(sum(valid_scores) / len(valid_scores),1) if valid_scores else 0
    def get_age(self):
        from datetime import datetime
        birthdate_obj = datetime.strptime(self.birthdate.text.replace("(", "").replace(")", ""), "%Y-%m-%d")
        today = datetime.now()
        return str(today.year - birthdate_obj.year - ((today.month, today.day) < (birthdate_obj.month, birthdate_obj.day)))
    def get_age_tuple(self):
        return self.age.get_tuple()
    def get_headshot_tuple(self):
        return self.headshot.get_tuple()
    def get_box_office_tuple(self):
        return self.box_office.get_tuple()
    def get_birthdate_tuple(self):
        return self.birthdate.get_tuple()
    def get_tomato_meter_Image_tuple(self):
        return self.tomato_meter.get_image_tuple()
    def get_popcorn_meter_Image_tuple(self):
        return self.popcorn_meter.get_image_tuple()
    def get_tomato_meter_Text_tuple(self):
        return self.tomato_meter.get_text_tuple()
    def get_popcorn_meter_Text_tuple(self):
        return self.popcorn_meter.get_text_tuple()
    def get_highest_tomatometer_movie(self,tempMovies=None):
        if tempMovies is not None:
            return max(tempMovies, key=lambda x: x.tomato_meter.score)
        return max(self.movies, key=lambda x: x.tomato_meter.score)
    def get_highest_popcornmeter_movie(self,tempMovies=None):
        if tempMovies is not None:
            return max(tempMovies, key=lambda x: x.popcorn_meter.score)
        return max(self.movies, key=lambda x: x.popcorn_meter.score)
    def parse_box_office(self, value):
        """Parse box office value with better error handling"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Remove currency symbols, commas, and spaces
                cleaned = value.replace('$', '').replace(',', '').replace(' ', '')
                if cleaned and cleaned.replace('.', '').isdigit():  # Check if it's a valid number
                    return float(cleaned)
            print(f"Invalid box office value: {value}")
            return 0.0
        except Exception as e:
            print(f"Error parsing box office value '{value}': {str(e)}")
            return 0.0
    def get_highest_grossing_movie(self, tempMovies=None):
        movies = tempMovies if tempMovies is not None else self.movies
        try:
            # Filter movies with valid box office numbers
            valid_movies = [movie for movie in movies 
                           if HelperMethods.get_float_from_box_office(movie.box_office.text) > 0]
            if not valid_movies:
                print("No movies found with valid box office numbers")
                return None
            return max(valid_movies, key=lambda x: HelperMethods.get_float_from_box_office(x.box_office.text))
        except Exception as e:
            print(f"Error finding highest grossing movie: {str(e)}")
            return None
    def get_lowest_tomatometer_movie(self,tempMovies=None):
        if tempMovies is not None:
            return min(tempMovies, key=lambda x: x.tomato_meter.score)
        return min(self.movies, key=lambda x: x.tomato_meter.score)
    def get_lowest_popcornmeter_movie(self,tempMovies=None):
        if tempMovies is not None:
            return min(tempMovies, key=lambda x: x.popcorn_meter.score)
        return min(self.movies, key=lambda x: x.popcorn_meter.score)
    def get_total_box_office(self,readable=False):
        value = sum(HelperMethods.get_float_from_box_office(movie.box_office.text) for movie in self.movies)
        if readable:
            return f"${numerize.numerize(value)}"
        return value
    def get_average_tomatometer(self,tempMovies=None):
        if tempMovies is not None:
            return round(sum(movie.tomato_meter.score for movie in tempMovies) / len(tempMovies))
        return round(sum(movie.tomato_meter.score for movie in self.movies) / len(self.movies))
    def get_average_popcornmeter(self,tempMovies=None):
        if tempMovies is not None:
            return round(sum(movie.popcorn_meter.score for movie in tempMovies) / len(tempMovies))
        return round(sum(movie.popcorn_meter.score for movie in self.movies) / len(self.movies))
    def get_starring_movies(self):

        filtered_movies = [
            movie for movie in self.movies
            if (data := omdb_api.get_movie_data(movie.title)) 
            and data['Response'] != 'False'
            and self.name.lower() in [actor.lower() for actor in data['Actors'].split(', ')]
        ]
        return filtered_movies
    def filter_movies_for_summary(self):
        tempMovies = self.get_starring_movies()
        current_year = datetime.now().year
        # Filter movies to only include those where the actor played a character role
        tempMovies = [movie for movie in tempMovies if 'character' in movie.role.lower()]
        # Filter out movies with invalid or missing box office data
        tempMovies = [movie for movie in tempMovies if movie.box_office.text not in ["N/A", "", "-1", "-"]]
        # Filter out future movies that haven't been released yet
        tempMovies = [movie for movie in tempMovies if int(movie.year.text) <= current_year]
        return tempMovies
    def get_summary_movies(self, remove_not_starring_roles=True):
        if remove_not_starring_roles:
            tempMovies = self.filter_movies_for_summary()
        else:
            tempMovies = self.movies
        
        # Get all summary movies, filtering out None values
        summary_movies = []
        for getter in [
            lambda: self.get_highest_tomatometer_movie(tempMovies),
            lambda: self.get_highest_popcornmeter_movie(tempMovies),
            lambda: self.get_highest_grossing_movie(tempMovies),
            lambda: self.get_lowest_tomatometer_movie(tempMovies),
            lambda: self.get_lowest_popcornmeter_movie(tempMovies)
        ]:
            try:
                movie = getter()
                if movie is not None:
                    summary_movies.append(movie)
            except Exception as e:
                print(f"Error getting summary movie: {str(e)}")
                continue
            
        return summary_movies
    def get_actor_summary_image(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            background_image = os.path.join(current_dir, "icons", "film_strip.png")
            # Load background image
            background = cv2.imread(background_image)
            if background is None:
                raise ValueError(f"Could not load background image from {background_image}")
                
            # Get image and text tuples from movie
            images = [
                self.get_headshot_tuple(),  # Movie poster image
                self.get_tomato_meter_Image_tuple(),  # Tomato meter icon
                self.get_popcorn_meter_Image_tuple()   # Popcorn meter icon
            ]
            
            texts = [
                self.get_birthdate_tuple(),         # Year text
                self.get_box_office_tuple(),   # Box office text
                self.get_age_tuple(),          # Age text
                self.get_tomato_meter_Text_tuple(),  # Tomato score text
                self.get_popcorn_meter_Text_tuple()   # Popcorn score text
            ]
            
        # Overlay movie content onto background
            result = overlay_images_and_text(background, images, texts)
        
            return result


def check_for_odd_names(actor_name):
    if "dicaprio" in actor_name.lower():
        return "Leonardo Di Caprio"
    return actor_name

def get_headshot_path(actor_name):
    """Get the path to the actor's headshot image"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    headshot_path = os.path.join(current_dir, "headshots", f"{actor_name.lower()}.jpg")
    
    # Return a default image if the headshot doesn't exist
    if not os.path.exists(headshot_path):
        return os.path.join(current_dir, "icons", "default_headshot.jpg")
    return headshot_path

def generate_actor_object(actor_name):
    try:
        print(f"Starting to generate actor object for {actor_name}")
        awards = Wikipedia_scraper.get_actor_awards("Brad Pitt")
        oscar_nominations = awards['nominations']
        oscar_wins = awards['wins']
        movies = scrape_actor_data2(actor_name)
        if not movies:
            print(f"No movies found for {actor_name}")
            return None
            
        print(f"Found {len(movies)} movies for {actor_name}")
        birthdate = get_actor_birthdate(actor_name)
        
        # Create the actor object
        actor = Actor(
            actor_name,
            str(birthdate),
            oscar_wins,
            oscar_nominations,
            get_headshot_path(actor_name),
            movies
        )
        
        return actor
        
    except Exception as e:
        print(f"Failed to generate actor object for {actor_name}: {str(e)}")
        return None

def parse_birthdate(date_str):
    if isinstance(date_str, datetime.date):
        return date_str.strftime('%B %d, %Y')
    try:
        return datetime.datetime.strptime(str(date_str), '%Y-%m-%d').strftime('%B %d, %Y')
    except Exception as e:
        print(f"Error parsing birthdate: {str(e)}")
        return ""