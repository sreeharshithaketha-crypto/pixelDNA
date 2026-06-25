from PIL import Image

img = Image.new("RGB", (500, 500), color="blue")

img.save("test_image.jpg")

print("Test image created successfully")