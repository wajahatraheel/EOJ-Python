import csv
import time
import logging
import sqlite3
import pandas as pd

start_time = time.time()


class ZL_Read_Recipe():


    __error = 0
    recipe_output_dictionary = {}
    recipe_read_successful = False

    def __int__(self, logger=None) -> None:

        #self.recipt_output_dictionary: dict = {}
        #self.recipt_read_successful: bool = False
        if logger == None:
            self.logger = logging
        else:
            self.logger = logger

    def __read_sqlite_parm_names(self, actual_machine_name):

        sq_lite_database = sqlite3.connect(
            'D:\EndOptik_Justage_magicLine\Controllino\sqlite_database/anotherexample.db')
        sql_query = """SELECT name FROM sqlite_master 
                WHERE type='table';"""
        cursor: object = sq_lite_database.cursor()
        # executing our sql query
        cursor.execute(sql_query)
        machine_name_sql: list = cursor.fetchall()
        for index in range(0, len(machine_name_sql)):
            machine_str = str(machine_name_sql[index])
            machine_str = machine_str[2:len(machine_str) - 3]
            if machine_str == actual_machine_name:
                break
        querry_message = "SELECT * FROM " + actual_machine_name
        db_dataframe = pd.read_sql_query(querry_message, sq_lite_database)
        return db_dataframe

    def read_recipe_table(self, module_dmc: str, recipe_file_address: str):

        recipe_group_row = 'Gruppe'  # See Recezipt.csv file for row named as 'Gruppe'
        recipe_parameter_row = 'Parameter'
        recipe_datentype_row = 'DatenTyp'
        required_group_index_array = [0]
        temp_index = 0

        try:
            database_dataframe = self.__read_sqlite_parm_names('Rezept_Tabelle_Param')
        except:
            ZL_Read_Recipe.__error = 1
            logging.error('Error : Sqlite3 failed to recgonize Table : read_recipe_table')

        if len(database_dataframe) != 0:
            db_df_row = (database_dataframe.shape[0])
        if database_dataframe.empty:
            ZL_Read_Recipe.__error = 1

        try:
            with open(recipe_file_address, 'r') as file:
                read_table: object = csv.reader(file, delimiter=';')
                recipe_table: object = list(read_table)
        except:
            ZL_Read_Recipe.__error = 1
            logging.error('Error : CSV File cannot be read from Server : read_recipe_table')
        del read_table
        if ZL_Read_Recipe.__error != 1:
            for table_row in recipe_table:
                if table_row[0] == recipe_group_row:
                    required_group_row: list = table_row
                if table_row[0] == recipe_parameter_row:
                    required_parameter_row: list = table_row
                if table_row[0] == recipe_datentype_row:
                    required_datatype: list = table_row
                if table_row[0] == module_dmc:
                    required_module_article_row: list = table_row
            for index_dataframe_column in range(0, len(database_dataframe.columns)):
                for index in range(0, len(required_group_row)):
                    if database_dataframe.columns[index_dataframe_column] == required_group_row[index]:
                        required_group_index_array[temp_index] = index
                        temp_index = temp_index + 1
                        required_group_index_array.append(1)
                temp_index = 0
                for index in range(0, db_df_row):
                    for index_1 in range(0, len(required_parameter_row)):
                        a = database_dataframe.iloc[index][index_dataframe_column]
                        b = required_parameter_row[index_1]
                        if database_dataframe.iloc[index][index_dataframe_column] == required_parameter_row[index_1]:
                            element_exist = required_group_index_array.count(index_1)
                            if element_exist >= 1:
                                c = required_module_article_row[index_1]
                                ZL_Read_Recipe.recipt_output_dictionary.update(
                                    {required_parameter_row[index_1]: required_module_article_row[index_1]})
                                break
                        if database_dataframe.iloc[index][index_dataframe_column] == None:
                            break
                        if index_1 == len(required_parameter_row) - 1:
                            ZL_Read_Recipe.recipt_output_dictionary.update(
                                {database_dataframe.iloc[index][index_dataframe_column]: "NOT FOUND"})
                            ZL_Read_Recipe.recipt_read_successful = False
                    if database_dataframe.iloc[index][index_dataframe_column] == None:
                        break
            if ZL_Read_Recipe.recipt_read_successful != False:
                ZL_Read_Recipe.recipt_read_successful = True

        print("--- %s seconds ---" % (time.time() - start_time))
