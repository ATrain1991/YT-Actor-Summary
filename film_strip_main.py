import os
from venv import logger
from PyQt6.QtWidgets import QApplication, QWidget
import sys
from PyQt6.QtCore import QTimer
from VideoManager import DEBUG
from film_strip_generator import FilmStripWidget
from Film_Strip import FilmStrip, Ui_Form
from models import noDB_actor
from single_actor_full import generate_actor_object
from video_manager import VideoManager
from pydub import AudioSegment
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6 import QtWidgets

ICON_DIR = "icons"
fresh_T_meter_icon = os.path.join(ICON_DIR, "FreshTomato.png")
fresh_P_meter_icon = os.path.join(ICON_DIR, "FreshPopcorn.png")
rotten_T_meter_icon = os.path.join(ICON_DIR, "RottenTomato.png") 
rotten_P_meter_icon = os.path.join(ICON_DIR, "RottenPopcorn.png")
box_office_icon = os.path.join(ICON_DIR, "box_office.png")

# Audio paths
current_dir = os.path.dirname(os.path.abspath(__file__))
soundclips_dir = os.path.join(current_dir, "soundclips")
ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
ffprobe_path = os.path.join(current_dir, "ffprobe.exe")

# Configure audio settings
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path 
AudioSegment.ffprobe = ffprobe_path

# Soundclip paths
CLIPS_DIR = soundclips_dir
best_critic_movie_clip = os.path.join(CLIPS_DIR, "CriticsFavorite.wav")
best_audience_movie_clip = os.path.join(CLIPS_DIR, "AudienceFavorite.wav")
highest_grossing_movie_clip = os.path.join(CLIPS_DIR, "MostSuccessful.wav")
worst_tomatometer_movie_clip = os.path.join(CLIPS_DIR, "CriticsLeastFavorite.wav")
worst_popcornmeter_movie_clip = os.path.join(CLIPS_DIR, "AudienceLeastFavorite.wav")

def get_sub_images(movie):
    """Get sub-images and scores for a movie poster"""
    try:
        box_office = movie.NumerizeBoxOffice()
        return [
            (fresh_T_meter_icon if float(movie.tomatometer) > 60.0 else rotten_T_meter_icon, f"{movie.tomatometer}%", 60),
            (fresh_P_meter_icon if float(movie.popcornmeter) > 60.0 else rotten_P_meter_icon, f"{movie.popcornmeter}%", 60),
            (box_office_icon, str(box_office), 45)
        ]
    except Exception as e:
        if DEBUG:
            logger.error(f"Error in get_sub_images: {e}")
        return []

def get_actor_sub_images(actor:noDB_actor):
    """Get sub-images and scores for actor summary poster"""
    try:
        box_office = actor.NumerizeTotalBoxOffice()
        avg_tmeter = actor.get_average_tomatometer()
        avg_pmeter = actor.get_average_popcornmeter()
        
        return [
            (fresh_T_meter_icon if avg_tmeter > 60.0 else rotten_T_meter_icon, f"{avg_tmeter}%", 60),
            (fresh_P_meter_icon if avg_pmeter > 60.0 else rotten_P_meter_icon, f"{avg_pmeter}%", 60),
            (box_office_icon, box_office, 45)
        ]
    except Exception as e:
        if DEBUG:
            logger.error(f"Error in get_actor_sub_images: {e}")
        return []

def create_test_film_strips():
    test_strips = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Debug prints
    print(f"Current directory: {current_dir}")
    film_strip_path = os.path.join(current_dir, "icons", "film_strip.png")
    print(f"Film strip path: {film_strip_path}")
    print(f"Film strip exists: {os.path.exists(film_strip_path)}")
    
    # Test loading the image directly
    test_pixmap = QPixmap(film_strip_path)
    if test_pixmap.isNull():
        print("Failed to load film strip image directly!")
    else:
        print(f"Successfully loaded film strip: {test_pixmap.width()}x{test_pixmap.height()}")
    
    for i in range(6):
        strip = FilmStrip(
            poster_path=os.path.join(current_dir, "Will Smith", "Wild_Wild_West.jpg"),
            tomato_icon_path=os.path.join(current_dir, "icons", "FreshTomato.png"),
            popcorn_icon_path=os.path.join(current_dir, "icons", "FreshPopcorn(background).png"),
            tomato_score="95",
            popcorn_score="90",
            year="2024",
            box_office="$152M"
        )
        
        # Test if the Film label exists and has a pixmap
        if hasattr(strip.ui, 'Film'):
            print(f"Film label exists for strip {i}")
            if strip.ui.Film.pixmap():
                print(f"Film label has pixmap: {strip.ui.Film.pixmap().width()}x{strip.ui.Film.pixmap().height()}")
            else:
                print("Film label has no pixmap!")
        else:
            print("No Film label found!")
        
        strip.setMinimumSize(1080, 1920)
        test_strips.append(strip)
        print(f"Test strip {i+1} created successfully")
    
    return test_strips

def create_actor_posters(actor:noDB_actor):
    """Create poster components for an actor's movies"""
    best_critic_movie = actor.get_critics_best_movie("tomatometer")
    best_audience_movie = actor.get_audience_best_movie("popcornmeter") 
    highest_grossing_movie = actor.get_highest_grossing_movie()
    worst_tomatometer_movie = actor.get_lowest_tomatometer_movie()
    worst_popcornmeter_movie = actor.get_lowest_popcornmeter_movie()

    poster_movies = [
        (best_critic_movie, best_critic_movie_clip),
        (highest_grossing_movie, highest_grossing_movie_clip),
        (best_audience_movie, best_audience_movie_clip),
        (worst_tomatometer_movie, worst_tomatometer_movie_clip),
        (worst_popcornmeter_movie, worst_popcornmeter_movie_clip)
    ]
    
    film_strip_components = []
    for movie, soundbite in poster_movies:
        try:
            main_img = os.path.join(actor.name, f"{movie.title.replace(' ', '_').replace('/', '_').replace('?', '').replace(':', '')}.jpg")
            # strip = FilmStrip.UiForm()
            # Create FilmStrip instance without showing it
            strip = FilmStrip(
                poster_path=main_img,
                tomato_score=movie.tomatometer,
                popcorn_score=movie.popcornmeter,
                year=movie.year,
                box_office=movie.NumerizeBoxOffice()
            )
            film_strip_components.append(strip)
            
        except Exception as e:
            if DEBUG:
                print(f"Error creating poster for {movie.title}: {e}")
            continue
            
    return film_strip_components


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create film strip components
    film_strip_components = create_test_film_strips()
    print(f"Created {len(film_strip_components)} components")
    
    # Create the film strip widget
    film_strip = FilmStripWidget(width=1080, height=1920)  # Match the height from FilmStrip class
    film_strip.components = film_strip_components  # Store reference to prevent garbage collection
    
    # Update the frames with our components
    film_strip.update_frames(film_strip_components)
    print("Updated frames")
    
    film_strip.setMinimumSize(400, 400)
    film_strip.setWindowFlags(film_strip.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
    film_strip.setStyleSheet("background-color: black;")
    film_strip.resize(1080, min(1920, QApplication.primaryScreen().availableGeometry().height()))
    
    print("Showing window...")
    film_strip.show()
    print("Window shown")
    
    sys.exit(app.exec())
