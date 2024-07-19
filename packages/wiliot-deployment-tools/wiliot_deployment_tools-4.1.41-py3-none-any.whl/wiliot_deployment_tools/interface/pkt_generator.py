import binascii
import datetime
from typing import Literal, List
import numpy as np
import random
import os

from wiliot_deployment_tools.ag.ut_defines import (
    BRIDGE_ID,
    NFPKT,
    PAYLOAD,
    RSSI,
    TIMESTAMP,
)
from wiliot_deployment_tools.interface.if_defines import ADVA_LENGTH, GAP_LENGTH, GROUP_ID_LENGTH, SERVICE_UUID_LENGTH
from wiliot_deployment_tools.ag.wlt_types import *
from wiliot_deployment_tools.ag.wlt_types_ag import (
    GROUP_ID_SIDE_INFO,
    GROUP_ID_BRG2GW,
    GROUP_ID_GW2BRG,
    Hdr,
    SideInfo,
)
from wiliot_deployment_tools.ag.wlt_types_data import DataPacket

# TODO Find a relevant place for this define that is not auto-generated.
BRG_LATENCY =                   "brg_latency"

# Shared Functions
def generate_random_adva(device:Literal['Tag', 'Bridge']):
    """generate random 6-byte AdvA

    :return: AdvA (12 hex chars)
    :rtype: str
    """
    adva = os.urandom(6).hex().upper()
    if device == 'Tag':
        adva = apply_adva_bitmask(adva, 'non_resolvable')
    if device == 'Bridge':
        adva = apply_adva_bitmask(adva, 'random_static')
    return adva

def apply_adva_bitmask(adva, address_type:Literal['random_static', 'non_resolvable']):
    """apply AdvA Bitmask 
    BRGs AdvA comply with BTLE Random Static Address
    Pixel AdvA comply with BTLE Random Private Non-Resolvable Address

    :param adva: AdvA
    :type adva: str
    :return: AdvA (12 hex chars)
    :rtype: str
    """ 
    masked_adva = bytearray(binascii.unhexlify(adva))
    if address_type == 'random_static':
        masked_adva[5] = masked_adva[5] | 0b11000000
    if address_type == 'non_resolvable':
        masked_adva[5] = masked_adva[5] & 0b00111111
    masked_adva = masked_adva.hex().upper()
    return masked_adva

def init_adva(adva=None, device:Literal['Tag', 'Bridge']='Tag'):
    """Init function helper

    :param adva: AdvA, defaults to None
    :type adva: str, optional
    :return: AdvA (12 hex chars)
    :rtype: str
    """
    if adva is None:
        adva = generate_random_adva(device)

    adva_type = ''
    if device == 'Bridge':
        adva_type = 'random_static'
    elif device == 'Tag':
        adva_type = 'non_resolvable'

    adva = apply_adva_bitmask(adva, adva_type)

    return adva

def increment_circular(x, num_to_inc, bits):
    """Increment object of {bits} size circularly
    :param x: number to increment
    :type x: int
    :param num_to_inc: number to increment
    :type num_to_inc: int
    :param bits: bit size
    :type bits: int
    """
    return (x + num_to_inc) % (2 ^ bits)

def decrease_circular(x, num_to_dec, bits):
    """Decrease object of {bits} size circularly
    :param x: number to decrease
    :type x: int
    :param num_to_dec: number to decrease
    :type num_to_dec: int
    :param bits: bit size
    :type bits: int
    """
    return (x-num_to_dec) % (2 ^ bits)

def generate_random_bridge_id():
    """Generate random 6 byte bridge ID

    :return: bridge ID - (12 hex chars, int)
    :rtype: tuple (str, int)
    """
    bridge_id = os.urandom(6).hex().upper()
    bridge_id_int = int.from_bytes(binascii.unhexlify(bridge_id), "big")
    return bridge_id, bridge_id_int


class TagPktGenerator:
    """Tag Packet Generator - represents 1 Wiliot Pixel"""
    def __init__(self, adva=None, group_id=None, service_uuid:Literal["tag", "bridge"]='bridge') -> None:
        """
        :param adva: AdvA, defaults to None
        :type adva: str, optional
        :param group_id: Tag's group id, defaults to 0x020000 if none given
        :type group_id: int, optional
        :param service_uuid: set the generator's service uuid ("tag"=0xAFFD, "bridge"=0xC6FC)
        :type service_uuid: string
        """
        self.adva = init_adva(adva, device='Tag')
        self.data_packet = DataPacket(group_id=group_id, service_uuid=service_uuid)
        pass
    
    def __repr__(self) -> str:
        return f'Tag: {self.adva}, PktID: {self.get_pkt_id()[0]}'
    
    def get_pkt_id(self):
        """Get generator's current packet ID

        :return: 6 byte packet ID - (12 hex chars, int)
        :rtype: tuple (str, int)
        """
        pkt_id_int = self.data_packet.generic.pkt_id
        pkt_id_bytes = pkt_id_int.to_bytes(4, "big").hex()
        return pkt_id_bytes, pkt_id_int
    
    def set_pkt_id(self, pkt_id_int):
        """Set generator's packet ID

        :param pkt_id_int: packet ID
        :type pkt_id_int: int
        """
        assert 0 < pkt_id_int < (2 ** 32), "PacketID Must be a 32 bit unsigned integer!"
        self.data_packet.generic.pkt_id = pkt_id_int
        
    def randomize_pkt_id(self):
        """Randomize generator's packet ID"""
        pkt_id_int = int.from_bytes(os.urandom(4), "big")
        self.set_pkt_id(pkt_id_int)
    
    def randomize_packet_payload(self):
        """Randomize Generator's packet payload (keep packet ID as is)"""
        self.data_packet.generic.payload = int.from_bytes(os.urandom(20), "big")
        
    def randomize_packet_payload_unified(self):
        """Randomize Generator's packet payload (keep packet ID as is) for unified packet"""
        self.data_packet.pkt.nonce_n_unique_id = int.from_bytes(os.urandom(10), "big")
        self.data_packet.pkt.mic = int.from_bytes(os.urandom(3), "big")
        self.data_packet.pkt.data = int.from_bytes(os.urandom(8), "big")
        self.data_packet.data_hdr.group_id_major == GROUP_ID_UNIFIED_PKT
           
    def increment_pkt_data(self):
        packet = self.get_packet()
        data = packet[(ADVA_LENGTH+GAP_LENGTH+SERVICE_UUID_LENGTH+GROUP_ID_LENGTH):]
        incremented_data = [bytes([((int(data[i:i+2], 16) + 1) % 256)]).hex().upper() for i in range(0, len(data), 2)]
        incremented_packet = packet[:ADVA_LENGTH+GAP_LENGTH+SERVICE_UUID_LENGTH+GROUP_ID_LENGTH] + ''.join(incremented_data)
        self.set_packet(incremented_packet)

    def get_packet(self):
        """Get current packet from generator (hex string)

        :return: Tag's Packet [12 char AdvA + 62 char BLE Packet]
        :rtype: str
        """
        return self.adva + self.data_packet.dump()
    
    def set_packet(self, pkt):
        """set packet to input pkt"""
        if len(pkt) == 74:
            self.adva = pkt[:12]
            pkt = pkt[12:]
        assert len(pkt) == 62, "packet must be 74 / 62 hex chars long!"
        self.data_packet.set(pkt)
    
    def get_expected_mqtt(self):
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        expected = {
            TIMESTAMP: timestamp,
            PAYLOAD: self.get_packet()[ADVA_LENGTH+GAP_LENGTH:]
        }
        return expected



class BrgPktGenerator:
    """Bridge Packet Generator - represents 1 wiliot Bridge"""
    def __init__(self, bridge_id:str=None):
        """
        :param bridge_id: bridge ID, defaults to randomly generated if None
        :type bridge_id: str, optional
        """
        if bridge_id is None:
            self.bridge_id, self.bridge_id_int = generate_random_bridge_id()
        else:
            self.bridge_id = bridge_id
            self.bridge_id_int = int.from_bytes(binascii.unhexlify(bridge_id), "big")
        self.adva = apply_adva_bitmask(self.bridge_id, 'random_static')
        # Data packet init
        self.tag_list:List[TagPktGenerator] = []
        self.append_data_pkt()
        # SI packet init
        self.si_list:List[WltPkt]
        self.update_si_list()
        
        # BRG CFG packet init
        self.brg_cfg = WltPkt(
            hdr=Hdr(group_id=GROUP_ID_BRG2GW),
            generic=Brg2GwCfgV7(
                msg_type=BRG_MGMT_MSG_TYPE_CFG_INFO,
                major_ver=3,
                minor_ver=12,
                build_ver=35,
                brg_mac=self.bridge_id_int,
            ),
        )
        self.brg_hb = WltPkt(
            hdr=Hdr(group_id=GROUP_ID_BRG2GW),
            generic=Brg2GwHbV7(
                msg_type=BRG_MGMT_MSG_TYPE_HB, brg_mac=self.bridge_id_int
            ),
        )
        self.brg_seq_id = 0
        
    def __repr__(self):
        return f'BRG {self.bridge_id}, Tags {self.tag_list}'

    def set_bridge_id(self, brg_mac):
        """Set generator's bridge ID

        :param brg_mac: bridge ID (12 hex chars)
        :type brg_mac: str
        """
        self.bridge_id = brg_mac
        self.bridge_id_int = int.from_bytes(binascii.unhexlify(brg_mac), "big")
        self.brg_cfg = WltPkt(
            hdr=Hdr(group_id=GROUP_ID_BRG2GW),
            generic=Brg2GwCfgV7(
                msg_type=BRG_MGMT_MSG_TYPE_CFG_INFO,
                major_ver=3,
                minor_ver=12,
                build_ver=35,
                brg_mac=self.bridge_id_int,
            ),
        )
        self.brg_hb = WltPkt(
            hdr=Hdr(group_id=GROUP_ID_BRG2GW),
            generic=Brg2GwHbV7(
                msg_type=BRG_MGMT_MSG_TYPE_HB, brg_mac=self.bridge_id_int
            ),
        )
    
    def set_random_bridge_id(self):
        bridge_id, bridge_id_int = generate_random_bridge_id()
        self.set_bridge_id(bridge_id)
    
    # Data Packet
    
    def append_data_pkt(self, data_pkt=None):
        """Append data packet to tag list
        if no data packet is input, a new TagPktGenerator object will be appended to tag list

        :param data_pkt: 62 hex char string, defaults to None
        :type data_pkt: str, optional
        """
        idx_to_append = len(self.tag_list)
        self.tag_list.append(None)
        self.set_data_pkt(tag_idx=idx_to_append, data_pkt=data_pkt)

    def set_data_pkt(self, tag_idx, data_pkt=None):
        """Set tag generator at specific idx's data packet from string
        if no data packet is input, a new TagPktGenerator object will be created at tag_idx

        :param tag_idx: tag index
        :type tag_idx: int
        :param data_pkt: data packet (62 hex chars), defaults to None
        :type data_pkt: str, optional
        """
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        tag_pkt_gen = TagPktGenerator()
        if data_pkt is not None:
            tag_pkt_gen.set_packet(data_pkt)
        self.tag_list[tag_idx] = tag_pkt_gen
    
    # SideInfo Packet
    
    def generate_si_from_pkt_id(self, pkt_id_int):
        """Generate SI from packet ID

        :param pkt_id_int: packet ID
        :type pkt_id_int: int
        :return: WltPkt for SideInfo, with RSSI, NFPKT zeroed out
        :rtype: WltPkt(hdr:Hdr, generic:SideInfo)
        """
        assert 0 <= pkt_id_int < (2 ** 32), "Packet ID must be a 32 bit unsigned integer!"
        si_packet = WltPkt(
            hdr=Hdr(group_id=GROUP_ID_SIDE_INFO),
            generic=SideInfo(brg_mac=self.bridge_id_int, pkt_id=pkt_id_int),
        )
        return si_packet
    
    def update_si_list(self):
        """Update the SI list according to current pixel's packet IDs"""
        si_table = []
        for tag in self.tag_list:
            tag_pkt_id_bytes, tag_pkt_id_int = tag.get_pkt_id()
            si_table.append(self.generate_si_from_pkt_id(tag_pkt_id_int))
        self.si_list = si_table
        
    def randomize_si_rssi_nfpkt(self):
        """Randomize all SI's rssi and nfpkt values
        """
        for si in self.si_list:
            rssi = int.from_bytes(os.urandom(1), "big")
            nfpkt = int.from_bytes(os.urandom(2), "big")
            si.generic.rssi = rssi
            si.generic.nfpkt = nfpkt
            
    def randomize_unified_rssi_nfpkt_latency_gpacing(self):
        """Randomize all rssi, nfpkt, global pacing and brg latency values
        """
        for tag in self.tag_list:
            tag.data_packet.pkt.rssi = random.randint(0,63) + 40
            tag.data_packet.pkt.nfpkt = int.from_bytes(os.urandom(1), "big")
            tag.data_packet.pkt.brg_latency = random.randint(0,63) 
            tag.data_packet.pkt.global_pacing_group = random.randint(0,15)
            tag.data_packet.hdr.group_id = 0x00003F
            tag.data_packet.data_hdr.group_id_major = GROUP_ID_UNIFIED_PKT 
            tag.data_packet.data_hdr.group_id_minor = 0x0000

    def set_rssi_nfpkt(self, rssi, nfpkt, tag_idx:int=None):
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        self.si_list[tag_idx].generic.rssi = rssi
        self.si_list[tag_idx].generic.nfpkt = nfpkt
    
    # Coupling (Shared Data + SideInfo)
    
    def set_tag_list(self, tag_list:List[TagPktGenerator]):
        self.tag_list = tag_list
        self.update_si_list()
    
    def increment_pkt_id(self, tag_idx:int=None):
        """Increment tag generator at specific idx's data packet's packet ID 

        :param tag_idx: tag index, defaults to None
        :type tag_idx: int, optional
        """
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        self.tag_list[tag_idx].generic.pkt_id = increment_circular(self.tag_list[tag_idx].generic.pkt_id, 1, 32)
        self.update_si_list()

    def randomize_data_packet(self, tag_idx:int=None):
        """Randomize tag generator at specific idx's data packet (payload + ID),
        Update SI to match

        :param tag_idx: tag index, defaults to None
        :type tag_idx: int, optional
        """
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        tag = self.tag_list[tag_idx]
        # randomize packet ID
        tag.randomize_pkt_id()
        # randomize packet payload
        tag.randomize_packet_payload()
        # update SI
        self.update_si_list()

    def randomize_packet_unified(self, tag_idx:int=None):
        """Randomize tag generator at specific idx's data packet (payload + ID)

        :param tag_idx: tag index, defaults to None
        :type tag_idx: int, optional
        """
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        tag = self.tag_list[tag_idx]
        # randomize packet ID
        tag.randomize_pkt_id()
        # randomize packet payload
        tag.randomize_packet_payload_unified()

    def get_data(self, tag_idx:int):
        """Get tag at index's data packet (AdvA + BLE Packet)

        :param tag_idx: tag index
        :type tag_idx: int
        :return: data packet (74 hex char)
        :rtype: str
        """
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        return self.tag_list[tag_idx].get_packet()
    
    def get_si(self, tag_idx:int):
        """Get tag at index's sideinfo packet (AdvA + BLE Packet)

        :param tag_idx: _description_
        :type tag_idx: int
        :return: _description_
        :rtype: _type_
        """
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        return self.adva + self.si_list[tag_idx].dump()

    def get_expected_coupled_mqtt(self, tag_idx:int=None):
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        si = self.si_list[tag_idx]
        """generates expected MQTT packet"""
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        expected = {
            TIMESTAMP: timestamp,
            BRIDGE_ID: self.bridge_id,
            NFPKT: si.generic.nfpkt,
            RSSI: si.generic.rssi,
            PAYLOAD: self.get_data(tag_idx)[(ADVA_LENGTH+GAP_LENGTH):]
        }
        return expected
    
    def get_expected_uncoupled_mqtt(self, tag_idx:int=None):
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        expected_data = {
            TIMESTAMP: timestamp,
            PAYLOAD: self.get_data(tag_idx)[(ADVA_LENGTH+GAP_LENGTH):]
        }
        expected_si = {
            TIMESTAMP: timestamp,
            PAYLOAD: self.get_si(tag_idx)[(ADVA_LENGTH+GAP_LENGTH):]
        }
        return [expected_data, expected_si]

    def get_expected_mqtt_unified(self, full_data_pkt, tag_idx:int=None):
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'

        def extract_param_from_pkt():
            # Take only the relevant digis from the data packet
            param_hex_string = full_data_pkt[46:-22]
            if len(param_hex_string) != 6:
                raise ValueError("The parameters hex representation must be 6 digits long")
            
            # Convert to decimal from binari and assign
            param_binari_string = bin(int(param_hex_string, 16))[2:].zfill(24)
            nfpkt = int(param_binari_string[:8], 2)
            rssi = int(param_binari_string[8:14], 2)
            # Note: rssi here is -40 then the actual value. This portion is to be added on cloud
            brg_latency = int(param_binari_string[14:20], 2)
            brg_global_pacing_group = int(param_binari_string[20:], 2)
            return [nfpkt, rssi, brg_latency, brg_global_pacing_group]

        """generates expected MQTT packet"""
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        pkt_param = extract_param_from_pkt()

        expected_data = {
            TIMESTAMP: timestamp,
            BRIDGE_ID: self.bridge_id,
            NFPKT: pkt_param[0],
            RSSI: pkt_param[1],
            BRG_LATENCY: pkt_param[2],
            BRG_GLOBAL_PACING_GROUP: pkt_param[3],
            PAYLOAD: full_data_pkt[(ADVA_LENGTH+GAP_LENGTH):]
        }
        return [expected_data]

    def get_expected_hb_mqtt(self):
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        expected = {
            TIMESTAMP: timestamp,
            PAYLOAD: self.get_brg_hb()[(ADVA_LENGTH+GAP_LENGTH):]
        }
        return expected
    # Management packets (Heartbeat / CFG)

    def increment_brg_seq_id(self):
        """Increment Bridge sequenceID (Relevant for CFG/HB Packets only)"""
        self.brg_seq_id = increment_circular(self.brg_seq_id, 2, 8)
        self.brg_cfg.generic.seq_id = decrease_circular(self.brg_seq_id, 2, 8)
        self.brg_hb.generic.seq_id = decrease_circular(self.brg_seq_id, 1, 8)

    def increment_hb_counters(self, num=1):
        """Update bridge HB counters values

        :param num: num to increment by, defaults to 1
        :type num: int, optional
        """
        self.brg_hb.generic.non_wlt_rx_pkts_ctr = increment_circular(self.brg_hb.generic.non_wlt_rx_pkts_ctr, num, 24)
        self.brg_hb.generic.bad_crc_pkts_ctr = increment_circular(self.brg_hb.generic.bad_crc_pkts_ctr, num, 24)
        self.brg_hb.generic.wlt_rx_pkts_ctr = increment_circular(self.brg_hb.generic.wlt_rx_pkts_ctr, num, 24)
        self.brg_hb.generic.wlt_tx_pkts_ctr = increment_circular(self.brg_hb.generic.wlt_tx_pkts_ctr, num, 16)
        self.brg_hb.generic.tags_ctr = len(self.tag_list)

    def increment_all(self):
        """Increment Bridge sequenceID and HB counters"""
        self.increment_brg_seq_id()
        self.increment_hb_counters()
        
    def get_brg_cfg(self):
        """Get bridge CFG Packet

        :return: CFG Packet (74 hex chars)
        :rtype: str
        """
        return self.adva + self.brg_cfg.dump()

    def get_brg_hb(self):
        """Get bridge HB Packet

        :return: HB Packet (74 hex chars)
        :rtype: str
        """
        return self.adva + self.brg_hb.dump()

    # General

    def get_existing_data_si(self, tag_idx:int=None) -> dict:
        """Get tag at tag_idx's Data packet and relevant SideInfo packet

        :param tag_idx: tag index, defaults to None
        :type tag_idx: int, optional
        :return: dictionary with data packet and sideinfo packet
        :rtype: dict
        """
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        existing_packets = {
            "data_packet": self.get_data(tag_idx),
            "si_packet": self.get_si(tag_idx)
        }
        return existing_packets
    
    def get_existing_data_unified(self, tag_idx:int=None) -> dict:
        """Get tag at tag_idx's Data packet for unified packet

        :param tag_idx: tag index, defaults to None
        :type tag_idx: int, optional
        :return: dictionary with data packet and sideinfo packet
        :rtype: dict
        """
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        existing_packets = {
            "data_packet": self.get_data(tag_idx)
        }
        return existing_packets
    
    def get_new_data_si(self, tag_idx:int=None) -> dict:
        """Generate new Data+SideInfo packets for tag at tag_idx

        :param tag_idx: tag index, defaults to None
        :type tag_idx: int, optional
        :return: dictionary with data packet and sideinfo packet
        :rtype: dict
        """
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        self.randomize_data_packet(tag_idx)
        self.randomize_si_rssi_nfpkt()
        self.increment_brg_seq_id()
        self.increment_hb_counters()
        return self.get_existing_data_si(tag_idx)
    
    def get_new_data_unified(self, tag_idx:int=None) -> dict:
        """Generate new unified Data packets for tag at tag_idx

        :param tag_idx: tag index, defaults to None
        :type tag_idx: int, optional
        :return: dictionary with data packet 
        :rtype: dict
        """
        if tag_idx is None:
            tag_idx = 0
        assert tag_idx <= len(self.tag_list), f'Tag index must be in {[i for i in range(len(self.tag_list))]}'
        # set the packet type to unified
        self.tag_list[tag_idx].data_packet.pkt = UnifiedEchoPkt()
        self.tag_list[tag_idx].adva = init_adva(self.bridge_id, 'Bridge')
        self.randomize_packet_unified(tag_idx)
        self.randomize_unified_rssi_nfpkt_latency_gpacing()
        self.increment_brg_seq_id()
        self.increment_hb_counters()
        return self.get_existing_data_unified(tag_idx) 
    
class BrgPktGeneratorNetwork:
    """Bridge Packet Generator Network - Represents multiple bridges setup at same location and echoing the same tags"""
    def __init__(self, num_brgs=3):
        """
        :param num_brgs: number of bridges in array, defaults to 3
        :type num_brgs: int, optional
        """
        assert num_brgs > 1, 'BrgArray cannot be smaller than 1!'
        self.brg_list = [BrgPktGenerator() for brg in range(num_brgs)]
        self.primary_brg = self.brg_list[0]
        self.secondary_brgs = self.brg_list[1:]
        for brg in self.secondary_brgs:
            brg.set_tag_list(self.primary_brg.tag_list)
    
    def get_new_pkt_pairs(self) -> list:
        """Get data/si pairs for all bridges in bridge network

        :return: List of dictionaries containing {bridge_id, data_packet, si_packet} key:value pairs
        :rtype: list[dict]
        """
        pkts = []
        new_pkt_primary = self.primary_brg.get_new_data_si()
        pkts.append(new_pkt_primary)
        for brg in self.secondary_brgs:
            brg.update_si_list()
            brg.randomize_si_rssi_nfpkt()
            pkts.append(brg.get_existing_data_si())
        for idx, pkt in enumerate(pkts):
            pkt.update({'bridge_id': self.brg_list[idx].bridge_id})
        return pkts
    
    def get_new_pkt_unified(self) -> list:
        """Get new unified pkt for all bridges in bridge network

        :return: List of dictionaries containing {bridge_id, data_packet} key:value pairs
        :rtype: list[dict]
        """ 
        pkts = []
        new_pkt_primary = self.primary_brg.get_new_data_unified()
        pkts.append(new_pkt_primary)
        for brg in self.secondary_brgs:
            brg.randomize_unified_rssi_nfpkt_latency_gpacing()
            brg.tag_list[0].adva = init_adva(brg.bridge_id, 'Bridge')
            pkts.append(brg.get_existing_data_unified())
        for idx, pkt in enumerate(pkts):
            pkt.update({'bridge_id': self.brg_list[idx].bridge_id})
        return pkts    
      
    def get_scattered_pkt_pairs(self, delay):
        """Get data/si pairs with scattered time delays

        :param delay: bridges rxTxPeriod equivalent (millisecond)
        :type delay: int
        """
        assert delay / len(self.brg_list) >= 10, 'Cannot get scattered PKT pairs for parameters! decrease num of brgs or increase delay'
        start_times = sorted(random.sample(list(np.arange(0, delay-10+1, 10)), k=len(self.brg_list)))
        start_times.append((start_times[0] + delay))
        pkts = self.get_new_pkt_pairs()
        
        for idx, pkt in enumerate(pkts):
            # minimum time between UART packet commands = 10ms
            pkt['time_delay'] = max(start_times[idx+1] - start_times[idx], 10)
        return pkts

class CloudPktGenerator:
    """Cloud Packet Generator - Represents """
    def __init__(self):
        self.bridge_id, self.bridge_id_int = generate_random_bridge_id()
        pass

    def generate_config_pkt(self, seq_id=None, bridge_id=None):
        if seq_id == None:
            seq_id = int.from_bytes(os.urandom(1), 'big')
        if bridge_id is not None:
            bridge_id_int = int.from_bytes(binascii.unhexlify(bridge_id), "big")

        pkt = WltPkt(Hdr(group_id=GROUP_ID_GW2BRG), generic=Gw2BrgCfgV7(
            msg_type=BRG_MGMT_MSG_TYPE_CFG_SET,
            global_pacing_group=random.getrandbits(4),
            output_power_sub_1_ghz=random.getrandbits(4),
            seq_id=random.getrandbits(8),
            brg_mac=bridge_id_int,
            unused0=0,
            pkt_types_mask=random.getrandbits(5),
            unused1=0,
            rxtx_period=random.getrandbits(8),
            tx_period=random.getrandbits(8),
            energy_pattern_idx=random.getrandbits(8),
            output_power_2_4=random.getrandbits(8),
            pacer_interval=random.getrandbits(16),
            unused2=0,
            tx_prob=random.getrandbits(3),
            tx_repetition=random.getrandbits(4),
            transmit_time_sub_1_ghz=random.getrandbits(4),
            sub1g_freq_profile=random.getrandbits(4),
            ))
        return pkt.dump()

    # def generate_action_pkt(self, action: Literal["blink", "reboot"], seq_id=None, bridge_id=None):
    #     if seq_id == None:
    #         seq_id = int.from_bytes(os.urandom(1), 'big')
    #     if bridge_id is not None:
    #         bridge_id_int = int.from_bytes(binascii.unhexlify(bridge_id), "big")

    #     pkt = WltPkt(Hdr(group_id=GROUP_ID_GW2BRG), generic=ActionV7(
    #         msg_type=BRG_MGMT_MSG_TYPE_ACTION,
    #         seq_id=seq_id,
    #         action_id=
    #                                                                  )