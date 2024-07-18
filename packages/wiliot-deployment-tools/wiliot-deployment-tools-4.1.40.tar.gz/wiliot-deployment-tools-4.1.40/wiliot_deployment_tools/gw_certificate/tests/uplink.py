import copy
import datetime
import os
import time
from typing import Literal
import pandas as pd
import plotly.express as px
import tabulate
from wiliot_deployment_tools.ag.ut_defines import BRIDGE_ID, NFPKT, PAYLOAD, RSSI, LAT, LNG
from wiliot_deployment_tools.api.extended_api import GatewayType
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.gw_certificate.api_if.gw_capabilities import GWCapabilities
from wiliot_deployment_tools.gw_certificate.tests.static.coupling_defines import INCREMENTAL_STAGE_ADVA
from wiliot_deployment_tools.interface.ble_simulator import BLESimulator
from wiliot_deployment_tools.interface.if_defines import BRIDGES, DEFAULT_DELAY, LOCATION
from wiliot_deployment_tools.interface.uart_if import UARTInterface
from wiliot_deployment_tools.gw_certificate.tests.static.uplink_defines import *
from wiliot_deployment_tools.interface.mqtt import MqttClient
from wiliot_deployment_tools.interface.pkt_generator import BrgPktGenerator, BrgPktGeneratorNetwork, TagPktGenerator
from wiliot_deployment_tools.gw_certificate.tests.static.generated_packet_table import TEST_COUPLING, TEST_UPLINK, TEST_UNIFIED, CouplingRunData, UplinkRunData, UnifiedRunData
from wiliot_deployment_tools.gw_certificate.tests.generic import PassCriteria, PERFECT_SCORE, MINIMUM_SCORE, INCONCLUSIVE_MINIMUM, INIT_INCONCLUSIVE_MINIMUM, GenericTest, GenericStage
from wiliot_deployment_tools.interface.packet_error import PacketError
from wiliot_deployment_tools.gw_certificate.api_if.api_validation import MESSAGE_TYPES, validate_message
from wiliot_deployment_tools.gw_certificate.tests.static.generated_packet_table import CSV_NAME
import pkg_resources


# HELPER DEFINES
TABLE_SUFFIX = "Table"

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

class UplinkTestError(Exception):
    pass

class GenericUplinkStage(GenericStage):
    def __init__(self, mqttc:MqttClient, ble_sim:BLESimulator, gw_capabilities:GWCapabilities, stage_name,
                **kwargs):
        self.__dict__.update(kwargs)
        super().__init__(stage_name=stage_name, **self.__dict__)
                
        # Clients
        self.mqttc = mqttc
        self.ble_sim = ble_sim

        # Packets list
        self.local_pkts = []
        self.mqtt_pkts = []
        
        # GW Capabilities
        self.gw_capabilities = gw_capabilities
        
        # Packet Error / Run data
        self.packet_error = PacketError()
        self.run_data = UplinkRunData
        
        # Unified stage
        self.run_data_unified = UnifiedRunData

        # Data extracted from the test csv
        self.all_test_payloads = None
        self.alias_bridge_id_df = None
    
    def prepare_stage(self, reset_ble_sim=True):
        super().prepare_stage()
        self.mqttc.flush_messages()
        if reset_ble_sim:
            self.ble_sim.set_sim_mode(True) 
        
    def fetch_mqtt_from_stage(self):
        mqtt_pkts = self.mqttc.get_all_tags_pkts()
        self.mqtt_pkts = list(map(lambda p: process_payload(p), mqtt_pkts))
    
    ## TODO - REWRITE
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
                
    def generate_stage_report(self):
        """
        Generates report for the stage
        """
        self.compare_local_mqtt()
        report = []
        num_pkts_sent = len(self.comparison)
        num_pkts_received = self.comparison['received'].eq(True).sum()
        self.stage_pass = num_pkts_received / num_pkts_sent * PERFECT_SCORE
        self.stage_pass, self.error_summary = PassCriteria.calc_for_stage_uplink(self.stage_pass, self.stage_name)

        report.append(((f'Number of unique packets sent'), num_pkts_sent))
        report.append(((f'Number of unique packets received'), num_pkts_received))
        report.append(((f'Number of total packets received'), self.pkts_received_count))
        report.append(((f'Number of duplicates out of total'), self.pkts_filtered_out_count))
        self.add_to_stage_report(f'---Stage {self.stage_name} {PassCriteria.to_string(self.stage_pass)}, Running time {datetime.datetime.now() - self.start_time}')
        self.add_to_stage_report(tabulate.tabulate(pd.DataFrame(report), showindex=False))
        not_received = self.comparison[self.comparison[RECEIVED]==False][REPORT_COLUMNS]
        if len(not_received) > 0:
            self.add_to_stage_report('Packets not received:')
            self.add_to_stage_report(tabulate.tabulate(not_received, headers='keys', showindex=False))
        self.comparison.to_csv(self.csv_path)
        self.add_to_stage_report(f'Stage data saved - {self.csv_path}')
        debug_print(self.report)
        
        # Generate HTML
        table_html = self.template_engine.render_template('table.html', dataframe=self.comparison.to_html(table_id=self.stage_name + TABLE_SUFFIX),
                                                          table_id=self.stage_name + TABLE_SUFFIX)
        self.report_html = self.template_engine.render_template('stage.html', stage=self, 
                                                                stage_report=self.report.split('\n'), table=table_html)
        
        return self.report
    
# Unified Stages
class OneBrgUnifiedPacketStage(GenericUplinkStage):
# currently only one bridge is simulated. If we want to simulate more, then make sure that they have different parameters to send (rssi,nfpkt,latency,global pacing group)
    def __init__(self, **kwargs):
        self.stage_tooltip = "Simulates advertisements from a single bridge. Expects the gateway to scan & upload them"

        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, stage_name=type(self).__name__)
        self.pkt_gen = BrgPktGenerator()

    def run(self):
        self.start_time = datetime.datetime.now()
        for duplication in UNIFIED_DUPLICATIONS:
            debug_print(f'Duplication {duplication}')
            for time_delay in UNIFIED_TIME_DELAYS:
                debug_print(f'Time Delay {time_delay}')
                run_data = self.run_data_unified.get_data(TEST_UNIFIED, duplication, time_delay, BRIDGES[0])
                data = run_data.data
                self.local_pkts.extend(run_data.expected_mqtt)
                for dup in range(duplication):
                    self.ble_sim.send_packet(data, duplicates=1, delay=time_delay)
            time.sleep(5)

class ThreeBrgUnifiedPacketStage(GenericUplinkStage):  

    def __init__(self, **kwargs):
        self.stage_tooltip = "Simulates advertisements from three bridges. Expects the gateway to scan & upload them"
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, stage_name=type(self).__name__)
        self.brg_network = BrgPktGeneratorNetwork()
    
    def run(self):
        self.start_time = datetime.datetime.now()
        for duplication in UNIFIED_DUPLICATIONS:
            debug_print(f'Duplication {duplication}')
            for time_delay in UNIFIED_TIME_DELAYS:
                debug_print(f'Time Delay {time_delay}')
                # Construct packet list from data
                pkts = []
                for brg_idx in BRIDGES:
                    pkt = {}
                    run_data = self.run_data_unified.get_data(TEST_UNIFIED, duplication, time_delay, brg_idx)
                    pkt['data_packet'] = run_data.data
                    pkt['bridge_id'] = run_data.bridge_id
                    self.local_pkts.extend(run_data.expected_mqtt)
                    pkts.append(pkt)
                # Send packets
                self.ble_sim.send_brg_network_pkts_unified(pkts, duplication, delay=time_delay)
        time.sleep(5)

class ApiValidationStage(GenericUplinkStage):
    def __init__(self, **kwargs):
        self.stage_tooltip = "Validates the JSON structure of messages uploaded by the gateway in previous stages"
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, stage_name=type(self).__name__)
    
    def prepare_stage(self):
        super().prepare_stage(reset_ble_sim=False)
        self.mqttc.flush_messages()

    def run(self):
        pass

    def generate_stage_report(self, **kwargs):
        report = []
        all_validations = []
        self.stage_pass = PERFECT_SCORE
                                
        for idx, message in enumerate(self.all_messages_in_test):
            message_body = message.body
            if len(message_body['packets']) == 0:
                continue
            validation = validate_message(MESSAGE_TYPES.DATA, message_body)
            errors = []
            for e in validation[1]:
                if e.message not in errors:
                    errors.append(e.message)
            all_validations.append({'valid':validation[0], 'errors': errors, 'message': message_body,})
            if not validation[0]:
                if 'Validation Errors:' not in report:
                    report.append('Validation Errors:')
                report.append(f'- Message (idx={idx}) Errors:')
                for e in errors:
                    report.append(e)
                self.stage_pass = MINIMUM_SCORE
                error_explainer = "API (JSON strcture) is invalid. "
                if error_explainer not in self.error_summary:
                    self.error_summary = error_explainer


        # Set stage as FAIL if no messages were received:
        if len(self.all_messages_in_test) == 0:
            self.stage_pass = MINIMUM_SCORE

        self.add_to_stage_report(f'---Stage {self.stage_name} {PassCriteria.to_string(self.stage_pass)}')
        # Add all messages that failed to validate to report
        for line in report:
            self.add_to_stage_report(line)
        all_validations_df = pd.DataFrame(all_validations)
        all_validations_df.to_csv(self.csv_path)
        self.add_to_stage_report(f'Stage data saved - {self.csv_path}')
        debug_print(self.report)
        
        #Generate HTML
        table_html = self.template_engine.render_template('table.html', dataframe=all_validations_df.to_html(table_id=self.stage_name + TABLE_SUFFIX),
                                                          table_id=self.stage_name + TABLE_SUFFIX)
        self.report_html = self.template_engine.render_template('stage.html', stage=self, 
                                                                stage_report=self.report.split('\n'))
        return self.report

class SequentialSequenceIdStage(GenericUplinkStage):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.stage_tooltip = "Validates expected sequenceId in all packets"
        super().__init__(**self.__dict__, stage_name=type(self).__name__)
    
    def prepare_stage(self):
        super().prepare_stage(reset_ble_sim=False)
        self.mqttc.flush_messages()

    def run(self):
        pass

    def generate_stage_report(self, **kwargs):
        report = []
        self.stage_pass = PERFECT_SCORE
        required_sequenceId = None
        sequenceId_valid = True

        def is_sequenceId_incremental(idx, message):
            nonlocal required_sequenceId, sequenceId_valid
            packets = message['packets']

            # check that there is sequenceId in all packets
            packets_w_seqid = list(filter(lambda p: 'sequenceId' in p, packets))
            if len(packets_w_seqid) == 0:
                sequenceId_valid = False
                report.append(f'No sequenceId in message {idx}. Expected sequenceId in all packets')
                self.error_summary = self.error_summary + 'No SequenceId in packets.'
                return False
            
            # initialize the required sequenceId 
            if idx == 0:
                first_pkt = packets[0]
                required_sequenceId = first_pkt['sequenceId'] 
            
            # check that for every packet in message the sequenceId is incremental:
            for pkt in packets:
                pkt_sequenceId = pkt['sequenceId']
                if pkt_sequenceId != required_sequenceId:
                    if sequenceId_valid == True:
                        report.append(f'SequenceId is not incremental. Expected sequenceId is {required_sequenceId} but the packet sequenceId is {pkt_sequenceId}')
                        self.stage_pass = MINIMUM_SCORE
                        self.error_summary = self.error_summary + 'SequenceId is not incremental. '
                        sequenceId_valid = False
                    break
                required_sequenceId += 1

        # Set message type according to coupling, location
        for idx, message in enumerate(self.all_messages_in_test):
            message_body = message.body
            is_sequenceId_incremental(idx=idx, message=message_body)

        self.add_to_stage_report(f'---Stage {self.stage_name} {PassCriteria.to_string(self.stage_pass)}')
        self.add_to_stage_report(f"{'---SequenceId is incremental' if sequenceId_valid else '---SequenceId is NOT incremental'}")
        debug_print(self.report)
        
        #Generate HTML
        self.report_html = self.template_engine.render_template('stage.html', stage=self, 
                                                                stage_report=self.report.split('\n'))
        return self.report

class AliasBridgeIDStage(GenericUplinkStage):
    def __init__(self, **kwargs):
        self.stage_tooltip = "Validates the expected alias bridge ID (For unified SideInfo packets)"
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, stage_name=type(self).__name__)
    
    def prepare_stage(self):
        super().prepare_stage(reset_ble_sim=False)
        self.mqttc.flush_messages()

    def run(self):
        pass

    def get_data_from_test_csv(self):
        relative_path = 'static/' + CSV_NAME
        csv_path = pkg_resources.resource_filename(__name__, relative_path)
        df = pd.read_csv(csv_path)

        # Store all test payloads
        all_payloads = df['data'].str[12:]
        self.all_test_payloads = all_payloads.tolist()

        def _parser(row, desired:Literal['adva', 'without_adva']):
            if desired == 'adva':
                output_string = row.at['data'][:12]
            elif desired == 'without_adva':
                output_string = row.at['data'][12:]
            else:
                raise ValueError
            return output_string

        # Create data set for alias bridge verification
        alias_bridge_id_df = df[df['test'] == 'unified'].copy()
        alias_bridge_id_df['payload'] = alias_bridge_id_df.apply(lambda row: _parser(row, 'without_adva'), axis=1)
        # .apply(lambda row: self._generate_interferers_data(), axis=1)
        alias_bridge_id_df['alias_bridge_id'] = alias_bridge_id_df.apply(lambda row: _parser(row, 'adva'), axis=1)
        # Convert bridge_id to little endian:
        alias_bridge_id_df['alias_bridge_id'] = alias_bridge_id_df['alias_bridge_id'].apply(lambda x: ''.join(format(byte, '02X') for byte in bytes.fromhex(x)[::-1]))
        self.alias_bridge_id_df = alias_bridge_id_df
   
    def generate_stage_report(self, **kwargs):
        report = []
        self.stage_pass = PERFECT_SCORE
        self.get_data_from_test_csv()
        aliasBridgeId_valid = True
            
        def filter_non_test_packets(message):
            packets = message['packets']
            filtered_pkts = []
            for pkt in packets:
                pkt = process_payload(pkt)
                payload = pkt['payload']
                if any(payload in test_payload for test_payload in self.all_test_payloads):
                    filtered_pkts.append(pkt)
            message['packets'] = filtered_pkts
                    
        def is_alias_bridge_id_valid(message): 
            nonlocal aliasBridgeId_valid
            packets = message['packets']

            for pkt in packets:
                if 'aliasBridgeId' in pkt: 
                    pkt_payload = pkt['payload']
                    pkt_alias_bridge_id = pkt['aliasBridgeId']
                    validation_data = self.alias_bridge_id_df[self.alias_bridge_id_df['payload'].str.contains(pkt_payload)] 
                    required_bridge_id = validation_data['alias_bridge_id'].iat[0]
                    if required_bridge_id != pkt_alias_bridge_id:
                        report.append(f"Alias bridge ID of the packet does not match. The required alias bridge ID is {required_bridge_id} but the packet alias bridge ID is {pkt_alias_bridge_id}")
                        self.stage_pass = MINIMUM_SCORE
                        self.error_summary = self.error_summary + "aliasBridgeId doesn't match the expected one of a packet. "
                        aliasBridgeId_valid = False 

        # Set message type according to coupling, location
        for idx, message in enumerate(self.all_messages_in_test):
            message_body = message.body
            filter_non_test_packets(message_body)
            if len(message_body['packets']) == 0:
                continue
            is_alias_bridge_id_valid(message=message_body)
        # Set stage as FAIL if no messages were received:
        if len(self.all_messages_in_test) == 0:
            self.stage_pass = MINIMUM_SCORE
            self.error_summary = self.error_summary + "No packets were recevied. "

        self.add_to_stage_report(f'---Stage {self.stage_name} {PassCriteria.to_string(self.stage_pass)}')
        self.add_to_stage_report(f"{'---Alias bridge ID is valid' if aliasBridgeId_valid else '---Alias bridge ID is NOT valid'}")
        # Add all messages that failed to validate to report
        debug_print(self.report)
        
        #Generate HTML
        self.report_html = self.template_engine.render_template('stage.html', stage=self, 
                                                                stage_report=self.report.split('\n'))
        return self.report



class GeolocationStage(GenericUplinkStage):
    def __init__(self, **kwargs):
        self.stage_tooltip = "Checks if lat/lng were uploaded under 'location' (optional JSON key) in the uploaded data messages"
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, stage_name=type(self).__name__)
        self.graph_html_path = os.path.join(self.test_dir, f'{self.stage_name}.html')

    
    def prepare_stage(self):
        super().prepare_stage(reset_ble_sim=False)
        self.mqttc.flush_messages()

    def run(self):
        pass
    
    def generate_stage_report(self, **kwargs):
        locations_list = []
        locations_df = pd.DataFrame()
        self.stage_pass = MINIMUM_SCORE
        self.error_summary = "No coordinates were uploaded. "

        # Set message type according to coupling, location
        for message in self.all_messages_in_test:
            message = message.body
            timestamp = message[TIMESTAMP]
            if LOCATION in message.keys():
                loc = message[LOCATION]
                loc.update({TIMESTAMP:timestamp})
                locations_list.append(loc)
        num_unique_locs = 0
        if len(locations_list) > 0:
            self.stage_pass = PERFECT_SCORE
            self.error_summary = ''
            locations_df = pd.DataFrame(locations_list)
            num_unique_locs = locations_df[['lat', 'lng']].drop_duplicates().shape[0]
            fig = px.scatter_mapbox(locations_df, lat=LAT, lon=LNG, color='timestamp', zoom=10)
            fig.update(layout_coloraxis_showscale=False)
            fig.update_layout(scattermode="group", scattergap=0.95, mapbox_style="open-street-map")

        self.add_to_stage_report(f'---Stage {self.stage_name} {PassCriteria.to_string(self.stage_pass)}')
        self.add_to_stage_report(f'Number of unique locations received: {num_unique_locs}')
        # Export all stage data
        locations_df.to_csv(self.csv_path)
        self.add_to_stage_report(f'Stage data saved - {self.csv_path}')
        if num_unique_locs > 0:
            fig.write_html(self.graph_html_path)
        debug_print(self.report)
        
        #Generate HTML
        graph_div = fig.to_html(full_html=False, include_plotlyjs='cdn') if num_unique_locs > 0 else "No graph to display"
        self.report_html = self.template_engine.render_template('stage.html', stage=self, 
                                                                stage_report=self.report.split('\n'), graph = graph_div)
        return self.report


# TEST CLASS
UNCOUPLED_STAGES = [OneBrgUnifiedPacketStage, ThreeBrgUnifiedPacketStage, ApiValidationStage, SequentialSequenceIdStage, AliasBridgeIDStage] 

class UplinkTest(GenericTest):
    def __init__(self, **kwargs):
        self.test_tooltip = "Stages related to gateway BLE scans & MQTT data uploads"
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, test_name=type(self).__name__)
        self.all_messages_in_test = []
        stages = UNCOUPLED_STAGES
        if self.gw_capabilities.geoLocationSupport:
            stages.append(GeolocationStage)
        self.stages = [stage(**self.__dict__) for stage in stages]
        

    def run(self):
        super().run()
        self.test_pass = PERFECT_SCORE
        for stage in self.stages:
            stage.prepare_stage()
            stage.run()
            self.add_to_test_report(stage.generate_stage_report())
            self.test_pass = PassCriteria.calc_for_test(self.test_pass, stage)
            self.all_messages_in_test.extend(self.mqttc.get_all_messages_from_topic('data'))
    
