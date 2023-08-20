#-----------------------------------------------------------------
#
#                       [CONSTANTS]
#
#
#
#-----------------------------------------------------------------

# Unique device identifier for IMU6050 StereoBench IMU
USB_DEVICE_ID = 605045882

# Number of packets (comma separated parameters) in device message
# This is used to filter out non-measurement or broken messages in 
# message parsing
NUM_MEAS_PACKETS = 4

# Serial Baud rate
BAUD_RATE = 115200 

# Interval in which a new measurement is grabbed and the chart is updated
REFRESH_INTERVAL_SEC = 0.8

# Number of grid cells in +/- direction
# Note: Total number of grid cells in x and y will be double of that 
NUM_GRID_CELLS_X = 60
NUM_GRID_CELLS_Y = 60

# Grid cell size 
GRID_CELL_SIZE_MM = 15

# Cell value that will be assigned to obstacles (non traversable)
OBSTACLE_VALUE = 0
# Cell value that will be assigned to non-obstacles (traversable)
NO_OBSTACLE_VALUE = 255

#-----------------------------------------------------------------