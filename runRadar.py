#-----------------------------------------------------------------------------------------
#         ReadMe
#-----------------------------------------------------------------------------------------
"""
Little project to visualize data generated from a dyi 'radar' bolting an optical vl53lox 
time of flight sensor on a servo and letting it scan a 90 degree window.

This script will automatically try to connect via USB serial to a ESP32 (which has the 
code under esp32 uploaded) and retrieve distance and servo angle data.

"""
#-----------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
import math
import threading

import parameters.constants as cnst

from util.PyLog import PyLog
from util.MapChart import MapChart
from util.SerialInterface import SerialInterface

from util.MeasData import MeasData
#-----------------------------------------------------------------------------------------
#         Parameters
#-----------------------------------------------------------------------------------------

# Create logger instance
log = PyLog()

# Create Serial interface
serialInterface = SerialInterface(log)

# Create measurement data instance 
meas = MeasData(serialInterface)
#-----------------------------------------------------------------------------------------
def main():
  
  log.pLogMsg('---------------------------------------')
  log.pLogMsg('           [Start Radar]')
  log.pLogMsg('---------------------------------------')
  
  if serialInterface.serialPortFound:
    
    # Open new thread to handle measurement queries from serial
    serialThread = threading.Thread(target=meas.measurementLoop, 
                                    name="GrabMeasurements")

    # Create chart instance 
    mapChart = MapChart(meas, serialThread, serialInterface, log)
    
    # Start measurement query thread
    serialThread.start()
    
    # Start chart animation
    mapChart.start()
    
  else:
    log.pLogErr('No valid serial device found. --> Exiting')
  
  log.close()
  
#-----------------------------------------------------------------------------------------
if __name__=="__main__":
  main()