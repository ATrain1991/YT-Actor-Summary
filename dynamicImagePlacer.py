import os
import cv2
import numpy as np

from ImageManager import overlay_images_and_text

def calculate_image_placements(background_image):
    """
    Calculates optimal placement locations and sizes for overlaid images based on background dimensions
    
    Args:
        background_image: numpy array of background image
        
    Returns:
        Dictionary containing calculated positions and dimensions:
        {
            'poster': (x, y, width, height),
            'tomato_meter': (x, y, width, height), 
            'popcorn_meter': (x, y, width, height)
        }
    """
    # Get background dimensions
    bg_height, bg_width = background_image.shape[:2]
    
    # Calculate poster dimensions (centered, taking up ~60% of height)
    poster_height = int(bg_height * 0.6)
    poster_width = int(poster_height * 0.56)  # Maintain movie poster aspect ratio
    poster_x = (bg_width - poster_width) // 2
    poster_y = int(bg_height * 0.1)  # Start 10% from top
    
    # Calculate meter dimensions (~15% of background width)
    meter_size = int(bg_width * 0.15)
    meter_y = poster_y + poster_height + int(bg_height * 0.05)  # Below poster
    
    # Tomato meter on left
    tomato_x = int(bg_width * 0.25) - (meter_size // 2)
    
    # Popcorn meter on right
    popcorn_x = int(bg_width * 0.75) - (meter_size // 2)
    
    placements = {
        'poster': (poster_x, poster_y, poster_width, poster_height),
        'tomato_meter': (tomato_x, meter_y, meter_size, meter_size),
        'popcorn_meter': (popcorn_x, meter_y, meter_size, meter_size)
    }
    
    return placements

def calculate_text_placements(background_image, image_placements):
    """
    Calculates optimal text placement locations based on image placements
    
    Args:
        background_image: numpy array of background image
        image_placements: dictionary of image placement coordinates
        
    Returns:
        Dictionary containing calculated text positions:
        {
            'year': (x, y, scale),
            'box_office': (x, y, scale),
            'tomato_score': (x, y, scale),
            'popcorn_score': (x, y, scale)
        }
    """
    bg_height, bg_width = background_image.shape[:2]
    
    # Calculate text scales based on background size
    base_scale = min(bg_width, bg_height) / 1000
    
    # Year text (top left)
    year_x = int(bg_width * 0.1)
    year_y = int(bg_height * 0.05)
    year_scale = base_scale * 2
    
    # Box office text (top right)
    box_office_x = int(bg_width * 0.9)
    box_office_y = year_y
    box_office_scale = base_scale * 1.5
    
    # Score text positions (centered below respective meters)
    tomato_meter = image_placements['tomato_meter']
    popcorn_meter = image_placements['popcorn_meter']
    
    score_y = tomato_meter[1] + tomato_meter[3] + int(bg_height * 0.02)
    score_scale = base_scale * 3
    
    text_placements = {
        'year': (year_x, year_y, year_scale),
        'box_office': (box_office_x, box_office_y, box_office_scale),
        'tomato_score': (tomato_meter[0] + tomato_meter[2]//2, score_y, score_scale),
        'popcorn_score': (popcorn_meter[0] + popcorn_meter[2]//2, score_y, score_scale)
    }
    
    return text_placements
def example_usage():
    """
    Example showing how to use the dynamic image and text placement functions
    """
    # Create sample background image (1920x1080)
    background = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Get optimal image placements
    image_placements = calculate_image_placements(background)
    Tscore= 92
    Pscore= 51
        
        # Build icon filename and position based on type and freshness
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Sample image paths
    poster_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Denzel Washington", "Glory.jpg")
    Tfreshness = "Fresh" if Tscore >=60 else "Rotten"
    Pfreshness = "Fresh" if Pscore >=60 else "Rotten"
    tomato_meter_path = os.path.join(current_dir, "icons", f"{Tfreshness}Tomato.png")
    popcorn_meter_path = os.path.join(current_dir, "icons", f"{Pfreshness}Popcorn.png")
    
    # Create list of image tuples (path, x, y, width, height)
    images_to_place = [
        (poster_path, *image_placements['poster']),
        (tomato_meter_path, *image_placements['tomato_meter']),
        (popcorn_meter_path, *image_placements['popcorn_meter'])
    ]
    
    # Get optimal text placements
    text_placements = calculate_text_placements(background, image_placements)
    
    # Create list of text tuples (text, x, y, scale, color, font, thickness)
    texts_to_place = [
        ("2023", *text_placements['year'], (255,255,255), cv2.FONT_HERSHEY_SIMPLEX, 2),
        ("$500M", *text_placements['box_office'], (255,255,255), cv2.FONT_HERSHEY_SIMPLEX, 2),
        (f'{Tscore}%', *text_placements['tomato_score'], (255,255,255), cv2.FONT_HERSHEY_SIMPLEX, 2),
        (f'{Pscore}%', *text_placements['popcorn_score'], (255,255,255), cv2.FONT_HERSHEY_SIMPLEX, 2)
    ]
    
    # Overlay images and text on background
    final_image = overlay_images_and_text(background, images_to_place, texts_to_place)
    
    return final_image

if __name__ == "__main__":
    result = example_usage()
    cv2.imshow("Dynamic Placement Example", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
