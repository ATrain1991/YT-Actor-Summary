import os
import cv2
import numpy as np
# from Meter import Meter, MeterType, Poster, Movie
from VideoManager import VideoManager
from models import Meter, MeterType, Poster, Movie, convert_to_movie_object
from cv_helper_methods import overlay_images_and_text
from single_actor_full import generate_actor_object

def stitch_film_strips(movie_images: list[np.ndarray]):
    """
    Stitches together multiple film strip images vertically with a small overlap
    
    Args:
        movie_images: List of film strip images to stitch together
        
    Returns:
        Combined image with all strips stitched vertically
    """
    if not movie_images:
        return None
        
    # Get dimensions from first image
    height, width = movie_images[0].shape[:2]
    
    # Calculate total height needed
    total_height = height * len(movie_images)
    
    # Create output image
    result = np.zeros((total_height, width, 3), dtype=np.uint8)
    
    # Place images vertically without overlap
    y_pos = 0
    for img in movie_images:
        result[y_pos:y_pos + height] = img
        y_pos += height
        
    return result
def get_image_output_path(actor_name: str):
    actor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), actor_name)
    return os.path.join(actor_dir,  "infographic.jpg")
def get_video_output_path(actor_name: str):
    actor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), actor_name)
    return os.path.join(actor_dir,  "infographic.mp4")
if __name__ == "__main__":
    # simple_usage()
    actor = generate_actor_object("Tom Hardy", 0, 0)
    
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), actor.name)
    movies = [convert_to_movie_object(movie,current_dir) for movie in actor.get_summary_movies()]
    print(len(movies))
    result = stitch_film_strips([movie.get_movie_image() for movie in movies])

    image_output_path = get_image_output_path(actor.name)
    cv2.imwrite(image_output_path, result)
    video_output_path = get_video_output_path(actor.name)
    VideoManager.create_scrolling_video2(image_output_path, video_output_path)
    # Create window with resize flag and set initial size
    cv2.namedWindow('Film Strip Result', cv2.WINDOW_NORMAL)
    # Calculate height to maintain aspect ratio
    aspect_ratio = result.shape[0] / result.shape[1]
    window_width = 800
    window_height = int(window_width * aspect_ratio)
    # Set window size and create trackbars for scrolling
    cv2.resizeWindow('Film Strip Result', window_width, window_height)

    cv2.destroyAllWindows()

