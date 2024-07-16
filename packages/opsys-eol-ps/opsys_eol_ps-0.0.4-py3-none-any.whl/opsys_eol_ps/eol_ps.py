"""
API for reading power supply parameters via MODBUS-RTU.

This module provides a Python interface for interacting with a power supply device using MODBUS-RTU protocol.
It includes methods for initializing the MODBUS connection, reading and writing registers, as well as specific methods
for retrieving and setting various power supply parameters such as output state, voltage limit, current limit, etc.

Requirements:
- minimalmodbus library (install via pip: pip install minimalmodbus)

Usage Example:
    import opsys_eol_ps

    # Initialize power supply object with COM port number
    ps = opsys_eol_ps.EolPs()
    ps.init_modbus_conn(com_num=1)


    # Read voltage limit
    voltage_limit = ps.get_volt_limit()

    # Set voltage limit to 5 volts
    ps.set_volt_limit(5.0)

    # Check if alarm is active
    alarm_active = ps.is_alarm_active()

"""
import minimalmodbus

# GLOBAL VARIABLES


#################
# MODBUS METHODS
#################
class EolPs():
    """
    Class representing a power supply device with MODBUS-RTU communication protocol.
    """
    def __init__(self):
        """
        Initialize the EolPs object.

        """
        self.PS_UNIT_ID = 1
        self.MODBUS_CONN = None
        # self.init_modbus_conn(com_num)

    def init_modbus_conn(self, com_num=4, close_port_after_each_call=True):
        """
        Initialize the MODBUS connection.

        Args:
            com_num (int, optional): COM port number to establish the MODBUS connection.
                                     Defaults to None.
            close_port_after_each_call (bool, optional): close automatically each time
                                     command is sent to the interface. Defaults to True.
        """
        try:
            self.MODBUS_CONN = minimalmodbus.Instrument("COM" + str(com_num), self.PS_UNIT_ID)
            self.MODBUS_CONN.serial.parity = 'E'
            self.MODBUS_CONN.close_port_after_each_call = close_port_after_each_call
        except:
            raise

    def read_reg(self, reg_adr, func_code):
        """
        Read a register from the power supply device.

        Args:
            reg_adr (int): Register address to read from.
            func_code (int): Function code for MODBUS read operation.

        Returns:
            int: Value read from the register.
        """
        try:
            return self.MODBUS_CONN.read_register(registeraddress = reg_adr, number_of_decimals = 0, functioncode = func_code, signed = False)
        except:
            raise

    def read_input_reg(self, reg_adr):
        """
        Read from an input register of the power supply device.

        Args:
            reg_adr (int): Register address to read from.

        Returns:
            int: Value read from the input register.
        """
        input_func_code = 4
        try:
            return self.read_reg(reg_adr, input_func_code)
        except:
            raise

    def read_holding_reg(self, reg_adr):
        """
        Read from a holding register of the power supply device.

        Args:
            reg_adr (int): Register address to read from.

        Returns:
            int: Value read from the holding register.
        """
        holding_func_code = 3
        try:
            return self.read_reg(reg_adr, holding_func_code)
        except:
            raise

    def write_holding_reg(self, reg_adr, value):
        """
        Write to a holding register of the power supply device.

        Args:
            reg_adr (int): Register address to write to.
            value (int): Value to write to the register.
        """
        try:
            self.MODBUS_CONN.write_register(registeraddress = reg_adr, value = value, number_of_decimals = 0, functioncode = 6, signed = False)
        except:
            raise

    #####################
    # PS SPECIFIC METHODS
    #####################

    def get_output_state(self, ):
        """
        Get the output state of the power supply device.

        Returns:
            bool: True if output is active, False otherwise.
        """
        return self.read_holding_reg(0) != 0

    def set_output_state(self, mode):
        """
        Set the output state of the power supply device.

        Args:
            mode (bool): Desired state of the output (True for ON, False for OFF).
        """
        value = 0
        if(mode):
            value = 1
        self.write_holding_reg(0, value)

    def get_volt(self, ):
        """
        Get the voltage output set on the power supply device.

        Returns:
            float: Voltage limit in volts.
        """
        value = self.read_holding_reg(103)
        return self.convert_dtoa_volts(value)

    def set_volt(self, volts):
        """
        Set the voltage on the power supply device.

        Args:
            volts (float): Desired voltage limit in volts, limited to 12[V].
        """
        value = 13
        if (volts <= value):
            value = volts
        self.write_holding_reg(103, self.convert_atod_volts(value))

    def get_volt_monitor(self, ):
        """
        Get the monitored voltage from the power supply device.

        Returns:
            float: Monitored voltage in volts.
        """
        value = self.read_input_reg(1)
        return self.convert_dtoa_volts(value)

    def get_current(self, ):
        """
        Get the curren set on the power supply device.

        Returns:
            float: Current limit in amps.
        """
        value = self.read_holding_reg(104)
        return self.convert_dtoa_current(value)

    def set_current(self, current):
        """
        Set the current on the power supply device.

        Args:
            current (float): Desired current limit in amps.
        """
        self.write_holding_reg(104, self.convert_atod_current(current))

    def get_current_monitor(self, ):
        """
        Get the monitored current from the power supply device.

        Returns:
            float: Monitored current in amps.
        """
        value = self.read_input_reg(2)
        return self.convert_dtoa_current(value)

    def get_upper_volt_lim(self, ):
        """
        Get the upper voltage limit set on the power supply device.

        Returns:
            float: Upper voltage limit in volts.
        """        
        value = self.read_holding_reg(105)
        return self.convert_dtoa_volts(value)

    def set_upper_volt_lim(self, volts):
        """
        Set the upper voltage limit on the power supply device.

        Args:
            volts (float): Desired upper voltage limit in volts.
        """
        self.write_holding_reg(105, self.convert_atod_volts(volts))

    # Alarm history is reset when turning output ON
    def is_alarm_active(self, ):
        """
        Check if there is an active alarm on the power supply device.

        Returns:
            bool: True if an alarm is active, False otherwise.
        """
        return self.read_input_reg(0) != 0

    #################
    # UTILITY METHODS
    #################

    # Input is 0-1024 scale, output is 0-24V
    def convert_dtoa_volts(self, d_volts):
        return round((d_volts*24)/1024,2)

    # Input is 0-24V scale, output is 0-1024
    def convert_atod_volts(self, a_volts):
        return round((a_volts*1024)/24,2)

    # Input is 0-1024 scale, output is 0-12A
    def convert_dtoa_current(self, d_amp):
        return round((d_amp*25)/1024,2)

    # Input is 0-12A scale, output is 0-1024
    def convert_atod_current(self, a_amp):
        return round((a_amp*1024)/25,2)
