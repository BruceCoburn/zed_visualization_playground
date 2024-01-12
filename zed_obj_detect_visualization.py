# Import native python libraries
import cv2
import numpy as np

# Import custom python libraries / modules
from world_frame_query import worldFrameQuery


def redraw_grid(img, pixels_per_grid_line):
    """
    This function redraws the grid on the image.
    :param img: np array representing the image
    :return:
    """

    # Draw white vertical lines
    for i in range(0, img.shape[1], pixels_per_grid_line):
        cv2.line(img, (i, 0), (i, img.shape[0]), (255, 255, 255), 1)
    # Draw white horizontal lines
    for i in range(0, img.shape[0], pixels_per_grid_line):
        cv2.line(img, (0, i), (img.shape[1], i), (255, 255, 255), 1)

if __name__ == "__main__":
    world_frame_length, world_frame_width = worldFrameQuery(use_default=True)
    print(f"World Frame Length (m): {world_frame_length}")
    print(f"World Frame Width (m): {world_frame_width}")
    # Length is Top to Bottom
    # Width is Left to Right

    # Define the scale (pixels per grid line, each grid line represents 0.5 meters)
    pixels_per_grid_line = 25  # If each grid line represents 0.5 meters,
                               # then 25 pixels per grid line is 50 pixels per meter
                               # or 2 pixels per centimeter

    # Calculate the number of grid lines and then the size of the image in pixels
    num_lines_length = int(world_frame_length / 0.5)
    num_lines_width = int(world_frame_width / 0.5)
    img_height = num_lines_width * pixels_per_grid_line # 1 meter = 50 pixels
    img_width = num_lines_length * pixels_per_grid_line # 1 meter = 50 pixels

    # Create a blank image
    img = np.zeros((img_height, img_width, 3), dtype=np.uint8)
    print(f"Image shape: {img.shape}")

    redraw_grid(img, pixels_per_grid_line)

    # Draw a red circle in the center of the image
    center = (img_width // 2, img_height // 2)
    radius = 10
    cv2.circle(img, center, radius, (0, 0, 255), -1)

    # Create a resizable window and display the image
    cv2.namedWindow("Grid", cv2.WINDOW_NORMAL)
    cv2.imshow("Grid", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
