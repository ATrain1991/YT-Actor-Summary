import os
import cv2
from dotenv import load_dotenv
import numpy as np
from VideoManager import VideoManager, CreateInfographicVideo
import Actor
import ImageManager
import Wikipedia_scraper

def ensure_directories(actor_name):
    # Create all necessary directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        os.path.join(base_dir, 'fonts'),
        os.path.join(base_dir, 'icons'),
        os.path.join(base_dir, 'headshots')#,
        # os.path.join(base_dir, actor_name)
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

def main(actor_name):    
    ensure_directories(actor_name)
    
    # Load environment variables
    load_dotenv(override=True)
    
    # Generate actor object
    actor = Actor.generate_actor_object(actor_name)
    if actor is None:
        print("Failed to generate actor object. Exiting.")
        return
        
    # Get output paths
    image_output_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "infographic images",
        f"{actor.name} infographic.jpg"
    ))
    
    video_output_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "infographic videos",
        f"{actor.name} infographic.mp4"
    ))
    
    # Process movies
    movies = actor.get_summary_movies()
    if not movies:
        print("No movies found for summary")
        return
        
    print(f"Processing {len(movies)} movies")
    
    # Generate and save results
    try:
        result = ImageManager.stitch_film_strips(
            [movie.get_movie_image() for movie in movies],
            actor.get_actor_summary_image()
        )
        
        cv2.imwrite(image_output_path, result)
        print(f"Saved image to {image_output_path}")
        # return image_output_path, video_output_path

        
    except Exception as e:
        print(f"Error generating output: {str(e)}")

if __name__ == "__main__":
    actor_name = "Meryl Streep"
    main(actor_name)    
    image_path = os.path.join("infographic images", f"{actor_name} infographic.jpg")
    
    CreateInfographicVideo(image_path)
    # VideoManager.create_scrolling_video(image_output_path, video_output_path)
    # if os.path.exists(video_output_path):
    #     print(f"Saved video to {video_output_path}")
    # else:
    #     print(f"Failed to save video to {video_output_path}")
