import cv2
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import os

def create_rating_timeline_video(ratings, years, output_path, width=1080, height=1920, duration=10):
    """
    Create a video showing ratings plotted on a timeline with animated connecting lines
    
    Args:
        ratings: List of rating values (0-100)
        years: List of years corresponding to ratings
        output_path: Path to save output video
        width: Video width in pixels
        height: Video height in pixels
        duration: Video duration in seconds
    """
    
    # Create blank video frame
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame.fill(255) # White background
    
    # Calculate timeline parameters
    margin = 100
    timeline_y = height - margin # Move timeline lower
    timeline_start = margin
    
    # Calculate total timeline width needed
    year_range = max(years) - min(years)
    pixels_per_year = 300  # More pixels per year for zoomed in view
    total_timeline_width = year_range * pixels_per_year + (2 * margin)
    
    # Calculate x positions for each year and rolling average y positions
    x_positions = []
    y_positions = []
    y_positions_rolling = []
    window_size = 3
    
    for i, (year, rating) in enumerate(zip(years, ratings)):
        # Calculate x position based on year
        x = timeline_start + ((year - min(years)) * pixels_per_year)
        x_positions.append(int(x))
        
        # Calculate y position based on rating (invert since y increases downward)
        y = timeline_y - int((rating/100) * (height - 2*margin))  # Scale rating to use most of frame height
        y_positions.append(y)
        
        # Calculate rolling average y position
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(ratings), i + window_size // 2 + 1)
        window = ratings[start_idx:end_idx]
        rolling_avg = sum(window) / len(window)
        y_rolling = timeline_y - int((rolling_avg/100) * (height - 2*margin))
        y_positions_rolling.append(y_rolling)
    
    # Create frames for animation
    frames = []
    fps = 30
    total_frames = duration * fps
    
    # Starting with timeline partially off screen on the right
    start_offset = -width//4  # Start with 1/4 of timeline visible
    end_offset = total_timeline_width - width + margin
    
    for frame_num in range(total_frames):
        current_frame = frame.copy()
        progress = frame_num / total_frames
        
        # Calculate scroll offset - smooth scroll from right to left
        scroll_offset = int(start_offset + (progress * (end_offset - start_offset)))
        
        # Draw rating scale markers and labels
        for rating_mark in [0, 25, 50, 75, 100]:
            y_pos = timeline_y - int((rating_mark/100) * (height - 2*margin))
            # Draw horizontal guide line
            cv2.line(current_frame, (margin, y_pos), (width-margin, y_pos), (200,200,200), 1)
            # Draw rating label
            cv2.putText(current_frame, str(rating_mark), 
                      (margin-40, y_pos+5),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
        
        # Draw base timeline
        cv2.line(current_frame, 
                 (timeline_start - scroll_offset, timeline_y),
                 (timeline_start + total_timeline_width - scroll_offset, timeline_y), 
                 (0,0,0), 2)
        
        # Draw points and lines
        for i in range(len(x_positions)):
            # Adjust positions for scroll
            current_x = x_positions[i] - scroll_offset
            
            # Only draw if point is in view
            if 0 <= current_x <= width:
                # Draw point (original rating)
                cv2.circle(current_frame, (current_x, y_positions[i]), 5, (0,0,255), -1)
                
                # Draw year and rating
                cv2.putText(current_frame, str(years[i]), 
                          (current_x-20, timeline_y+30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
                cv2.putText(current_frame, str(ratings[i]), 
                          (current_x-20, y_positions[i]-10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
                
                # Draw connecting line using rolling average points
                if i > 0:
                    prev_x = x_positions[i-1] - scroll_offset
                    
                    # Calculate line drawing progress based on rightmost point position
                    line_progress = min(1.0, max(0.0, (width - current_x) / width))
                    
                    if 0 <= prev_x <= width:
                        # Calculate interpolated end point
                        end_x = prev_x + (current_x - prev_x) * line_progress
                        end_y = y_positions_rolling[i-1] + (y_positions_rolling[i] - y_positions_rolling[i-1]) * line_progress
                        
                        cv2.line(current_frame, 
                                (prev_x, y_positions_rolling[i-1]),
                                (int(end_x), int(end_y)), 
                                (255,0,0), 2)
        
        frames.append(current_frame)
    
    # Convert frames to video
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()

def test_timeline_video():
    # Example usage
    ratings = [51, 91,76, 85, 92, 78, 95, 88, 90,46]
    years = [2016,2017,2018, 2019, 2020, 2021, 2022, 2023,2024]
    output_path = "rating_timeline.mp4"
    
    create_rating_timeline_video(ratings, years, output_path)

if __name__ == "__main__":
    ratings = [51, 91,76, 85, 92, 78, 95, 88, 90,46]
    years = [2016,2017,2018, 2019, 2020, 2021, 2022, 2023,2024]
    test_output = "sample_timeline.mp4"
    
    # print("Creating sample timeline video...")
    create_rating_timeline_video(ratings, years, test_output)
    print(f"Timeline video created at: {test_output}")
