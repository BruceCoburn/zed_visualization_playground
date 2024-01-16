import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel)

class WorldFrameMeasurements(QDialog):
    def __init__(self, world_frame_length_default=10, world_frame_width_default=8):
        super().__init__()

        # Initialize default values
        self.world_frame_length = world_frame_length_default
        self.world_frame_width = world_frame_width_default

        # Initialize UI
        self.initUI()
        self.adjustSizeToTitle(self.windowTitle())

    def initUI(self):
        self.mainLayout = QVBoxLayout()

        #########
        # World Frame length label and input
        #########
        self.lengthLayout = QHBoxLayout()
        self.lengthLabel = QLabel("World Frame Length (m): ", self)
        self.lengthLayout.addWidget(self.lengthLabel)
        self.lengthInput = QLineEdit(self)
        self.lengthInput.setText(f"{self.world_frame_length}")  # Default value
        self.lengthInput.setMaximumWidth(50)
        self.lengthLayout.addWidget(self.lengthInput, 1)
        # Add to main layout
        self.mainLayout.addLayout(self.lengthLayout)

        #########
        # World Frame width label and input
        #########
        self.widthLayout = QHBoxLayout()
        self.widthLabel = QLabel("World Frame Width (m): ", self)
        self.widthLayout.addWidget(self.widthLabel)
        self.widthInput = QLineEdit(self)
        self.widthInput.setText(f"{self.world_frame_width}")  # Default value
        self.widthInput.setMaximumWidth(50)
        self.widthLayout.addWidget(self.widthInput, 1)
        # Add to main layout
        self.mainLayout.addLayout(self.widthLayout)

        # Confirm button
        self.confirmButton = QPushButton('Confirm values', self)
        self.confirmButton.clicked.connect(self.onConfirm)
        self.mainLayout.addWidget(self.confirmButton)

        self.setLayout(self.mainLayout)
        self.setWindowTitle('Enter World Frame Length and Width (m)')

    def adjustSizeToTitle(self, title):
        # Estimate the average pixel width per character
        avgCharWidth = 7  # This is a rough average, adjust as needed
        minWidth = len(title) * avgCharWidth
        self.setMinimumWidth(minWidth)

    def onConfirm(self):
        self.world_frame_length = float(self.lengthInput.text())
        self.world_frame_width = float(self.widthInput.text())
        self.accept()

def worldFrameQuery(world_frame_length=10, world_frame_width=8, use_default=False):

    if not use_default:
        print(f"Getting world frame measurements from user...")
        app = QApplication(sys.argv)

        dialog = WorldFrameMeasurements(world_frame_length, world_frame_width)

        if dialog.exec_():  # Execute the dialog and check if accepted
            world_frame_length = dialog.world_frame_length
            world_frame_width = dialog.world_frame_width
        else:
            print("User cancelled input...")

    return world_frame_length, world_frame_width

if __name__ == '__main__':
    worldFrameQuery()
