
#=============================CONTROLLINO PLC LIBRARY=======================================
#  CAN BE USED WITH ANY CONTROLLINO ( MINI; MAXI ; MEGA )
#  DEVELOPED BY WRA
#=============================CONTROLLINO PLC LIBRARY=======================================

import socket,logging

class Controllino():
    def __init__(self, logger=None):
        super().__init__()
        # use default/root logger in case of no logger was defined as input parameter
        if logger == None:
            self.logger = logging
        else:
            self.logger = logger
        self.message_from_plc = ''

    def openSocket(self, server_ip:str, server_port:str):
        server_port = int(server_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.settimeout(2)
            self.client_socket.connect((server_ip, server_port))
            self.logger.info('Connection established with Controllino PLC with address: ' + str(server_ip))
            self.message_from_plc = 'PLC Connected'
        except socket.error:
            self.logger.error('Failed to establish connection with Controllino PLC with address: ' + str(server_ip))

    def closeSocket(self, address:str):
        try:
            self.client_socket.close()
            self.logger.info('Connection closed with Controllino with address: ' + str(address))
        except socket.error:
            self.logger.error('Failed to close connection with Controllino with address: ' + str(address))

    def __receiveMessageFromServer(self, message_to_plc:str):

        '''the function receives the telegram from the controllino plc, and first it checks if the plc command is correct, then
        for the digital output value, it checks if the plc has returned the same value as it was given as output by user. this condition is same as
        relay output. for INTPUT, it just gives the value of input to the client( PC ). if no INPUT performed, the return value is -1 whichs means error
        for input.'''
        raw_message =""
        try:
            # split_message_from_plc = message_to_plc.split('_') #message_to_server is split based on underscore. e.g ['SET', 'D4', 'IO', '1']
            message_to_plc_split = message_to_plc.split('_')
        except Exception:
            self.logger.error('Invalid Cmd : receiveMessageFromServer')
        try:
            while 1:
                tcp_byte_data = self.client_socket.recv(100).decode()
                raw_message = raw_message + tcp_byte_data
                if "\r" in tcp_byte_data:
                    break
                else:
                    continue
            self.message_from_plc = raw_message.split("\r")[0]
            if message_to_plc_split[0] == 'SET':
                if self.message_from_plc != message_to_plc_split[3]:
                    self.logger.error('Error :PLC Output '+message_to_plc+'not performed')
            if message_to_plc_split[0] == 'GET':
                if self.message_from_plc == '-1':
                    self.logger.error('Error :PLC Input ' + message_to_plc + 'not performed')
            del raw_message,tcp_byte_data
        except Exception:
            self.logger.error('Error in PLC FUnction : receiveMessageFromServer')

    def setOutput(self, pin_number:str, pin_value:int):
        '''SETS THE OUTPUT FOR TELEGRAM: for example SET_D0_IO_1 for relay output SET_R0_IO_1 for PWM output
        SET_D0_PWM_100.'''
        self.message_from_plc=""
        try:
            if (pin_number[0] == 'D' or pin_number[0] == 'A' or pin_number[0] == 'R') and pin_number[1] == 'O':
                if pin_number[0] == 'D':
                    if pin_value==0 or pin_value==1:
                        # for example : SET_D1_IO_<value>
                        msg_to_plc = 'SET'+'_' +'D'+pin_number[2:]+'_'+'IO'+'_'+str(pin_value)
                        self.client_socket.sendall(msg_to_plc.encode())
                        # receive data from plc server
                        self.__receiveMessageFromServer(msg_to_plc)
                    else:
                        self.logger.error('Digital output value out of reach. Check PLC Cmd')
                # ANALOG OUTPUT SET
                if pin_number[0] == 'A':
                    if pin_value >= 0 and pin_value <= 254:
                        # for example : SET_D1_PWM_<value>
                        msg_to_plc = 'SET' + '_' + 'D' + pin_number[2:] + '_' + 'PWM' + '_' + str(pin_value)
                        self.client_socket.sendall(msg_to_plc.encode())
                        # receive data from plc server
                        self.__receiveMessageFromServer(msg_to_plc)
                    else:
                        self.logger.error('PWM value out of reach. Check PLC Cmd')

                # RELAY OUTPUT SET
                if pin_number[0] == 'R':
                    if(pin_value == 0 or pin_value == 1):
                        # for example : SET_R1_IO_<value>
                        msg_to_plc = 'SET' + '_' + 'R' + pin_number[2:] + '_' + 'IO' + '_' + str(pin_value)
                        self.client_socket.sendall(msg_to_plc.encode())
                        # receive data from plc server
                        self.__receiveMessageFromServer(msg_to_plc)
                    else:
                        self.logger.error('Relay output value out of reach. Check PLC Cmd')
            else:
                self.logger.error('Error in function setOutput(). Check Cmd')
        except Exception:
            self.logger.error('Error in PLC function setOutput(). Check Cmd')

    def getInput(self, pin_number:str):
        '''Get  input from PLC COntrollino. THE COMMAND IS GET_A0_A( <<<<for analog input)
        for digital input >>>>> SET_A0_D'''
        try:
            # Raise Error if output command is given instead of input command
            if pin_number[1] != 'I':
                self.logger.error('Error : Check Controllino Input Cmd ')

            #  FOR ANALOG INPUT
            if pin_number[0] == 'A':
                # for example: GET_A15_A
                self.message_to_server = 'GET' + '_' + 'A' + pin_number[2:] + '_' + 'A'
                self.client_socket.sendall(self.message_to_server.encode())
                # receive data from plc server
                self.__receiveMessageFromServer(self.message_to_server)

            #  FOR DIGITAL INPUT
            if pin_number[0] == 'D':
                # for example: GET_A15_D
                self.message_to_server = 'GET' + '_' + 'A' + pin_number[2:] + '_' + 'D'
                self.client_socket.sendall(self.message_to_server.encode())
                # receive data from plc server
                self.__receiveMessageFromServer(self.message_to_server)
        except Exception:
            self.logger.error('Error in  PLC function getInput()')

