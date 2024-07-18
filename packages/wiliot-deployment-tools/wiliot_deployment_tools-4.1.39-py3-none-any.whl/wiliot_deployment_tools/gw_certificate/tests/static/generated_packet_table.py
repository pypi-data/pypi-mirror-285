from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.interface.pkt_generator import BrgPktGeneratorNetwork
from wiliot_deployment_tools.interface.if_defines import *
from wiliot_deployment_tools.interface.packet_error import PacketError
import pkg_resources
import pandas as pd

CSV_NAME = 'packet_table.csv'
PACKET_TABLE_CSV_PATH = pkg_resources.resource_filename(__name__, CSV_NAME)

TEST_STRESS = 'stress'
TEST_COUPLING = 'coupling'
TEST_DOWNLINK = 'downlink'
TEST_UPLINK = 'uplink'
TEST_UNIFIED = 'unified'

TESTS = [TEST_COUPLING, TEST_UPLINK, TEST_UNIFIED]
class GeneratedPacketTable:
    
    def __init__(self) -> None:
        self.brg_network = BrgPktGeneratorNetwork()
        self.table = pd.read_csv(PACKET_TABLE_CSV_PATH)
    
    def get_data(self, test, duplication, time_delay, bridge_idx) -> list:    
        assert test in TESTS, 'Invalid Test'
        assert (duplication in UPLINK_DUPLICATIONS) or (duplication in UNIFIED_DUPLICATIONS), 'Invalid Duplication'
        assert (time_delay in UPLINK_TIME_DELAYS) or (time_delay in UNIFIED_TIME_DELAYS), 'Invalid Time Delay'
        assert bridge_idx in BRIDGES, 'Invalid Bridge'
        
        t = self.table
        return t.loc[((t['test'] == test) &
                      (t['duplication']==duplication) &
                      (t['time_delay'] == time_delay) &
                      (t['bridge_idx'] == bridge_idx))].to_dict('records')[0]
    
    def get_stress_data(self) -> pd.DataFrame:
        t = self.table
        return t.loc[((t['test'] == 'stress'))] 
            
    def _generate_packet_table(self):
        packet_list = []
        
        # UPLINK TEST
        for duplication in UPLINK_DUPLICATIONS:
            debug_print(f'Duplication {duplication}')
            for time_delay in UPLINK_TIME_DELAYS:
                debug_print(f'Time Delay {time_delay}')
                pkts = self.brg_network.get_new_pkt_pairs()
                for idx, brg in enumerate(self.brg_network.brg_list):
                    debug_print(f'Bridge {idx}')
                    data = pkts[idx]['data_packet']
                    si = pkts[idx]['si_packet']
                    brg_id = self.brg_network.brg_list[idx].bridge_id
                    # log the sent packet with relevant info from run
                    expected_pkt = brg.get_expected_uncoupled_mqtt()
                    for pkt in expected_pkt:
                        pkt.update({'duplication': duplication, 'time_delay': time_delay})
                    packet_list.append({'test': TEST_UPLINK,
                                        'duplication': duplication,
                                        'time_delay': time_delay,
                                        'bridge_idx': idx,
                                        'expected_mqtt': expected_pkt
                                        ,'data': data, 'si': si, 'bridge_id': brg_id,
                                        })
                    
        # UNIFIED TEST (BASED ON UPLINK TEST)
        for duplication in UNIFIED_DUPLICATIONS:
            debug_print(f'Duplication {duplication}')
            for time_delay in UNIFIED_TIME_DELAYS:
                debug_print(f'Time Delay {time_delay}')
                pkts = self.brg_network.get_new_pkt_unified()
                for idx, brg in enumerate(self.brg_network.brg_list):
                    debug_print(f'Bridge {idx}')
                    data = pkts[idx]['data_packet']
                    brg_id = self.brg_network.brg_list[idx].bridge_id
                    # log the sent packet with relevant info from run
                    expected_pkt = brg.get_expected_mqtt_unified(full_data_pkt=data)
                    for pkt in expected_pkt:
                        pkt.update({'duplication': duplication, 'time_delay': time_delay})
                    packet_list.append({'test': TEST_UNIFIED,
                                        'duplication': duplication,
                                        'time_delay': time_delay,
                                        'bridge_idx': idx,
                                        'expected_mqtt': expected_pkt
                                        ,'data': data, 'bridge_id': brg_id,
                                        })        

        #STRESS TEST
        i = 0
        while i < 5000:
            i += 1
            pkts = self.brg_network.get_new_pkt_unified()
            target_idx = 0  
            brg = self.brg_network.brg_list[target_idx]
            debug_print(f'Bridge {target_idx}')
            data = pkts[target_idx]['data_packet']
            brg_id = brg.bridge_id
            expected_pkt = brg.get_expected_mqtt_unified(full_data_pkt=data)
            packet_list.append({
                'test': TEST_STRESS,
                'bridge_idx': target_idx,
                'expected_mqtt': expected_pkt,
                'data': data,
                'bridge_id': brg_id,
            })          
        
        pd.DataFrame(packet_list).to_csv(PACKET_TABLE_CSV_PATH)

class CouplingRunData:
    def __init__(self, data) -> None:
        self.test = data['test']
        self.duplication = data['duplication']
        self.time_delay = data['time_delay']
        self.bridge_idx = data['bridge_idx']
        self.packet_error = eval(data['packet_error'])
        self.expected_mqtt = eval(data['expected_mqtt'])
        self.data = data['data']
        self.si = data['si']
        self.bridge_id = data['bridge_id']
        self.scattered_time_delay = data['scattered_time_delay']


    @classmethod
    def get_data(cls, test, duplication, time_delay, bridge_idx):
        packet_data = GeneratedPacketTable().get_data(test, duplication, time_delay, bridge_idx)
        return cls(packet_data)

class UplinkRunData:
    def __init__(self, data) -> None:
        self.test = data['test']
        self.duplication = data['duplication']
        self.time_delay = data['time_delay']
        self.bridge_idx = data['bridge_idx']
        self.expected_mqtt = eval(data['expected_mqtt'])
        self.data = data['data']
        self.si = data['si']
        self.bridge_id = data['bridge_id']   

    @classmethod
    def get_data(cls, test, duplication, time_delay, bridge_idx):
        packet_data = GeneratedPacketTable().get_data(test, duplication, time_delay, bridge_idx)
        return cls(packet_data)
    
class UnifiedRunData:
    def __init__(self, data) -> None:
        self.test = data['test']
        self.duplication = data['duplication']
        self.time_delay = data['time_delay']
        self.bridge_idx = data['bridge_idx']
        self.expected_mqtt = eval(data['expected_mqtt'])
        self.data = data['data']
        self.bridge_id = data['bridge_id']   

    @classmethod
    def get_data(cls, test, duplication, time_delay, bridge_idx):
        packet_data = GeneratedPacketTable().get_data(test, duplication, time_delay, bridge_idx)
        return cls(packet_data)

class StressRunData:
    def __init__(self) -> None:
        self.data = GeneratedPacketTable().get_stress_data()

if __name__ == "__main__":
    GeneratedPacketTable()._generate_packet_table()
