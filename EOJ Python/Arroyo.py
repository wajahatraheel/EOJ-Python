
import serial,logging,datetime,time


'''global variables'''

global error_state
error_state = 'ERRSTR?' + '\r'+'\n'
error_state_encode = error_state.encode()
arroyo_com_delay = 0.15
interlock = 0

class Arroyo():

    def __int__(self,logger = None):


        self.device_connected =1
        self.arroyo_device_error_list=''
        self.arroyo_ld_on =0
        self.arroyo_ld_measured_current =0
        self.arroyo_ld_current_max = 0
        self.arroyo_mode =''
        self.arroyo_ld_voltage_limit =0
        self.interlock = 0


        if logger == None:
            self.logger = logging
        else:
            self.logger = logger



    def __receiveArroyoMsg(self):
        '''
        FUNCTION TYPE = PRIVATE
        FUNCTION RETURNS THE MESSAGE FROM ARROYO SUPPLY: THE MESSAGE DOES NOT INCLUDE CARRIGE RETURN OR LINE FEEED
        RETURN VALUE IS IN STR FORM
        '''
        try:
            raw_data = self.arroyo_serial.readline(1024).decode()
            self.device_connected =1
            split_raw_data = raw_data.split("\r")
            return split_raw_data[0]
            if not raw_data:
                self.device_connected = 0
                return split_raw_data[0]==''
                raise Exception
        except Exception:
            logging.error("Error Arroyo Timeout: No Receive Message")


    def __condition_register_decoded(self,condition_register):
        '''
        this function converts the hex number coming from command COND? which checks the condition of laser.
        this converts the hex into 16 bit binary array. based on these bits, the error command is decoded.
        SEE Laser Condition Status Register LASer:COND? IN USER MANUAL
        :param condition_register:
        :return: laser_condition
        '''
        hex_string = condition_register
        # Convert the hexadecimal string to an integer using the base 16
        hex_integer = int(hex_string, 16)
        binary_string = bin(hex_integer)
        # Remove the '0b' prefix from the binary string
        binary_string = binary_string[2:]
        '''SEE USER MANUAL FOR CONDITION REGISTER 'COND?' command.'''
        full_binary_string = binary_string.zfill(16) #SEE USER MANUAL FOR CONDITION REGISTER 'COND?' command.

        #===============================================NOT USED==============================================
        '''ERROR LIST condition_register_dictonary'''
        condition_register_dictionary = {'1':'Thermal Trip','2':'T Limit','3':'R Limit','6':'Output On','7'
        :'Laser Out of Tolerance','8':'Laser Output Short','9':'Laser Open Circuit','12':'Laser Interlock','13'
        :'PD Power Limit','14':'PD Current Limit','15':'Voltage Limit','16':'Current Limit'}
        # ===================================================================================================

        one_index_in_binary = [pos for pos, char in enumerate(full_binary_string) if char == '1']

        one_index_in_binary = [x+1 for x in one_index_in_binary]
        laser_condition = ''

        if 6 in one_index_in_binary:
            laser_condition = 'Laser On'
            self.interlock = 0
        if 12 in one_index_in_binary:
            laser_condition = 'Error : Laser Interlock'
            self.interlock = 1
        if 6 not in one_index_in_binary and 12 not in one_index_in_binary:
            laser_condition= 'Error, Check Laser Diode'
        return laser_condition

    def connectArroyo(self,comport:str,baudrate:str,):
        '''
        IT CONNECTS THE ARROYO: OPEN COMPORT FOR ARROYO:
        ARROYO BAUDRATE = 115200
        '''
        baud = int(baudrate)
        connect_string_message =""
        try:
            self.arroyo_serial = serial.Serial(port=comport, baudrate=baud, timeout=0.1)
            self.arroyo_serial.write(error_state_encode)
            self.arroyoComDelay()
            connect_string_message = self.__receiveArroyoMsg()
            if not connect_string_message:
                raise Exception
        except Exception:
            logging.error('Error : Arroyo comport not opened')

    def closeArroyoPort(self):

        '''
        CLOSES THE COMPORT OF ARROYO
        :return: NONE
        '''
        self.arroyo_serial.reset_input_buffer()
        try:
            self.arroyo_serial.close()
        except serial.SerialException:
            logging.error('Error : Arroyo ComPort not closed')

    def arroyoComDelay(self):
        time.sleep(arroyo_com_delay)


    def arroyoOperationComplete(self):

        call_timeout = 5
        call_timeout = datetime.datetime.now() + datetime.timedelta(seconds=call_timeout)
        while(1):
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

        return event_register #if operation completes, it will return 1

    def arroyoLaserStatus(self):

        """
        Keep Checking the laser Interlock and laser status
        :return: arroyo_ld_on
        """

        while 1:
            self.messageToArroyo('LASer:COND?')  # Returns the laser condition register. ( see arroyo Manual for Details)
            self.arroyoComDelay()
            arroyo_status = self.__receiveArroyoMsg()
            first_try_status = arroyo_status
            #print("laser Status ", arroyo_status)

            decoded_cond_message = self.__condition_register_decoded(arroyo_status) #decoding condition register of arroyo

            if arroyo_status == '1024':  # 1024 value for stable connection and loop breaks
                self.arroyo_ld_on = 1
                break
            if not arroyo_status:
                self.arroyo_ld_on = 0
                logging.error("Error arroyoLaser Comm Prob")
            if arroyo_status == '0':
                self.arroyo_ld_on = 0
                break
            if first_try_status == arroyo_status:
                self.arroyo_ld_on = 0
                logging.error(decoded_cond_message)
                break


    def messageToArroyo(self,message_to_arroyo:str):
        '''
        SENDS MESSAGE TO ARROYO
        :param message_to_arroyo: string message to be send to arroyo
        :return: NONE
        '''
        self.arroyo_serial.flushOutput()
        self.arroyo_serial.flushInput()
        message_to_arroyo = message_to_arroyo + '\r'+'\n'
        encoded_message_to_arroyo = message_to_arroyo.encode()
        self.arroyo_serial.write(encoded_message_to_arroyo)
        self.arroyoComDelay()
        #self.arroyo_serial.write(error_state_encode)

    def arroyoLaserON(self,laser_parameters:dict):
        '''
        TURNS ON THE LASER DIODE
        :param laser_parameters: dictonary of laser parameter to be passed from the calling function.
        the parameters include
        1) ldcurrentmax
        2) ldcurrent
        :return: NONE
        '''

        if type(laser_parameters) != dict:
            logging.error("Error arroyoLaserOn: Attribute should be Dictonary")
        sec_to_timeout_arroyo = 5
        exec_end_time_arroyo = datetime.datetime.now() + datetime.timedelta(seconds=sec_to_timeout_arroyo)

        self.messageToArroyo('ERRSTR?')
        self.arroyo_device_error_list = self.__receiveArroyoMsg()
        if not self.arroyo_device_error_list :
            logging.error("Error Arroyo Disconnected :No Receive Message from Arroyo :arroyoLaserON")
        else:

            if 'ldcurrentmax' not in laser_parameters or 'ldcurrent' not in laser_parameters :
                logging.error("Error arroyoLaserON , DeviceData.ini Section not found")
            else:
                ld_max_current = 'LASer:LIMit:LDI ' + laser_parameters[
                    'ldcurrentmax']  # LASer:LIMit:LDI<space><laser diode max current> Command for Arroyo
                ld_drive_current = 'LASer:LDI ' + laser_parameters['ldcurrent']  # LASer:LDI<space><ldcurrent>

            self.messageToArroyo('LASer:MODE:ILBW')  # Laser current control (Io/ACC) mode, low bandwidth
            event_complete = self.arroyoOperationComplete()

            #self.messageToArroyo('LASer:MODE?')  # QUERY ARROYO MODE . SEE MANUAL FOR DETAILS

            self.messageToArroyo(ld_max_current)  # SET LASER CURRENT MAX

            self.messageToArroyo(ld_drive_current) #SET LASER DRIVE CURRENT

            #self.messageToArroyo('LASer:LIMit:LDI?') #QUERY LASER CURRENT MAX LIMIT

            #self.arroyo_ld_current_max = self.__receiveArroyoMsg()

            self.messageToArroyo('LASer:LIMit:LDV 7')  #SET LASER VOLTAGE LIMIT

            #self.messageToArroyo('LASer:LIMit:LDV?') #QUERY LASER VOLTGE LIMIT

            #self.arroyo_ld_voltage_limit = self.__receiveArroyoMsg()

            self.messageToArroyo('ONDELAY 150') #The delay[ms], from the time the output is turned on with the LAS:OUTPUT

            self.messageToArroyo('LASer:TOLerance 1,0.1')  #LASer:TOLerance <mA>,<mseconds> READ MORE IN MANUAL

            self.messageToArroyo('LASer:OUTput 1') #+TURN LASER ON
            time.sleep(0.5)
            event_complete = self.arroyoOperationComplete()
            #time.sleep(0.5)

            if event_complete == '1':
                self.messageToArroyo('ERRSTR?')
                self.arroyoComDelay()

                self.arroyo_device_error_list = self.__receiveArroyoMsg()

                self.messageToArroyo('*WAI') #The *WAI command will pause command processing until the Operation Complete flag is true

                if self.arroyo_device_error_list =='0':
                    ''' wait for laser to turn on and become stable
                        the loop runs for 10 seconds and if no stable output, error is generated'''
                    self.arroyoLaserStatus()

                if self.arroyo_device_error_list !='0':
                    self.arroyoLaserStatus()
                    error_string = "Arroyo LD Error " + self.arroyo_device_error_list
                    logging.error(error_string)
            if event_complete != '1':
                logging.error('Operation Timeout')

    def arroyoLaserOFF(self):
        try:
            self.messageToArroyo('ERRSTR?')

            self.arroyo_device_error_list = self.__receiveArroyoMsg()

            if  not self.arroyo_device_error_list:
                logging.error("Error Arroyo Disconnected : No Receive Message from Arroyo :arroyoLaserOff")
            else:
                self.messageToArroyo('LASer:OUTput 0') #TURN OFF THE LASER
                self.messageToArroyo('*ESR?')
                #print(self.__receiveArroyoMsg())
        except:
            logging.error("Error Arroyo Disconnected : No Receive Message from Arroyo :arroyoLaserOff")



















