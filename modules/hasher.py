import imagehash
from PIL import Image

def generate_hash(image_path):
    """
    Generates a perceptual hash for an image.
    Similar images produce similar hashes, even after compression/screenshots.
    """
    img = Image.open(image_path)
    phash = imagehash.phash(img)
    print(f"Perceptual hash: {phash}")
    return phash

def compare_hashes(image_path1, image_path2, threshold=10):
    """
    Compares two images using perceptual hash difference.
    Lower difference = more similar. threshold defines tamper cutoff.
    """
    hash1 = generate_hash(image_path1)
    hash2 = generate_hash(image_path2)
    
    diff = hash1 - hash2
    print(f"Hash difference: {diff}")
    
    if diff <= threshold:
        print("Result: Images are similar (likely same origin)")
    else:
        print("Result: Images are significantly different (possible tamper/different image)")
    
    return diff

if __name__ == "__main__":
    compare_hashes("test_image.jpg", "tampered_test.jpg")