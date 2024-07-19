from wiliot_deployment_tools.interface.uart_if import UARTInterface
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.interface.if_defines import *
import datetime
import time

class BLESimulator():
    def __init__(self, uart:UARTInterface):
        self.uart = uart
        self.sim_mode = False

    def set_sim_mode(self, sim_mode):
        self.uart.flush()
        mode_dict = {True: 1, False: 0}
        self.sim_mode = sim_mode
        self.uart.reset_gw()
        self.uart.write_ble_command(f"!ble_sim_init {mode_dict[sim_mode]}")
        if not sim_mode:
            self.uart.reset_gw()
        time.sleep(3)

    def send_packet(self, raw_packet, duplicates=DEFAULT_DUPLICATES, output_power=DEFAULT_OUTPUT_POWER, channel=SEND_ALL_ADV_CHANNELS, delay=DEFAULT_DELAY):
        assert self.sim_mode is True, 'BLE Sim not initialized!'
        if len(raw_packet) == 62:
            # Add ADVA
            raw_packet = DEFAULT_ADVA + raw_packet
        if len(raw_packet) != 74:
            raise ValueError('Raw Packet must be 62/74 chars long!')
        self.uart.write_ble_command(f"!ble_sim {str(raw_packet)} {str(duplicates)} {str(output_power)} {str(channel)} {str(delay)}")
        if delay > 0:
            diff = time.perf_counter()
            time.sleep((delay/1000) * duplicates)
            diff = time.perf_counter() - diff
            debug_print(f'Desired Delay: {(delay/1000) * duplicates} Actual Delay {diff}')

    
    def send_data_si_pair(self, data_packet, si_packet, duplicates, output_power=DEFAULT_OUTPUT_POWER, delay=DEFAULT_DELAY, packet_error=None):
        if packet_error is None:
            packet_error = [True for i in range (duplicates * 2)]
        # debug_print(packet_error)
        # print(f'delay {delay}')
        packet_to_send = data_packet
        def switch_packet(packet_to_send):
            if packet_to_send == data_packet:
                return si_packet
            else:
                return data_packet
        for dup in range(duplicates * 2):
            diff = time.perf_counter()
            if packet_error[dup]:
                debug_print(f'Sending Packet {dup}')
                self.send_packet(packet_to_send, duplicates=1, output_power=output_power, channel=SEND_ALL_ADV_CHANNELS, delay=0)
            else:
                debug_print(f'Dropping Packet {dup}')
            time.sleep(delay/1000)
            diff = time.perf_counter() - diff
            debug_print(f'Desired Delay: {delay/1000} Actual Delay {diff}')
            packet_to_send = switch_packet(packet_to_send)
    
    def trigger_by_time_stamp(self, ts):
        if ts == None:
            return
        current_time = datetime.datetime.timestamp(datetime.datetime.now()) * 1000
        time_difference = ts-current_time
        print(f"The test will start in: {time_difference/1000} secondes")
        time.sleep(time_difference/1000)

    def send_brg_network_pkts(self, pkts, duplicates, output_power=DEFAULT_OUTPUT_POWER):
        num_brgs = len(pkts)
        total_pkts_to_send = num_brgs * 2 * duplicates
        for pkt_idx in range(total_pkts_to_send):
            brg_idx = pkt_idx % 3
            pkt = pkts[brg_idx]
            pkt_idx_per_brg = pkt_idx // num_brgs
            if not bool(pkt_idx % 2):
                packet_to_send = pkt['data_packet']
            else:
                packet_to_send = pkt['si_packet']
            packet_error = pkt['packet_error']
            if packet_error[pkt_idx_per_brg]:
                debug_print(f'BRG {pkt["bridge_id"]}: Sending Packet {pkt_idx_per_brg}')
                self.send_packet(packet_to_send, duplicates=1, output_power=output_power,
                                 channel=SEND_ALL_ADV_CHANNELS, delay=0)
            else:
                debug_print(f'BRG {pkt["bridge_id"]}: Dropping Packet {pkt_idx_per_brg}')
            diff = time.perf_counter()
            delay = pkt['time_delay']
            time.sleep(delay/1000)
            diff = time.perf_counter() - diff
            debug_print(f'Desired Delay: {delay/1000} Actual Delay {diff}')

    def send_brg_network_pkts_unified(self, pkts, duplicates, delay, output_power=DEFAULT_OUTPUT_POWER):
        num_brgs = len(pkts)
        total_pkts_to_send = num_brgs * duplicates
        for pkt_idx in range(total_pkts_to_send):
            brg_idx = pkt_idx % 3
            pkt = pkts[brg_idx]
            pkt_idx_per_brg = pkt_idx // num_brgs
            packet_to_send = pkt['data_packet']
            debug_print(f'BRG {pkt["bridge_id"]}: Sending Packet {pkt_idx_per_brg}')
            self.send_packet(packet_to_send, duplicates=1, output_power=output_power,
                                channel=SEND_ALL_ADV_CHANNELS, delay=delay)