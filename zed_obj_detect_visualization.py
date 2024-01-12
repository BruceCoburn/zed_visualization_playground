# Import native python libraries
import cv2
import numpy as np

# Import custom python libraries / modules
from world_frame_query import worldFrameQuery

if __name__ == "__main__":
    world_frame_length, world_frame_width = worldFrameQuery()
    print(f"World Frame Length (m): {world_frame_length}")
    print(f"World Frame Width (m): {world_frame_width}")
    # Length is Top to Bottom
    # Width is Left to Right

    # Define the scale (pixels per grid line, each grid line represents 0.5 meters)
    scale = 25  # example scale

    # Calculate the number of grid lines and then the size of the image in pixels
    num_lines_length = int(world_frame_length / 0.5)
    num_lines_width = int(world_frame_width / 0.5)
    img_height = num_lines_width * scale
    img_width = num_lines_length * scale

    # Create a blank image
    img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

    # Draw vertical lines
    for i in range(0, img_width, scale):
        cv2.line(img, (i, 0), (i, img_height), (255, 255, 255), 1)

    # Draw horizontal lines
    for i in range(0, img_height, scale):
        cv2.line(img, (0, i), (img_width, i), (255, 255, 255), 1)

    # Draw a circle in the center of the image
    center = (img_width // 2, img_height // 2)
    radius = 10
    cv2.circle(img, center, radius, (0, 0, 255), -1)

    # Create a resizable window and display the image
    # cv2.namedWindow("Grid", cv2.WINDOW_NORMAL)
    cv2.imshow("Grid", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
