import pyzed.sl as sl
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer

class ZEDCameraWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.translationLabel = QLabel("Translation: ")
        self.orientationLabel = QLabel("Orientation: ")
        self.imuLabel = QLabel("IMU Data: ")

        self.layout.addWidget(self.translationLabel)
        self.layout.addWidget(self.orientationLabel)
        self.layout.addWidget(self.imuLabel)

        self.setLayout(self.layout)
        self.setWindowTitle('ZED Camera Tracking')
        self.show()

    def updateData(self, translation, orientation, imu_data):
        self.translationLabel.setText(f"Translation: {translation}")
        self.orientationLabel.setText(f"Orientation: {orientation}")
        self.imuLabel.setText(f"IMU Data: {imu_data}")

def update_gui(window, zed, zed_pose, zed_sensors, can_compute_imu):
    if zed.grab() == sl.ERROR_CODE.SUCCESS:

        # Get the pose of the left eye of the camera with reference to the world frame
        zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)

        # Display the translation and timestamp
        py_translation = sl.Translation()
        tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
        ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
        tz = round(zed_pose.get_translation(py_translation).get()[2], 3)
        print("Translation: Tx: {0}, Ty: {1}, Tz {2}, Timestamp: {3}\n".format(tx, ty, tz,
                                                                               zed_pose.timestamp.get_milliseconds()))

        # Display the orientation quaternion
        py_orientation = sl.Orientation()
        ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
        oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
        oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
        ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)
        print("Orientation: Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}\n".format(ox, oy, oz, ow))

        if can_compute_imu:
            zed.get_sensors_data(zed_sensors, sl.TIME_REFERENCE.IMAGE)
            zed_imu = zed_sensors.get_imu_data()
            # Display the IMU acceleratoin
            acceleration = [0, 0, 0]
            zed_imu.get_linear_acceleration(acceleration)
            ax = round(acceleration[0], 3)
            ay = round(acceleration[1], 3)
            az = round(acceleration[2], 3)
            print("IMU Acceleration: Ax: {0}, Ay: {1}, Az {2}\n".format(ax, ay, az))

            # Display the IMU angular velocity
            a_velocity = [0, 0, 0]
            zed_imu.get_angular_velocity(a_velocity)
            vx = round(a_velocity[0], 3)
            vy = round(a_velocity[1], 3)
            vz = round(a_velocity[2], 3)
            print("IMU Angular Velocity: Vx: {0}, Vy: {1}, Vz {2}\n".format(vx, vy, vz))

            # Display the IMU orientation quaternion
            zed_imu_pose = sl.Transform()
            ox = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[0], 3)
            oy = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[1], 3)
            oz = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[2], 3)
            ow = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[3], 3)
            print("IMU Orientation: Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}\n".format(ox, oy, oz, ow))

        # Update the GUI
        window.updateData(f"Tx: {tx}, Ty: {ty}, Tz: {tz}",
                          f"Ox: {ox}, Oy: {oy}, Oz: {oz}, Ow: {ow}",
                          f"IMU Acceleration: Ax: {ax}, Ay: {ay}, Az: {az}, "
                          f"IMU Angular Velocity: Vx: {vx}, Vy: {vy}, Vz: {vz}")



def main():
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.AUTO
    print(f"Camera Resolution: {init_params.camera_resolution}")
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
    init_params.coordinate_units = sl.UNIT.METER

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Camera Open : {repr(err)}. Exit program.")
        exit()

    # Enable positional tracking with default parameters
    py_transform = sl.Transform()
    tracking_parameters = sl.PositionalTrackingParameters(_init_pos=py_transform)
    err = zed.enable_positional_tracking(tracking_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Enable_positional_tracking : {repr(err)}. Exit program.")
        zed.close()
        exit()

    # Track the camera position
    zed_pose = sl.Pose()

    zed_sensors = sl.SensorsData()
    runtime_parameters = sl.RuntimeParameters()

    can_compute_imu = zed.get_camera_information().camera_model != sl.MODEL.ZED
    print(f"Can compute IMU: {can_compute_imu}")

    # Create a GUI window
    app = QApplication(sys.argv)
    window = ZEDCameraWindow()

    timer = QTimer()
    timer.timeout.connect(lambda: update_gui(window, zed, zed_pose, zed_sensors, can_compute_imu))
    timer.start(1000)

    # Start the application's event loop
    exit_code = app.exec_()

    # Close the camera
    zed.close()

    # Exit the application with the exit code
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
