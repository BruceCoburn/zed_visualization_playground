import pyzed.sl as sl
import sys
import cv2
import math
import random

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap, QGuiApplication
from PyQt5.QtCore import QTimer, Qt

import numpy as np

from world_frame_query import worldFrameQuery

class ObjDetectionMap(QLabel):
    def __init__(self,
                 frame_length,
                 frame_width,
                 pixels_per_grid_line,
                 parent=None):
        super().__init__(parent)

        # Start in the center of the image
        self.reference_x_pos = frame_length // 2
        self.reference_y_pos = frame_width // 2

        self.x_pos = self.reference_x_pos
        self.y_pos = self.reference_y_pos

        self.mouth_angle = 45

        self.pixels_per_grid_line = pixels_per_grid_line

        # Draw reference grid image
        self.grid_img = np.zeros((frame_width, frame_length, 3), dtype=np.uint8)
        self.draw_grid()

        self.tracking_img = self.grid_img.copy()
        print(f"Tracking Image shape: {self.tracking_img.shape}")
        qImg = QImage(self.grid_img.data,
                      self.grid_img.shape[1],
                      self.grid_img.shape[0],
                      self.grid_img.strides[0],
                      QImage.Format_RGB888).rgbSwapped()
        self.setPixmap(QPixmap.fromImage(qImg))

    def draw_grid(self):
        """
        This function redraws the grid on the image.
        :param img: np array representing the image
        :return:
        """

        # Random number between 0 -255
        r = random.randint(0, 255)

        # Draw white vertical lines
        for i in range(0, self.grid_img.shape[1], self.pixels_per_grid_line):
            cv2.line(self.grid_img, (i, 0), (i, self.grid_img.shape[0]), (255, r, 255), 1)
        # Draw white horizontal lines
        for i in range(0, self.grid_img.shape[0], self.pixels_per_grid_line):
            cv2.line(self.grid_img, (0, i), (self.grid_img.shape[1], i), (r, 255, 255), 1)

    def update_positions(self, tx, ty):

        # Update positions

        # Update y position (need to flip ty due to coordinate system)
        self.y_pos = self.reference_y_pos - int(ty * self.pixels_per_grid_line)
        # print(f"Ty: {ty}, Y Pos (px): {self.y_pos}")

        # Update x position
        self.x_pos = self.reference_x_pos + int(tx * self.pixels_per_grid_line)
        # print(f"Tx: {tx}, X Pos (px): {self.x_pos}")

        # Clear image and redraw grid
        self.tracking_img = self.grid_img.copy()

        # Determine positions
        self.determine_positions(translation=None, orientation=None)

        # Draw camera circle
        cv2.circle(self.tracking_img, (self.x_pos, self.y_pos), 7, (0, 0, 255), -1) # cv2 is BGR

        # Angle for the mouth
        self.mouth_angle += 5  # You can change this value

        # Calculate the starting and ending points of the pie slice
        start_angle = (90 + self.mouth_angle) % 360
        end_angle = start_angle + 90

        # Draw the pie slice (Pacman mouth)
        cv2.ellipse(self.tracking_img, # Image
                    (self.x_pos, self.y_pos), # Center
                    (7, 7), # Axes lengths (Radius)
                    0, # Angle of rotation of ellipse
                    start_angle, # Start angle of the arc
                    end_angle, # End angle of the arc
                    (255, 255, 255),
                    -1)

        # Update tracking image
        self.update_tracking_image()

    def update_tracking_image(self):
        qImg = QImage(self.tracking_img.data,
                      self.tracking_img.shape[1],
                      self.tracking_img.shape[0],
                      self.tracking_img.strides[0],
                      QImage.Format_RGB888).rgbSwapped().scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.setPixmap(QPixmap.fromImage(qImg))

    def determine_positions(self, translation, orientation):
        """
        This function determines the x and y position of the camera in the image.
        :param translation: The translation of the camera in the world frame
        :param orientation: The orientation of the camera in the world frame
        :return:
        """
        pass

class ZEDCameraWindow(QWidget):
    def __init__(self, frame_length, frame_width, pixels_per_grid_line):
        super().__init__()

        # Initialize default translation values
        self.tx = int(0)
        self.ty = int(0)
        self.tz = int(0)
        self.translation_str = f"Tx: {self.tx}, Ty: {self.ty}, Tz: {self.tz}"

        # Initialize default orientation values
        self.ox = int(0)
        self.oy = int(0)
        self.oz = int(0)
        self.ow = int(0)
        self.orientation_str = f"Ox: {self.ox}, Oy: {self.oy}, Oz: {self.oz}, Ow: {self.ow}"

        # Initialize the UI
        self.initUI(frame_length, frame_width, pixels_per_grid_line)

    def initUI(self, frame_length, frame_width, pixels_per_grid_line=25):
        self.layout = QVBoxLayout()

        self.translationLabel = QLabel("Translation: ")
        self.orientationLabel = QLabel("Orientation: ")

        self.tracking_img = ObjDetectionMap(frame_length, frame_width, pixels_per_grid_line)

        # Get the size of the screen
        screen = QGuiApplication.primaryScreen().size()
        screen_width = screen.width()
        screen_height = screen.height()

        # Calculate 80% of the screen size
        width_80_percent = int(screen_width * 0.8)
        height_80_percent = int(screen_height * 0.8)

        self.layout.addWidget(self.translationLabel)
        self.layout.addWidget(self.orientationLabel)

        self.tracking_img.setFixedSize(width_80_percent, height_80_percent)
        self.layout.addWidget(self.tracking_img)

        self.setLayout(self.layout)
        self.setWindowTitle('ZED Camera Tracking')
        self.showMaximized()

    def updateData(self,
                   tx, ty, tz,
                   ox, oy, oz, ow):

        self.translation_str = f"Tx: {tx}, Ty: {ty}, Tz: {tz}"
        self.orientation_str = f"Ox: {ox}, Oy: {oy}, Oz: {oz}, Ow: {ow}"

        self.translationLabel.setText(f"Translation: {self.translation_str}")
        self.orientationLabel.setText(f"Orientation: {self.orientation_str}")

        self.tracking_img.update_positions(tx, ty)

def update_gui(window, zed, zed_pose, zed_sensors, can_compute_imu):
    if zed.grab() == sl.ERROR_CODE.SUCCESS:

        # Get the pose of the left eye of the camera with reference to the world frame
        zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)

        # Display the translation and timestamp
        py_translation = sl.Translation()
        tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
        ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
        tz = round(zed_pose.get_translation(py_translation).get()[2], 3)
        # print("Translation: Tx: {0}, Ty: {1}, Tz {2}, Timestamp: {3}\n".format(tx, ty, tz,
        #                                                                        zed_pose.timestamp.get_milliseconds()))

        # Display the orientation quaternion
        py_orientation = sl.Orientation()
        ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
        oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
        oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
        ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)
        # print("Orientation: Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}\n".format(ox, oy, oz, ow))

        # Update the GUI
        window.updateData(tx, ty, tz,
                          ox, oy, oz, ow)


def main():

    # Get world frame measurements
    world_frame_length, world_frame_width = worldFrameQuery(use_default=True)
    print(f"World Frame Length (m): {world_frame_length}")
    print(f"World Frame Width (m): {world_frame_width}")

    # Define the scale (pixels per grid line, each grid line represents 0.5 meters)
    pixels_per_grid_line = 25  # If each grid line represents 0.5 meters,
    # then 25 pixels per grid line is 50 pixels per meter
    # or 2 pixels per centimeter

    # Calculate the number of grid lines and then the size of the image in pixels
    num_lines_length = int(world_frame_length / 0.5)
    num_lines_width = int(world_frame_width / 0.5)
    world_frame_width_quant = num_lines_width * pixels_per_grid_line  # 1 meter = 50 pixels
    world_frame_length_quant = num_lines_length * pixels_per_grid_line  # 1 meter = 50 pixels

    # Create a Camera object
    print("Initializing ZED Camera...")
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    print(f"Setting configuration parameters...")
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.AUTO
    print(f"Camera Resolution: {init_params.camera_resolution}")
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
    init_params.coordinate_units = sl.UNIT.METER

    # Open the camera
    print(f"Opening Camera...")
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Camera Open : {repr(err)}. Exit program.")
        exit()

    # Enable positional tracking with default parameters
    print(f"Enabling Positional Tracking...")
    py_transform = sl.Transform()
    tracking_parameters = sl.PositionalTrackingParameters(_init_pos=py_transform)
    err = zed.enable_positional_tracking(tracking_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Enable_positional_tracking : {repr(err)}. Exit program.")
        zed.close()
        exit()

    # Track the camera position
    print(f"Tracking Camera Position...")
    zed_pose = sl.Pose()

    zed_sensors = sl.SensorsData()
    runtime_parameters = sl.RuntimeParameters()

    can_compute_imu = zed.get_camera_information().camera_model != sl.MODEL.ZED
    print(f"Can compute IMU: {can_compute_imu}")

    # Create a GUI window
    print(f"Creating GUI window...")
    app = QApplication(sys.argv)
    window = ZEDCameraWindow(world_frame_length_quant, world_frame_width_quant, pixels_per_grid_line)

    timer = QTimer()
    timer.timeout.connect(lambda: update_gui(window, zed, zed_pose, zed_sensors, can_compute_imu))
    timer.start(100)

    # Start the application's event loop
    exit_code = app.exec_()

    # Close the camera
    zed.close()

    # Exit the application with the exit code
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
