from Controllino import Controllino
import configparser as cf
import psutil
import time
import datetime
from ZL_Read_Recipe import  ZL_Read_Recipe
from CurrentSource import Arroyo485_02_15


def ini_file_read_controllino():

    conf_pars = cf.ConfigParser()
    filename = 'U:\TDMS_Datenbank\Rezepturen\ZX\DeviceData.ini'
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


    #dic = ini_file_read_controllino()
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

    #===========================ARROYO TEST PROGRAM MANUAL==========================

    # ===========================ARROYO TEST PROGRAM  MANUAL==========================
    '''arroyo_obj = Arroyo()
    arroyo_obj.connectArroyo(comport = 'COM106',baudrate='115200')
    dict_laserdiode = ini_file_read_controllino()

    #arroyo_obj.arroyoLaserON(dict_laserdiode)
    choice = ""
    while choice != "exit":
        choice = input("What would you like to do      :  ")
        if choice == '1':
            arroyo_obj.arroyoLaserON(dict_laserdiode)
            time.sleep(0.2)
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


    #0000000000000000000000000000 ARROYO Auto TEST PROGRAM========================
    arroyo_obj = Arroyo485_02_15()

    arroyo_obj.connectArroyo(comport='COM106', baudrate='115200')

    dict_laserdiode = ini_file_read_controllino()
    a=0
    iteration = 0
    while(1):
        arroyo_obj.arroyoLaserStatus()
        print(arroyo_obj.arroyo_ld_on)
        print(arroyo_obj.arroyo_ld_measured_current)
        print(arroyo_obj.arroyo_ld_electrical_power)
        if a == 0:
            arroyo_obj.arroyoLaserON(dict_laserdiode)
            a =1
        #time.sleep(0.3)
        if a == 1 and iteration == 10:
            arroyo_obj.arroyoLaserOFF()
        if a==1 and iteration ==15:
            arroyo_obj.arroyoLaserON(dict_laserdiode)
        if iteration == 19:
            arroyo_obj.arroyoLaserOFF()
        if iteration == 20:
            arroyo_obj.closeArroyoPort()
            break
        iteration = iteration +1

    # 0000000000000000000000000000 ARROYO TEST PROGRAM========================




    #=======================================Receipe Test Program begins============================
    '''recip_object = ZL_Read_Recipe()
    parameters_file_name = 'D:\EndOptik_Justage_magicLine\Controllino\EOJ Codes\EOJ Python/recipe_table_parameters.ini'
    receipe_file_directory = 'Rezepturen.csv'
    recip_object.read_recipe_table('722035006',receipe_file_directory,parameters_file_name,write_to_ini=False)'''
    # =======================================Receipe Test Program begins============================





















    #arroyo_obj.messageToArroyo('*IDN?')

    #arroyo_obj.closeArroyoPort()














