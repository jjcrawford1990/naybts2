import csv  # For reading the master_config.csv file
from pathlib import Path
from comms import Communication  # Review how this module is dealt with (inheritance or importing etc.)

class Default:

    def __init__(self):
        ''' Open the master_config.csv and sees if super user has altered for new paths.
            This means that a password protected method can be used for future config file without changing
            any other class methods.
            Communication object is instantiated from here. '''
        path = Path(__file__).parent.absolute()  # Finds current modules path.
        master_config_file = str(path) + '\master_config.csv'  # Append master_config file
        self.__master_config_dict = dict()  # Holds Bool state of library along with file path (if bool=1)
        with open(master_config_file, encoding="utf-8-sig") as file:
            csv_open = csv.DictReader(file)
            for row in csv_open:
                self.__master_config_dict[row['type_of_config']] = (row['bool_state'], row['path'])
        # If statements which send file path if bool is set to 1, otherwise leave empty.
        self.instantiate_comms()

    def instantiate_comms(self):
        if int(self.__master_config_dict['register_map'][0]) == 1 and int(self.__master_config_dict['serial_config'][0]) == 1:
            self.a = Communication(register_map = self.__master_config_dict['register_map'][1], 
                          serial_config = self.__master_config_dict['serial_config'][1])
        elif int(self.__master_config_dict['register_map'][0]) == 1:
            self.a = Communication(register_map = self.__master_config_dict['register_map'][1])
        elif int(self.__master_config_dict['serial_config'][0]) == 1:
            self.a = Communication(serial_config = self.__master_config_dict['serial_config'][1])
        else:
            self.a = Communication()  # Pass no arguments