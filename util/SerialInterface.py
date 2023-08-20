import serial
import time 
import sys 
import glob
import numpy as np
import math

import parameters.constants as cnst

class SerialInterface():

    # IMU message delimiter
    messageDelimiter = ','

    usb_port = ''
    serial_timeout_s=1
    
    serialPortFound = False

    # Number of messages to wait for until parsing and evaluation, while looking for the 
    # correct imu port 
    port_finder_msg_attempts = 5

    def __init__(self, log):
        self.log = log 
        # Find usb ports
        usb_ports = self._listSerialPorts()
        if len(usb_ports) > 0:
            self.log.pLogMsg(f"Multiple serial ports ({len(usb_ports)}) found. Searching for Device ... ")
            self.log.pLogMsg(f'Detected ports: {usb_ports}')
            isValidPortFound = False
            for portCounter, usb_port in enumerate(usb_ports):
                self.log.pLogMsg(f'Open and check port {portCounter}')
                # Try to open and read from port 
                self.usb_port = usb_port
                self.serCon = serial.Serial(self.usb_port, 
                                            cnst.BAUD_RATE, 
                                            timeout=self.serial_timeout_s)

                if self.serCon.isOpen():
                    self.serCon.close()

                # Open connection    
                self._openConnection()

                # Take several messages to make sure a vaild one comes through
                for iCounter in range(self.port_finder_msg_attempts):
                    message = self.serCon.readline()\
                    # If message is completely empty
                    # -> Thats not our port, moving on
                    if message == b'':
                        break

                if (self._parseMessage(message))['dev_id'] == cnst.USB_DEVICE_ID:
                    self._closeConnection()
                    self.log.pLogMsg(f'Device found on port {portCounter}')
                    isValidPortFound = True
                    self.serialPortFound = True
                    break
            if not isValidPortFound:
                self.log.pLogMsg(f'ERROR: Device port not found! ')
                self.log.pLogMsg('Exiting')
                exit(1)
        else:
            self.log.pLogErr(f'No serial port found')

    def stream(self):
        self._openConnection()
        
        while True:
            message = self.serCon.readline()
            try:
                measurement = self._parseMessage(message)
                self.log.pLogMsg(f'[{measurement["msg_id"]}|{measurement["msg_id"]}] == {measurement["servo_angle_deg"]} {measurement["distance_meas_mm"]} ')
            except:
                self.log.pLogMsg('Error: Parsing message failed')
                
            time.sleep(0.1)
        
    def listenForMeasurements(self):
        self._openConnection()
        prevID = -1
        measCounter = 0
        while True:
            message = self.serCon.readline()
            measurement = self._parseMessage(message)
            if measurement["msg_id"] != prevID and measurement["msg_id"] != -1:
                self.log.pLogMsg(f'[{measurement["msg_id"]}|{measurement["msg_id"]}] == {measurement["servo_angle_deg"]} {measurement["distance_meas_mm"]} ')
                self.mapChart.addMeasurement(measurement["servo_angle_deg"],
                                            measurement["distance_meas_mm"])
                measCounter = measCounter + 1
            prevID = measurement["msg_id"]
            time.sleep(0.1)
            
        self._closeConnection()
    
    def grabMeasurement(self):
        message = self.serCon.readline()
        try:
            measurement = self._parseMessage(message)
            self.log.pLogMsg(f'[{measurement["msg_id"]}|{measurement["msg_id"]}] ==> | {measurement["servo_angle_deg"]} deg | {measurement["distance_meas_mm"]} mm | ')
            return measurement
        except:
            self.log.pLogWrn('Parsing serial message failed.')
            return {'dev_id': -1,'msg_id': -1,'servo_angle_deg':  -1,'distance_meas_mm': -1,}
        
    #-------------------------------------------------------------------------
    #       [Private Functions]
    #-------------------------------------------------------------------------
    def _parseMessage(self, message_in):
        message = str(message_in.decode("utf-8") )
        strArray = message.split(self.messageDelimiter)

        if len(strArray) != cnst.NUM_MEAS_PACKETS:
            # Message not valid
            measurement = {
                'dev_id': -1,
                'msg_id': -1,
                'servo_angle_deg':  -1,
                'distance_meas_mm': -1,
            }
        else:
            # Message not valid -> Parsing to dict
            measurement = {
                'dev_id': int(strArray[0]),
                'msg_id': int(strArray[1]),
                'servo_angle_deg':  float(strArray[2]),
                'distance_meas_mm': float(strArray[3]),
                }

        return measurement

    def _openConnection(self):
        if self.serCon.isOpen():
            self.serCon.close()
        
        # Open serial port 
        self.serCon.open()

    def _closeConnection(self):
        self.log.pLogMsg("close serial")
        self.serCon.close()
        
    def _listSerialPorts(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    #-------------------------------------------------------------------------