import copy
import datetime
import os
import re
import time
from typing import Literal
import pandas as pd
import plotly.express as px
import tabulate
from wiliot_deployment_tools.ag.ut_defines import PAYLOAD
from wiliot_deployment_tools.api.extended_api import GatewayType
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.gw_certificate.api_if.gw_capabilities import GWCapabilities
from wiliot_deployment_tools.interface.ble_simulator import BLESimulator
from wiliot_deployment_tools.interface.uart_if import UARTInterface
from wiliot_deployment_tools.gw_certificate.tests.static.uplink_defines import *
from wiliot_deployment_tools.interface.mqtt import MqttClient
from wiliot_deployment_tools.interface.pkt_generator import BrgPktGenerator
from wiliot_deployment_tools.gw_certificate.tests.static.generated_packet_table import StressRunData
from wiliot_deployment_tools.gw_certificate.tests.generic import PassCriteria, PERFECT_SCORE, GenericTest, GenericStage, INFORMATIVE
from wiliot_deployment_tools.interface.packet_error import PacketError
from wiliot_deployment_tools.gw_certificate.tests.static.generated_packet_table import CSV_NAME
import pkg_resources


# HELPER FUNCTIONS

def process_payload(packet:dict):
    payload = packet[PAYLOAD]
    payload = payload.upper()
    if len(payload) == 62:
        if payload[:4] == '1E16':
            payload = payload [4:]
    # big2little endian
    if payload[:4] == 'FCC6':
        payload = 'C6FC' + payload[4:]
    packet[PAYLOAD] = payload
    return packet


# TEST STAGES

class StressTestError(Exception):
    pass

class GenericStressStage(GenericStage):
    def __init__(self, mqttc:MqttClient, ble_sim:BLESimulator, gw_capabilities:GWCapabilities, stage_name,
                **kwargs):
        self.__dict__.update(kwargs)
        super().__init__(stage_name=stage_name, **self.__dict__)
        
        self.result_indication = INFORMATIVE        
        
        # Clients
        self.mqttc = mqttc
        self.ble_sim = ble_sim

        # Packets list
        self.local_pkts = []
        self.mqtt_pkts = []
        self.full_test_pkts = pd.DataFrame()
        
        # GW Capabilities
        self.gw_capabilities = gw_capabilities
        
        # Packet Error
        self.packet_error = PacketError()

        #Run Data
        self.run_stress_data = StressRunData()
        
        # Data extracted from the test csv
        self.all_test_payloads = None
    
    def prepare_stage(self, reset_ble_sim=True):
        super().prepare_stage()
        self.mqttc.flush_messages()
        if reset_ble_sim:
            self.ble_sim.set_sim_mode(True) 
        
    def fetch_mqtt_from_stage(self):
        mqtt_pkts = self.mqttc.get_all_tags_pkts()
        self.mqtt_pkts = list(map(lambda p: process_payload(p), mqtt_pkts))
    
    def compare_local_mqtt(self):
        self.fetch_mqtt_from_stage()
        local_pkts_df = pd.DataFrame(self.local_pkts)
        mqtt_pkts_df = pd.DataFrame(self.mqtt_pkts)
        comparison = local_pkts_df

        if PAYLOAD not in mqtt_pkts_df.columns:
            mqtt_pkts_df[PAYLOAD] = ''
        received_pkts_df = pd.merge(local_pkts_df[PAYLOAD], mqtt_pkts_df[PAYLOAD], how='inner')
        
        received_pkts = set(received_pkts_df[PAYLOAD])

        self.pkts_received_count = pd.Series.count(received_pkts_df)
        unique_received_count = len(received_pkts)
        self.pkts_filtered_out_count = self.pkts_received_count - unique_received_count

        comparison[RECEIVED] = comparison[PAYLOAD].isin(received_pkts)
        comparison['pkt_id'] = comparison['payload'].apply(lambda x: x[-8:])
        self.comparison = comparison

class StressTestStage(GenericStressStage):
    
    def __init__(self, mqttc, ble_sim, gw_capabilities, **kwargs):
        super().__init__(mqttc, ble_sim, gw_capabilities, stage_name=type(self).__name__, **kwargs)
        self.delays = [255, 200, 130, 100, 60, 30, 20, 10, 5]
        self.duplicates = 3
        self.report_data = {}
        self.stage_tooltip = "Attempts different PPS (packets per second) rates to examine the gateway limit"
        
    def run(self):
        for delay in self.delays:
            self.stress_delay = delay
            debug_print(f"---Running Stress Test with delay of {delay}")
            self.run_full_stress_test(delay)

    def run_full_stress_test(self, delay):
        self.prepare_stage()
        self.run_stress_test_with_delay(delay)
        self.generate_stage_report()
        self.teardown_stage()

    def prepare_stage(self):
        super().prepare_stage()
        self.local_pkts = []
        self.start_time = datetime.datetime.now()

    def run_stress_test_with_delay(self, delay):
        run_data = self.run_stress_data.data
        for index, row in run_data.iterrows():
            if datetime.datetime.now() > self.start_time + datetime.timedelta(seconds=60):
                break
            data = row['data']
            expected_mqtt = eval(row['expected_mqtt'])
            self.local_pkts.extend(expected_mqtt)
            self.ble_sim.send_packet(data, duplicates=self.duplicates, delay=delay)
        time.sleep(15)

    def teardown_stage(self):
        self.ble_sim.set_sim_mode(False)
        self.mqttc.flush_messages()

    def generate_stage_report(self):
        def save_to_csv(df, csv_path):
            """
            Save a DataFrame to a CSV file without overwriting existing content.
            
            :param df: The DataFrame to be saved.
            :param csv_path: The path to the CSV file.
            """
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                df.to_csv(csv_path, mode='a', header=False, index=False)
            else:
                df.to_csv(csv_path, mode='w', header=True, index=False)
                
        self.compare_local_mqtt()
        report = []
        num_pkts_sent = len(self.comparison)
        num_pkts_received = self.comparison['received'].eq(True).sum()
        self.stage_pass = PERFECT_SCORE    
        self.comparison['time_delay'] = self.stress_delay
        self.full_test_pkts = pd.concat([self.full_test_pkts, self.comparison], ignore_index=True)
        save_to_csv(self.comparison, self.csv_path)
        
        if str(self.stress_delay) not in self.report_data:
                self.report_data[str(self.stress_delay)] = {}
        self.report_data[str(self.stress_delay)]['pkts_sent'] = num_pkts_sent
        self.report_data[str(self.stress_delay)]['pkts_recieved'] = num_pkts_received
        self.report_data[str(self.stress_delay)]['pkts_per_sec_desired'] = 1000 / (self.stress_delay * self.duplicates)
        self.report_data[str(self.stress_delay)]['pkts_per_sec_actual'] = num_pkts_sent / 60
        self.report_data[str(self.stress_delay)]['percent_of_false_recieved'] = 100 - (num_pkts_received * 100 / num_pkts_sent)
        
        if self.stress_delay == self.delays[-1]:
            
            self.stage_pass = PassCriteria.calc_for_stage_stress(self.stage_pass, self.stage_name)
            
            for delay in self.delays:
                delay = str(delay)
                report.append((f'Test - {self.report_data[delay]["pkts_per_sec_desired"]} packets per second. Actual packet per second - ', self.report_data[delay]["pkts_per_sec_actual"]))
                report.append(((f'Number of packets sent'), self.report_data[delay]['pkts_sent']))
                report.append(((f'Number of packets received'), self.report_data[delay]['pkts_recieved']))
            self.add_to_stage_report(f'---Stage {self.stage_name} {PassCriteria.to_string(self.stage_pass)}, Running time {datetime.datetime.now() - self.start_time}')
            self.add_to_stage_report(tabulate.tabulate(pd.DataFrame(report), showindex=False))   
            self.add_to_stage_report(f'Stage data saved - {self.csv_path}')
            fig_data = pd.DataFrame.from_dict(self.report_data, orient='index')
            fig_data.reset_index(inplace=True)
            fig_data.rename(columns={'index': 'time_delay'}, inplace=True)
            fig = px.line(fig_data, x='pkts_per_sec_actual', y='percent_of_false_recieved', title='Percentage of packets not recieved by packets per second sent',
              labels={'pkts_per_sec_actual': 'Packets Sent Per Second', 'false_percentage': 'Percentage of packets not recieved'})
            graph_div = fig.to_html(full_html=False, include_plotlyjs='cdn')
            
            # Generate HTML
            table_html = self.template_engine.render_template('table.html', dataframe=self.comparison.to_html(table_id=self.stage_name), table_id=self.stage_name)
            self.report_html = self.template_engine.render_template('stage.html', stage=self, 
                                                                    stage_report=self.report.split('\n'), graph=graph_div)
            
            return self.report
        
        
STAGES = [StressTestStage] 

class StressTest(GenericTest):
    def __init__(self, **kwargs):        
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, test_name=type(self).__name__)
        self.all_messages_in_test = []
        self.stages = [stage(**self.__dict__) for stage in STAGES]
        self.result_indication = INFORMATIVE
        self.test_tooltip = "Stages attempting to stress test a maximum throughput"

    def run(self):
        super().run()
        self.test_pass = PERFECT_SCORE
        for stage in self.stages:
            stage.prepare_stage()
            stage.run()
            self.test_pass = PassCriteria.calc_for_test(self.test_pass, stage)
            self.all_messages_in_test.extend(self.mqttc.get_all_messages_from_topic('data'))
    
