import unittest
from unittest.mock import patch, MagicMock
from opsys_eol_ps.eol_ps import EolPs

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


    @ patch.object(EolPs, 'convert_atod_current')
    def test_convert_atod_current(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.convert_atod_current()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'convert_atod_volts')
    def test_convert_atod_volts(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.convert_atod_volts()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'convert_dtoa_current')
    def test_convert_dtoa_current(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.convert_dtoa_current()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'convert_dtoa_volts')
    def test_convert_dtoa_volts(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.convert_dtoa_volts()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'get_current')
    def test_get_current(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.get_current()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'get_current_monitor')
    def test_get_current_monitor(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.get_current_monitor()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'get_output_state')
    def test_get_output_state(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.get_output_state()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'get_upper_volt_lim')
    def test_get_upper_volt_lim(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.get_upper_volt_lim()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'get_volt')
    def test_get_volt(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.get_volt()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'get_volt_monitor')
    def test_get_volt_monitor(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.get_volt_monitor()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'init_modbus_conn')
    def test_init_modbus_conn(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.init_modbus_conn()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'is_alarm_active')
    def test_is_alarm_active(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.is_alarm_active()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'read_holding_reg')
    def test_read_holding_reg(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.read_holding_reg()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'read_input_reg')
    def test_read_input_reg(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.read_input_reg()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'read_reg')
    def test_read_reg(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.read_reg()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'set_current') 
    def test_set_current(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.set_current()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'set_output_state')
    def test_set_output_state(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.set_output_state()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'set_upper_volt_lim')
    def test_set_upper_volt_lim(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.set_upper_volt_lim()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'set_volt')
    def test_set_volt(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.set_volt()
        ps_mock.assert_called_once_with()

    @ patch.object(EolPs, 'write_holding_reg')
    def test_write_holding_reg(self, ps_mock: MagicMock):
        ps = EolPs()
        ps.write_holding_reg()
        ps_mock.assert_called_once_with()
if __name__ == '__main__':
    unittest.main()
