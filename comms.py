import serial
import minimalmodbus
import csv  # For reading the register map .csv file.
import sys

default_register_map_file = r"C:\Users\Josh\Desktop\Work\BTS\registermap.csv"
default_serial_configuration = r"C:\Users\Josh\Desktop\Work\BTS\serialconfig.csv"

class Communication:
    '''Class serves following functions:
    - Implement methods for functionality of each register.
    - Carry out status requests at the defined interval or when requested.
    - Take responses from devices and pass on to Viewer and Graphing module. '''

    def __init__(self, **kwargs):
        ''' Creates the device dictionary of instrument objects to be associated with this instance of the Communication class.

            Populates the register map and serial configuration for this object either based
            on default files, or if provided as keyword arguments, the provided map/config files. '''
        self.__device_dict = dict()
        self.dude = 'Dummy'
        # If the optional arguments for register_map or serial_config file paths are provided.
        if 'register_map' in kwargs:
            self._open_register_map_file(kwargs['register_map'])
        else:
            self._open_register_map_file(default_register_map_file)
        if 'serial_config' in kwargs:
            self._open_serial_config_file(kwargs['serial_config'])
        else:
            self._open_serial_config_file(default_serial_configuration)
            
    def add_device(self, car_no, slave_addr, com_port):
        '''Method to create a new instrument object (adding a new Industruino)
        to communicate with. This is added to the device dictionary. '''
        self.__device_dict[car_no] = minimalmodbus.Instrument(com_port, slave_addr, minimalmodbus.MODE_RTU, close_port_after_each_call=True)
        self.__device_dict[car_no].serial.baudrate = self.__serial_config_dict['baudrate']
        self.__device_dict[car_no].serial.stopbits = self.__serial_config_dict['stop_bits']
        self.__device_dict[car_no].serial.timeout = self.__serial_config_dict['timeout']

    def _open_register_map_file(self, register_map_file):
        ''' Takes the register map .csv, parses and enters into the register dictionary.
            this dictionary has the name of the register as the key and register no. as value.
            This allows the register map to be rearranged or appended and the register can still be identified
            by its name e.g. PB_RVAL as opposed to the register number. '''
        self.__register_dict = dict()  # Dict of register names and associated register number
        self.__register_groups_dict = dict()  # Dict of register names and which group they belong to
        with open(register_map_file, encoding="utf-8-sig") as file:
            rows = csv.DictReader(file)
            for row in rows:
                self.__register_dict[row['name']] = int(row['regno'])
                if row['group'] in self.__register_groups_dict:
                    self.__register_groups_dict[row['group']].append(row['name'])  # Need way of appending, not overwriting value.
                else:
                    self.__register_groups_dict[row['group']] = [row['name']]

    def _open_serial_config_file(self, serial_config_file):
        ''' Takes the serial configuration .csv and enters into the serial config dictionary.
            These values are used when creating each new serial object.
            Also allows for potential in future for differing baudrate based on priority by different Communication objects. '''
        self._serial_config_dict = dict()
        with open(serial_config_file, encoding="utf-8-sig") as file:
            rows = csv.DictReader(file)
            for row in rows:
                self._serial_config_dict['baudrate'] = int(row['baudrate'])
                self._serial_config_dict['no_bits'] = int(row['no_bits'])
                self._serial_config_dict['parity'] = row['parity']
                self._serial_config_dict['stop_bits'] = int(row['stop_bits'])
                self._serial_config_dict['timeout'] = float(row['timeout'])

    def data_request(self, car_no, register_name):
        '''Public method to allow for Viewer/periodic checker to request specific data from a/many end devices.
        Takes the register name and then finds the correct register no for reading. '''
        register_no = self.__register_dict[register_name]
        device = self.__device_dict[car_no]
        data = self.__read_holding_reg(register_no, device)
        value_read = self.__message_parse(data, register_name)
        return value_read

    def __read_holding_reg(self, register, device):
        ''' Send a register request to interrogate Industruino device.
            Can also be used in a 'Maintenance mode' as a way of interrogating
            the devices with specific binary messages. '''
        data = device.read_register(register, 0)
        return data

    def __message_parse(self, data, register_name):
        ''' Parse the message received after reading a register.
            Future parse can be added with this method by simply adding an elif statement. '''
        for group, names in self.__register_groups_dict.items():
            for name in names:
                if register_name == name:
                    member_group = group
        # Takes the integer value from device and splits to hi/lo byte and then into float.
        if member_group == 'sval' or member_group == 'rval':
            if data > 255:  # 3Chars or more
                hi_byte = (hex(data)[2:-2])  # Slice data into a hex based on first byte
                hi_byte = int(hi_byte, 16)  # Turn hex string into int, 2 nd arg is base of 16
                lo_byte = (hex(data)[-2:])  # Slice data for last 2 chars
                lo_byte = int(lo_byte, 16)
            elif data < 255 and data > 0:  # 2 Chars or less
                hi_byte = 0
                lo_byte = (hex(data)[2:])  # Read either 1 or 2 chars after '0x'
                lo_byte = int(lo_byte, 16)
            value_read = hi_byte + (lo_byte/100)
        return value_read

    def data_set(self, car_no, register_name, setting_value):
        ''' Public method to allow for Viewer to set holding register of a/many end devices. '''
        register_no = self.__register_dict[register_name]
        device = self.__device_dict[car_no]
        write_success = self.__set_holding_reg(register_no, device, setting_value)
        if write_success == False:
            pass  # Display something to indicate nonresponse. To be implemented later.

    def __set_holding_reg(self, register_no, device, setting_value):
        ''' Send message for setting a holding register value. '''
        try:
            device.write_register(register_no, setting_value, 0)  # Final parameter must be 0 (dp) or sends float and nothing works!
            return True
        except:
            return False



''' Class shall be instantiated through creation of object.
    Once created the object shall have only 1 public attribute, which is a list
    of all available COM ports. 
    No public interface methods are required as initialisation runs method to find ports.'''

class ComPorts:
    ''' Class serves to find all COM ports for any which are available.
    This is for the RS485 transceiver which is used for MODBUS communications.'''

    def __init__(self):
        """ Creates empty list for assigning ports.
        raises EnvironmentError if not on Windows platform. """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        else:
            raise EnvironmentError('Unsupported platform')
        self.__available_ports = self.find_ports(ports)  # Returns list of available COM ports.
    
    def find_ports(self, ports):
        ''' Tries to open all COM ports and create Serial object.
            If not possible the exception is caught, otherwise, the 
            port is added to a list, which is returned. '''
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

#cheeky = Communication()  # Pass the device upon which the communication shall be with.
#cheeky.add_device(1,2,'COM5')
#cheeky.data_set(1,'BC_SVAL',65534)  # 2583 equates to 10.23bar for testing.
#print(cheeky.data_request(1, 'BC_SVAL'))