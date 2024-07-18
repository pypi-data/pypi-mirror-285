import unittest
from unittest.mock import patch, MagicMock
from opsys_led_panel.led_panel_controller import LedPanelController


class Test(unittest.TestCase):
    @ classmethod
    def setUp(self):
        pass

    @ classmethod
    def setUpClass(cls):
        pass

    @ classmethod
    def tearDownClass(cls):
        pass

    @ patch.object(LedPanelController, 'connect')
    def test_connect(self, relay_mock: MagicMock):
        port = 'COM3'
        relay_conn = LedPanelController()
        relay_conn.connect(port)
        relay_mock.assert_called_once_with('COM3')

    @ patch.object(LedPanelController, 'disconnect')
    def test_disconnect(self, relay_mock: MagicMock):
        relay_conn = LedPanelController()
        relay_conn.disconnect()
        relay_mock.assert_called_once_with()

    @ patch.object(LedPanelController, 'set_program')
    def test_set_program(self, relay_mock: MagicMock):
        program_number = 1
        relay_conn = LedPanelController()
        relay_conn.set_program(program_number=program_number)
        relay_mock.assert_called_once_with(program_number=1)

    @ patch.object(LedPanelController, 'get_serial_number')
    def test_get_serial_number(self, relay_mock: MagicMock):
        relay_conn = LedPanelController()
        relay_conn.get_serial_number()
        relay_mock.assert_called_once_with()

    @ patch.object(LedPanelController, 'get_sw_version')
    def test_get_sw_version(self, relay_mock: MagicMock):
        relay_conn = LedPanelController()
        relay_conn.get_sw_version()
        relay_mock.assert_called_once_with()

    @ patch.object(LedPanelController, 'set_program_and_led_type')
    def test_set_program_and_led_type(self, relay_mock: MagicMock):
        program_number, led_type = 1, 1
        relay_conn = LedPanelController()
        relay_conn.set_program_and_led_type(program_number, led_type)
        relay_mock.assert_called_once_with(1, 1)
        
    @ patch.object(LedPanelController, 'set_startup_program')
    def test_set_startup_program(self, relay_mock: MagicMock):
        program_number = 1
        relay_conn = LedPanelController()
        relay_conn.set_startup_program(program_number=program_number)
        relay_mock.assert_called_once_with(program_number=1)
        
    @ patch.object(LedPanelController, 'set_program_name')
    def test_set_program_name(self, relay_mock: MagicMock):
        program_name = 'program1'
        relay_conn = LedPanelController()
        relay_conn.set_program_name(program_name=program_name)
        relay_mock.assert_called_once_with(program_name='program1')
        
    @ patch.object(LedPanelController, 'set_led_type')
    def test_set_led_type(self, relay_mock: MagicMock):
        led_type = 1
        relay_conn = LedPanelController()
        relay_conn.set_led_type(led_type=led_type)
        relay_mock.assert_called_once_with(led_type=1)
        
    @ patch.object(LedPanelController, 'set_led_output')
    def test_set_led_output(self, relay_mock: MagicMock):
        output_parameter = 0
        relay_conn = LedPanelController()
        relay_conn.set_led_output(output_parameter=output_parameter)
        relay_mock.assert_called_once_with(output_parameter=0)
        
    @ patch.object(LedPanelController, 'confirm_led_output')
    def test_confirm_led_output(self, relay_mock: MagicMock):
        relay_conn = LedPanelController()
        relay_conn.confirm_led_output()
        relay_mock.assert_called_once_with()
        
    @ patch.object(LedPanelController, 'set_autocal')
    def test_set_autocal(self, relay_mock: MagicMock):
        relay_conn = LedPanelController()
        relay_conn.set_autocal()
        relay_mock.assert_called_once_with()
        
    @ patch.object(LedPanelController, 'set_target_luminance')
    def test_set_target_luminance(self, relay_mock: MagicMock):
        luminance = 20
        relay_conn = LedPanelController()
        relay_conn.set_target_luminance(luminance=luminance)
        relay_mock.assert_called_once_with(luminance=20)
        


if __name__ == '__main__':
    unittest.main()
