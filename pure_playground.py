import numpy as np
import cv2
import math

# Initialize the image
img_height, img_width = 400, 500
img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

# Function to draw grid
def draw_grid(img):
    for i in range(0, img.shape[1], 25):  # vertical lines
        cv2.line(img, (i, 0), (i, img.shape[0]), (255, 255, 255), 1)
    for i in range(0, img.shape[0], 25):  # horizontal lines
        cv2.line(img, (0, i), (img.shape[1], i), (255, 255, 255), 1)

# Circle motion parameters
radius = 75
angle = 0
center_of_rotation = (img_width // 2, img_height // 2)

# Animation loop
while True:
    # Clear image and redraw grid
    img.fill(0)
    draw_grid(img)

    # Calculate circle position
    x = int(center_of_rotation[0] + radius * math.cos(angle))
    y = int(center_of_rotation[1] + radius * math.sin(angle))

    # Draw circle
    cv2.circle(img, (x, y), 10, (0, 0, 255), -1)

    # Show image
    cv2.imshow("Animated Circle on Grid", img)
    if cv2.waitKey(50) & 0xFF == ord('q'):  # Press 'q' to quit
        break

    # Update angle for next frame
    angle += 0.1

cv2.destroyAllWindows()
