from PIL import Image
import os
import re

def flexible_open_image(input_file):
    # Base directory where the images are located
    source_dir = "source/"
    
    # Remove file extension and split the input filename into parts
    file_base_name = os.path.splitext(input_file)[0]
    
    # Create a regex pattern that allows underscores at any position
    pattern = re.compile('_*'.join(re.escape(part) for part in file_base_name) + r'\.png$', re.IGNORECASE)
    
    # Search for the matching file in the source directory
    for filename in os.listdir(source_dir):
        if pattern.fullmatch(filename):
            file_path = os.path.join(source_dir, filename)
            # Open and return the image
            return Image.open(file_path)
    
    # If no matching file is found, raise an error
    raise FileNotFoundError(f"No file matching {input_file} found in {source_dir}")

def process_and_crop_image(input_file, width=16, scale=1, file_name=None):
    # Load the image
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    image = flexible_open_image(input_file)
    
    # Ensure the image is 1024x1024
    if image.size[0] != image.size[1]:
        raise ValueError(f"The input image must be square. {base_name}")
    
    base_scale = 1024
    scale_multiplier = image.size[0] // base_scale
    
    if scale != 1:
        scaled_width = image.size[0] // (scale * scale_multiplier)
        scaled_image = image.resize((scaled_width, scaled_width))
    else:
        scaled_image = image

    base_name = file_name if file_name else base_name
    output_dir = "ctm/" + base_name
    os.makedirs(output_dir, exist_ok=True)

    image_plain = scaled_image.copy()
    image_plain = image_plain.resize((width, width))
    output_plain = os.path.join(output_dir, f"{base_name}.png")
    image_plain.save(output_plain)

    suffix = 0
    crop_size = width
    crop_count = scaled_width//width
    for i in range(crop_count):
        for j in range(crop_count):
            left = j * crop_size
            top = i * crop_size
            right = left + crop_size
            bottom = top + crop_size
            cropped_image = scaled_image.crop((left, top, right, bottom))
            
            # Save each cropped image
            output_file = os.path.join(output_dir, f"{suffix}.png")
            suffix += 1
            cropped_image.save(output_file)
            #print(f"Saved: {output_file}")
    properties = open(f"{output_dir}/{base_name}.properties", "w+")
    properties.write(f"method=repeat\ntiles=0-{crop_count**2-1}\nmatchBlocks=oxygen:{base_name}\nwidth={crop_count}\nheight={crop_count}")

def crop_image_to_tiles(input_file):
    # Load the image
    image = Image.open(input_file)
    
    # Ensure the image is 192x64
    if image.size != (192, 64):
        raise ValueError("The input image must be 192x64 pixels.")
    
    # Output directory
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = base_name + "_tiles"
    os.makedirs(output_dir, exist_ok=True)
    
    # Crop into 16x16 pieces
    tile_width, tile_height = 16, 16
    tile_count = 0
    for y in range(0, 64, tile_height):
        for x in range(0, 192, tile_width):
            # Define the box to crop
            box = (x, y, x + tile_width, y + tile_height)
            cropped_image = image.crop(box)
            
            # Save each cropped image
            output_file = os.path.join(output_dir, f"{tile_count}.png")
            cropped_image.save(output_file)
            print(f"Saved: {output_file}")
            tile_count += 1
"""
mode = input("Mode (1-2): ")
input_filename = input("Enter file name: ")+'.png'
match mode:
    case '1':
        size = input("Enter crop size(default 16): ")
        scale = input("Enter scale(larger are smaller detail): ")
        if size == '':
            size = 341
        else:
            size = int(size)
        if scale == '':
            scale = 1
        else:
            scale = int(scale)
        process_and_crop_image(input_filename, size, scale)
    case '2':
        crop_image_to_tiles(input_filename)
"""