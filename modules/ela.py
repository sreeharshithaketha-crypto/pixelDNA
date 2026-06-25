from PIL import Image, ImageChops, ImageEnhance
import os

def generate_ela(image_path, output_path, quality=90):
    """
    Generates an Error Level Analysis image.
    Highlights regions that were likely edited/tampered.
    """
    original = Image.open(image_path).convert('RGB')
    
    temp_path = f"{output_path}.temp.jpg"
    original.save(temp_path, 'JPEG', quality=quality)
    resaved = Image.open(temp_path)
    
    diff = ImageChops.difference(original, resaved)
    
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    
    ela_image = ImageEnhance.Brightness(diff).enhance(scale)
    ela_image.save(output_path)
    
    os.remove(temp_path)
    
    print(f"ELA generated -> {output_path}")
    print(f"Max difference detected: {max_diff}")
    return max_diff

if __name__ == "__main__":
    generate_ela("test_image.jpg", "ela_output.jpg")