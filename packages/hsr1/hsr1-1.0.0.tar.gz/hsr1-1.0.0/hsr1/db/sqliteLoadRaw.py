# -*- coding: utf-8 -*-
"""
copyright 2024 Peak Design
this file is part of hsr1, which is distributed under the GNU Lesser General Public License v3 (LGPL)
"""
import os

import sqlite3

from hsr1.db import (SqliteDBLoad,
                     Serialisation)



class SqliteLoadRaw():
    def __init__(self, db_name:str):
        if os.path.isfile(db_name):
            self.exists = True
        else:
            self.exists = False
        self.db_name = db_name
    
    
    def load(self, columns:[str]=[], 
             start_time=None, 
             end_time=None):
        
        if columns == []:
            columns = self.load_table_names()
            
            if not "raw_data" in columns:
                raise ValueError("this database dosent have raw_data")
            
            columns = columns["raw_data"]
        
        
        if not os.path.isfile(self.db_name):
            raise ValueError(f"database '{self.db_name}' does not exist")
        
        time_col = "pc_time_end_measurement"
        
        time_condition = " WHERE "
        if start_time != None:
            times_after = time_col+" > \""+str(start_time)+"\" and "
            time_condition += times_after
        
        if end_time != None:
            times_before =  time_col+" < \""+str(end_time)+"\" and "
            time_condition += times_before
        
        if time_condition == " WHERE ":
            time_condition = ""
        
        sql = "SELECT "+", ".join(columns)+" FROM raw_data" + time_condition
        
        load = SqliteDBLoad(self.db_name)
        result = load.load_sql(sql)
        
        result.columns = columns
        
        
        
        ser = Serialisation("numpy")
        result = ser.decode_dataframe(result, columns[1:])
        
        return result
    
    
    def load_table_names(self):
        """return a dictionary of all the table names and their corresponding column names"""
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        
        ##### get all the table names
        sql = "SELECT name FROM sqlite_schema WHERE type='table'"
        cur.execute(sql)
        table_names = [table[0] for table in cur.fetchall()]
        
        ##### get all the column headers for each table
        column_headers = {}
        for table in table_names:
            sql = "PRAGMA table_info("+table+");"
            cur.execute(sql)
            column_headers[table] = [column[1] for column in cur.fetchall()]
        
        con.close()
        return column_headers