#!/bin/env python
import serial
import time
import logging
import argparse

OPT=[
    'set_power',
    'get_power'
]
SLOT_LIST=[0, 1, 2, 3]
SERIAL_PORT_LIST=['/dev/ttyCH9344USB0','/dev/ttyCH9344USB4', '/dev/ttyCH9344USB6']
BP_DEBUG = False

crc_high_table = [
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
    0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
    0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
    0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40]
    
crc_low_table = [
    0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06,
    0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD,
    0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
    0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A,
    0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4,
    0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
    0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3,
    0xF2, 0x32, 0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4,
    0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
    0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29,
    0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED,
    0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
    0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60,
    0x61, 0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67,
    0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
    0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68,
    0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA, 0xBE, 0x7E,
    0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
    0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71,
    0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92,
    0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
    0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B,
    0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B,
    0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
    0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42,
    0x43, 0x83, 0x41, 0x81, 0x80, 0x40]

class NpmUtils:
    
    def makeByte(integer):
        res = []
        res.append(integer & 0xFF)
        res.append((integer >> 8) & 0xFF)
        res.append((integer >> 16) & 0xFF)
        res.append((integer >> 24) & 0xFF)
        return res
    makeByte = staticmethod(makeByte)

    def makeShort(low, high):
        return (low | (high << 8))
    makeShort = staticmethod(makeShort)
    
    def makeInt(byte0, byte1, byte2, byte3):
        return (byte0 | (byte1 << 8) | (byte2 << 16) | (byte3 << 24))
    makeInt = staticmethod(makeInt)
    
    def calculateChecksum(data, length = 0):
        res = 0
        if length == 0:
            length = len(data)
        for i in range(0, length):
            res += data[i]
            res = NpmUtils.makeByte(res)[0];
        return res
    calculateChecksum = staticmethod(calculateChecksum)
    
    def calculateCrc16Modbus(data, data_len):
        result = 0
        crc_high = 0xff
        crc_low = 0xff
        for i in range(data_len):
            index = crc_low ^ (0xff & data[i])
            crc_low = crc_high ^ crc_high_table[index]
            crc_high = crc_low_table[index]

        result = (crc_high << 8 | crc_low)
        return result
    calculateCrc16Modbus = staticmethod(calculateCrc16Modbus)
    
class NpmCommand:
    
    STX = 0xF7
    ETX = 0x70
    ID0 = 0xAA
    ID1 = 0x55

    STATUS_ACK = 0x10
    STATUS_PROFILE_READY = 0x20
    STATUS_INVALID_CMD = 0x40
    STATUS_CMD_BUSY = 0x80
    
    DEFAULT_READ_TIMEOUT = 700
    DEFAULT_WRITE_TIMEOUT = 700
    DEFAULT_RESPONSE_LENGTH = 9
    
    RETRIES = 7
    RETRY_DELAY = 0.100

    def __init__(self, npmIndex, arg1, arg2, arg3, arg4):
        self._stx = NpmCommand.STX
        self._id0 = NpmCommand.ID0
        self._id1 = NpmCommand.ID1
        self._npmIndex = npmIndex
        self._command = self._getCommandCode()
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3
        self._arg4 = arg4
        self._crc = 0
        #self._checksum = NpmUtils.calculateChecksum(self._getBytes(), len(self._getBytes()) - 1)
        self._crc = NpmUtils.calculateCrc16Modbus(self._getBytes(), len(self._getBytes()) - 2)
        
        self._executed = False
        self._response = None
    
    def _getCommandCode(self):
        return None

    def _getBytes(self):
        res = []
        res.append(self._stx)
        res.append(self._id0)
        res.append(self._id1)
        res.append(self._npmIndex)
        res.append(self._command)
        res.append(self._arg1)
        res.append(self._arg2)
        res.append(self._arg3)
        res.append(self._arg4)
        res.append(self._crc & 0xFF)
        res.append((self._crc >> 8) & 0xFF)
        return res
    
    def _getResponseLength(self):
        return NpmCommand.DEFAULT_RESPONSE_LENGTH
    
    def _getReadTimeout(self):
        return NpmCommand.DEFAULT_READ_TIMEOUT
    
    def _getWriteTimeout(self):
        return NpmCommand.DEFAULT_WRITE_TIMEOUT
    
    def execute(self, npmTty):
        self._response = self._sendReceiveCommand(npmTty)
        self._executed = True
        return self
        
    def getResult(self):
        return None

    def _sendReceiveCommand(self, npmTty):
        #npmTty.lock()

        try:
            if True != npmTty.isOpen():
                npmTty.open()
                if True != npmTty.isOpen():
                    raise ValueError('npmtty open failed.')
            # When using multiple networked cards (and only then) sometimes cards mysteriously fail to respond.
            retriesLeft = NpmCommand.RETRIES
            while True:
                retriesLeft -= 1
                try:
                    # Write command
                    npmTty.write(self._getBytes())
                    # Read response
                    response = npmTty.read(self._getResponseLength())
                    #print(len(response))
                    # Check response
                    self._verifyResponse(response)
            
                    return response
                except Exception as e:
                    if retriesLeft == 0:
                        raise e
                    npmTty.flush()
                    time.sleep(NpmCommand.RETRY_DELAY)
        finally:
            npmTty.close()

    def _verifyResponse(self, response):
        # Check header
        if response[0] != NpmCommand.ETX or response[1] != NpmCommand.ID1 or response[2] != NpmCommand.ID0:
            raise ValueError("incorrect response header")

        # Check checksum
        #if NpmUtils.calculateChecksum(response, len(response) - 1) != response[len(response) - 1]:
        #    raise ValueError("response checksum mismatch")
            
        if NpmUtils.calculateCrc16Modbus(response, len(response) - 2) != NpmUtils.makeShort(response[len(response) - 2], response[len(response) - 1]):
            raise ValueError("response crc mismatch")

        # Check index
        if response[3] != self._npmIndex:
            raise ValueError("response from a wrong NPM card")

        # Check status
        if (response[4] & NpmCommand.STATUS_ACK) == 0:
            raise ValueError("response has no ack bit")

        # Check if command valid
        if (response[4] & NpmCommand.STATUS_INVALID_CMD) != 0:
            raise ValueError('command not recognized')

        # Check if busy
        if (response[4] & NpmCommand.STATUS_CMD_BUSY) != 0:
            raise ValueError('card busy, command not accepted')

        # Check command
        if (response[4] & 0x0F) != self._command:
            raise ValueError("response for a wrong command")
        
class NpmCommandSwitchSATA(NpmCommand):
    
    COMMAND_CODE = 0x01

    def __init__(self, npmIndex):
        NpmCommand.__init__(self, npmIndex, 0x53, 0x41, 0x05, 0)    #'S' 'A' '5'
        
    def _getCommandCode(self):
        return NpmCommandSwitchSATA.COMMAND_CODE

class NpmCommandSwitchUTwo(NpmCommand):
    
    COMMAND_CODE = 0x01

    def __init__(self, npmIndex):
        NpmCommand.__init__(self, npmIndex, 0x55, 0x32, 0x12, 0)    #'U' '2' 0x12
        
    def _getCommandCode(self):
        return NpmCommandSwitchUTwo.COMMAND_CODE

class NpmCommandSetVoltage(NpmCommand):
    
    COMMAND_CODE = 0x03
    
    def __init__(self, npmIndex, voltage):

        NpmCommand.__init__(self, npmIndex,
                voltage & 0xff,
                (voltage >> 8) & 0xff,
                0,
                0)
    
    def _getCommandCode(self):
        return NpmCommandSetVoltage.COMMAND_CODE
    
    

class NpmStatusData:
    
    def __init__(self, voltageCurrentData, temperature, version, profileReady):
        self.voltageCurrentData = voltageCurrentData
        self.temperature = temperature
        self.version = version
        self.profileReady = profileReady
        
    def __str__(self):
        return 'voltage and current: %s, temperature: %s, version: %s, profileReady: %s' % (self.voltageCurrentData, self.temperature, self.version, self.profileReady)

class NpmCommandGetStatus(NpmCommand):

    RESPONSE_LENGTH = 20
    ADC_FACTOR = 1
    COMMAND_CODE = 0x05    
    LOWER_CURRENT_FLAG = 0x80
    SET_FLAG = 0x10000
    #CURRENT_FACTOR = 64  #66mA/1024*1000
    CURRENT_FACTOR = 16.113  #66mA/4096*1000
    MSB_MASK = 0x7F
    
    def __init__(self, npmIndex):
        self.log = logging.getLogger(__name__)
        NpmCommand.__init__(self, npmIndex, 0, 0, 0, 0)

    def _getCommandCode(self):
        return NpmCommandGetStatus.COMMAND_CODE
    
    def _getResponseLength(self):
        return NpmCommandGetStatus.RESPONSE_LENGTH
    
    def getResult(self):
        profileReady = bool(self._response[4] & NpmCommand.STATUS_PROFILE_READY)
        voltage = 0
        current = 0
        voltage = int(NpmUtils.makeShort(self._response[7], self._response[8]) * NpmCommandGetStatus.ADC_FACTOR)
        if (self._response[10] & NpmCommandGetStatus.LOWER_CURRENT_FLAG) == 0 :
            current = int(NpmUtils.makeShort(self._response[9], self._response[10]) * NpmCommandGetStatus.ADC_FACTOR)
        else:
            tmp_current = int(NpmUtils.makeShort(self._response[9], (self._response[10] & NpmCommandGetStatus.MSB_MASK)) * NpmCommandGetStatus.ADC_FACTOR)
            current = int(tmp_current*NpmCommandGetStatus.CURRENT_FACTOR) / 1000.0
        #voltages[1] = int(NpmUtils.makeShort(self._response[11], self._response[12]) * NpmCommandGetStatus.ADC_FACTOR)
        #currents[1] = int(NpmUtils.makeShort(self._response[13], self._response[14]) * NpmCommandGetStatus.ADC_FACTOR)
        temperature = NpmUtils.makeShort(self._response[15], self._response[16])
        version = self._response[17]
        if BP_DEBUG:
            print('NPM voltage %s, current %s' % (voltage, current))

        res = dict()
        res['voltage'] = voltage
        res['current'] = current
        return res


class PowerControl():
    def __init__(self, npmIndex, uartPort):
        self._npmIndex = npmIndex
        self._npmTty = serial.Serial()
        self._npmTty.baudrate = 19200
        self._npmTty.port = uartPort
        self._npmTty.timeout = 1

        
    def setVoltage(self, voltage):
        NpmCommandSetVoltage(self._npmIndex, voltage).execute(self._npmTty)

    def getVoltageCurrent(self):
        return NpmCommandGetStatus(self._npmIndex).execute(self._npmTty).getResult()

    def SwitchU2(self):
        return NpmCommandSwitchUTwo(self._npmIndex).execute(self._npmTty)

    def SwitchSATA(self):
        return NpmCommandSwitchSATA(self._npmIndex).execute(self._npmTty)


def port_transfer(slot):
    match slot:
        case 0:
            npmIndex = 0
            uartPort = SERIAL_PORT_LIST[2]
        case 1:
            npmIndex = 1
            uartPort = SERIAL_PORT_LIST[2]
        case 2:
            npmIndex = 2
            uartPort = SERIAL_PORT_LIST[2]
        case 3:
            npmIndex = 3
            uartPort = SERIAL_PORT_LIST[2]
        case 4:
            npmIndex = 0
            uartPort = SERIAL_PORT_LIST[0]
        case 5:
            npmIndex = 1
            uartPort = SERIAL_PORT_LIST[0]
        case 6:
            npmIndex = 2
            uartPort = SERIAL_PORT_LIST[0]
        case 7:
            npmIndex = 3
            uartPort = SERIAL_PORT_LIST[0]
        case 8:
            npmIndex = 0
            uartPort = SERIAL_PORT_LIST[1]
        case 9:
            npmIndex = 1
            uartPort = SERIAL_PORT_LIST[1]
        case 10:
            npmIndex = 2
            uartPort = SERIAL_PORT_LIST[1]
        case 11:
            npmIndex = 3
            uartPort = SERIAL_PORT_LIST[1]
    return npmIndex, uartPort


def set_voltage_uart(slot, voltage):
    npmIndex, uartPort = port_transfer(slot)
    pc = PowerControl(npmIndex, uartPort)
    if voltage != None:
        pc.setVoltage(voltage)
        return True
    else:
        print("Wrong voltage settings!")
        return False

def get_voltage_current_uart(slot):
    npmIndex, uartPort = port_transfer(slot)
    pc = PowerControl(npmIndex, uartPort)
    if pc.getVoltageCurrent():
        print(pc.getVoltageCurrent())
    else: 
        return False
        

        
