import datetime
import json
import os
import time
import pandas as pd
import numpy as np
import plotly.express as px
import jinja2

from wiliot_api.api_client import WiliotCloudError
from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.interface.ble_sniffer import BLESniffer, BLESnifferContext
from wiliot_deployment_tools.interface.if_defines import RX_CHANNELS
from wiliot_deployment_tools.gw_certificate.tests.static.downlink_defines import *
from wiliot_deployment_tools.interface.mqtt import MqttClient
from wiliot_deployment_tools.interface.pkt_generator import BrgPktGenerator
from wiliot_deployment_tools.gw_certificate.tests.generic import PassCriteria, PERFECT_SCORE, MINIMUM_SCORE, INCONCLUSIVE_MINIMUM, GenericTest, GenericStage

class GenericDownlinkStage(GenericStage):
    def __init__(self, sniffer:BLESniffer, mqttc:MqttClient, pkt_gen:BrgPktGenerator, stage_name, **kwargs):
        self.__dict__.update(kwargs)
        super().__init__(stage_name=stage_name, **self.__dict__)        
        
        #Clients
        self.sniffer = sniffer
        self.mqttc = mqttc
        self.pkt_gen = pkt_gen
        
        #Stage Params
        self.sent_pkts = []
        self.sniffed_pkts = pd.DataFrame()
        
        #Paths
        self.sent_csv_path = os.path.join(self.test_dir, f'{self.stage_name}_sent.csv')
        self.sniffed_csv_path = os.path.join(self.test_dir, f'{self.stage_name}_sniffed.csv')
        self.graph_html_path = os.path.join(self.test_dir, f'{self.stage_name}.html')

        
    def prepare_stage(self):
        super().prepare_stage()
        self.sniffer.flush_pkts()
    
    def send_adv_payloads(self, tx_max_durations=TX_MAX_DURATIONS, retries=RETRIES):
        sent_pkts = []
        for tx_max_duration in tx_max_durations:
            debug_print(f'Tx Max Duration {tx_max_duration}')
            for retry in retries:
                self.pkt_gen.increment_all()
                brg_hb = self.pkt_gen.get_brg_hb()
                tx_max_retries = tx_max_duration//100
                sent_payload = self.mqttc.advertise_packet(raw_packet=brg_hb, tx_max_duration=tx_max_duration, use_retries=self.use_retries)
                debug_print(f'{sent_payload} sent to GW')

                sent_payload = json.dumps(sent_payload)
                sent_pkts.append({'tx_max_duration': tx_max_duration, 'tx_max_retries': tx_max_retries,
                                    'retry': retry, 'pkt': brg_hb[12:], 'payload': sent_payload, 'time_sent': datetime.datetime.now()})
                time.sleep(max(MAX_RX_TX_PERIOD_SECS, (tx_max_duration/1000)*1.2))
        time.sleep(10)
        return sent_pkts
        
    def process_sniffed_pkts(self, sent_pkts, sniffer:BLESniffer):
        for pkt in sent_pkts:
            # Get vars from dict
            raw_packet = pkt['pkt']
            # Get packets from sniffer
            sniffed_pkts = sniffer.get_filtered_packets(raw_packet=raw_packet)
            pkt['channel'] = str(sniffer.rx_channel)
            pkt['num_pkts_received'] = len(sniffed_pkts)
            self.sniffed_pkts = pd.concat([self.sniffed_pkts, sniffed_pkts.to_pandas()])
        self.sent_pkts += sent_pkts

    def generate_stage_report(self):
        # Create graph and trendline
        self.sent_pkts = pd.DataFrame(self.sent_pkts)
        x_value = ('tx_max_duration', 'TX Max Duration') if not self.use_retries else ('tx_max_retries', 'TX Max Retries')
        fig = px.scatter(self.sent_pkts, x=x_value[0], y='num_pkts_received', color='channel', title=f'Packets Received by Sniffer / {x_value[1]}',
                         trendline='ols', labels={x_value[0]: x_value[1], 'num_pkts_received': 'Number of packets received', 'channel': "BLE Adv. Channel"})
        fig.update_layout(scattermode="group", scattergap=0.95)
        trendline_info = px.get_trendline_results(fig)
        # Calculate whether stage pass/failed
        self.stage_pass = PERFECT_SCORE
        for channel, channel_df in trendline_info.groupby('BLE Adv. Channel'):
            channel_pass = PERFECT_SCORE
            channel_pkts = self.sent_pkts[self.sent_pkts['channel'] == channel]
            channel_trendline = channel_df['px_fit_results'].iloc[0]
            slope = channel_trendline.params[1]
            rsquared = channel_trendline.rsquared
            # Determine Channel Pass
            channel_pass, self.error_summary = PassCriteria.calc_for_stage_downlink(rsquared, slope, self.stage_name)
            if channel_pass < self.stage_pass:
                self.stage_pass = channel_pass
            self.add_to_stage_report(f"Channel {channel}: {PassCriteria.to_string(channel_pass)}")
            self.add_to_stage_report(f"- Total {len(channel_pkts['payload'])} MQTT payloads sent")
            self.add_to_stage_report(f"- Total {sum(channel_pkts['num_pkts_received'])} BLE Packets received by sniffer")
            self.add_to_stage_report(f"- R Value: {rsquared} | Slope: {slope}")
        # Export all stage data
        self.sent_pkts.to_csv(self.sent_csv_path)
        self.add_to_stage_report(f'Sent data saved - {self.sent_csv_path}')
        self.sniffed_pkts.to_csv(self.sniffed_csv_path)
        self.add_to_stage_report(f'Sniffed data saved - {self.sniffed_csv_path}')
        fig.write_html(self.graph_html_path)
        self.add_to_stage_report(f'Graph saved - {self.graph_html_path}')
        debug_print(self.report)
        
        # Generate HTML
        graph_div = fig.to_html(full_html=False, include_plotlyjs='cdn')
        self.report_html = self.template_engine.render_template('stage.html', stage=self, 
                                                                stage_report=self.report.split('\n'), graph = graph_div)
        return self.report
        
class SanityStage(GenericDownlinkStage):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.stage_tooltip = ("Verifies that the gateway advertises requested packets. "
                              "These are requested via Advertisement actions published to the 'update' topic (MQTT)")
        super().__init__(**self.__dict__, stage_name=type(self).__name__)

    def run(self):                
        self.start_time = datetime.datetime.now()
        for channel in RX_CHANNELS:
            debug_print(f'RX Channel {channel}')
            with BLESnifferContext(self.sniffer, channel) as sniffer:
                # Send the packets
                sent_pkts = self.send_adv_payloads(STAGE_CONFIGS[SANITY_STAGE][0], STAGE_CONFIGS[SANITY_STAGE][1])
                # Process sniffed packets
                self.process_sniffed_pkts(sent_pkts, sniffer)
        return True
class CorrelationStage(GenericDownlinkStage):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.stage_tooltip = ("Checks how consistently the gateway advertises packets. "
                              "Expects a consistently increasing packets count with increasing 'txMaxDuration'")
        super().__init__(**self.__dict__, stage_name=type(self).__name__)

    def run(self):                
        self.start_time = datetime.datetime.now()
        for channel in RX_CHANNELS:
            debug_print(f'RX Channel {channel}')
            with BLESnifferContext(self.sniffer, channel) as sniffer:
                # Send the packets
                sent_pkts = self.send_adv_payloads(STAGE_CONFIGS[CORRELATION_STAGE][0], STAGE_CONFIGS[CORRELATION_STAGE][1])
                # Process sniffed packets
                self.process_sniffed_pkts(sent_pkts, sniffer)
        return True
    
STAGES = [SanityStage, CorrelationStage]

class DownlinkTest(GenericTest):
    def __init__(self, **kwargs):        
        self.test_tooltip = "Stages related to actions & gateway advertisements"
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, test_name=type(self).__name__)
        self.pkt_gen = BrgPktGenerator()
        self.pkt_gen.set_bridge_id(DEFAULT_BRG_ID)
        self.use_retries = self.topic_suffix == '-test'
        self.stages = [stage(**self.__dict__) for stage in STAGES]
    
    def run(self):
        super().run()
        self.test_pass = PERFECT_SCORE
        for stage in self.stages:
            stage.prepare_stage()
            stage.run()
            self.add_to_test_report(stage.generate_stage_report())
            self.test_pass = PassCriteria.calc_for_test(self.test_pass, stage)
