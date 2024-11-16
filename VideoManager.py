from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip,CompositeAudioClip
from pydub import AudioSegment
import cv2
import os
import time
import logging
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
import numpy as np

logger = logging.getLogger(__name__)
DEBUG = False

class VideoManager:
    def __init__(self):
        self.recording = False
        self.video_writer = None
        self.frame_count = 0
        self.capture_timer = None

    @staticmethod
    def create_looping_video(image_path, output_path, duration=15, scroll_mode="slow_and_pause", pause_frames=25, lerp_frames=15):
        """Create a seamlessly looping video
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path for output video
            duration (int): Duration in seconds
            scroll_mode (str): One of "continuous", "lerp_pause", "lerp_only", "full_pause" 
            pause_frames (int): Number of frames to pause for in lerp_pause/full_pause modes
            lerp_frames (int): Number of frames to lerp over in lerp modes
        """
        try:
            # Create a temp directory in our project folder
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create temp files in our temp directory
            temp_video_path = os.path.join(temp_dir, 'temp_video.mp4')
            temp_audio_path = os.path.join(temp_dir, 'temp_audio.mp3')
            
            # Read the input image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return

            # Get image dimensions
            img_height, img_width = image.shape[:2]

            # YouTube Shorts dimensions
            shorts_width = 1080
            shorts_height = 1920

            # Resize image width to match Shorts width while maintaining aspect ratio
            scale = shorts_width / img_width
            new_height = int(img_height * scale)
            image = cv2.resize(image, (shorts_width, new_height))

            # Create extended image with duplicated top/bottom sections
            top_section = image[:shorts_height, :]
            extended_image = np.concatenate([image, top_section])

            # Create temporary video file
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, 60, (shorts_width, shorts_height))

            # Calculate scroll speed (pixels per frame)
            total_frames = duration * 60  # 60 fps
            scroll_distance = extended_image.shape[0] - shorts_height
            scroll_speed = scroll_distance / total_frames

            # Calculate pause positions (center of each poster)
            poster_height = shorts_height
            num_posters = extended_image.shape[0] // poster_height
            pause_positions = [(i * poster_height + poster_height // 2) for i in range(num_posters-1)]

            def get_frame(scroll_pos, extended_image, shorts_height, shorts_width):
                window = extended_image[int(scroll_pos):int(scroll_pos) + shorts_height, 0:shorts_width]
                if window.shape[0] < shorts_height:
                    frame = np.zeros((shorts_height, shorts_width, 3), dtype=np.uint8)
                    frame[0:window.shape[0], 0:shorts_width] = window
                else:
                    frame = window
                return frame

            def lerp(start, end, t):
                return start + (end - start) * t

            # Create scrolling effect based on mode
            current_frame = 0
            scroll_pos = 0
            slow_zone = 50 if scroll_mode in ["lerp_pause", "lerp_only"] else 0

            while current_frame < total_frames:
                current_center = scroll_pos + shorts_height // 2
                
                if scroll_mode != "continuous":
                    closest_pause = min(pause_positions, key=lambda x: abs(x - current_center), default=None)
                    distance_to_pause = abs(current_center - closest_pause) if closest_pause is not None else float('inf')
                    closest_pause_idx = pause_positions.index(closest_pause) if closest_pause in pause_positions else -1

                    if distance_to_pause < slow_zone and closest_pause_idx < len(pause_positions) - 1:
                        if scroll_mode == "full_pause" and distance_to_pause < 5:
                            # Full pause - stay at exact pause position for 12 frames
                            pause_scroll_pos = closest_pause - shorts_height // 2
                            for _ in range(12):
                                frame = get_frame(int(pause_scroll_pos), extended_image, shorts_height, shorts_width)
                                out.write(frame)
                                current_frame += 1
                                if current_frame >= total_frames:
                                    break
                        elif scroll_mode in ["lerp_pause", "lerp_only"]:
                            # Lerp slowdown
                            slowdown = 0.3 + (0.7 * (distance_to_pause / slow_zone))
                            scroll_pos += scroll_speed * slowdown
                            
                            if scroll_mode == "lerp_pause" and distance_to_pause < 5:
                                for _ in range(pause_frames):
                                    frame = get_frame(int(scroll_pos), extended_image, shorts_height, shorts_width)
                                    out.write(frame)
                                    current_frame += 1
                                    if current_frame >= total_frames:
                                        break
                    else:
                        scroll_pos += scroll_speed
                else:
                    # Continuous scroll
                    scroll_pos += scroll_speed

                frame = get_frame(int(scroll_pos), extended_image, shorts_height, shorts_width)
                out.write(frame)
                current_frame += 1

            out.release()

            # Load the video
            video = VideoFileClip(temp_video_path)

            # Load background music and adjust volume
            current_dir = os.path.dirname(os.path.abspath(__file__))
            wav_path = os.path.join(current_dir, "soundclips", "background.wav")
            mp3_path = os.path.join(current_dir, "soundclips", "background.mp3")
            if not os.path.exists(mp3_path):
                AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3")
            bg_music = AudioFileClip(mp3_path)
            bg_music = bg_music.volumex(1)
            
            # Loop bg_music if shorter than video
            if bg_music.duration < video.duration:
                bg_music = bg_music.loop(duration=video.duration)
            else:
                bg_music = bg_music.subclip(0, video.duration)

            # Create commentary audio with mode-dependent delay
            commentary = AudioSegment.silent(duration=int(duration * 1000))  # Duration in ms
            
            # Calculate timing for each section
            section_duration = (duration * 1000) / 6  # 6 sections total, time in ms
            
            # Adjust delay based on scroll mode
            if scroll_mode in ["continuous", "lerp_only"]:
                initial_delay = 500  # 0.5 second delay for faster modes
                clip_delay = -300
            else:
                initial_delay = 1500  # 1.5 second delay for slower/pausing modes
                clip_delay = 100
            # Commentary sound clips mapping
            sound_clips = {
                1: "CriticsFavorite.mp3",
                2: "AudienceFavorite.mp3", 
                3: "MostSuccessful.mp3",
                4: "CriticsLeastFavorite.mp3",
                5: "AudienceLeastFavorite.mp3",
                6: None   # Last section - no sound
            }

            # Add commentary clips at appropriate times with initial delay
            for section in range(1, 6):
                clip_file = sound_clips[section]
                if clip_file:
                    clip_path = os.path.join(current_dir, "soundclips", clip_file)
                    if os.path.exists(clip_path):
                        section_clip = AudioSegment.from_file(clip_path)
                        position = int(initial_delay + (section - 1) * section_duration + clip_delay)  # Only delay the start
                        commentary = commentary.overlay(section_clip, position=position)

            # Export commentary to our temp directory
            commentary.export(temp_audio_path, format="mp3")
            commentary_clip = AudioFileClip(temp_audio_path)
            commentary_clip = commentary_clip.volumex(1.5)
            
            # Combine video with both audio tracks
            final_video = video.set_audio(CompositeVideoClip([
                video.set_audio(bg_music),
                video.set_audio(commentary_clip)
            ]).audio)

            # Write final video
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

            # Cleanup
            try:
                video.close()
                bg_music.close()
                commentary_clip.close()
                os.remove(temp_video_path)
                os.remove(temp_audio_path)
                # Optionally remove temp directory if empty
                if not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"Cleanup error (non-fatal): {e}")
                
        except Exception as e:
            print(f"Error creating looping video: {e}")
            import traceback
            traceback.print_exc()


@staticmethod
def overlay_video_on_image(video_path, image_path, scale_factor=0.5, position=(50, 50)):
    try:
        # Normalize and validate input paths
        video_path = os.path.normpath(video_path)
        image_path = os.path.normpath(image_path)
        
        if not os.path.exists(video_path):
            logger.error(f"Could not find infographic video at: {video_path}")
            return
            
        if not os.path.exists(image_path):
            logger.error(f"Could not find headshot at: {image_path}")
            return
            
        # Create output path
        output_dir = os.path.dirname(video_path)
        base_name = os.path.basename(video_path)
        
        # Create 'overlay_videos' directory if it doesn't exist
        overlay_dir = os.path.join(output_dir, "overlay_videos")
        os.makedirs(overlay_dir, exist_ok=True)
        
        # Construct output path
        output_path = os.path.join(overlay_dir, base_name)
        print(f"Output path: {output_path}")
        
        # Load the video and image
        video = VideoFileClip(video_path)
        background = cv2.imread(image_path)
        
        if background is None:
            logger.error(f"Failed to load background image: {image_path}")
            return
            
        # Convert background to RGB
        background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
        
        # Scale down the video
        new_width = int(video.w * scale_factor)
        new_height = int(video.h * scale_factor)
        video_resized = video.resize((new_width, new_height))
        # Get background dimensions
        bg_height, bg_width = background.shape[:2]
        
        # Calculate center position, accounting for scaled video size
        center_x = (bg_width - new_width) // 2
        center_y = (bg_height - new_height) // 2
        
        # Create a mask to crop top and bottom 200px
        def crop_top_bottom(frame):
            # Create black bars for top and bottom
            frame[:200, :] = 0
            frame[-200:, :] = 0
            return frame
            
        # Apply the cropping mask
        # video_resized = video_resized.fl_image(crop_top_bottom)
        
        # Update position to center
        position = (center_x, center_y)
        # Create shadow effect
        def add_shadow(frame):
            frame = frame.astype(float)
            height = frame.shape[0]
            shadow_height = int(height * 0.15)
            
            # Create a gradient for the roll effect
            roll_height = int(height * 0.1)  # Height of the roll effect at top/bottom
            
            # Top roll gradient (darker to lighter)
            top_roll = np.linspace(0.4, 1.0, roll_height)
            # Bottom roll gradient (lighter to darker) 
            bottom_roll = np.linspace(1.0, 0.4, roll_height)
            
            # Apply darkening gradient to create 3D roll effect
            for i in range(roll_height):
                # Top roll
                frame[i] *= top_roll[i]
                # Add slight horizontal distortion for top
                shift = int(np.sin(i/roll_height * np.pi) * 3)
                if shift > 0:
                    frame[i, shift:] = frame[i, :-shift]
                    frame[i, :shift] = frame[i, shift]
                
                # Bottom roll
                frame[-(i+1)] *= bottom_roll[i]
                # Add slight horizontal distortion for bottom
                shift = int(np.sin(i/roll_height * np.pi) * 3)
                if shift > 0:
                    frame[-(i+1), shift:] = frame[-(i+1), :-shift]
                    frame[-(i+1), :shift] = frame[-(i+1), shift]
            
            return frame.astype(np.uint8)
            
        # Apply shadow effect to video
        video_with_shadow = video_resized.fl_image(add_shadow)
        
        # Create a clip from the background image
        background_clip = ImageClip(background).set_duration(video.duration)
        
        # Position the video overlay
        video_with_shadow = video_with_shadow.set_position(position)
        
        # Composite the video over the background
        final_clip = CompositeVideoClip([background_clip, video_with_shadow])
        
        # Write output
        print(f"Writing video to: {output_path}")
        final_clip.write_videofile(output_path, codec='libx264', fps=30)
        
        # Clean up
        video.close()
        final_clip.close()
        
        print(f"Successfully created overlay video: {output_path}")
        
    except Exception as e:
        logger.error(f"Error overlaying video: {str(e)}")
        import traceback
        traceback.print_exc()

def CreateInfographicVideo(image_path):
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define output directory
    output_dir = os.path.join(base_dir, "infographic videos")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    type = "lerp_pause"
    # Create output filename
    image_filename = os.path.basename(image_path)
    output_filename = f"{os.path.splitext(image_filename)[0]}_{type}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"Processing {image_filename}...")
    VideoManager.create_looping_video(image_path, output_path, scroll_mode=type)
    print(f"Created video: {output_filename}")
def Loop_all_infographic_images():
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output directories
    input_dir = os.path.join(base_dir, "infographic images")
    output_dir = os.path.join(base_dir, "infographic videos")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all image files from input directory
    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

    # Define scroll modes to cycle through
    scroll_modes = ["continuous", "lerp_pause", "lerp_only"]
    
    for i, image_file in enumerate(image_files):
        input_path = os.path.join(input_dir, image_file)
        
        # Get scroll mode for this image
        scroll_mode = scroll_modes[i % len(scroll_modes)]
        
        # Create output filename including scroll mode
        output_filename = f"{os.path.splitext(image_file)[0]}_{scroll_mode}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Processing {image_file} with {scroll_mode} mode...")
        VideoManager.create_looping_video(input_path, output_path, scroll_mode=scroll_mode)
        print(f"Created video: {output_filename}")

if __name__ == "__main__":
    Loop_all_infographic_images()
