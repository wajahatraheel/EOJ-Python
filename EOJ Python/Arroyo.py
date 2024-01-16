import serial,logging, time



class Arroyo():
    def __int__(self,logger = None):
        # use default/root logger in case of no logger was defined as input parameter
        if logger == None:
            self.logger = logging
        else:
            self.logger = logger
        self.timeout_value = 1 # timeout value in seconds
        self.arroyo_acknowledgement = ""  # Message or Error Return to Main User

    def openArroyoPort(self,comport:str,baudrate:str,):
        baud = int(baudrate)

        try:
            self.arroyo_serial = serial.Serial(port=comport, baudrate=baud, timeout=1)
        except Exception:
            logging.error('Error : Arroyo ComPort not opened')

    def closeArroyoPort(self):
        self.arroyo_serial.reset_input_buffer()

        try:
            self.arroyo_serial.close()
        except serial.SerialException:
            logging.error('Error : Arroyo ComPort not closed')

    def messageToArroyo(self,message_to_arroyo:str,doide_parameters:list,diode_status:str):
        message_from_arroyo =""
        message_to_arroyo = message_to_arroyo + '\r'+'\n'
        a = message_to_arroyo.encode()
        self.arroyo_serial.write(a)
        while 1:
            raw_data = self.arroyo_serial.read().decode()
            message_from_arroyo = message_from_arroyo + raw_data
            if "\r" in raw_data:
                break
            else:
                continue
        print(message_from_arroyo)
        time.sleep(0.2)


    def arroyoDiodeON(self):
        pass
    def arroyoDiodeOFF(self):
        pass











