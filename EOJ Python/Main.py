from Controllino import Controllino
import configparser as cf
import psutil
import time
from Arroyo import Arroyo
import datetime


def ini_file_read_controllino():

    conf_pars = cf.ConfigParser()
    filename = 'DeviceData.ini'
    try:
        conf_pars.read(filename)
        try:
            conf_pars.has_section('100998410')
            lst = conf_pars.items('100998410')
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

    for k in range(0,1):
        for i in range(0,24):
            pin = 'DO'
            num = str(i)
            pin = pin+num
            Controllino_Mega_comm.setOutput(pin_number=pin, pin_value=1)
            print(pin)
            #time.sleep(1)
        for i in range(0,16):
            pin ='RO'
            num = str(i)
            pin = pin + num
            Controllino_Mega_comm.setOutput(pin_number=pin, pin_value=1)

        for i in range(0,24):
            pin = 'DO'
            num = str(i)
            pin = pin+num
            Controllino_Mega_comm.setOutput(pin_number=pin, pin_value=0)
            print(pin)
            #time.sleep(1)
        for i in range(0,16):
            pin ='RO'
            num = str(i)
            pin = pin + num
            Controllino_Mega_comm.setOutput(pin_number=pin, pin_value=0)

    Controllino_Mega_comm.closeSocket(address=dict_controllino['ip_address'] )'''
    '''===================ARROYO TEST================='''
    arroyo_obj = Arroyo()
    arroyo_obj.connectArroyo(comport = 'COM106',baudrate='115200')

    dict_laserdiode = ini_file_read_controllino()

    #arroyo_obj.arroyoLaserON(dict_laserdiode)
    choice = ""


    '''while choice != "exit":        
        choice = input("What would you like to do      :  ")
        if choice == '1':
            arroyo_obj.arroyoLaserON(dict_laserdiode)
            arroyo_obj.arroyoLaserStatus()
            if arroyo_obj.arroyo_ld_on ==1 :
                print("Laser ON")
            else:
                print("Laser OFF")
        elif choice == '2':
            arroyo_obj.arroyoLaserOFF()
            arroyo_obj.arroyoLaserStatus()
            if arroyo_obj.arroyo_ld_on == 1:
                print("Laser ON")
            else:
                print("Laser OFF")

        elif choice == '3':
            print("You chose 3")
        else:
            print("Program Exit.")'''
    a=0
    iteration = 0
    while(1):
        arroyo_obj.arroyoLaserStatus()
        print(arroyo_obj.arroyo_ld_on )
        if a == 0:
            arroyo_obj.arroyoLaserON(dict_laserdiode)
            a =1
        time.sleep(1)
        if a == 1 and iteration == 10:
            arroyo_obj.arroyoLaserOFF()
        if a==1 and iteration ==15:
            arroyo_obj.arroyoLaserON(dict_laserdiode)
        if iteration == 19:
            arroyo_obj.arroyoLaserOFF()
        if iteration == 20:
            break
        iteration = iteration +1
























    #arroyo_obj.messageToArroyo('*IDN?')

    #arroyo_obj.closeArroyoPort()














