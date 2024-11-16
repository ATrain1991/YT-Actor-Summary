from PIL import Image, ImageEnhance, ImageTk
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk

class ImagePreviewWindow:
    def __init__(self, original_img, filename):
        self.proceed = False
        self.original_img = original_img
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title(f"Preview Enhancement - {filename}")
        
        # Initialize enhancement values
        self.sharpness_value = tk.DoubleVar(value=1.5)
        self.contrast_value = tk.DoubleVar(value=1.2)
        self.brightness_value = tk.DoubleVar(value=1.1)
        self.color_value = tk.DoubleVar(value=1.1)
        
        # Calculate display size (maintain aspect ratio, max 800px width)
        max_width = 800
        scale = min(max_width / original_img.width, max_width / original_img.width)
        self.display_width = int(original_img.width * scale)
        self.display_height = int(original_img.height * scale)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create frames for images and controls
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=0, column=0, padx=10)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=1, padx=10, sticky=(tk.N, tk.S))
        
        # Labels for images
        ttk.Label(image_frame, text="Original Image").grid(row=0, column=0, pady=5)
        ttk.Label(image_frame, text="Enhanced Image").grid(row=0, column=1, pady=5)
        
        # Create and display original image
        original_display = original_img.resize((self.display_width, self.display_height))
        self.original_photo = ImageTk.PhotoImage(original_display)
        ttk.Label(image_frame, image=self.original_photo).grid(row=1, column=0, padx=5)
        
        # Create label for enhanced image (will be updated)
        self.enhanced_label = ttk.Label(image_frame)
        self.enhanced_label.grid(row=1, column=1, padx=5)
        
        # Create sliders
        ttk.Label(control_frame, text="Adjustments").grid(row=0, column=0, pady=(0, 10))
        
        # Sharpness slider
        ttk.Label(control_frame, text="Sharpness:").grid(row=1, column=0, sticky=tk.W)
        sharpness_slider = ttk.Scale(control_frame, from_=0.0, to=3.0, length=200,
                                   variable=self.sharpness_value, command=self.update_preview)
        sharpness_slider.grid(row=2, column=0, pady=(0, 10))
        
        # Contrast slider
        ttk.Label(control_frame, text="Contrast:").grid(row=3, column=0, sticky=tk.W)
        contrast_slider = ttk.Scale(control_frame, from_=0.0, to=2.0, length=200,
                                  variable=self.contrast_value, command=self.update_preview)
        contrast_slider.grid(row=4, column=0, pady=(0, 10))
        
        # Brightness slider
        ttk.Label(control_frame, text="Brightness:").grid(row=5, column=0, sticky=tk.W)
        brightness_slider = ttk.Scale(control_frame, from_=0.0, to=2.0, length=200,
                                    variable=self.brightness_value, command=self.update_preview)
        brightness_slider.grid(row=6, column=0, pady=(0, 10))
        
        # Color slider
        ttk.Label(control_frame, text="Color:").grid(row=7, column=0, sticky=tk.W)
        color_slider = ttk.Scale(control_frame, from_=0.0, to=2.0, length=200,
                               variable=self.color_value, command=self.update_preview)
        color_slider.grid(row=8, column=0, pady=(0, 10))
        
        # Reset button
        ttk.Button(control_frame, text="Reset to Defaults", command=self.reset_values).grid(row=9, column=0, pady=10)
        
        # Save/Skip buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=10, column=0, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save_image).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Skip", command=self.skip_image).grid(row=0, column=1, padx=5)
        
        # Initial preview update
        self.update_preview()
        
        # Center window on screen
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'+{x}+{y}')
        
        self.root.mainloop()
    
    def update_preview(self, *args):
        """Update the preview image based on current slider values"""
        try:
            # Apply enhancements
            img = self.original_img
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Apply all enhancements
            sharpener = ImageEnhance.Sharpness(img)
            img = sharpener.enhance(self.sharpness_value.get())
            
            contraster = ImageEnhance.Contrast(img)
            img = contraster.enhance(self.contrast_value.get())
            
            brightener = ImageEnhance.Brightness(img)
            img = brightener.enhance(self.brightness_value.get())
            
            colorer = ImageEnhance.Color(img)
            enhanced = colorer.enhance(self.color_value.get())
            
            # Update preview
            enhanced_display = enhanced.resize((self.display_width, self.display_height))
            self.enhanced_photo = ImageTk.PhotoImage(enhanced_display)
            self.enhanced_label.configure(image=self.enhanced_photo)
            
            # Store the enhanced image for saving
            self.enhanced_result = enhanced
            
        except Exception as e:
            print(f"Error updating preview: {str(e)}")
    
    def reset_values(self):
        """Reset all sliders to default values"""
        self.sharpness_value.set(1.5)
        self.contrast_value.set(1.2)
        self.brightness_value.set(1.1)
        self.color_value.set(1.1)
        self.update_preview()
    
    def save_image(self):
        self.proceed = True
        self.root.quit()
        self.root.destroy()
    
    def skip_image(self):
        self.proceed = False
        self.root.quit()
        self.root.destroy()

def enhance_image_resolution(input_folder, output_folder):
    """
    Enhance the resolution of images in the input folder and save them to the output folder.
    Shows a preview window with adjustment sliders for each image before saving.
    
    Args:
        input_folder (str): Path to the folder containing source images
        output_folder (str): Path to the folder where enhanced images will be saved
    """
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Supported image formats
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        # Check if the file is an image
        if any(filename.lower().endswith(fmt) for fmt in supported_formats):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            try:
                # Open the image
                with Image.open(input_path) as img:
                    # Show preview window
                    preview = ImagePreviewWindow(img, filename)
                    
                    # Save if user clicked "Save"
                    # if preview.proceed:
                    if filename.lower().endswith(('.jpg', '.jpeg')):
                        preview.enhanced_result.save(output_path, 'JPEG', quality=95, optimize=True)
                    elif filename.lower().endswith('.png'):
                        preview.enhanced_result.save(output_path, 'PNG', optimize=True)
                    else:
                        preview.enhanced_result.save(output_path, quality=95)
                    print(f"Saved enhanced version of: {filename}")
                    # else:
                    #     print(f"Skipped: {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

if __name__ == "__main__":
    # Example usage
    input_folder = "posters(1080x1920)"
    output_folder = "enhanced_posters"
    
    enhance_image_resolution(input_folder, output_folder)