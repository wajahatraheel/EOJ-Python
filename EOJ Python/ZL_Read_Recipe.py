import csv
import configparser
import time
import logging
import sqlite3
import pandas as pd
start_time = time.time()



class ZL_Read_Recipe():


    def __int__(self,logger = None):

        if logger == None:
            self.logger = logging
        else:
            self.logger = logger



    def __read_sqlite_parm_names(self,actual_machine_name):

        sq_lite_database = sqlite3.connect('D:\EndOptik_Justage_magicLine\Controllino\sqlite_database/anotherexample.db')
        sql_query = """SELECT name FROM sqlite_master 
                WHERE type='table';"""
        cursor :object = sq_lite_database.cursor()
        # executing our sql query
        cursor.execute(sql_query)
        machine_name_sql : list  = cursor.fetchall()
        for index in range(0, len(machine_name_sql)):
            machine_str = str(machine_name_sql[index])
            machine_str = machine_str[2:len(machine_str) - 3]
            if machine_str == actual_machine_name:
                break
        querry_message = "SELECT * FROM "+actual_machine_name

        db_dataframe  = pd.read_sql_query(querry_message, sq_lite_database)
        #a = db_dataframe.columns
        #j = a[0]
        #k=1
        a = db_dataframe.iloc[0:,0]
        k = a[1]
        return db_dataframe

    def __store_parm_in_inifiles(self,filename_ini : str):
       pass

    def read_recipe_table(self,module_dmc:str,recipe_file_address:str,parameters_file_name:str,write_to_ini:bool):

        database_dataframe = self.__read_sqlite_parm_names('EOJ')
        no_of_groups = len(database_dataframe.columns)


        recipe_group_row = 'Gruppe' # See Recezipt.csv file for row named as 'Gruppe'
        recipe_parameter_row = 'Parameter'
        recipe_datentype_row = 'DatenTyp'

        #file_address = "Rezepturen.csv"
        with open(recipe_file_address, 'r') as file:
            read_table: object = csv.reader(file, delimiter=';')
            recipe_table: object = list(read_table)

        del read_table
        required_group_index_array =[0]
        required_parm_index_array =[0]
        tem_index = 0
        tem_index_parm = 0

        for table_row in recipe_table:
            if table_row[0] == recipe_group_row:
                required_group_row: list = table_row
                '''for index_dataframe_column in range(0,len(database_dataframe.columns)):
                    for index_required_group in range(0,len(required_group_row)):
                        if database_dataframe.columns[index_dataframe_column] == required_group_row[index_required_group]:
                            required_group_index_array[tem_index] = index_required_group
                            tem_index = tem_index+1
                            required_group_index_array.append(1)'''

            if table_row[0] == recipe_parameter_row:
                required_parameter_row :list = table_row

            if table_row[0] == recipe_datentype_row:
                required_datatype :list= table_row

            if table_row[0] == module_dmc:
                required_module_article_row :list= table_row

        for index_dataframe_column in range(0, len(database_dataframe.columns)):
            for index_required_group in range(0, len(required_group_row)):
                if database_dataframe.columns[index_dataframe_column] == required_group_row[index_required_group]:
                    required_group_index_array[tem_index] = index_required_group
                    tem_index = tem_index + 1
                    required_group_index_array.append(1)
            for index_column_parm in range(0,len(database_dataframe.iloc[0:,index_dataframe_column])):

                for index_req_parm in range(0,len(required_parameter_row)):
                    if database_dataframe.iloc[0:,index_dataframe_column][1] == required_parameter_row[index_req_parm]:
                        required_parm_index_array[tem_index_parm] = index_req_parm
                        tem_index_parm = tem_index_parm +1
                        required_parm_index_array.append(1)





        print(type(required_group_row))
        print(required_module_article_row)
        print("--- %s seconds ---" % (time.time() - start_time))










