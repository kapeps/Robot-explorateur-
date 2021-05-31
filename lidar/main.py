import rplidar
import i2c_bus

print("Initializing I2C bus object")
i2c = i2c_bus.I2C_bus()

print("Creating lidar object")
lidar = rplidar.RPLidar()
lidar.reset()
i2c.setLidarMemoryViews(lidar.get_headings_mv(), lidar.get_distances_mv())
i2c.sendLidarReadings()
lidar.start_scanning()

while True:
    lidar.update()
    i2c.update(lidar)