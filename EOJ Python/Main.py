from Controllino import Controllino
import configparser as cf
import psutil
import time
from Arroyo import Arroyo


def ini_file_read_controllino():

    conf_pars = cf.ConfigParser()
    filename = 'controllino.ini'
    try:
        conf_pars.read(filename)
        try:
            conf_pars.has_section('Controllino_Mega')
            lst = conf_pars.items('Controllino_Mega')
            t = tuple(lst)
            d = dict(t) #for accessing dict items di['port']
            return d
        except Exception as e:
            print(e)
    except Exception as e:
        print('Failed to Read ini File')



if __name__ =="__main__":
    '''dict_controllino = ini_file_read_controllino()
    Controllino_Mega_comm = Controllino()
    Controllino_Mega_comm.openSocket(server_ip=dict_controllino['ip_address'] ,server_port=dict_controllino['port'])

    #Controllino_Mega_comm.setOutput(pin_number=dict_controllino['light_tower_red'],pin_value=0)

    for i in range(0,10):
        Controllino_Mega_comm.setOutput(pin_number=dict_controllino['light_tower_green'], pin_value=1)
        #time.sleep(1)
        Controllino_Mega_comm.setOutput(pin_number=dict_controllino['light_tower_green'], pin_value=0)
    Controllino_Mega_comm.closeSocket(address=dict_controllino['ip_address'] )'''

    arroyo_obj = Arroyo()
    arroyo_obj.openArroyoPort(comport = 'COM100',baudrate='9600')
    arroyo_obj.messageToArroyo('*IDN?')
    arroyo_obj.closeArroyoPort()














