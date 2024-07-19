# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 10:19:09 2023

@author: Yerke
"""

import serial
import struct
import os

class GalileoFlowSDK:
    """Galileo is a class that allows the user to communicate with Galileo Flow Sensors

    Parameters
    ----------
    comport_name: Comport Number of the Galileo Flows Sensor. Example: 'COM13'

    Attributes
    ----------
    
    Methods
    -------
    connect()
        Connects the serial port of the Galileo Flow Sensor.
    update_snc(snc)
        Update the serial number of the Cartridge.  
    update_liquid(liquid_type)
        Updates the liquid type for proper viscosity estimation
    """
    def __init__(self, comport_name):
        self.__PIECEWISE = 129
        self.__SINGLE    = 128
        
        self.__MESSAGE_TOKEN            = 0x23
        self.__WRITE_REQUEST            = 0x57
        self.__READ_REQUEST             = 0x52
        self.__CHANGE_BANK_REQUEST      = 0x43
        self.__BOOT_UPDATE_REQUEST      = 0x42

        self.__BOOT_ACK                 = 0x5f
        self.__BOOT_NACK                = 0xaa
        
        self.__comport_name = comport_name # comport_number
        self.__registers = {'FLOW' : 6, 'STATE' : 9, 'CLOGGING' : 8, 'SNC' : 12,  'LIQUID': 14}
        self.__clogging = {0: 'No Clogging', 1 : 'Clogging', 2 : 'Partial Clogging'}
        self.__liquids ={0:'WATER', 1: 'IP', 2: 'DMEM', 3: 'ETHANOL'}
        self.__states = {0:'HALT', 1:'CARTRIDGE DISCONNECTION DETECT', 2:'CARTRIDGE DETECT', 3:'CARTRIDGE INITIALIZATION'\
                         , 4:'FLOW MEASUREMENT', 5 : 'CALIBRATION REQUEST', 6:'COMMUNCATION ERROR'}
        self.__connect()
        if self.__read_reg(self.__registers["STATE"]) != 'FLOW MEASUREMENT':
            raise Exception('Verify that the cartridge is connected to the Galileo')
            

    def __connect(self):
        """Connects the serial port of the Galileo Flow Sensor.  
        
        If the specified comport does not exst, it thows an error
        
        Args:
            none
        """
        
        self.serial_com = serial.Serial(port = self.__comport_name,baudrate = 115200, timeout = 1)
        command_message = [self.__MESSAGE_TOKEN, self.__READ_REQUEST, 12]
        self.serial_com.write(bytearray(command_message))
        self.serial_com.read(4)
        #self.read_flow()
        # try:
        #     self.serial_com = serial.Serial(port = self.__comport_name,baudrate = 115200, timeout = 10)
        # except:
        #     print('cannot open the serial port.: ',  self.__comport_name, '. Check the cables and the port number')

    def __read_reg(self, reg_number):
        """Reads the specified registers
        
        This method allows the user to read a register of the Galieo Flow sensor:
        'FLOW' : 6, 'CLOGGING' : 8, 'STATE' : 9, 'SNC' : 12, 
        In addition, this method does not
        necessarily require delay when readings the registers.

        Args:
            reg_number: the register number to be read. Possible values:
            
        """
        command_message = [self.__MESSAGE_TOKEN, self.__READ_REQUEST, 0]
        if reg_number in self.__registers.values():
            command_message[2] = reg_number
            self.serial_com.write(bytearray(command_message))
            # clogging:
            if reg_number == self.__registers['CLOGGING']:
                message_in = self.serial_com.read(1)
                raw_data = struct.unpack('<B', message_in)[0]
                return self.__clogging[raw_data]
            #state:
            elif reg_number == self.__registers['STATE']:
                message_in = self.serial_com.read(1)
                raw_data = struct.unpack('<B', message_in)[0]
                return self.__states[raw_data]
            
            elif reg_number == self.__registers['SNC']:
                message_in = self.serial_com.read(4)
                raw_data = struct.unpack('<I', message_in)[0]
                return raw_data
            # liquid type
            elif reg_number == self.__registers['LIQUID']:
                message_in = self.serial_com.read(4)
                raw_data = struct.unpack('<I', message_in)[0]
                return self.__liquids[raw_data]
            # flow
            elif reg_number == self.__registers['FLOW']:
                message_in = self.serial_com.read(4)
                raw_data = struct.unpack('<f', message_in)[0]
                return raw_data
            else:
                return 0
        else:
            raise Exception("Enter a proper register")
        
    def read_flow(self):
        """Read the flow rate [ul / min]
        
        Read the flow rate computed by the Galileo Flow Sensor
        
        Args:
            None
        """
        return self.__read_reg(self.__registers['FLOW'])
    def read_serial_number(self):
        """Read the cartridge serial number
        
        This method returns the serial number of the cartridge
        
        Args:
            None
        """
        return self.__read_reg(self.__registers['SNC'])
    def read_liquid(self):
        """read the liquid.  
        
        This method returns the liquid type set in the sensor
        
        Args:
            None
        """
        return self.__read_reg(self.__registers['LIQUID'])
    
    def check_clogging(self):
        """Check the clogging
        
        This method is necessary to check the clogging statu of the cartridge
        
        Args:
            none
        """
        return self.__read_reg(self.__registers['CLOGGING'])

    def update_liquid(self, liquid_type):
        """Update the liquid type of the sensor.  
        
        This function the liquid type of the sensor
        
        Args:
            liquid_type: the liquid flowing through the sensor (0: water, 1:ip, 2:dmem, 3:ethanol)
        """
        if liquid_type >3:
            raise Exception("Liquid type does not exist")
        command_message = [self.__MESSAGE_TOKEN, self.__WRITE_REQUEST, self.__registers['LIQUID'], liquid_type]
        b = bytes()
        b = b.join((struct.pack('<'+format, val) for format,val in zip('BBBI',command_message)))
        self.serial_com.write(b)
    
    def disconnect(self):
        """Disconnect from the sensor  
        
        This method is nedded to disconnect from the sensor
        
        Args:
            None
        """
        self.serial_com.close()

    def __compute_crc(self, buff, length):
        crc = 0xFFFFFFFF
        #print(length)
        for byte in buff[0:length]:
            crc = crc ^ (byte)
            for i in range(32):
                if(crc & 0x80000000):
                    crc = (crc << 1) ^ 0x04C11DB7
                else:
                    crc = (crc << 1)
        return crc &  0xFFFFFFFF

    def update_firmware(self, file_name):
        """Update the firmware  
        
        This method is necessary to update the firmware of the sensor
        
        Args:
            file_name: path to the binary file
        """
        WINDOW_SIZE  = 128
        try:
            flash_bin_file = open(file_name, 'rb')
        except:
            Exception('cannot open the bin file')
        size = os.path.getsize(file_name)
        data_sent = [self.__MESSAGE_TOKEN, self.__BOOT_UPDATE_REQUEST, size]
        b = bytes()
        b = b.join((struct.pack('<'+format, val) for format,val in zip('BBI',data_sent)))
        self.serial_com.write(b)
        size_copy = size
        while size > 0 and self.__read_boot_reply() == self.__BOOT_ACK:
            data_sent = flash_bin_file.read(WINDOW_SIZE)
            size = size - len(data_sent)
            data_sent = data_sent + (struct.pack('<I',self.__compute_crc(data_sent, WINDOW_SIZE)))
            self.serial_com.write(data_sent)
            print('Firmware update ' + str(int(100 * (size_copy - size)/size_copy)) +' %' +': ' + int(50 * (size_copy - size)/size_copy) * '#', end = '\r')
            
        if self.__read_boot_reply() != self.__BOOT_ACK or size > 0:
            print("flash update failed")
            Exception("flash update failed")
        else:
            print('Firmware update ' + str(int(100 * (size_copy - size)/size_copy)) +' %' +': ' + int(20 * (size_copy - size)/size_copy) * '#')
            print('Firmware update is over')

    def __read_boot_reply(self):
        ack_value = self.serial_com.read(1)
        if len(ack_value) > 0 and ack_value[0] == self.__BOOT_ACK:
            return self.__BOOT_ACK
        else:
            return self.__BOOT_NACK