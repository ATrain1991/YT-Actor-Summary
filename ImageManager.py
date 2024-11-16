import cv2
import numpy as np
import os

import requests



class PlaceElement:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class PlaceText(PlaceElement):
    def __init__(self, text: str, x: int = 0, y: int = 0, scale: float = 1.0, 
                 color: tuple = (255, 255, 255), font: str = "RozhaOne-Regular.ttf", 
                 thickness: int = 2):
        super().__init__(x, y)
        self.text = text
        self.scale = scale
        self.color = color
        self.font = font
        self.thickness = thickness
    def get_tuple(self):
        # Returns (image_path, x_pos, y_pos, width, height) for movie poster
        return (self.text, self.x, self.y, self.scale, self.color, self.font, self.thickness)
class PlaceImage(PlaceElement):
    def __init__(self, image_path: str, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        super().__init__(x, y)
        self.image_path = image_path
        self.width = width 
        self.height = height
    
    def get_tuple(self):
        return (self.image_path, self.x, self.y, self.width, self.height)
class PlaceImageFromURL(PlaceImage):
    def __init__(self, image_url: str, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        super().__init__(image_url, x, y, width, height)

def stitch_film_strips(movie_images: list[np.ndarray],actor_image: list[np.ndarray] = None ):
    """
    Stitches together multiple film strip images vertically with a small overlap
    
    Args:
        movie_images: List of film strip images to stitch together
        
    Returns:
        Combined image with all strips stitched vertically
    """
    if not movie_images:
        return None
    total_images = len(movie_images)
    if actor_image is not None:
        movie_images.insert(0, actor_image)
        total_images += 2
    # Get dimensions from first image
    height, width = movie_images[0].shape[:2]
    
    # Calculate total height needed
    total_height = height * total_images
    
    # Create output image
    result = np.zeros((total_height, width, 3), dtype=np.uint8)
    
    # Place images vertically without overlap
    y_pos = 0
    for img in movie_images:
        result[y_pos:y_pos + height] = img
        y_pos += height
    # Add actor image to end if it exists
    if actor_image is not None:
        result[y_pos:y_pos + height] = actor_image
    return result

def overlay_images_and_text(background, image_tuples, text_tuples):
        """
        Overlays images and text on background
        
        Args:
            background: Background image array
            images: List of 3 (image_path, x, y, width, height) tuples
            texts: List of 4 (text, x, y, font_scale, color) tuples
            
        Returns:
            Final composited image
        """
        # Load background if it's a tuple (path, x, y, width, height)
        if background is None:
            print("No background provided, creating new background")
            return None
        
        # Overlay images
        for image_path, x, y, width, height in image_tuples:
            # Convert and validate dimensions

            try:
                width = int(width)
                height = int(height)
                
                # Ensure minimum dimensions
                if width <= 0 or height <= 0:
                    print(f"Invalid dimensions for image {image_path}: {width}x{height}")
                    continue
                
                if os.path.exists(str(image_path)):
                    img = cv2.imread(str(image_path))
                else:
                    # Download image from URL and convert to cv2 format
                    response = requests.get(str(image_path))
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                # Debug print
                print(f"Resizing image to {width}x{height}")
                
                # Resize with validated dimensions
                img = cv2.resize(img, (width, height))
                
                # Convert coordinates and dimensions to integers
                x = int(x)
                y = int(y)
                width = int(width)
                height = int(height)
                
                # Convert coordinates for numpy slicing
                y1 = max(0, y)
                y2 = min(background.shape[0], y + height)
                x1 = max(0, x)
                x2 = min(background.shape[1], x + width)
                
                if y2 > y1 and x2 > x1:
                    # Crop image to match the actual region being modified
                    img = img[:(y2-y1), :(x2-x1)]
                    
                    # Create mask matching the cropped image dimensions
                    mask = np.ones(img.shape[:2], dtype=np.float32)
                    mask = cv2.GaussianBlur(mask, (7,7), 0)
                    
                    for c in range(3):
                        background[y1:y2, x1:x2, c] = (
                            background[y1:y2, x1:x2, c] * (1 - mask) +
                            img[:,:,c] * mask
                        )
            
            except Exception as e:
                print(f"Error processing image {image_path}: {str(e)}")
                continue
        
        # Add text
        for text, x, y, scale, color, font, thickness in text_tuples:
            if text is None:
                continue
                
            # Convert coordinates and parameters to appropriate types
            x = int(x)
            y = int(y) 
            scale = float(scale)
            thickness = int(thickness)
            
            # Convert text to string and handle None values
            text_str = str(text) if text is not None else ""
            
            cv2.putText(background, text_str, (x, y), load_font(font), scale, color, thickness, cv2.LINE_AA)
    
        return background

def load_font(font_path):
    # Guard against non-string input
    if not isinstance(font_path, (str, bytes, os.PathLike)):
        print(f"Invalid font_path type: {type(font_path)}")
        return cv2.FONT_HERSHEY_DUPLEX
        
    try:
        font_path = os.path.normpath(str(font_path))
        if os.path.exists(font_path):
            return cv2.FONT_HERSHEY_DUPLEX
        else:
            print(f"Font file not found at: {font_path}")
            return cv2.FONT_HERSHEY_DUPLEX
    except Exception as e:
        print(f"Error loading font: {str(e)}")
        return cv2.FONT_HERSHEY_DUPLEX