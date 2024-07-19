import datetime
import time
from wiliot_api.api_client import WiliotCloudError
from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.interface.ble_simulator import BLESimulator
from wiliot_deployment_tools.interface.if_defines import DEFAULT_DELAY, SEP
from wiliot_deployment_tools.interface.pkt_generator import BrgPktGenerator
from wiliot_deployment_tools.gw_certificate.tests.generic import PASS_STATUS, GenericTest


class GenericBrgMgmtStage():
    def __init__(self, ble_sim:BLESimulator, edge:ExtendedEdgeClient, stage_name, **kwargs):
        #Clients
        self.ble_sim = ble_sim
        self.edge = edge
        #Stage Params
        self.stage_name = stage_name
        self.stage_pass = False
        self.report = ''
        self.start_time = None

    def prepare_stage(self):
        debug_print(f'### Starting Stage: {self.stage_name}')
        self.ble_sim.set_sim_mode(True)

    def add_to_stage_report(self, report):
        self.report += '\n' + report

class InitStage(GenericBrgMgmtStage):
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, stage_name='init_stage')
        self.pkt_gen = BrgPktGenerator()
        
    def run(self):
        self.start_time = datetime.datetime.now()
        cfg_sent = datetime.datetime.now()- datetime.timedelta(minutes=1)
        hb_sent = datetime.datetime.now()- datetime.timedelta(minutes=1)
        now = datetime.datetime.now()
        brg_claimed = False
        brg_id = self.pkt_gen.bridge_id
        print(brg_id)
        while datetime.datetime.now() - self.start_time < datetime.timedelta(minutes=5) and not brg_claimed:
            pkts = self.pkt_gen.get_new_packets()
            if now - datetime.timedelta(seconds=5) > hb_sent:
                brg_hb = pkts['brg_hb']
                self.ble_sim.send_packet(brg_hb)
                time.sleep(DEFAULT_DELAY)
                print(pkts['brg_hb'].__dict__)
                hb_sent = now
            if now - datetime.timedelta(seconds=5) > cfg_sent:
                brg_cfg = pkts['brg_cfg']
                self.ble_sim.send_packet(brg_cfg)
                time.sleep(DEFAULT_DELAY)
                print(pkts['brg_cfg'].__dict__)
                cfg_sent = now
            try:
                self.edge.claim_bridge(brg_id)
            except WiliotCloudError as e:
                print(e)
            now = datetime.datetime.now()

STAGES = [InitStage]

class BrgMgmtTest(GenericTest):
    def __init__(self, **kwargs):        
        self.__dict__.update(kwargs)
        super().__init__(**self.__dict__, test_name=type(self).__name__)
        self.stages = [stage(**self.__dict__) for stage in STAGES]
    
    def run(self):
        self.start_time = datetime.datetime.now()
        self.test_pass = True
        for stage in self.stages:
            stage.prepare_stage()
            stage.run()
            # self.add_to_test_report(stage.generate_stage_report())
            # if stage.stage_pass == False:
            #     self.test_pass = False
        run_time = datetime.datetime.now() - self.start_time
        debug_print(f'\n{SEP}')
        debug_print(f'Bridge Management Test {PASS_STATUS[self.test_pass]}, Running time {run_time}')
        debug_print(self.report)
