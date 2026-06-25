import numpy as np
import cv2

# Creates a random colored 400x400 test image
img = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
cv2.imwrite("test_image.jpg", img)
print("test_image.jpg created successfully")