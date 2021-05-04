from rplidar import RPLidar
import time


lidar = RPLidar()
print("Lidar object created")
lidar.get_health()
time.sleep(2)
lidar.start_scanning()