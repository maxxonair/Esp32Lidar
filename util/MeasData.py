
import numpy as np 
import math

import parameters.constants as cnst

class MeasData():
  
  servoAngleCorrection_deg = 45
  
  numMeasCounter = 0 
  numMeasOutsideRange = 0 
  numMeasNotValid = 0
  numTotalMeasQuery = 0 
  
  isQueryNewMeasurements = True
  
  def clearMapData(self):
      self.mapData = cnst.NO_OBSTACLE_VALUE * np.ones(shape=(cnst.NUM_GRID_CELLS_X * 2, 
                                                             cnst.NUM_GRID_CELLS_Y * 2))
  def __init__(self, serialInterface):
    self.serialInterface = serialInterface
    
    self.clearMapData()
    
    self.numMeasCounter = 0 
    
    self.xMax =   cnst.NUM_GRID_CELLS_X * cnst.GRID_CELL_SIZE_MM
    self.yMax =   cnst.NUM_GRID_CELLS_Y * cnst.GRID_CELL_SIZE_MM
    self.xMin = - cnst.NUM_GRID_CELLS_X * cnst.GRID_CELL_SIZE_MM
    self.yMin = - cnst.NUM_GRID_CELLS_Y * cnst.GRID_CELL_SIZE_MM
    
  #-----------------------------------------------------------------------------------------
  def _findCellIndex(self, x, numGridCells):
    index = -1
    xLoop = 0
    if x >= 0:
      for iCounter in range(numGridCells):
        if abs(x - (xLoop)) < cnst.GRID_CELL_SIZE_MM:
          index = numGridCells + iCounter
          break
        else:
          xLoop += cnst.GRID_CELL_SIZE_MM
    else:
      for iCounter in range(numGridCells):
        if abs(x - (xLoop)) < cnst.GRID_CELL_SIZE_MM:
          index = numGridCells - iCounter
          break
        else:
          xLoop -= cnst.GRID_CELL_SIZE_MM
    return index 

  def _addMeasurement(self, boresightAngle_deg, distance_mm):
      # Apply angle correction
      # This is to align the middle of the observation cone with the x-axis
      boresightAngle_deg = boresightAngle_deg + self.servoAngleCorrection_deg
      
      # Compute the coordinates of the observed obstacle
      x = distance_mm * math.sin(math.radians(boresightAngle_deg))
      y = distance_mm * math.cos(math.radians(boresightAngle_deg))
      
      # Check if measurement is outside the grid
      if x > self.xMax or x < self.xMin or y > self.yMax or y < self.yMin:
        self.numMeasOutsideRange += 1
      else:
        # Find nearest cell index      
        ix = self._findCellIndex(x, cnst.NUM_GRID_CELLS_X)
        iy = self._findCellIndex(y, cnst.NUM_GRID_CELLS_Y)
            
        # Check if both indices have been found
        if ix != -1 and iy != -1 :
          self.mapData[ix,iy] = cnst.OBSTACLE_VALUE
          self.numMeasCounter += 1
        else:
          self.numMeasNotValid += 1

  def queryMeasurement(self):
    # Grab measurement from serial connection
    measurement = self.serialInterface.grabMeasurement()
    
    self.numTotalMeasQuery += 1
    
    # Check if measurement is valid
    if measurement["dev_id"] != -1 and measurement["distance_meas_mm"] > 0:
      self._addMeasurement(measurement["servo_angle_deg"],
                          measurement["distance_meas_mm"])
    else:
      self.numMeasNotValid += 1
      
  def measurementLoop(self):
    # Open serial connection
    self.serialInterface._openConnection()
    
    # Endless loop for new measurements
    while self.isQueryNewMeasurements:
      self.queryMeasurement()