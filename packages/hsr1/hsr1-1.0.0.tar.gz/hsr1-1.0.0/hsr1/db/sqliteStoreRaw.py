# -*- coding: utf-8 -*-
"""
copyright 2024 Peak Design
this file is part of hsr1, which is distributed under the GNU Lesser General Public License v3 (LGPL)
"""
import uuid

import pandas as pd

from hsr1.db import (SqliteDBStore,
                    Serialisation)



class SqliteStoreRaw:
    def __init__(self, driver):
        self.driver = driver
        self.serialisation = Serialisation("numpy")
    
    def store(self, dfs, deployment_metadata):
        """takes a list of dfs containing time and individual channel data"""
        table_names = ["channel_"+str(i) for i in range(len(dfs))]
        
        big_df = pd.DataFrame()
        for i, df in enumerate(dfs):
            channel = pd.DataFrame(Serialisation.listify_and_serialise_numpy(df), columns=[table_names[i]])
            channel = channel.reset_index()
            channel.columns = ["pc_time_end_measurement", table_names[i]]
            channel["pc_time_end_measurement"] = channel["pc_time_end_measurement"].astype(str)
            if len(big_df) == 0:
                big_df = channel
            else:
                big_df = big_df.merge(channel, on="pc_time_end_measurement")
        
        
        store = SqliteDBStore(self.driver)
        
        deployment_metadata = deployment_metadata.reset_index(drop=True)
        
        # TODO: more thorough check if db exists
        ##### checks if appending to a database or making new one, and if it already exists, checks to see if its the same deployment
        if self.driver.exists():
            db_load = self.driver.db_load
            store = SqliteDBStore(self.driver)
            deployment_metadata = store.match_deployment_ids(deployment_metadata, db_load)
            deployment_metadata = store.match_dataseries_ids(deployment_metadata, db_load)
        else:
            deployment_metadata["deployment_id"] = str(uuid.uuid1())
            deployment_metadata["dataseries_id"] = str(uuid.uuid1())
        
        store.store_dataframe(deployment_metadata, "deployment_metadata")
        store.store_dataframe(big_df, "raw_data")    
    