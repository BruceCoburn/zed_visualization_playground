from PyQt5.QtCore import QTimer

# Print 'test' every 100 ms
timer = QTimer()
timer.timeout.connect(lambda: print('test'))

# Start the timer
timer.start(100)

# Stop the timer after 3 seconds
QTimer.singleShot(3000, timer.stop)

# Start the event loop
app.exec_()
