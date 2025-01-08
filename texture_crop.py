from PIL import Image
import os

def process_and_crop_image(input_file, width=16, scale=1):
    # Load the image
    image = Image.open("source/"+input_file)
    
    # Ensure the image is 1024x1024
    if image.size != (1024, 1024):
        raise ValueError("The input image must be 1024x1024 pixels.")
    
    # Scale down to 1023x1023
    if scale != 1:
        scaled_width = image.size[0] // scale
        scaled_image = image.resize((scaled_width, scaled_width))
    else:
        scaled_image = image
    
    # Prepare the output directory
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = "ctm/" + base_name
    os.makedirs(output_dir, exist_ok=True)
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
            print(f"Saved: {output_file}")
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