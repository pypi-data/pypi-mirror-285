import ast
import logging
import pandas as pd
from wiliot_deployment_tools.interface.uart_if import UARTInterface
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.interface.if_defines import *
import time
import datetime
import threading
import binascii

class SnifferPkt():
    def __init__(self, raw_output, time_received, rx_channel):
        self.adva = raw_output[:12]
        self.packet = raw_output[12:74]
        try:
            self.rssi = int.from_bytes(binascii.unhexlify(raw_output[74:]), 'big') * -1
        except ValueError:
            self.rssi = 99
        self.time_received = time_received
        self.rx_channel = rx_channel

    def __repr__(self):
        return f'CH{self.rx_channel}|{self.adva}{self.packet} RSSI:{self.rssi} {self.time_received}'

    def to_dict(self):
        return {'adva': self.adva, 'packet': self.packet, 'rssi': self.rssi, 'time_received': self.time_received, 'rx_channel': self.rx_channel}

class SnifferPkts():
    def __init__(self, pkts=[]):
        self.pkts = pkts

    def __add__(self, other):
        return SnifferPkts(self.pkts + other.pkts)

    def __len__(self):
        return len(self.pkts)

    def __repr__(self):
        return self.pkts

    def process_pkt(self, raw_output, time_received, rx_channel, print_pkt=False):
        pkt = SnifferPkt(raw_output, time_received, rx_channel)
        self.pkts.append(pkt)
        if print_pkt:
            print(pkt)
        return pkt

    def filter_pkts(self, raw_packet=None, adva=None, time_range:tuple=None):
        result = []
        for pkt in self.pkts:
            if (raw_packet is not None) and (pkt.packet == raw_packet) or \
                (adva is not None) and (pkt.adva == adva) or \
                (time_range is not None) and (time_range[0] < pkt.time_received < time_range[1]):
                result.append(pkt)
        return SnifferPkts(result)

    def flush_pkts(self):
        self.pkts = []

    def to_list(self):
        return [p.to_dict() for p in self.pkts]

    def to_pandas(self):
        return pd.DataFrame().from_dict(self.to_list())

def cur_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class BLESniffer():
    def __init__(self, uart:UARTInterface, print_pkt=False, logger_filepath=None):
        self.uart = uart
        self.listener_thread = None
        self.sniffer_pkts = SnifferPkts()
        self.listening = False
        self.listener_lock = threading.Lock()
        self.print = print_pkt
        self.rx_channel = 0
        
        # Configure Logger
        logger = logging.getLogger('ble_sniffer')
        logger.setLevel(logging.DEBUG)
        if logger_filepath is not None:
            # create file handler
            fh = logging.FileHandler(logger_filepath)
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            logger.propagate = False # Do not send logs to 'root' logger
            debug_print(f'BLE Sniffer Logger initialized at {logger_filepath}')
        self.logger = logger

    def packet_listener(self):
        while self.listening:
            line = self.uart.read_line()
            if line is not None and len(line) == 76:
                with self.listener_lock:
                    pkt = self.sniffer_pkts.process_pkt(line, datetime.datetime.now(), self.rx_channel, self.print)
                    self.logger.info(pkt)

    # Change sniffing modes
    def start_sniffer(self, rx_channel):
        self.logger.debug(f'{cur_time()} | Starting Sniffer on CH{rx_channel}')
        self.uart.set_sniffer(rx_channel)
        self.rx_channel = rx_channel
        self.listener_thread = threading.Thread(target=self.packet_listener)
        self.listening = True
        self.listener_thread.start()

    def stop_sniffer(self):
        self.logger.debug(f'{cur_time()} | Stopping Sniffer')
        self.flush_pkts()
        self.listening = False
        if self.listener_thread is not None:
            self.listener_thread.join()
            self.listener_thread = None
            self.uart.cancel_sniffer()
        self.rx_channel = 0

    def reset_sniffer(self, rx_channel):
        self.logger.debug(f'{cur_time()} | Reseting Sniffer')
        self.stop_sniffer()
        self.start_sniffer(rx_channel)
        self.flush_pkts()

    # Data Handling
    def get_all_pkts(self):
        return self.sniffer_pkts

    def get_filtered_packets(self, raw_packet=None, adva=None, time_range:tuple=None):
        return self.sniffer_pkts.filter_pkts(raw_packet, adva, time_range)

    def flush_pkts(self):
        self.logger.debug(f'{cur_time()} | Flushing packets')
        self.sniffer_pkts.flush_pkts()

    def to_pandas(self):
        return self.sniffer_pkts.to_pandas()

    # Packet Counters
    def get_pkts_cntrs(self, channel, lookout_time=DEFAULT_LOOKOUT_TIME):
        self.logger.debug(f'{cur_time()} | Getting pkt counters for CH{channel}')
        if self.rx_channel != channel:
            self.uart.set_rx(channel)
            self.rx_channel = channel
        
        lookout_time = lookout_time
        pkt_cntrs = None
        self.uart.flush()
        self.uart.write_ble_command(GET_LOGGER_COUNTERS)
        start_time = time.time()
        current_time = start_time
        while current_time - start_time < lookout_time:
            line = self.uart.read_line()
            if line is not None and "'bad_crc'" in line:
                start_of_cntr_index = line.find('{')
                pkt_cntrs = line[start_of_cntr_index:]
                debug_print(f"pkt_cntrs: {pkt_cntrs}")
                return ast.literal_eval(pkt_cntrs)
            current_time = time.time()
        debug_print(f"No counter received within the time limit of {lookout_time} seconds")
        return pkt_cntrs

class BLESnifferContext():
    def __init__(self, ble_sniffer:BLESniffer, rx_channel):
        self.ble_sniffer = ble_sniffer
        self.rx_channel = rx_channel

    def __enter__(self):
        self.ble_sniffer.flush_pkts()
        self.ble_sniffer.start_sniffer(self.rx_channel)
        return self.ble_sniffer

    def __exit__(self, exc_type, exc_value, traceback):
        if self.ble_sniffer:
            self.ble_sniffer.stop_sniffer()