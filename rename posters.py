import os
import shutil

def rename_posters():
    source_dir = 'posters(1080x1920)'
    
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: The directory '{source_dir}' does not exist.")
        return

    # Iterate through all files in the source directory
    for filename in os.listdir(source_dir):
        if filename.startswith('resized_'):
            # Construct the full file paths
            old_path = os.path.join(source_dir, filename)
            new_filename = filename.replace('resized_', '', 1)
            new_path = os.path.join(source_dir, new_filename)
            
            # Rename the file
            try:
                shutil.move(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {str(e)}")

if __name__ == "__main__":
    rename_posters()
    print("Poster renaming process completed.")
