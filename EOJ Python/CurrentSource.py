import datetime
import logging
import serial
import time


class Arroyo485_02_15():
    '''
    DEVELOPED BY M.WAJAHAT RAHEEL 14/03/2024
    the class is also used with Arroyo Model : 485 Series LaserPak
    the Manual and part can be found @
    https://www.arroyoinstruments.com/product-category/oem-products/485-series-laserpak-oem-products/


    Functions :
    1) connectArroyo(comport:str,baudrate:str)
    2) arroyoLaserStatus()
    3) arroyoLaserON(laser_parameters:dict)
    4) def arroyoLaserOFF()
    5) closeArroyoPort()

    output parm
    1) self.device_connected
    2) self.arroyo_ld_on
    3) self.arroyo_ld_measured_current
    4) self.arroyo_ld_measured_electrical_power
    5)self.arroyo_interlock
    '''

    arroyo_communication_dealy = 0.2  # Constant delay for communication [seconds]

    def __init__(self, logger=None):

        # Param initilization
        super().__init__()
        self.device_connected = 0
        self.arroyo_ld_on = 0
        self.arroyo_ld_measured_current = 0
        self.arroyo_ld_electrical_power = 0
        if logger == None:
            self.logger = logging
        else:
            self.logger = logger

    def connectArroyo(self, comport: str, baudrate: str, ):
        '''
        IT CONNECTS THE ARROYO: OPEN COMPORT FOR ARROYO:
        ARROYO BAUDRATE = 115200
        '''
        baud = int(baudrate)
        try:
            start_state = 'ERRSTR?' + '\r' + '\n'
            start_state_encode = start_state.encode()
            self.arroyo_serial = serial.Serial(port=comport, baudrate=baud, timeout=0.1)
            self.arroyo_serial.write(start_state_encode)
            self.arroyoComDelay()
            connect_string_message = self.__receiveArroyoMsg()
            if not connect_string_message:
                self.device_connected = 0
                raise Exception
                # logging.error('Error : Arroyo Comport not opened : connectArroyo')
        except Exception:
            logging.error('Error : Arroyo Comport not opened: connectArroyo')

    def arroyoComDelay(self):
        time.sleep(Arroyo485_02_15.arroyo_communication_dealy)

    def __condition_register_decoded(self, condition_register: str):
        '''
        this function converts the hex number coming from command COND? which checks the condition of laser.
        this converts the hex into 16 bit binary array. based on these bits, the error command is decoded.
        SEE Laser Condition Status Register LASer:COND? IN USER MANUAL
        :param condition_register:
        :return: laser_condition
        '''
        try:

            if condition_register == '':
                int_cond_register = -1
            else:
                int_cond_register = int(condition_register)
            if int_cond_register < 0 or int_cond_register > 65535:
                logging.error(" Error : Invalid Message from Arroyo .Check Communication")
                laser_condition = -1  # in case of invalid condition register
            else:
                hex_string = condition_register
                # Convert the hexadecimal string to an integer using the base 16
                hex_integer = int(hex_string, 16)
                binary_string = bin(hex_integer)
                # Remove the '0b' prefix from the binary string
                binary_string = binary_string[2:]
                '''SEE USER MANUAL FOR CONDITION REGISTER 'COND?' command.'''
                full_binary_string = binary_string.zfill(16)  # SEE USER MANUAL FOR CONDITION REGISTER 'COND?' command.

                # ===============================================NOT USED==============================================
                condition_register_dictionary = {'1': 'Thermal Trip', '2': 'T Limit', '3': 'R Limit', '6': 'Output On',
                                                 '7'
                                                 : 'Laser Out of Tolerance', '8': 'Laser Output Short',
                                                 '9': 'Laser Open Circuit', '12': 'Laser Interlock', '13'
                                                 : 'PD Power Limit', '14': 'PD Current Limit', '15': 'Voltage Limit',
                                                 '16': 'Current Limit'}
                # ===================================================================================================

                one_index_in_binary = [pos for pos, char in enumerate(full_binary_string) if char == '1']
                one_index_in_binary = [x + 1 for x in one_index_in_binary]
                laser_condition = ''
                if 6 in one_index_in_binary:
                    laser_condition = 'Laser On'
                if 12 in one_index_in_binary:
                    laser_condition = 'Laser Interlock OFF'
                    self.interlock = False
                if 6 not in one_index_in_binary and 12 not in one_index_in_binary:
                    laser_condition = 'Error, Check Laser Diode'
        except:
            logging.error('Error : Arroyo Com Failure : __condition_register_decoded')

        return laser_condition

    def closeArroyoPort(self):

        '''
        CLOSES THE COMPORT OF ARROYO
        :return: NONE
        '''
        self.arroyo_serial.reset_input_buffer()
        try:
            self.arroyo_serial.close()
            self.device_connected = 0
        except serial.SerialException:
            logging.error('Error : Arroyo ComPort not closed')

    def __receiveArroyoMsg(self):
        '''
        FUNCTION TYPE = PRIVATE
        FUNCTION RETURNS THE MESSAGE FROM ARROYO SUPPLY: THE MESSAGE DOES NOT INCLUDE CARRIGE RETURN OR LINE FEEED
        RETURN VALUE IS IN STR FORM
        '''
        try:
            raw_data = self.arroyo_serial.readline(1024).decode()
            if raw_data != '':
                self.device_connected = 1
                split_raw_data = raw_data.split("\r")
                return split_raw_data[0]
            if not raw_data:
                self.device_connected = 0
                raise Exception
        except Exception:
            logging.error("Error No Receive Message : receiveArroyoMsg")

    def arroyoLaserStatus(self):

        """
        Keep Checking the laser Interlock and laser parameters
        :return: arroyo_ld_on, ld current and ld electrical power
        """
        try:

            if self.device_connected == 1:
                while 1:
                    self.messageToArroyo(
                        'LASer:COND?')  # Returns the laser condition register. ( see arroyo Manual for Details)
                    self.arroyoComDelay()
                    arroyo_status = self.__receiveArroyoMsg()
                    first_try_status = arroyo_status
                    decoded_cond_message = self.__condition_register_decoded(
                        arroyo_status)  # decoding condition register of arroyo

                    if arroyo_status == '1024':  # 1024 value for stable connection and loop breaks
                        self.arroyo_ld_on = 1
                        self.messageToArroyo('LASer:LDI?')  # measure actual laser current when on
                        current: str = self.__receiveArroyoMsg()
                        self.arroyo_ld_measured_current: float = float(current)
                        self.messageToArroyo('LASer:LDV?')
                        voltage: str = self.__receiveArroyoMsg()

                        float_volt = float(voltage)
                        power = float_volt * self.arroyo_ld_measured_current
                        self.arroyo_ld_electrical_power = power / 1000
                        self.arroyo_ld_electrical_power = float("{:.3f}".format(self.arroyo_ld_electrical_power))
                        break
                    if not arroyo_status:
                        logging.error("Error arroyoLaser Comm Error : arroyoLaserStatus")
                        break
                    if arroyo_status == '0':
                        self.arroyo_ld_on = 0
                        self.arroyo_ld_measured_current = 0
                        self.arroyo_ld_voltage = 0
                        self.arroyo_ld_electrical_power = 0
                        break
                    if first_try_status == arroyo_status:
                        self.arroyo_ld_on = 0
                        self.arroyo_ld_measured_current = 0
                        self.arroyo_ld_electrical_power = 0
                        logging.error(decoded_cond_message)
                        break
            if self.device_connected == 0:
                self.arroyo_ld_on = 0
                self.arroyo_ld_measured_current = 0
                self.arroyo_ld_voltage = 0
        except:
            Exception

    def messageToArroyo(self, message_to_arroyo: str):
        '''
        SENDS MESSAGE TO ARROYO
        :param message_to_arroyo: string message to be send to arroyo
        :return: NONE
        '''
        self.arroyo_serial.flushOutput()
        self.arroyo_serial.flushInput()
        message_to_arroyo = message_to_arroyo + '\r' + '\n'
        encoded_message_to_arroyo = message_to_arroyo.encode()
        self.arroyo_serial.write(encoded_message_to_arroyo)
        self.arroyoComDelay()

    def arroyoLaserON(self, laser_parameters: dict):
        '''
        TURNS ON THE LASER DIODE
        :param laser_parameters: dictonary of laser parameter to be passed from the calling function.
        the parameters include
        1) ldcurrentmax
        2) ldcurrent
        :return: NONE
        '''
        if self.device_connected == 1:
            if type(laser_parameters) != dict:
                logging.error("Error arroyoLaserOn: Attribute should be Dictonary :arroyoLaserON")

            self.messageToArroyo('ERRSTR?')
            self.arroyo_device_error_list = self.__receiveArroyoMsg()
            if not self.arroyo_device_error_list:
                logging.error("Error Arroyo Disconnected :No Receive Message from Arroyo :arroyoLaserON")
            else:
                if 'ldcurrentmax' not in laser_parameters or 'ldcurrent' not in laser_parameters:
                    logging.error("Error arroyoLaserON , DeviceData.ini Section not found :arroyoLaserON")
                else:
                    ld_max_current = 'LASer:LIMit:LDI ' + laser_parameters[
                        'ldcurrentmax']  # LASer:LIMit:LDI<space><laser diode max current> Command for Arroyo
                    ld_drive_current = 'LASer:LDI ' + laser_parameters['ldcurrent']  # LASer:LDI<space><ldcurrent>
                self.messageToArroyo('LASer:MODE:ILBW')  # Laser current control (Io/ACC) mode, low bandwidth
                # self.messageToArroyo('LASer:MODE?')  # QUERY ARROYO MODE . SEE MANUAL FOR DETAILS
                self.messageToArroyo(ld_max_current)  # SET LASER CURRENT MAX
                self.messageToArroyo(ld_drive_current)  # SET LASER DRIVE CURRENT
                # self.messageToArroyo('LASer:LIMit:LDI?') #QUERY LASER CURRENT MAX LIMIT
                # self.arroyo_ld_current_max = self.__receiveArroyoMsg()
                self.messageToArroyo('LASer:LIMit:LDV 7')  # SET LASER VOLTAGE LIMIT
                # self.messageToArroyo('LASer:LIMit:LDV?') #QUERY LASER VOLTGE LIMIT
                # self.arroyo_ld_voltage_limit = self.__receiveArroyoMsg()
                self.messageToArroyo(
                    'ONDELAY 150')  # The delay[ms], from the time the output is turned on with the LAS:OUTPUT
                self.messageToArroyo('LASer:TOLerance 1,0.1')  # LASer:TOLerance <mA>,<mseconds> READ MORE IN MANUAL
                self.messageToArroyo('LASer:OUTput 1')  # +TURN LASER ON
                time.sleep(0.5)
                event_complete = self.arroyoOperationComplete()

                if event_complete == '1':
                    self.messageToArroyo('ERRSTR?')
                    self.arroyoComDelay()
                    self.arroyo_device_error_list = self.__receiveArroyoMsg()
                    self.messageToArroyo(
                        '*WAI')  # The *WAI command will pause command processing until the Operation Complete flag is true
                    if self.arroyo_device_error_list == '0':
                        ''' wait for laser to turn on and become stable
                            the loop runs for 10 seconds and if no stable output, error is generated'''
                        self.arroyoLaserStatus()
                    if self.arroyo_device_error_list != '0':
                        self.arroyoLaserStatus()
                        error_string = "Arroyo LD Error " + self.arroyo_device_error_list
                        logging.error(error_string)
                if event_complete != '1':
                    logging.error('Operation Timeout')
        if self.device_connected == 0:
            self.arroyo_ld_on = 0
            self.arroyo_ld_measured_current = 0
            logging.error('Error : Laser Com Error : arroyoLaserON')

    def arroyoLaserOFF(self):
        time.sleep(0.5)
        if self.device_connected != 0:
            try:
                self.messageToArroyo('ERRSTR?')
                self.arroyo_device_error_list = self.__receiveArroyoMsg()

                if not self.arroyo_device_error_list:
                    logging.error(
                        "Error Arroyo Disconnected : No Receive Message from Arroyo :arroyoLaserOff :arroyoLaserON")
                else:
                    self.messageToArroyo('LASer:OUTput 0')  # TURN OFF THE LASER
                    self.messageToArroyo('*ESR?')
            except:
                logging.error(
                    "Error Arroyo Disconnected : No Receive Message from Arroyo :arroyoLaserOff :arroyoLaserON")
        if self.device_connected == 0:
            self.arroyo_ld_on = 0
            self.arroyo_ld_measured_current = 0

    def arroyoOperationComplete(self):

        call_timeout = 5
        call_timeout = datetime.datetime.now() + datetime.timedelta(seconds=call_timeout)
        while (1):
            self.arroyoComDelay()
            self.messageToArroyo('*ESR?')
            event_register = self.__receiveArroyoMsg()
            if event_register == '1':
                break
            if datetime.datetime.now() >= call_timeout:
                logging.error("Error arroyoLaserON Communication Timeout")
                break
            else:
                continue
        return event_register  # if operation completes, it will return 1
