import logging
from importlib import reload
import os
import shutil
import subprocess
import datetime
from itertools import combinations, chain
from time import sleep
from pathlib import Path
import inspect
from appdirs import user_data_dir

import plotly.express as px
import pandas as pd
import numpy as np
from plotly.offline import plot
from wiliot_deployment_tools.common.debug import debug_print, is_databricks
from os.path import exists
import tabulate
try:
    from wiliot_deployment_tools.internal.utils.network_packet_list import NetworkPacketList, network_data_preparation, DecryptedTagCollection
except ImportError:
    pass
from wiliot_deployment_tools.common.utils import convert_timestamp_to_datetime, current_timestamp, mstimestamp_to_timezone


if is_databricks():
    logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

class WiliotTableError(Exception):
    pass

class WiliotDatabricksUtils:

    def __init__(self, spark):
        self.spark = spark
        self.is_databricks = is_databricks()

    def get_seen_tags(self, table, start_time, end_time, tags_list=None, bridges_list=None, gateways_list=None,external_rawdata_path=None):
        """
        does an SQL query of the packet data table between specified timestamps
        filters the data for specified tags/bridges/gateways (if specified)
        returns relevant values from the table
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type tags_list: list
        :param tags_list: list of tags to filter from the data
        :type bridges_list: list
        :param bridges_list: list of bridges to filter from the data
        :type gateways_list: list
        :param gateways_list: list of gateways to filter from the data
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """
        # TODO - debug the SQL Query with different types of lists
        if bridges_list is not None:
            if len(bridges_list) == 1:
                bridges_list = list(bridges_list) + [""]
            bridges_list = tuple(bridges_list)
        if gateways_list is not None:
            if len(gateways_list) == 1:
                gateways_list = list(gateways_list) + [""]
            gateways_list = tuple(gateways_list)
        if tags_list is not None:
            if len(tags_list) == 1:
                tags_list = list(tags_list) + [""]
            tags_list = tuple(tags_list)
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        if external_rawdata_path:
            query_data = pd.read_csv(external_rawdata_path)
            return query_data
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=24)
        end_datetime = query_end_datetime + datetime.timedelta(hours=24)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = ''
        if 'enriched' in table:
            sql_method = f"""
            select gatewayId, decryptedData, sequenceId, timestamp, nonce, mic, encryptedData, rawPacket, rssi, bridgeId, tagId, externalId, packet_counter, packetVersion, flowVersion, dco, gpio, charge_time, internal_tmp, nfpkt, temp_sensor_dc, assetId
            from {table}
            where date between {start_date} and {end_date}
            and timestamp between {start_time} and {end_time}
            """
        else:
            sql_method = f"""
            select gatewayId, decryptedData, sequenceId, timestamp, nonce, mic, encryptedData, rawPacket, rssi, bridgeId, tagId, externalId, packet_counter, packetVersion, flowVersion, dco, gpio, charge_time, internal_tmp, nfpkt, temp_sensor_dc
            from {table}
            where date between {start_date} and {end_date}
            and timestamp between {start_time} and {end_time}
            """
        if tags_list is not None and tags_list != ():
            sql_method = sql_method + f"""and externalId in {tags_list}
        """
        if bridges_list is not None and bridges_list != ():
            sql_method = sql_method + f"""and bridgeId in {bridges_list}
        """
        if gateways_list is not None and gateways_list != ():
            sql_method = sql_method + f"""and gatewayId in {gateways_list}
        """
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    def get_seen_events(self, table, start_time, end_time, bridges_list=None, gateways_list=None, platform=False):
        """
        does an SQL query of the packet data table between specified timestamps
        filters the data for specified tags/bridges/gateways (if specified)
        returns relevant values from the table
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type bridges_list: list
        :param bridges_list: list of bridges to filter the data by
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :type platform: bool
        :param platform: platform/management (true/false)
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """
        # TODO - debug the SQL Query with different types of lists
        devices_list = ()
        if bridges_list is not None:
            if len(bridges_list) == 1:
                devices_list = list(bridges_list) + [""]
            devices_list = tuple(devices_list)
        if gateways_list is not None:
            if len(gateways_list) == 1 and devices_list == ():
                devices_list = list(gateways_list) + [""]
            elif devices_list is not None:
                devices_list = devices_list + tuple(gateways_list)
            devices_list = tuple(devices_list)

        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select *
        from {table}
        where date between {start_date} and {end_date} 
        and start between {start_time} and {end_time} 
        """
        if not platform:
            connectivity_event = "name = 'NTWK'"
            id_filter = "id"
        else:
            connectivity_event = "eventName = 'connectivity'"
            id_filter = "assetId"

        if devices_list is not None:
            sql_method = sql_method + f"""and ({connectivity_event} or {id_filter} in {devices_list})
        """
        else:
            sql_method = sql_method + f"""and {connectivity_event}"""
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    def get_sequence_id_data(self, table, start_time, end_time, gateways_list=None):
        """
        does an SQL query of the packet data table between specified timestamps
        returns only sequence id
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """

        if gateways_list is not None:
            if len(gateways_list) == 1:
                gateways_list = list(gateways_list) + [""]
            gateways_list = tuple(gateways_list)
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select sequenceId, timestamp, gatewayId, gatewayName
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time} 
        """
        if gateways_list is not None:
            sql_method = sql_method + f"""and gatewayId in {gateways_list}
        """
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    def get_statistics_data(self, table, start_time, end_time, gateways_list=None):
        """
        does an SQL query of the statistics data table between specified timestamps
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """

        if gateways_list is not None:
            if len(gateways_list) == 1:
                gateways_list = list(gateways_list) + [""]
            gateways_list = tuple(gateways_list)
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select *
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time} 
        """
        if gateways_list is not None:
            sql_method = sql_method + f"""and gatewayId in {gateways_list}
        """
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    def get_heartbeat_data(self, table, start_time, end_time, gateways_list=None, bridges_list=None):
        """
        does an SQL query of the statistics data table between specified timestamps
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """

        if gateways_list is not None:
            if len(gateways_list) == 1:
                gateways_list = list(gateways_list) + [""]
            gateways_list = tuple(gateways_list)
        
        if bridges_list is not None:
            if len(bridges_list) == 1:
                bridges_list = list(bridges_list) + [""]
            bridges_list = tuple(bridges_list)
        
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select *
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time} 
        """
        if gateways_list is not None:
            sql_method = sql_method + f"and gatewayId in {gateways_list}\n"
        if bridges_list is not None:
            sql_method = sql_method + f"and bridgeId in {bridges_list}\n"
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    
    def get_num_seen_bridges(self, table, start_time, end_time, gateways_list=None):
        """
        gets number of unique bridges seen by each gateways (bridge has to send data packets)
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :return: dictionary of number of seen bridges per gateway
        """
        if gateways_list is not None:
            if len(gateways_list) == 1:
                gateways_list = list(gateways_list) + [""]
            gateways_list = tuple(gateways_list)
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select gatewayId, count(distinct bridgeId) as countBridge
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time} 
        """
        if gateways_list is not None:
            sql_method = sql_method + f"""and gatewayId in {gateways_list}
        """
        sql_method = sql_method + "group by gatewayId"
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            query_data = dict(zip(query_data['gatewayId'], query_data['countBridge']))
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")


    def get_sequence_id_loss(self, packets_table, statistics_table, start_time, end_time, gateways_list=None, sync_tables=True):
        """
        calculates sequence ID loss (takes reboot into consideration) per GW in table
        :type packets_table: str | DataFrame
        :param packets_table: name of data table | data table DataFrame
        :type statistics_table: str | DataFrame
        :param statistics_table: name of statistics table | statistics table DataFrame
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :type sync_tables: bool
        :param sync_tables: sync table start/end by timestamp (relevant for running directly after DB table updates)
        :return: dictionary of statistics
        """

        RESET_THRESHOLD = 1000
        
        def sync_data_and_statistics_tables(data_table, statistics_table, gw_list):
            """
            sync data and statistics table by timestamps
            """
            def get_first_stat_timestamp(statistics_table):
                first_stat_timestamp = 0
                for gw in statistics_table['gatewayId'].unique():
                    gw_first_stat_timestamp = np.sort(statistics_table[statistics_table['gatewayId'] == gw]['timestamp'])[0]
                    if gw_first_stat_timestamp > first_stat_timestamp:
                        first_stat_timestamp = gw_first_stat_timestamp
                return first_stat_timestamp
            
            # 'sync' statistics table and data table latest timestamps:
            max_data_timestamp = data_table['timestamp'].max()
            max_stats_timestamp = statistics_table['timestamp'].max()
            last_synced = min(max_data_timestamp, max_stats_timestamp)
            # truncate end of data tables to timeslot
            data_table = data_table[data_table['timestamp']<= last_synced]
            statistics_table = statistics_table[statistics_table['timestamp'] <= last_synced]
            
            first_stat_timestamp = get_first_stat_timestamp(statistics_table)
            stat_start_timestamp = first_stat_timestamp - (datetime.timedelta(seconds = 60).total_seconds() * 1000)
            data_start_timestamp = data_table['timestamp'].min()
            while data_start_timestamp > stat_start_timestamp:
                statistics_table = statistics_table[statistics_table['timestamp']>first_stat_timestamp]
                first_stat_timestamp = get_first_stat_timestamp(statistics_table)
                stat_start_timestamp = first_stat_timestamp - (datetime.timedelta(seconds = 60).total_seconds() * 1000)

            return data_table, statistics_table
                

        
        def get_stats_for_continuous_sequence_ids(sequence):
            """
            generate statistics for contiuous sequence IDs
            :type sequence: list
            :param sequence: array of sequence ID
            :rtype: dict
            :return: dictionary of statistics
            """
            stats = {}

            # remove duplicates
            sequence = np.unique(sequence)
            # sort by descending order
            sequence = -np.sort(-sequence)

            s_max = np.max(sequence)
            s_min = np.min(sequence)
            s_rec = len(np.unique(sequence)) # TODO - Compare with len(sequence) / num of coupled packets from table
            s_expected = (s_max - s_min)+1
            stats['maxSequenceId'] = s_max
            stats['minSequenceId'] = s_min
            stats['receivedSequenceIds'] = s_rec
            stats['expectedSequenceIds'] = s_expected
            return stats

        def process_sequences(df_array, num_mgmt_packets=0):
            """
            generate statistics for (normalized by duration) for array of sequence IDs (compensated for GW Reboots)
            :type df_array: list of DataFrames
            :param df_array: list of DataFrames with continuous sequence IDs
            :type num_mgmt_packets: int
            :param num_mgmt_packets: number of management packets
            :rtype: dict
            :return: dictionary of statistics
            """
            total_stats = {}
            total_received_packets = num_mgmt_packets
            total_expected_packets = 0
            for df in df_array:
                stats = get_stats_for_continuous_sequence_ids(df['sequenceId'])
                total_received_packets += stats['receivedSequenceIds']
                total_expected_packets += stats['expectedSequenceIds']
            if total_expected_packets == 0:
                breakpoint()
            loss_percentage = (1 - (total_received_packets / total_expected_packets) )* 100
            total_stats['totalManagementPackets'] = num_mgmt_packets
            total_stats['totalDataPackets'] = total_received_packets - num_mgmt_packets
            total_stats['totalReceivedPackets'] = total_received_packets
            total_stats['totalExpectedPackets'] = total_expected_packets
            total_stats['lossPercentage'] = round(loss_percentage, 3)
            total_stats['numResets'] = len(df_array)-1
            return total_stats

        results = {}
        if isinstance(packets_table, pd.DataFrame):
            data = packets_table
        else:
            data = self.get_sequence_id_data(packets_table, start_time, end_time, gateways_list).sort_values(by='timestamp', ascending=False)
        gw_list = data['gatewayId'].unique()
        if gw_list is None:
            return None
        if isinstance(statistics_table, pd.DataFrame):
            statistics_data = statistics_table
        else:
            statistics_data = self.get_statistics_data(statistics_table, start_time, end_time, gw_list)
        if sync_tables:
            data, statistics_data = sync_data_and_statistics_tables(data, statistics_data, gw_list)

        for gw in gw_list:
            gw_name = data[data['gatewayId'] == gw]['gatewayName'].iloc[0]
            num_mgmt_packets = statistics_data[statistics_data['gatewayId'] == gw]['managementPktCount'].sum()
            gw_results = []
            gw_df = data[data['gatewayId'] == gw].reset_index()
            gw_df['diff'] = gw_df['sequenceId'].diff()
            gw_df['reset'] = np.where(gw_df['diff']>RESET_THRESHOLD, True, False)
            gw_resets = gw_df[gw_df['reset'] == True]
            sequences = np.array_split(gw_df, gw_resets.index)
            gw_results = process_sequences(sequences, num_mgmt_packets)
            gw_results.update({'gwName': gw_name})
            results[gw] = gw_results
        return results



    def get_amount_of_unique_tags_per_data_path(self, table, start_time, end_time, gateways_list=None,
                                                tags_to_ignore=None, bridges_list=None):
        """
        does an SQL query of the packet data table between specified timestamps
        returns amount of unique externalIds per data path (bridge->gw) in the given timeframe
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type tags_to_ignore: list
        :param tags_to_ignore: list of tags to ignore in the query (will not be counted)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :type bridges_list: list
        :param bridges_list: list of bridges to filter the data by
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """
        if bridges_list is not None:
            if len(bridges_list) == 1:
                bridges_list = list(bridges_list) + [""]
            bridges_list = tuple(bridges_list)
        if gateways_list is not None:
            if len(gateways_list) == 1:
                gateways_list = list(gateways_list) + [""]
            gateways_list = tuple(gateways_list)
        if tags_to_ignore is not None:
            if len(tags_to_ignore) == 1:
                tags_to_ignore = list(tags_to_ignore) + [""]
            tags_to_ignore = tuple(tags_to_ignore)
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select gatewayId, bridgeId, count(distinct externalId)
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time} 
        """
        if tags_to_ignore is not None and tags_to_ignore != ():
            sql_method = sql_method + f"""and externalId not in {tags_to_ignore}
        """
        if bridges_list is not None and bridges_list != ():
            sql_method = sql_method + f"""and bridgeId in {bridges_list}
        """
        if gateways_list is not None and gateways_list != ():
            sql_method = sql_method + f"""and gatewayId in {gateways_list}
        """
        sql_method = sql_method + f"""group by gatewayId, bridgeId   order by gatewayId, bridgeId"""
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    def get_amount_of_unique_tags_per_brg(self, table, start_time, end_time, tags_to_ignore=None, bridges_list=None):
        """
        does an SQL query of the packet data table between specified timestamps
        returns amount of unique externalIds per data path (bridge->gw) in the given timeframe
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type tags_to_ignore: list
        :param tags_to_ignore: list of tags to ignore in the query (will not be counted)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :type bridges_list: list
        :param bridges_list: list of bridges to filter the data by
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """
        if bridges_list is not None:
            if len(bridges_list) == 1:
                bridges_list = list(bridges_list) + [""]
            bridges_list = tuple(bridges_list)
        if tags_to_ignore is not None:
            if len(tags_to_ignore) == 1:
                tags_to_ignore = list(tags_to_ignore) + [""]
            tags_to_ignore = tuple(tags_to_ignore)
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select gatewayId, bridgeId, count(distinct externalId)
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time} 
        """
        if tags_to_ignore is not None and tags_to_ignore != ():
            sql_method = sql_method + f"""and externalId not in {tags_to_ignore}
        """
        if bridges_list is not None and bridges_list != ():
            sql_method = sql_method + f"""and bridgeId in {bridges_list}
        """
        sql_method = sql_method + f"""group by bridgeId   order by bridgeId"""
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    def get_amount_of_unique_tags_per_gw(self, table, start_time, end_time, gateways_list=None, tags_to_ignore=None):
        """
        does an SQL query of the packet data table between specified timestamps
        returns amount of unique externalIds per data path (bridge->gw) in the given timeframe
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :type tags_to_ignore: list
        :param tags_to_ignore: list of tags to ignore in the query (will not be counted)
        :type gateways_list: list
        :param gateways_list: list of gateways to filter the data by
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """

        if gateways_list is not None:
            if len(gateways_list) == 1:
                gateways_list = list(gateways_list) + [""]
            gateways_list = tuple(gateways_list)
        if tags_to_ignore is not None:
            if len(tags_to_ignore) == 1:
                tags_to_ignore = list(tags_to_ignore) + [""]
            tags_to_ignore = tuple(tags_to_ignore)
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=36)
        end_datetime = query_end_datetime + datetime.timedelta(hours=36)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select gatewayId, count(distinct externalId)
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time} 
        """
        if tags_to_ignore is not None and tags_to_ignore != ():
            sql_method = sql_method + f"""and externalId not in {tags_to_ignore}
        """
        if gateways_list is not None and gateways_list != ():
            sql_method = sql_method + f"""and gatewayId in {gateways_list}
        """
        sql_method = sql_method + f"""group by gatewayId   order by gatewayId"""
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")

    def get_last_data(self, table, mins=60, tags_list=None, bridges_list=None, gateways_list=None):
        """
        function querys back specified minutes from data table (counts back from last entry in table)
        :type table: str
        :param table: databricks data table name
        :type mins: int
        :param mins: minutes to query back, defaults to 1 hour
        :param tags_list: tags list
        :type tags_list: list
        :param tags_list: list of tags to filter from the data
        :type bridges_list: list
        :param bridges_list: list of bridger to filter from the data
        :type gateways_list: list
        :param gateways_list: list of gateways to filter from the data
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """
        end_timestamp = self.get_last_entry_timestamp(table)
        end_datetime = mstimestamp_to_timezone(end_timestamp)
        start_timestamp = end_timestamp - (mins * 60 * 1000)
        start_datetime = mstimestamp_to_timezone(start_timestamp)
        debug_print(f'Getting last {mins} mins from {table}')
        debug_print(f'Last entry at {end_timestamp}')
        debug_print(f'querying {start_datetime} -> {end_datetime}')
        return self.get_seen_tags(table, start_timestamp, end_timestamp, tags_list, bridges_list, gateways_list)

    def get_last_entry_timestamp(self, table):
        """
        function gets name of data table and returns the timestamp of the last entry (in milliseconds)
        :type table: str
        :param table: name of table
        """
        today = datetime.datetime.now()
        yesterday = today-datetime.timedelta(days=1)
        today_date = datetime.datetime.strftime(today, '%Y%m%d')
        yesterday_date = datetime.datetime.strftime(yesterday, '%Y%m%d')

        # Try to get last timestamp from last day
        sql_method = f"""
        select MAX (timestamp)
        from {table}
        where date between {yesterday_date} and {today_date} 
        """
        if self.spark is not None:
            query_data = self.spark.sql(sql_method)
            query_data = query_data.toPandas()
            last_entry_ts = query_data.iloc[0][0]
            if not np.isnan(last_entry_ts):
                return query_data.iloc[0][0]
            else:
                # Query all packets in table
                sql_method = ''.join(sql_method.split('\n')[:-2])
                query_data = self.spark.sql(sql_method)
                query_data = query_data.toPandas()
                last_entry_ts = query_data.iloc[0][0]
                if not np.isnan(last_entry_ts):
                    return query_data.iloc[0][0]
                else:
                    raise WiliotTableError(f'Cannot get last entry, no entries in data table {table}')
        else:
            raise EnvironmentError("Unable to detect dbutils function")

    def wait_for_data(self, table, requested_timestamp, timeout_mins=70):
    # TODO - implement date search
        """
        function waits for data timed at requested_timestamp (or later) to appear in the data table.
        :type table: str
        :param table: data table name
        :type requested_timestamp: int
        :param requested_timestamp: timestamp to wait to appear in the table
        """
        last_entry_timestamp = self.get_last_entry_timestamp(table)
        table_ready = last_entry_timestamp >= requested_timestamp
        start = current_timestamp()
        while not table_ready:
            if (current_timestamp() - start) >= 1000 * 60 * timeout_mins:
                debug_print(f"""{timeout_mins} minute timeout reached! Table still does not have the requested data
                Run test again or get raw data with wait_for_data=False""")
                exit_notebook(f'Wait for table timeout reached after {timeout_mins} minutes')
            debug_print(
                f'Waiting for table to get data. \n'
                f'Requested timestamp {requested_timestamp} | ({mstimestamp_to_timezone(requested_timestamp)}) \n'
                f'Table latest timestamp {last_entry_timestamp} | ({mstimestamp_to_timezone(last_entry_timestamp)})')
            mins_behind = (requested_timestamp - last_entry_timestamp) / 60000
            debug_print(f'Data table {mins_behind} minutes behind , trying again in 30 seconds', center=True)
            sleep(30)
            last_entry_timestamp = self.get_last_entry_timestamp(table)
            table_ready = last_entry_timestamp >= requested_timestamp
        debug_print(
            f'Table is updated. \n'
            f'Requested timestamp {requested_timestamp}, table latest timestamp {last_entry_timestamp} \n'
            f'Table latest timestamp {last_entry_timestamp} | ({mstimestamp_to_timezone(last_entry_timestamp)})')
        mins_ahead = (last_entry_timestamp - requested_timestamp) / 60000
        debug_print(f'Data table {mins_ahead} minutes ahead', center=True)

    def get_seen_edge_devices_from_packets(self, table, start_time, end_time):
        """
        does an SQL query of the packet data table between specified timestamps
        returns dictionary of seen gateways and bridges from slice of packet table
        :type table: str
        :param table: name of data table
        :type start_time: float
        :param start_time: time filter start timestamp (UTC milliseconds)
        :type end_time: float
        :param end_time: time filter end timestamp (UTC milliseconds)
        :rtype: pandas DataFrame
        :return: dataframe of data from table
        """
        # adding search by date to improve search time (most tables in data bricks partition is by date)
        query_start_datetime = convert_timestamp_to_datetime(str(start_time))
        query_end_datetime = convert_timestamp_to_datetime(str(end_time))
        start_datetime = query_start_datetime - datetime.timedelta(hours=24)
        end_datetime = query_end_datetime + datetime.timedelta(hours=24)
        start_date = datetime.datetime.strftime(start_datetime, '%Y%m%d')
        end_date = datetime.datetime.strftime(end_datetime, '%Y%m%d')
        sql_method = f"""
        select gatewayId, bridgeId, gatewayName, max(timestamp) as timestamp
        from {table}
        where date between {start_date} and {end_date} 
        and timestamp between {start_time} and {end_time}
        group by gatewayId, gatewayName, bridgeId 
        """
        if self.spark is not None:
            debug_print('Running SQL query...', center=True)
            debug_print(sql_method)
            query_data = self.spark.sql(sql_method).toPandas()
            query_data['gatewayId'] = query_data['gatewayId'].str.upper()
            query_data['bridgeId'] = query_data['bridgeId'].str.upper()
            return query_data
        else:
            raise EnvironmentError("SQL query can only run in databricks")


def process_tagstats(params, tag_stats_df, working_directory, test_no):
    """
        function gets tag stats dataframe and creates downloadable cdf graph for specified parameters
        :type params: list
        :param params: tag stats metrics to create graphs for
        :type tag_stats_df: pandas DataFrame
        :param tag_stats_df: tag stats DataFrame (can be created using get_tagstats_from_test)
        :type working_directory: string
        :param working_directory: directory to save the graphs HTML files
        :type test_no: string
        :param test_no: test number
    """
    if params is None:
        debug_print('No parameters specified. Creating graphs for all possible parameters.')
        params = ['num_packets', 'num_cycles', 'sprinkler_counter_mean', 'sprinkler_counter_std',
                  'sprinkler_counter_min', 'sprinkler_counter_max', 'tbp_mean', 'tbp_std', 'tbp_min', 'tbp_max',
                  'tbp_num_vals', 'per_mean', 'per_std', 'rssi_mean', 'rssi_std', 'rssi_min', 'rssi_max', 'ttfp',
                  'ttfp_seconds', 'end_time', 'duration', 'rx_rate_normalized', 'rx_rate', 'charge_time_min',
                  'charge_time_max', 'packet_counter_min', 'packet_counter_max', 'packet_counter_first',
                  'estimated_packet_counter_resets', 'estimated_total_packet_rate', 'estimated_total_per',
                  'externalId']
    tests_list = tag_stats_df['testId'].unique()
    for param in params:
        debug_print(f"""*****************************{param}*****************************""")
        graph = pd.DataFrame()
        for test in tests_list:
            df = tag_stats_df[tag_stats_df.testId == test]
            test_curveset = cdf_dataframe(df, param, test)
            graph = pd.concat([test_curveset, graph])
            debug_print(f"""test {test} added to graph""")
        fig = px.scatter(graph, x=param, y='TagCount', color=['testName'])
        fig.update_layout(title=param)
        fig.update_yaxes()
        if param == 'ttfp_seconds':
            fig.update_xaxes(title_text='Time to first packet [seconds]')
        if param == 'estimated_total_packet_rate':
            fig.update_xaxes(title_text='Estimated total packet rate [counters/second]')
        filepath = f"""{working_directory}{test_no}_{param}_graph.html"""
        open(filepath, 'a').close()
        fig.write_html(filepath)
        # debug_print(filepath)
        # p = plot(fig, output_type='div')
        # display_html(p)
        create_download_link(filepath, file_name=f"""{param} graph""")

def file_exists(path):
    """
    function checks if file exists
    :type path: str
    :param path: path to file
    :rtype: bool
    :return: file exists
    """
    path = path.replace('/dbfs', 'dbfs:')
    try:
        db_utils().fs.head(path)
        return True
    except Exception:
        try:
            return exists(path)
        except Exception:
            return False

def get_tagstats_from_test(tests_config_df=None, tests_config_csv_path=None, rawdata_df=None,
                           rawdata_csv_path=None, tagdeployment_df=None, tagdeployment_csv_path=None):
    """
        function gets test config df/csv and rawdata (from datatables) df/csv as input
        the function processes the data and created a new dataframe containing tag statistics for each test.
        :type tests_config_df: pandas DataFrame
        :param tests_config_df: dataframe of test config
        :type tests_config_csv_path: string
        :param tests_config_csv_path: path to test config csv
        :type rawdata_df: pandas DataFrame
        :param rawdata_df: dataframe of raw data
        :type rawdata_csv_path: string
        :param rawdata_csv_path: path to raw data csv
        :type tagdeployment_df: pandas DataFrame
        :param tagdeployment_df:dataframe of tag deployment data
        :type tagdeployment_csv_path: string
        :param tagdeployment_csv_path: path to tag deployment data csv
    """
    if tests_config_csv_path is not None and not tests_config_df:
        tests_config_df = pd.read_csv(tests_config_csv_path)
    if rawdata_csv_path is not None and not rawdata_df:
        rawdata_df = pd.read_csv(rawdata_csv_path)
    if tagdeployment_csv_path is not None:
        tagdeployment_df = pd.read_csv(tagdeployment_csv_path)
    testid_list = tests_config_df['testId'].unique()
    master_tag_stats = pd.DataFrame()
    for testid in testid_list:
        if  testid not in rawdata_df.testId.unique():
            debug_print(f"""0 data for testId {testid} in raw data! please check tables/test config""")
            continue
        currenttest_df = rawdata_df[rawdata_df.testId == testid].copy()
        start_time = tests_config_df[tests_config_df.testId == testid].get('startTimestamp').item()
        debug_print(f"""***** Processing {testid} data. Test Timestart = {start_time}""")
        currenttest_packets = analyze_packets_data(packets_df=currenttest_df, test_time_start=start_time)
        tag_stats_dict = currenttest_packets.get_group_statistics(group_by_col='externalId')
        tag_stats_df = pd.DataFrame.from_dict(tag_stats_dict, orient='index')
        tag_stats_df['testId'] = testid
        master_tag_stats = pd.concat([master_tag_stats, tag_stats_df])
    if tagdeployment_df is not None:
        debug_print('***********Tag deployment information merged with tag stats from test***********')
        master_tag_stats = pd.merge(master_tag_stats, tagdeployment_df, how='outer', on='externalId'). \
            sort_values('testId').set_index('externalId')
    master_tag_stats.insert(18, 'ttfp_seconds', master_tag_stats.ttfp / 1000)
    return master_tag_stats

def massagedata(dataset, param):
    curveset = pd.DataFrame(columns=[param, 'TagCount'])
    count = 0
    reftme_stmp = None
    for index, row in dataset.iterrows():
        if pd.isna(row[param]):
            continue
        if reftme_stmp is None:
            reftme_stmp = row[param]
        if reftme_stmp == row[param]:
            count += 1
        else:
            curveset = curveset.append({param: reftme_stmp, 'TagCount': count}, ignore_index=True)
            reftme_stmp = row[param]
            count += 1
    curveset = curveset.append({param: reftme_stmp, 'TagCount': count}, ignore_index=True)
    return curveset

def display_html(html):
    """
    Use databricks displayHTML from an external package
    :type html: string
    :param html: html document to display
    """
    for frame in inspect.getouterframes(inspect.currentframe()):
        global_names = set(frame.frame.f_globals)
        # Use multiple functions to reduce risk of mismatch
        if all(v in global_names for v in ["displayHTML", "display", "spark"]):
            return frame.frame.f_globals["displayHTML"](html)
    raise EnvironmentError("Unable to detect displayHTML function")

def display_print(todisplay, console_only=False, **kwargs):
    """
    Use databricks display func from an external package.
    uses tabulate library to display dataframe in case running locally
    :type todisplay: pandas DataFrame
    :param todisplay: variable to display
    :type console_only: bool
    :param console_only: if true, prints the data table to console (even if running in DB notebook) using tabulate
    """
    if not console_only:
        for frame in inspect.getouterframes(inspect.currentframe()):
            # call dbutils display
            global_names = set(frame.frame.f_globals)
            if all(v in global_names for v in ["display"]):
                try:
                    return frame.frame.f_globals["display"](todisplay)
                except ValueError:
                    debug_print('ValueError when reading DataFrame! Trying to print in console', center=True)
                except KeyError:
                    debug_print('KeyError when reading DataFrame! Trying to print in console', center=True)
                except TypeError:
                    debug_print('TypeError when reading DataFrame! Trying to print in console', center=True)
    if isinstance(todisplay, pd.DataFrame) or console_only:
        debug_print('\n' + tabulate.tabulate(todisplay, **kwargs))
        return None
    raise EnvironmentError("Unable to detect Display function")

def db_utils_rm(dbfs_path):
    """
    helper function to remove files/folders from dbfs
    """
    dbfs_path = dbfs_path.replace('/dbfs', 'dbfs:')
    return db_utils().fs.rm(dbfs_path)

def db_utils():
    """
    Use databricks dbutils from an external package
    for example: to use dbutils.fs.head() - use db_utils().fs.head()
    """
    for frame in inspect.getouterframes(inspect.currentframe()):
        global_names = set(frame.frame.f_globals)
        # Use multiple functions to reduce risk of mismatch
        if all(v in global_names for v in ["dbutils"]):
            return frame.frame.f_globals["dbutils"]()
    raise EnvironmentError("Unable to detect dbutils function")

def get_secret(scope, key):
    """
    get databrickst secret, return None if not running in databricks
    :param scope: secret scope
    :param key: secret key
    """
    try:
        secret = db_utils().secrets.get(scope=scope, key=key)
        return secret
    except EnvironmentError:
        raise(EnvironmentError('Cannot get secret when not running in databricks!'))


def create_download_link(dbfs_path, file_name='file'):
    """
    accepts path to dbfs file, and creates a download link to the file in the notebook
    the function only works with files saved in /dbfs/FileStore
    :type dbfs_path: string
    :param dbfs_path: path to dbfs path (accepts either spark API or file API format)
    :type file_name: string
    :param file_name: name of file (this will be the name of the link created)
    """
    if is_databricks():
        if not ('/dbfs/FileStore' in dbfs_path or 'dbfs:/FileStore' in dbfs_path):
            raise ValueError('the path must start with /dbfs/FileStore or dbfs:/FileStore!')
        dbfs_path = dbfs_path.replace('/dbfs/FileStore', '/files')
        dbfs_path = dbfs_path.replace('dbfs:/FileStore', '/files')
        display_html(f"""<a href="{dbfs_path}" download>Download {file_name} </a>""")
    debug_print(f"""File available at {dbfs_path}""")

def cdf_dataframe(dataset, param, dataset_name, groupby=None, comp=False):
    """
    function accepts dataframe as input the function returns dataframe of CDF
    complementary cumulative distribution function (of tag count) according to param,
    and labels it by dataset_name
    :type dataset: pandas DataFrame
    :param dataset: dataset to create CDF
    :type param: string
    :param param: parameter to create the CDF
    :type dataset_name: string
    :param dataset_name: name to add to the result
    :type groupby: str
    :param groupby: added parameter (in dataset) to group results by
    :type comp: bool
    :param comp: whether to create CDF (comp = False) or CCDF (comp = True)
    """
    curveset = pd.DataFrame(columns=[param, 'TagCount', groupby])
    dataset = dataset.sort_values(param, ascending=True)
    if groupby is None:
        iterations = [None]
    else:
        iterations = dataset[groupby].unique()
    for group in iterations:
        group_curveset = pd.DataFrame(columns=[param, groupby])
        if group is not None:
            group_dataset = dataset[dataset[groupby] == group]
        else: 
            group_dataset = dataset 
        values = group_dataset[param].unique()
        group_curveset[param] = values
        if group is not None:
            group_curveset[groupby] = group
        for index, value in group_curveset[param].items():
            biggerthan = group_dataset[group_dataset[param] > value][param].count()
            smallerorequals = group_dataset[group_dataset[param] <= value][param].count()
            if comp:
                group_curveset.at[index, 'TagCount'] = biggerthan
            else:
                group_curveset.at[index, 'TagCount'] = smallerorequals
        if comp:
            group_curveset['testName'] = dataset_name + '_CCDF'
        else:
            group_curveset['testName'] = dataset_name + '_CDF'
        curveset = pd.concat([curveset, group_curveset])

    return curveset

def multi_plot_dataframe(dataset, param, dataset_name, graph_type, tags_physical_param, groupby=None, comp=False):

    """
    function accepts dataframe as input the function returns dataframe of CDF
    complementary cumulative distribution function (of tag count) according to param,
    and labels it by dataset_name
    :type dataset: pandas DataFrame
    :param dataset: dataset to create CDF
    :type param: string
    :param param: parameter to create the CDF
    :type dataset_name: string
    :param dataset_name: name to add to the result
    :type groupby: str
    :param groupby: added parameter (in dataset) to group results by
    :type comp: bool
    :param comp: whether to create CDF (comp = False) or CCDF (comp = True)
    """
    curveset = pd.DataFrame(columns=[param, 'TagCount', groupby])
    dataset = dataset.sort_values(param, ascending=True)
    if groupby is None:
        iterations = [None]
    else:
        debug_print(f'dataset is: {dataset}')
        debug_print(f'dataset[groupby] is: {dataset[groupby]}')
        iterations = dataset[groupby].unique()
    for group in iterations:
        columns_group_curvset = [param, groupby, 'testId'] + tags_physical_param
        group_curveset = pd.DataFrame(columns=columns_group_curvset)
        if group is not None:
            group_dataset = dataset[dataset[groupby] == group]
        else: 
            group_dataset = dataset 
        group_curveset[[param, 'testId'] + tags_physical_param] = group_dataset[[param, 'testId'] + tags_physical_param]

        if group is not None:
            group_curveset[groupby] = group
        for index, value in group_curveset[param].items():
            biggerthan = group_dataset[group_dataset[param] > value][param].count()
            smallerorequals = group_dataset[group_dataset[param] <= value][param].count()
            if comp:
                group_curveset.at[index, 'TagCount'] = biggerthan
            else:
                group_curveset.at[index, 'TagCount'] = smallerorequals

        if graph_type == 'overall_analysis':
            curveset_to_plot = group_curveset

        if graph_type == 'location_analysis':
            location_curvset = group_curveset.groupby(['testId', 'location']).apply(sort_and_add_index, param=param, comp=comp)
            location_curvset.reset_index(drop=True, inplace=True)
            curveset_to_plot = location_curvset 

        if graph_type == 'position_analysis':
            position_curveset = group_curveset  
            position_curveset['index'] = group_curveset.groupby(['surface', 'orientation', 'testId'])[param].rank(method='first').astype(int)    
            curveset_to_plot = position_curveset

        if comp:
            curveset_to_plot['testName'] = dataset_name + '_CCDF'
        else:
            curveset_to_plot['testName'] = dataset_name + '_CDF' 
        curveset = pd.concat([curveset, curveset_to_plot])

    return curveset

def sort_and_add_index(group, param, comp=False):
    group['index'] = range(1, len(group) + 1)
    return group.sort_values(param, ascending=not comp)

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

def analyze_packets_data(packets_df=None, csv_path=None, test_time_start=None, test_time_conf_received=None,
                         no_duplications=True):

    """
    gets dataframe of packets / csv of packets, returns NetworkPacketList of packets
    :type csv_path: string
    :param csv_path: path to the packets csv file
    :type packets_df: dataframe
    :param packets_df: packets dataframe
    :type test_time_start: timestamp (int)
    :param test_time_start: UTC millisecond timestamp of the beginning of the test
    :type test_time_conf_received: timestamp (int)
    :param test_time_conf_received: UTC millisecond timestamp of the time the test configuration was received
    :type no_duplications: bool
    :param no_duplications: if False, will keep duplications of same rawPacket
    :return: NetworkPacketList created from .csv located in path
    """
    if test_time_start is None:
        debug_print('Test time start was not passed, some metrics will not be calculated!')
    else:
        debug_print(f'Test time start {test_time_start} | ')
    if csv_path is None and packets_df is None:
        debug_print("no data was given!()")
        return None
    if csv_path is not None:
        packets_df = pd.read_csv(csv_path)

    debug_print('Preprocessing raw data...')

    # remove duplicate rows
    dup_rows = packets_df.shape[0]
    packets_df.sort_values(by='timestamp', ascending=True, ignore_index=True, inplace=True)
    if no_duplications:
        packets_df.drop_duplicates('rawPacket', ignore_index=True, inplace=True)
        dup_rows = dup_rows - packets_df.shape[0]
        if dup_rows > 0:
            debug_print(f'{dup_rows} duplicate rows removed')

    # fix adva
    packets_df['rawPacket'] = packets_df['rawPacket'].apply(lambda x: x[4:] if x.startswith('1E16') else x)

    # flag bugged tags packets
    flag_bugged_tags(packets_df)

    debug_print('Creating NetworkPacketList from DataFrame...')
    packets_list = NetworkPacketList(list_custom_data={'test_time_start': test_time_start})
    if test_time_conf_received is not None:
        packets_list.list_custom_data['test_time_conf_received'] = test_time_conf_received
    packets_list = packets_list.import_packet_df(import_all=True, packet_df=packets_df, obj_out=None)
    return packets_list

def create_zip(dir_path):
    """
    gets path to FileStore directory and creates a download link to a zip file of the files in given directory
    zip file will be saved inside the dir_path directory
    :type dir_path: string
    :param dir_path: path to FileStore directory to zip
    """
    if dir_path[-1] == '/':
        dir_path = dir_path[:-1]
    dir_name = dir_path.rsplit('/', 1)[-1]
    if file_exists(dir_path + '/' + dir_name + '.zip'):
        db_utils().fs.rm(dir_path.replace('/dbfs', 'dbfs:') + '/' + dir_name + '.zip')
    zip_tmp_path = shutil.make_archive('/tmp/zips/tmpzip', 'zip', dir_path)
    zip_download_path = dir_path.replace('/dbfs', 'dbfs:') + '/' + dir_name + '.zip'
    db_utils().fs.mv(f'file:{zip_tmp_path}', zip_download_path)
    create_download_link(zip_download_path, f'{dir_name}.zip')

def exit_notebook(message):
    """
    closes notebook and prints out error message
    :type message: str
    :param message: error message
    """
    debug_print(message, center=True)
    try:
        db_utils().notebook.exit(message)
    except EnvironmentError as e:
        raise Exception(message)

def save_df(df, path, name=None, withindex=False, silent=False):
    """
    saves DataFrame to path, displays the DataFrame and creates a download link
    :type df: pandas Dataframe
    :param df: dataframe to save
    :type path: str
    :param path: path to save can be entered either as filename to save or directory to save in
    :type name: str
    :param name: name of dataframe (this displays in the download link and as a header before the link
    :type withindex: bool
    :param withindex: flag to choose if to export the dataframe with/without index
    :type silent: bool
    :param silent: if true does not generate HTML link
    """
    # save as dataframe.csv if no filename given
    if path[-1] == '/':
        path = path + 'dataframe'
    if path[-4:] != '.csv':
        path = path + '.csv'
    if name is None:
        name = path.split()[-1]
    if is_databricks():
        path = path.replace(' ', '_')
    debug_print(f'Saving DataFrame at {path}')
    if not is_databricks():
        df.to_csv(path, index=withindex)
        return True
    try:
        df.to_csv(path, index=withindex)
    except OSError:
        mkdirs_path = path.replace('/dbfs', 'dbfs:').rsplit('/', 1)[0]
        db_utils().fs.mkdirs(mkdirs_path)
        df.to_csv(path, index=withindex)
    if not silent:
        if is_databricks():
            display_html(f'<h1>{name}</h1>')
            create_download_link(dbfs_path=path, file_name=name)
            display_print(pd.read_csv(path), headers="keys")
        else:
            debug_print(f'{name} available at {path}')

def initialize_logger(working_directory=None):
    """
    initializes the logger to print to log and to logfile, which by default is named by the current timestamp (ms)
    when calling the function.
    :param working_directory: working directory to save logfile (in case running locally)
    :type working_directory: str
    :return: logger fileHandler filename
    """
    logging.shutdown()
    reload(logging)
    logger = logging.getLogger()
    for handler in logger.handlers:
        try:
            # extract current filename from log
            filename = handler.baseFilename.split('\\')[-1].split('.')[0]
            debug_print(f'Logger already initialized! passing logfile {filename}')
            return filename
        except Exception:
            pass
    logger_filename = int(current_timestamp())
    if is_databricks():
        db_utils().fs.put(f'file:/databricks/driver/{logger_filename}.log', '', overwrite=True)
        logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s | %(levelname)s | %(message)s',
                            handlers=[
                                logging.FileHandler(f'{logger_filename}.log', 'a'),
                                # logging.handlers.RotatingFileHandler
                                logging.StreamHandler()
                            ], force=True)
        logging.getLogger().handlers[0].setLevel(logging.DEBUG)
        logging.getLogger().handlers[1].setLevel(logging.INFO)
        debug_print(f'logger initialized at {logger_filename}', center=True)
        debug_print(f'logfile located at file:/databricks/driver/{logger_filename}.log')
    else:
        if working_directory is None:
            working_directory = os.path.join(user_data_dir(), 'wiliot', 'deployment_tools')
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s | %(levelname)s | %(message)s',
                            handlers=[
                                logging.FileHandler(f'{working_directory}/{logger_filename}.log', 'a'),
                                # logging.handlers.RotatingFileHandler
                                logging.StreamHandler()
                            ])
        # filter stream to show info and up
        logging.getLogger().handlers[0].setLevel(logging.DEBUG)
        logging.getLogger().handlers[1].setLevel(logging.INFO)
        debug_print(f'logger initialized at {logger_filename}', center=True)
        debug_print(f'logfile located at {working_directory}/{logger_filename}.log')
    logging.getLogger().setLevel(logging.DEBUG)
    return logger_filename

def create_logfile(logger_filename, working_directory, copy_filename):
    """
        function copies the logfile for recent run to the test working directory and creates link for download
        :type logger_filename: str
        :param logger_filename: filename of log file
        :type working_directory: str
        :param working_directory: directory to copy logfile to
        :type copy_filename: str
        :param copy_filename: name of logfile when copied
    """
    if not is_databricks():
        debug_print('Cannot create logfile, logfile available already!')
    debug_print('Creating Logfile...', center=True)
    debug_print(f'cp {logger_filename}.log {copy_filename}.log')
    subprocess.run(f'cp {logger_filename}.log {copy_filename}.log', shell=True)
    copy_directory = working_directory.replace('/dbfs', 'dbfs:')
    debug_print(f'copy directory {copy_directory}')
    db_utils().fs.mkdirs(f'{copy_directory}')
    debug_print(f'mkdirs {copy_directory}')
    db_utils().fs.cp(f'file:/databricks/driver/{copy_filename}.log', copy_directory)
    debug_print(f'cp file:/databricks/driver/{copy_filename}.log, copy_directory')
    create_download_link(working_directory + f'{copy_filename}.log', f'{copy_filename}.log')
    debug_print(f"create download link - {working_directory} + f'{copy_filename}.log', f'{copy_filename}.log'")

def get_packet_table_name(owner, env, platform=False, is_enriched=False):
    """
    function gets ownerId and environment and return the name of the packet table (in databricks)
    :type owner: str
    :param owner: ownerId
    :type env: str
    :param env: wiliot environment (prod/test/dev)
    :type platform: bool
    :param platform: wiliot platform
    :rtype: str
    :return: data table name
    """
    env = 'prod' if env is None else env
    data_table = ''
    if is_enriched:
        data_table = owner + '' + f'_enriched_packets_data_{env}'
    else:
        data_table = owner + '' + f'_packet_data_{env}'
    data_table = '_' + data_table
    return data_table

def get_event_table_name(owner, env=None, platform=False):
    """
    function gets ownerId and environment and return the name of the event table (in databricks)
    :type owner: str
    :param owner: ownerId
    :type env: str
    :param env: wiliot environment (prod/test/dev)
    :type platform: bool
    :param platform: wiliot platform
    :rtype: str
    :return: data table name
    """
    env = 'prod' if env is None else env
    if not platform:
        event_table = owner + '' + f'_event_data_{env}'
    else:
        event_table = owner + '' + f'_assets_metrics_data_{env}'
    if owner.isnumeric():
        event_table = '_' + event_table
    return event_table

def get_heartbeat_table_name(env=None):
    """
    function gets environment and returns the name of the heartbeat table (in databricks)
    :type owner: str
    :param owner: ownerId
    :type env: str
    :param env: wiliot environment (prod/test/dev)
    :rtype: str
    :return: hearbeat table name
    """
    env = 'prod' if env is None else env
    hearbeat_table = f'_network_heartbeat_statistics_{env}'
    return hearbeat_table

def get_statistics_table_name(env=None):
    """
    function gets environment and returns the name of the heartbeat table (in databricks)
    :type owner: str
    :param owner: ownerId
    :type env: str
    :param env: wiliot environment (prod/test/dev)
    :rtype: str
    :return: hearbeat table name
    """
    env = 'prod' if env is None else env
    hearbeat_table = f'_network_data_statistics_{env}'
    return hearbeat_table

def get_configuration_table_name(owner, env=None):
    """
    function gets ownerId and environment and return the name of the configuration table (in databricks)
    :type owner: str
    :param owner: ownerId
    :type env: str
    :param env: wiliot environment (prod/test/dev)
    :rtype: str
    :return: configuration table name
    """
    env = 'prod' if env is None else env
    configuration_table = owner + '' + f'_network_configuration_{env}'
    if owner.isnumeric():
        configuration_table = '_' + configuration_table
    return configuration_table

def process_graph(fig, graph_name, display_graph=True, save_graph=False, directory=None, pass_as_is=False):
    """
    function processes graph - displays and saves the graph (according to entered flags)
    :type fig: plotly Figure
    :param fig: graph to display
    :type graph_name: str
    :param graph_name: name of graph, and the filename by which it will be saved
    :type display_graph: bool
    :param display_graph: flag to choose if to display the graph in DataBricks Notebook
    :type save_graph: bool
    :param save_graph: flag to choose if to save the graph
    :type directory: str
    :param directory: directory to save graph
    :type pass_as_is: bool
    :param pass_as_is: if true the fig entered is already a plot
    """
    debug_print(f'Processing Graph - {graph_name}', center=True)
    if save_graph:
        if directory is None:
            exit_notebook('Need to supply directory to save graph!')
        if directory[-1] != '/':
            directory = directory + '/'
        filepath = f"""{directory}{graph_name}.html"""
        Path(directory).mkdir(parents=True, exist_ok=True)
        open(filepath, 'a').close()
        fig.write_html(filepath)
        create_download_link(filepath, file_name=graph_name)
    if display_graph:
        if is_databricks():
            if not pass_as_is:
                fig = plot(fig, output_type='div')
            display_html(fig)
        else:
            fig.show(renderer="browser")

def get_spark():
    try:
        from pyspark.sql import SparkSession
        return SparkSession.builder.getOrCreate()
    except NameError:
        raise NameError('Spark is not installed!')


def analyze_packets_data_per_brg(df, brg_list, time_start, test_time_conf_received=None):
    df = df.drop_duplicates(subset=["rawPacket", "bridgeId"])
    tag_stats_df = pd.DataFrame()
    for brg in brg_list:
        brg_df = df[df['bridgeId'] == brg]
        debug_print(f'Processing {brg_df.shape[0]} packets from {brg}')
        if brg_df.empty:
            continue
        df_tagstats = analyze_packets_data(packets_df=brg_df, test_time_start=time_start,
                                           test_time_conf_received=test_time_conf_received)
        tag_stats_dict = df_tagstats.get_group_statistics(group_by_col='externalId')
        tag_stats_df_tmp = pd.DataFrame.from_dict(tag_stats_dict, orient='index')
        tag_stats_df_tmp['bridgeId'] = brg
        tag_stats_df = pd.concat([tag_stats_df, tag_stats_df_tmp])
    if 'externalId' not in tag_stats_df.columns:
        tag_stats_df['externalId'] = tag_stats_df.index
    tag_stats_df = tag_stats_df.sort_values('rx_rate_normalized', ascending=False).drop_duplicates(
        'externalId').sort_index()
    return tag_stats_df


def flag_bugged_tags(rawdata_df):
    """
    function gets raw data dataframe, adds 'isBugged' column
    'isBugged' is true for each packet of a bugged tag, false otherwise
    :type rawdata_df: pandas DataFrame
    :param rawdata_df: raw packet data
    """
    rawdata_df['isBugged'] = None
    unique_tags = rawdata_df['externalId'].unique()
    for tag in unique_tags:
        tmp_df = rawdata_df.loc[rawdata_df['externalId'] == tag]
        tmp_df = tmp_df[['packet_counter', 'timestamp']]
        tmp_df = tmp_df.sort_values(by=['timestamp'])
        prev_packet_counter = 0
        cycles = 0
        orig_cycles = tmp_df['packet_counter'].unique()
        for timestamp in tmp_df['timestamp'].unique():
            # TODO - see when this function throws error
            try:
                packet_counter = tmp_df.loc[tmp_df['timestamp'] == timestamp, 'packet_counter'].unique().item()
            except Exception:
                continue
            if packet_counter + 256 * cycles < prev_packet_counter:
                cycles = cycles + 1
            prev_packet_counter = packet_counter + 256 * cycles
            tmp_df.loc[tmp_df['timestamp'] == timestamp, 'packet_counter'] = prev_packet_counter
        tmp_df2 = tmp_df.diff(axis=0)
        tmp_df2['rate'] = (1000 * tmp_df2['packet_counter'] / tmp_df2['timestamp'])
        max_rate = tmp_df2['rate'].max()
        is_bugged = False
        if max_rate > 6:
            is_bugged = True
            debug_print(f'{tag} is bugged! Flagging packets')
        rawdata_df.loc[rawdata_df['externalId'] == tag, 'isBugged'] = is_bugged


def parse_commastring(string):
    """
    parse string with comma or comma+space seperated values to list
    :type string: str
    :param string: input
    :rtype: list
    :return: list of values
    """
    if type(string) == float:
        try:
            if np.isnan(string):
                return None
        except Exception as e:
            pass
    if type(string) == list:
        return string
    if string is None:
        return list()
    cmd_list = ''.join(string.split()).split(',')
    return cmd_list


def parse_commastring_array(array):
    """
    parses Pandas array (DataFrame column) to list of all unique values
    :type array: Pandas array
    :param array: array
    :rtype: list
    :return: list of unique values
    """
    if len(array) == 1:
        return parse_commastring(array[0])
    result = list()
    for item in array:
        item_values = parse_commastring(item)
        if len(item_values) == 1:
            item_values
            if item_values[0] not in result:
                result.extend(item_values)
        else:
            for value in item_values:
                if value not in result:
                    result.extend([value])
    return result