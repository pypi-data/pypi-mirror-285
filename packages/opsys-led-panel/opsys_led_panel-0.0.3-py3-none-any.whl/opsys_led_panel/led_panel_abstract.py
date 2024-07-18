from abc import ABC, abstractmethod


class LedPanelAbstract(ABC):
    """ ########################################################### Basic ####################################################### """

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def set_program(self, program_number: int):
        pass
    
    @abstractmethod
    def get_serial_number(self):
        pass
    
    @abstractmethod
    def get_sw_version(self):
        pass
    
    @abstractmethod
    def set_program_and_led_type(self, program_number: int, led_type: int):
        pass
    
    """ ##################################################### Parameter setting ################################################# """
    
    @abstractmethod
    def set_startup_program(self, program_number: int):
        pass
    
    @abstractmethod
    def set_program_name(self, program_name: str):
        pass
    
    @abstractmethod
    def set_led_type(self, led_type: int):
        pass
    
    @abstractmethod
    def set_led_output(self, output_parameter: int):
        pass
    
    @abstractmethod
    def confirm_led_output(self):
        pass
    
    """ ########################################################### Autocal ##################################################### """
    
    @abstractmethod
    def set_autocal(self):
        pass
    
    @abstractmethod
    def set_target_luminance(self, luminance: int):
        pass
