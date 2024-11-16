from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from PIL import Image
import os
import json
from pathlib import Path
import time

class ThumbnailProcessor:
    def __init__(self):
        self.target_width = 1280
        self.target_height = 720
        self.max_file_size = 2 * 1024 * 1024  # 2MB in bytes
        
    def resize_image(self, image, upscale=False):
        """Resize image to target resolution, maintaining aspect ratio"""
        # Calculate aspect ratio
        aspect_ratio = self.target_width / self.target_height
        img_aspect_ratio = image.width / image.height
        
        # Calculate new dimensions
        if img_aspect_ratio > aspect_ratio:
            new_width = self.target_width
            new_height = int(new_width / img_aspect_ratio)
        else:
            new_height = self.target_height
            new_width = int(new_height * img_aspect_ratio)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with target dimensions and paste resized image
        final = Image.new('RGB', (self.target_width, self.target_height), (0, 0, 0))
        x_offset = (self.target_width - new_width) // 2
        y_offset = (self.target_height - new_height) // 2
        final.paste(resized, (x_offset, y_offset))
        
        return final
    
    def optimize_file_size(self, image, max_quality=95):
        """Optimize image file size while maintaining quality"""
        quality = max_quality
        while quality > 5:
            # Save image to bytes buffer
            from io import BytesIO
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=quality)
            size = buffer.tell()
            
            if size <= self.max_file_size:
                return buffer.getvalue()
            
            quality -= 5
        
        raise ValueError("Unable to optimize image to under 2MB while maintaining acceptable quality")
    
    def process_thumbnail(self, image_path, output_path=None, upscale=True):
        """Process thumbnail to meet YouTube requirements"""
        try:
            # Open and convert to RGB
            image = Image.open(image_path).convert('RGB')
            
            # Resize image
            processed = self.resize_image(image, upscale=upscale)
            
            # Optimize file size
            image_data = self.optimize_file_size(processed)
            
            # Save processed image
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return output_path
            else:
                output_path = f"{os.path.splitext(image_path)[0]}_processed.jpg"
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return output_path
                
        except Exception as e:
            print(f"Error processing thumbnail: {str(e)}")
            return None

class YoutubeShortsUploader:
    def __init__(self, client_secrets_file):
        self.client_secrets_file = client_secrets_file
        self.credentials = None
        self.youtube = None
        self.thumbnail_processor = ThumbnailProcessor()
        
    def authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0"""
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
                  'https://www.googleapis.com/auth/youtube.force-ssl']
        
        if os.path.exists('token.json'):
            self.credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.credentials or not self.credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
            self.credentials = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.credentials.to_json())
        
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
    
    def set_thumbnail(self, video_id, thumbnail_path):
        """Set a custom thumbnail for a video"""
        if not os.path.exists(thumbnail_path):
            print(f"Thumbnail file not found: {thumbnail_path}")
            return False
            
        try:
            # Process thumbnail
            processed_thumbnail = self.thumbnail_processor.process_thumbnail(
                thumbnail_path,
                output_path=f"{os.path.splitext(thumbnail_path)[0]}_youtube.jpg"
            )
            
            if not processed_thumbnail:
                return False
            
            # Upload processed thumbnail
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(
                    processed_thumbnail,
                    mimetype='image/jpeg',
                    resumable=True
                )
            )
            response = request.execute()
            print(f"Thumbnail set successfully for video {video_id}")
            
            # Clean up processed thumbnail
            os.remove(processed_thumbnail)
            return True
            
        except Exception as e:
            print(f"Error setting thumbnail: {str(e)}")
            return False
    
    # ... [rest of the YoutubeShortsUploader class remains the same] ...

def main():
    # Initialize uploader
    uploader = YoutubeShortsUploader('client_secrets.json')
    uploader.authenticate()
    
    # Example metadata file structure:
    # {
    #     "video1.mp4": {
    #         "title": "My Cool Short",
    #         "description": "Check out this awesome content!",
    #         "tags": ["funny", "viral", "shorts"],
    #         "thumbnail": "thumbnails/video1_thumb.jpg"
    #     }
    # }
    
    # Example of processing a single thumbnail
    # processor = ThumbnailProcessor()
    # processed_path = processor.process_thumbnail(
    #     "original_thumbnail.jpg",
    #     "processed_thumbnail.jpg",
    #     upscale=True
    # )
    
    # Perform bulk upload
    results = uploader.bulk_upload(
        directory='shorts_folder',
        metadata_file='metadata.json'
    )
    
    print("\nUpload Results:")
    for result in results:
        print(f"Uploaded {result['file']} - Video ID: {result['video_id']}")

if __name__ == '__main__':
    # Get all video files from infographic videos folder
    video_dir = "infographic videos"
    headshots_dir = "headshots"
    metadata = {}
    
    # Prepare metadata for each video
    for video_file in os.listdir(video_dir):
        if video_file.endswith('.mp4'):
            # Extract actor name from video filename (assumes format "Actor Name infographic.mp4")
            actor_name = " ".join(video_file.split()[:2])
            
            # Get matching headshot
            headshot = os.path.join(headshots_dir, f"{actor_name}.jpg")
            if not os.path.exists(headshot):
                print(f"Warning: No headshot found for {actor_name}")
                continue
                
            metadata[video_file] = {
                "title": f"{actor_name}'s Career Highlights #shorts",
                "description": f"{actor_name}'s career overview: starring roles only",
                "tags": [
                    "movies",
                    "film", 
                    "actor",
                    "hollywood",
                    "filmography",
                    "career",
                    "boxoffice",
                    "moviestar",
                    actor_name.lower().replace(" ", ""),
                    "shorts",
                    "viral",
                    "trending"
                ],
                "thumbnail": headshot
            }
    
    # Write metadata to json file
    with open('metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
        
    # Initialize YouTube uploader
    # Create a YouTube uploader instance with our OAuth client secrets file
    uploader = YoutubeShortsUploader('client_secrets_Role_Rush.json')
    
    # Authenticate with YouTube using OAuth flow
    uploader.authenticate()
    
    # Bulk upload all videos in video_dir using metadata from metadata.json
    # This will:
    # 1. Read the metadata.json file we created above
    # 2. For each video in video_dir, upload it with its corresponding metadata
    # 3. Return list of results with video IDs and filenames
    results = uploader.bulk_upload(
        directory=video_dir,  # Directory containing the video files
        metadata_file='metadata.json'  # JSON file with video metadata we created
    )
    
    # Print upload results
    print("\nUpload Results:")
    for result in results:
        print(f"Uploaded {result['file']} - Video ID: {result['video_id']}")
    main()