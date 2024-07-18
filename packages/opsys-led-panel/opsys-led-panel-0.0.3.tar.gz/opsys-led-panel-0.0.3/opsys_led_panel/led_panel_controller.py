import time
import serial
from serial import SerialException
from .led_panel_abstract import LedPanelAbstract

# avoild COMs detection at deployment
try:
    from serial.tools.list_ports import comports
except Exception as e:
    print(e)


class LedPanelController(LedPanelAbstract):
    """
    USB LED Panel controller
    """
    __buffer_delimiter = '\r'

    def __init__(self, conn_timeout=15, delay_time = 0.3, baudrate = 9600):
        """
        Initialize parameters

        Args:
            conn_timeout (int, optional): serial connection timeout. Defaults to 15.
            delay_time (float, optional): serial connection delay in sec. Defaults to 0.3.
            baudrate (int, optional): COM port baudrate. Defaults to 9600.
        """
        self.conn_timeout = conn_timeout
        self.delay_time = 0.3
        self.baudrate = 9600
        
    def read_buffer(self):
        """
        Read buffer output

        Returns:
            list: buffer response bytes
        """
        output = b""  # init binary string
        start_time = time.time()

        while True:  # read from buffer
            output += self.conn.read()

            if r'\r' in str(output):
                break
            # stop on timeout
            if (time.time() - start_time) >= self.conn_timeout:
                raise SerialException('Connection timeout!')

        return output.decode('ascii').rstrip('\r').split(',')
    
    def get_cmd_response(self):
        """
        Read sent command response

        Returns:
            str: command response
        """
        response = self.read_buffer()
        self.conn.flush()  # flush output
        
        if response[0] == 'ER1':
            print(f'Error reading response from buffer!')
            return response[0]

        elif response[0] == 'OK':
            return response[1:]
    
    def send_command(self, command):
        """
        Send command to device

        Args:
            command (str): command to send
                           to device
                           
        Returns:
            str: command response
        """
        command += self.__buffer_delimiter
        
        try:
            self.conn.write(command.encode('ascii'))
            return self.get_cmd_response()
        except:
            print(f'Failed to send command: {command}')
            return 'Error'

    def connect(self, com_port=None):
        """
        Connect to led panel

        Args:
            com_port (str, optional): Serial port name.
                                      Defaults to None.
                   
        Returns:
            None
        """
        if com_port is not None:
            self.conn = serial.Serial(com_port, self.baudrate)
            self.conn.timeout = self.delay_time
            return
        else:  # no com port provided
            for com, _, _ in sorted(comports()):
                self.conn = serial.Serial(com, self.baudrate)
                self.conn.timeout = self.delay_time
                # try to receive valid data from buffer
                if self.get_serial_number() != 'Error':
                    return

        raise SerialException("No valid COM port found")

    def disconnect(self):
        """
        Disconnect from LED panel
        """
        self.conn.close()
        
    def set_program(self, program_number=1):
        """
        Set program to LED panel

        Args:
            program_number (int, optional): program number.
                                            Defaults to 1. 
        """
        self.send_command(command=f'P,{program_number}')
        print(f'Set program to P{program_number} done')
        
    def get_serial_number(self):
        """
        Get device serial number
        
        Returns:
            str: device SN
        """
        response = self.send_command(command='RSNO')
        return response[0] if response != 'Error' else 'Error'
    
    def get_sw_version(self):
        """
        Get device SW version
        """
        response = self.send_command(command='VER')
        return response[0] if response != 'Error' else 'Error'
    
    def get_model(self):
        """
        Get device model
        """
        response = self.send_command(command='VER')
        return response[1] if response != 'Error' else 'Error'
    
    def set_program_and_led_type(self, program_number=1, led_type=1):
        """
        Set program and LED type

        Args:
            program_number (int, optional): program number.
                                            Defaults to 1.
            led_type (int, optional): LED type.
                                      Defaults to 1.
        """
        self.send_command(command=f'PL,{program_number},{led_type}')
        print(f'Set startup program to P{program_number} and LED type to {led_type} done')
    
    def set_startup_program(self, program_number=1):
        """
        Set startup program

        Args:
            program_number (int, optional): program number.
                                            Defaults to 1.
        """
        self.send_command(command=f'SPG,{program_number}')
        print(f'Set startup program to P{program_number} done')
    
    def set_program_name(self, program_name):
        """
        Set program name

        Args:
            program_name (str): program name
        """
        self.send_command(command=f'SNAME,{program_name}')
        print(f'Set program name to {program_name} done')
    
    def set_led_type(self, led_type=1):
        """
        Set LED type

        Args:
            led_type (int, optional): LED type.
                                      Defaults to 1.
        """
        self.send_command(command=f'SLT,{led_type}')
        print(f'Set LED type to {led_type} done')
    
    def set_led_output(self, output_parameter):
        """
        Set LED output parameter

        Args:
            output_parameter (int): 0~4095
        """
        self.send_command(command=f'SV,{output_parameter}')
        print(f'Confirm LED output to {output_parameter} done')
        
    def confirm_led_output(self):
        """
        LED output parameter confirmation
        """
        self.send_command(command='RV')
        print('Confirm LED output done')
    
    def set_autocal(self):
        """
        Set AUTOCAL
        """
        self.send_command(command='AC')
        print('Set AUTOCAL done')
    
    def set_target_luminance(self, luminance):
        """
        Set target luminance in AUTOCAL execution

        Args:
            luminance (int): luminance value.
                             Accepted in range 0.0000~30000(cd/m2).
        """
        self.send_command(command=f'SBV,{luminance}')
        print(f'Set target luminance to {luminance} done')
