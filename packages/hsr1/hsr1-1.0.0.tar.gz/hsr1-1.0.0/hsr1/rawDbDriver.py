# -*- coding: utf-8 -*-
"""
copyright 2024 Peak Design
this file is part of hsr1, which is distributed under the GNU Lesser General Public License v3 (LGPL)
"""

import os

from hsr1.db import (SqliteStoreRaw,
                    SqliteLoadRaw)


class RawDbDriver:
    def __init__(self, db_name, db_type="sqlite"):
        """kwargs is here to catch old parameters that used to be useful"""
        self.db_name = db_name
        
        if db_type == "sqlite":
            self.db_store = SqliteStoreRaw(self)
            self.db_load = SqliteLoadRaw(db_name)
        else:
            raise NotImplementedError("Only sqlite databases are supported")
    
    
    def exists(self) -> bool:
        ##### TODO: move somewhere, this is sqlite specific
        """checks if a database exists and has all columns, returns bool"""
        if not os.path.isfile(self.db_name):
            print("no db file found")
            return False
        column_headings = self.db_load.load_table_names()
        if len(column_headings) >= 4:
            return True
        else:
            return False
    
    def load_table_names(self):
        return self.db_load.load_table_names()
    
    def load(self, columns:[str]=[], start_time=None, end_time=None):
        return self.db_load.load(columns, start_time, end_time)
    
    
    def store(self, dfs, deployment_metadata):
        return self.db_store.store(dfs, deployment_metadata)
    