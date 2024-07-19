import random
import pandas as pd

class PacketError:
    def __init__(self):
        pass
            
    @staticmethod
    def _generate_packet_error(duplication):
        # data is sent first
        data_idx = range(0, duplication*2, 2)
        # si is sent after every data packet
        si_idx = range(1, (duplication*2)+1, 2)
        # never drop all data / si packets
        dropped_data = random.sample(data_idx, k=random.randint(0, duplication-1))
        dropped_si = random.sample(si_idx, k=random.randint(0, duplication-1))
        dropped_packets = dropped_data+dropped_si
        drop_packet_by_idx = [True for idx in range(duplication*2)]
        # mark chosen packets as False (dropped)
        for idx in dropped_packets:
            drop_packet_by_idx[idx] = False
        return drop_packet_by_idx