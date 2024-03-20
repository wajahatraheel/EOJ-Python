import csv
import time
import logging
import sqlite3
import pandas as pd
import os




class ZL_Read_Recipe():


    def __init__(self, logger = None):

        self.recipe_output: dict = {}
        self.recipe_read: bool = True
        self.__error = False

        if logger == None:
            self.logger = logging
        else:
            self.logger = logger


    def check_article_no(self,dmc):
        try:
            separated_characters = dmc.split(';')
            article_no = separated_characters[1]
        except:
            self.__error = True
            self.recipe_read = False
            del separated_characters
            logging.error('Error : Check DMC Code :read_recipe_table')

        if len(article_no) != 9 or article_no =='':
            self.__error = True
            self.recipe_read = False
            del separated_characters
            logging.error('Error : Check DMC Code :read_recipe_table')
        if self.__error == False:
            if article_no.isnumeric():
                self.__error = False
                self.recipe_read = True
            else:
                self.__error = True
                self.recipe_read = False
                del separated_characters
                logging.error('Error : Check DMC Code :read_recipe_table')

        del separated_characters

        return article_no

    def __read_sqlite_parm_names(self, table_name,sqlite_path):

        if self.__error == False:
            try :
                sq_lite_database = sqlite3.connect(sqlite_path)
                sql_query = """SELECT name FROM sqlite_master 
                        WHERE type='table';"""
                cursor: object = sq_lite_database.cursor()
                # executing our sql query
                cursor.execute(sql_query)
                machine_name_sql: list = cursor.fetchall()
                for index in range(0, len(machine_name_sql)):
                    machine_str = str(machine_name_sql[index])
                    machine_str = machine_str[2:len(machine_str) - 3]
                    if machine_str == table_name:
                        break
                querry_message = "SELECT * FROM " + table_name
                db_dataframe = pd.read_sql_query(querry_message, sq_lite_database)
            except Exception as e:
                db_dataframe = []
                self.recipe_read = False
                logging.error(e+' : __read_sqlite_parm_names')
        if self.__error == True:
            db_dataframe = []
            self.recipe_read = False

        return db_dataframe

    def read_recipe_table(self, module_dmc: str, recipe_file_address: str,sqlite_path : str):

        recipe_group_row = 'Gruppe'  # See Recezipt.csv file for row named as 'Gruppe'
        recipe_parameter_row = 'Parameter'
        recipe_datentype_row = 'DatenTyp'
        required_group_index_array = [0]
        temp_index = 0
        database_dataframe = []
        table_name = 'Rezept_Tabelle_Param'
        required_module_article_row = []
        required_group_row = []
        required_parameter_row = []
        required_datatype= []

        module_dmc = self.check_article_no(module_dmc)

        if os.path.isfile(sqlite_path):
            self.__error = False
        else:
            self.__error = True
            self.recipe_read = False
            logging.error('Error : SQL File name or File does not Exist :read_recipe_table ')

        try:
            database_dataframe = self.__read_sqlite_parm_names(table_name,sqlite_path)
            if database_dataframe.empty:
                self.__error = True
                self.recipe_read = False
            else:
                self.__error = False
        except Exception as e:
            self.recipe_read = False
            self.__error = True
            logging.error(e)

        if self.__error == False:

            if len(database_dataframe) != 0:
                db_df_row = (database_dataframe.shape[0])
            if database_dataframe.empty:
                self.__error = True
                self.recipe_read = False

            try:
                with open(recipe_file_address, 'r') as file:
                    read_table: object = csv.reader(file, delimiter=';')
                    recipe_table: object = list(read_table)
            except:
                self.__error = True
                self.recipe_read = False
                logging.error('Error : CSV File cannot be read from Server : read_recipe_table')

        if self.__error == False:

            del read_table

            for table_row in recipe_table:
                if table_row[0] == recipe_group_row:
                    required_group_row: list = table_row
                if table_row[0] == recipe_parameter_row:
                    required_parameter_row: list = table_row
                if table_row[0] == recipe_datentype_row:
                    required_datatype: list = table_row
                if table_row[0] == module_dmc:
                    required_module_article_row: list = table_row

            if not required_module_article_row or not required_parameter_row or not required_group_row:
                self.__error = True
                self.recipe_read = False
                logging.error('Error : Article Not Found in Recipe Table : read_recipe_table')

            if self.__error == False:

                for index_dataframe_column in range(0, len(database_dataframe.columns)):
                    for index in range(0, len(required_group_row)):
                        if database_dataframe.columns[index_dataframe_column] == required_group_row[index]:
                            required_group_index_array[temp_index] = index
                            temp_index = temp_index + 1
                            required_group_index_array.append(1)
                    temp_index = 0

                    for index in range(0, db_df_row):
                        for index_1 in range(0, len(required_parameter_row)):

                            if database_dataframe.iloc[index][index_dataframe_column] == required_parameter_row[index_1]:
                                element_exist = required_group_index_array.count(index_1)
                                if element_exist >= 1:

                                    self.recipe_output.update(
                                        {required_parameter_row[index_1]: required_module_article_row[index_1]})
                                    break
                            if database_dataframe.iloc[index][index_dataframe_column] is None:
                                break
                            if index_1 == len(required_parameter_row) - 1:
                                self.recipe_output.update(
                                    {database_dataframe.iloc[index][index_dataframe_column]: "NOT FOUND"})
                                self.recipe_read = False
                        if database_dataframe.iloc[index][index_dataframe_column] is None:
                            break
                if self.recipe_read:
                    self.recipt_read = True


