import os
from PIL import Image

def resize_image(input_path, output_path, new_width, new_height):
    """Resizes an image to the specified dimensions and saves it."""

    try:
        with Image.open(input_path) as img:
            # Calculate aspect ratios
            img_ratio = img.width / img.height
            target_ratio = new_width / new_height

            if img_ratio > target_ratio:
                # Image is too wide, crop it
                new_img_width = int(new_height * img_ratio)
                img = img.resize((new_img_width, new_height), Image.LANCZOS)
                left = (img.width - new_width) / 2
                top = 0
                right = (img.width + new_width) / 2
                bottom = new_height
                img = img.crop((left, top, right, bottom))
            else:
                # Image is not too wide, resize normally
                img = img.resize((new_width, new_height), Image.LANCZOS)

            img.save(output_path)
    except Exception as e:
        print(f"Error processing image {input_path}: {str(e)}")

def resize_image_return(input_path, new_width, new_height):
    """Resizes an image to the specified dimensions and returns the image object."""

    try:
        with Image.open(input_path) as img:
            # Calculate aspect ratios
            img_ratio = img.width / img.height
            target_ratio = new_width / new_height

            if img_ratio > target_ratio:
                # Image is too wide, crop it
                new_img_width = int(new_height * img_ratio)
                img = img.resize((new_img_width, new_height), Image.LANCZOS)
                left = (img.width - new_width) / 2
                top = 0
                right = (img.width + new_width) / 2
                bottom = new_height
                img = img.crop((left, top, right, bottom))
            else:
                # Image is not too wide, resize normally
                img = img.resize((new_width, new_height), Image.LANCZOS)

            return img
    except Exception as e:
        print(f"Error processing image {input_path}: {str(e)}")
        return None

def resize_root_poster_folder(input_folder,output_folder,width=1080,height=1920):
    import os

    # Create the output folder if it doesn't exist

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    poster_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Resize each poster
    for poster in poster_files:
        input_path = os.path.join(input_folder, poster)
        output_path = os.path.join(output_folder, poster)
        resize_image(input_path, output_path, width, height)

    print(f"Resized {len(poster_files)} posters to {width}x{height} and saved in '{output_folder}'")
    # input_image = "your_image.jpg"
    # output_image = "resized_image.jpg"
    # width = 1080
    # height = 1920

    # resize_image(input_image, output_image, width, height)
def image_upscaler(input_image, output_image):
    from super_image import EdsrModel, ImageLoader
    import torch
    image = Image.open(input_image)

    model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=2)
    inputs = ImageLoader.load_image(image)
    preds = model(inputs)

    ImageLoader.save_image(preds, './scaled_2x.png')
    ImageLoader.save_compare(inputs, preds, './scaled_2x_compare.png')
    # image = Image.open(input_image)
    # image_loader = ImageLoader()
    # image_loader.load_image(image)
    # model = EdsrModel()
    # model.load_state_dict(torch.load("edsr_x4.pth"))
    # model.eval()
    # upscaled_image = model.predict(image_loader)
    # upscaled_image.save(output_image)

# image_upscaler("posters(1080x1920)/resized_2_Guns.jpg", "movie_posters/1080x1920/resized_1080x1920_1_upscaled.jpg")


def create_side_by_side_image(input_folder, images):
    """Creates side-by-side images from the input folder by cutting each image in half and combining them"""
    
    # Get all image files in the folder
    image_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    for image_file in image_files:
        input_path = os.path.join(input_folder, image_file)
        
        # Open and split the image
        with Image.open(input_path) as img:
            # Calculate dimensions
            half_width = img.width // 2
            
            # Create new blank image with same height but double width
            # Create new image with double width to fit two copies
            new_image = Image.new('RGB', (img.width * 2, img.height))
            
            # Paste the full original image twice
            new_image.paste(img, (0, 0))
            new_image.paste(img, (img.width, 0))
            # Save the new image with a modified filename
            output_filename = f"sidebyside_{image_file}"
            output_path = os.path.join(input_folder, output_filename)
            new_image.save(output_path)


if __name__ == "__main__":
    resize_root_poster_folder("celebrity images","celebrity images(1080x1920)")

