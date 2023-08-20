
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
import time

import parameters.constants as cnst

class MapChart():
  
  # Grid limits
  xMax = -1
  yMax = -1 
  xMin = -1
  yMin = -1 
  
  isUiCreated = False
  
  isAnimationPaused = False
  
  # Coordinate System
  # A [x]
  # |
  # |
  # |
  # |
  # |
  # |
  # -------------------------> [y]

  def _createFigAndAxes(self):
    self.fig = plt.figure(figsize = (6, 5))
    self.ax  = plt.subplot(1,1,1)

  def __init__(self, meas, serialThread, serial, log):
    self.log = log
    self.meas = meas
    self.serialThread = serialThread
    self.serial = serial
    
    self._createFigAndAxes()
    self._initGrid()
    
  def _updatePlot(self, index):
      
    self.ax.clear()

    self.ax.pcolormesh(self.ChartAxisY,
                       self.ChartAxisX,
                       self.meas.mapData,
                       cmap='gray',
                       vmin=cnst.OBSTACLE_VALUE,
                       vmax=cnst.NO_OBSTACLE_VALUE,
                       alpha=1)
    
    self.ax.scatter(0,
                    0,
                    marker='+',
                    color='r',
                    s=50)
    
    self.ax.set_title("Radar")
    # self.fig.tight_layout()
    self.ax.grid(color='gray', linestyle='-', linewidth=0.5)
    
    
    if not self.isUiCreated:
      self.isUiCreated = True
      
      # Set callback on close event 
      self.fig.canvas.mpl_connect('close_event', self._callbackOnWindowClose)
      
      self.axpause = self.fig.add_axes([0.7, 0.02, 0.1, 0.035])
      self.axclear = self.fig.add_axes([0.81, 0.02, 0.15, 0.035])
      
      self.bClear = Button(self.axclear, 'Clear Map', hovercolor='gray')
      self.bClear.on_clicked(self._callbackButtonClearMap)
      
      self.bPause = Button(self.axpause, 'Pause')
      self.bPause.color = 'red'
      self.bPause.on_clicked(self._callbackPauseResume)
    
    self.ax.set_xlabel("y [m]")
    self.ax.set_ylabel("x [m]")
    self.ax.axis('equal')
    
    
  def start(self):
    self.MonitorAnimation = animation.FuncAnimation(self.fig, 
                                                    self._updatePlot, 
                                                    interval=cnst.REFRESH_INTERVAL_SEC*1000)
    plt.show()
  
  def _initGrid(self):
    self.xMax =   cnst.NUM_GRID_CELLS_X * cnst.GRID_CELL_SIZE_MM
    self.yMax =   cnst.NUM_GRID_CELLS_Y * cnst.GRID_CELL_SIZE_MM
    self.xMin = - cnst.NUM_GRID_CELLS_X * cnst.GRID_CELL_SIZE_MM
    self.yMin = - cnst.NUM_GRID_CELLS_Y * cnst.GRID_CELL_SIZE_MM
    self.ChartAxisX = np.arange(self.xMin, self.xMax, cnst.GRID_CELL_SIZE_MM)  
    self.ChartAxisY = np.arange(self.yMin, self.yMax, cnst.GRID_CELL_SIZE_MM)
   
  def _callbackOnWindowClose(self, event):
    self.meas.isQueryNewMeasurements = False
    time.sleep(0.2)
    self.serial._closeConnection()
    self.serialThread.join() 
    self.MonitorAnimation.pause
    self.log.pLogMsg('---------------------------------------------')
    self.log.pLogMsg('--------------  [ EXITING ]   ---------------')
    self.log.pLogMsg('')
    self.log.pLogMsg(f'Total measurements queried       : {self.meas.numTotalMeasQuery}')
    self.log.pLogMsg(f'Total measurements mapped        : {self.meas.numMeasCounter}')
    self.log.pLogMsg(f'Total measurements outside range : {self.meas.numMeasOutsideRange}')
    self.log.pLogMsg(f'Total measurements not valid     : {self.meas.numMeasNotValid}')
    self.log.pLogMsg('')
    self.log.pLogMsg('---------------------------------------------')
    plt.close()
    
  def _callbackButtonClearMap(self, event):
    self.meas.clearMapData()
    self.log.pLogMsg(f'Clear map data')
    
  def _callbackPauseResume(self, event):
    if self.isAnimationPaused:
      self.MonitorAnimation.resume()
      self.log.pLogMsg(f'Resume monitoring')
      self.bPause.color = 'red'
      self.isAnimationPaused = False
    else:
      self.MonitorAnimation.pause()
      self.log.pLogMsg(f'Pause monitoring')
      self.bPause.color = 'gray'
      self.isAnimationPaused = True