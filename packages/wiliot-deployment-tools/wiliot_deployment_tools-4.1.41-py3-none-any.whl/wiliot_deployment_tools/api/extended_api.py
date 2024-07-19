# External Imports
import pandas as pd
import math
import pytz
from requests import JSONDecodeError
from enum import Enum
from time import sleep
import datetime
import random
import urllib.parse
from packaging import version
from typing import Literal

# Internal Imports
from wiliot_api.api_client import WiliotCloudError
from wiliot_api.platform.platform import PlatformClient
from wiliot_api.edge.edge import EdgeClient, BridgeAction
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.common.utils_defines import BO_DICT, BROADCAST_DST_MAC, GW_DATA_MODE, GW_DATA_SRC, SEP, gw_rx_channel

EXCEPTIONS_TO_CATCH = (AttributeError, WiliotCloudError, JSONDecodeError)


# Enum Classes
class GatewayType(Enum):
    UNKNOWN = 'unknown'
    WIFI = 'wifi'
    LTE = 'lte'
    MOBILE = 'mobile'
    IOS = 'ios'
    ANDROID = 'android'
    ERM = 'erm'
    RIGADO = 'rigado'
    OTHER = 'other'


class GatewayAction(Enum):
    ADD_SSID = 'addSsid'
    TOGGLE_SSID = 'toggleDefaultSsid'
    REBOOT_GW = 'rebootGw'
    START_BRIDGE_OTA = '!send_msg_to_brg'
    ENTER_DEV_MODE = 'DevModeEnable'
    UART_UP_STREAM = '!us'

class UartPacketOrigin(Enum):
    TRANSPARENT = 'p0'
    TAG = 'p1'
    COUPLED = 'p2'
    SENSOR = 'p3'

class AndroidGatewayAction(Enum):
    DISABLE_UPLINK = -2
    ENABLE_UPLINK = -3
    DISABLE_BLE_LOGS = -4
    ENABLE_BLE_LOGS = -5

class BridgeThroughGatewayAction(Enum):
    REBOOT = '01'
    BLINK = '02'
    POWER_MGMT = '03'
    RESTORE_DEFAULTS = '04'
    SEND_HB = '05'
    PRODUCTION_MODE = '06'
    SPARSE_37 = '07'
    GW_HB = '08'


class BoardTypes(Enum):
    FANSTEL_SINGLE = 'FanstelSingleBandV0'
    FANSTEL_DUAL = 'FanstelDualBandV0'
    MINEW_SINGLE = 'MinewSingleBandV0'
    MINEW_DUAL = 'MinewDualBandV0'
    ENERGOUS = 'EnergousV0'

class BoardTypesActive(Enum):
    ENERGOUS = 'Energous Dual-Band (v0)'
    FANSTEL_SINGLE = 'Fanstel Single-Band (v0)'
    FANSTEL_DUAL = 'Fanstel Dual-Band (v0)'
    MINEW_SINGLE = 'Minew Single-Band (v0)'
    MINEW_DUAL = 'Minew Dual-Band (v0)'
    MOKO = 'Moko Dual-Band (v0)'


# API Clients

class ParamMissingError(Exception):
    pass

class ExtendedEdgeClientError(Exception):
    pass


class ExtendedEdgeClient(EdgeClient):
    def __init__(self, api_key, owner_id, env='prod', region='us-east-2', cloud='',log_file=None, logger_=None):
        # Support for GCP
        region='us-central1' if cloud=='gcp' else region
        super().__init__(api_key=api_key, owner_id=owner_id, env=env, region=region, cloud=cloud, log_file=log_file, logger_=logger_)
    
    # Get Info
    def get_connected_brgs(self, gw, ignore_bridges=None):
        """
            returned all bridges connected to gateway and claimed by owner
            :type gw: string
            :param gw: desired gw to get its connected bridges
            :type ignore_bridges: list
            :param ignore_bridges: list of bridges ID to ignore
            output type: array of dictionaries
            output param: array with a dictionary to every connected bridge.
                            dictionary includes its current configurations
            example:
            print(wiliot.get_connected_brgs("GW0CDC7EDB1674")):
            TODO: add output
        """
        ignore_bridges = ignore_bridges if ignore_bridges is not None else []
        brg_list = self.get_bridges_connected_to_gateway(gw)

        for brg in brg_list:
            if brg["id"] in ignore_bridges:
                brg_list.remove(brg)
        brg_list_connected = [b for b in brg_list if
                              any([c["connected"] and c["gatewayId"] == gw for c in b["connections"]])]
        brg_list_connected = [b for b in brg_list_connected if b['owned']]
        return brg_list_connected

    def get_bridge_status(self, bridge_id):
        """
        Get bridge status: online or offline
        :param : A string- the target bridge
        :return: A string: online or offline
        """
        online_brgs = super().get_bridges(online = True)
        for brg in online_brgs:
            if bridge_id in brg["id"]:
                return 'online'
        return 'offline'

    def get_bridges(self, online=None, gateway_id=None):
        """
        Get all bridges "seen" by gateways owned by the owner
        :param online: A boolean - optional. Allows to filter only online (True) or offline (False) bridges
        :param gateway_id: A string / list - optional. Allows to filter only bridges currently connected to the gateway / gateways
        :return: A list of bridges
        """
        # check type
        if gateway_id is not None and type(gateway_id) not in [str, list]:
            raise TypeError('Gateway ID must be either str/list!')
        gws_list = None
        if type(gateway_id) == list:
            gws_list = gateway_id
        if type(gateway_id) == str:
            gws_list = [gateway_id]

        bridges = super().get_bridges(online)
        if gws_list is not None:
            bridges = [b for b in bridges if any([c["connected"] and c["gatewayId"] in gws_list for c
                                                      in b["connections"]])]
        return bridges
        
    def get_gateways_from_bridges(self, brg_ids=None):
        """
        gets connected gateways from bridge IDs
        :type brg_ids: list
        :param brg_ids: bridge IDs
        :rtype: dict
        :return: dict of {gatewayId: [list of bridgeIds]} of all connected bridges / specified brg_ids
        """
        brgs = self.get_bridges()
        owners_gws = [g['gatewayId'] for g in self.get_gateways()]
        gws_list = {}
        for brg_dict in brgs:
            brg_id = brg_dict['id'] 
            # Filter only bridges in brg_ids
            if brg_ids is not None:
                if brg_dict['id'] not in brg_ids:
                    continue
            for connection in brg_dict['connections']:
                if connection['connected']:
                    gw = connection['gatewayId']
                    if gw not in owners_gws:
                        continue
                    if gw not in gws_list.keys():
                        gws_list[gw] = [brg_id]
                    else:
                        gws_list[gw].append(brg_id)
        return gws_list


    def get_bridge_relevant_gw(self, bridge_id, get_gw_list = False):
        """
        Returns relevant GW for sending actions to bridge
        :param bridge_id: Bridge ID
        :rtype: str
        :return: relevant Gateway ID
        """

        # TODO - return list of potential GWs
        potential_gws = list()
        owner_gws = self.get_gateways()
        owner_gw_ids = []
        owner_gw_ids.extend(g['gatewayId'] for g in owner_gws)
        for gw in self.get_bridge(bridge_id)['connections']:
            if gw['gatewayId'] not in owner_gw_ids:
                continue
            gw_id = gw['gatewayId']
            gw_dict = self.get_gateway(gw_id)
            if gw['connected'] and \
                    bridge_id in self.get_seen_bridges(gw_id) and \
                    self.check_gw_compatible_for_action(gw_id):
                if bridge_id in self.get_seen_bridges(gw['gatewayId']):
                    potential_gws.append(gw['gatewayId'])
        if len(potential_gws) == 0:
            raise ExtendedEdgeClientError(f'No relevant GW connected to bridge! Check deployment')
        if get_gw_list:
            return potential_gws
        return potential_gws[0]        
            
    def get_seen_bridges(self, gw, ignore_bridges=None):
        """
        return all bridges 'seen' by GW
        :type gw: str
        :param gw: gateway ID
        :type ignore_bridges: list
        :param ignore_bridges: list of bridge IDs to ignore
        :rtype: list
        :return: list of Bridge IDs
        """
        bridges = [b['bridgeId'] for b in self.get_gateway(gw)['connections']]
        if ignore_bridges is not None:
            bridges = list(set(bridges) - set(ignore_bridges))
        return bridges

    def get_gateway_type(self, gateway_id):
        """
        Returns GatewayType of gateway ID
        :param gateway_id: String - gateway ID
        :rtype: GatewayType
        """
        type = self.get_gateway(gateway_id)['gatewayType'].upper()
        return GatewayType.__getitem__(type)

    def get_gateways_types(self, gw_ids):
        """
        returns dict of gatewaytype:[gatewayIds]
        :param gw_ids: gateways IDs
        :type gw_ids: list
        """
        res = {}
        for gw in gw_ids:
            try:
                gw_type = self.get_gateway_type(gw)
            except WiliotCloudError: 
                gw_type = GatewayType.UNKNOWN
            if gw_type not in res.keys():
                res[gw_type] = []
            res[gw_type].append(gw)
        return res
    
    def get_owner_gateways_types(self):
        gateways = self.get_gateways()
        gateways_types = {}
        for gw in gateways:
            gw_id = gw['gatewayId']
            gw_type = GatewayType.UNKNOWN
            try:
                gw_type = GatewayType.__getitem__(gw['gatewayType'].upper())
                if gw_type == GatewayType.MOBILE:
                    if '-' in gw_id:
                        gw_type = GatewayType.IOS
                    else:
                        gw_type = GatewayType.ANDROID
            except KeyError as e:
                debug_print(f'KeyError {e} when checking GW {gw_id} type')
            gateways_types[gw_id] = gw_type
        return gateways_types

    def check_gw_online(self, gw_ids):
        gws_online = True
        for gw_id in gw_ids:
            gw = self.get_gateway(gw_id)
            if not gw['online']:
                debug_print("Gateway {} is offline".format(gw_id))
                gws_online = False
            else:
                debug_print(f'Gateway {gw_id} is online')
        return gws_online

    def test_if_bridge_connected(self, brg):
        """
            :type brg: dictionary
            :param brg: bridge data structure
            :return: True if bridge is connected, False otherwise
        """
        for connection in brg['connections']:
            if connection['connected']:
                return True
        return False

    def get_bridge_board(self, brg_id):
        """
        :type brg_id: string
        :param brg_id: bridge id
        """
        board_type = self.get_bridge(brg_id)['boardType']
        if board_type in [member.value for member in BoardTypes.__members__.values()]:
            return board_type
        else:
            try:
                return (BoardTypes[BoardTypesActive(board_type).name]).value
            except:
                return None

    # Gateway & Bridge Actions
    def send_action_to_gateway(self, gateway_id, action, **kwargs):
        """
        Send an action to a gateway
        :param gateway_id: String - the ID of the gateway to send the action to
        :param action: GatewayAction - Required
        :return: True if the cloud successfully sent the action to the gateway, False otherwise
        """
        gw_type = self.get_gateway_type(gateway_id)
        assert gw_type in [GatewayType.WIFI, GatewayType.MOBILE], 'gateway does not support action API!'
        if gw_type == GatewayType.WIFI:
            assert action in GatewayAction, 'action not valid for WIFI GW!'
        if gw_type == GatewayType.MOBILE:
            assert action in AndroidGatewayAction, 'action not valid for Mobile GW!'
        if action == GatewayAction.ADD_SSID:
            assert 'ssid' in kwargs.keys(), "Missing a 'ssid' parameter"
        if action == GatewayAction.START_BRIDGE_OTA:
            assert 'bridge_id' in kwargs.keys(), "Missing a 'bridge_id' parameter"
        path = "gateway/{}/action".format(gateway_id)
        action_payload = action.value
        if action == GatewayAction.START_BRIDGE_OTA:
            action_payload = action_payload + f' {kwargs["bridge_id"]} 1'
        if action == GatewayAction.UART_UP_STREAM:
            action_payload = action_payload + ' ' + ' '.join(str(value) for value in kwargs.values())
        else:
            for key, value in kwargs.items():
                action_payload = action_payload + f' {key}:{value}'
        payload = {
            "action": action_payload
        }
        try:
            res = self._post(path, payload)
            return res['data'].lower().find("ok") != -1
        except WiliotCloudError as e:
            print("Failed to send action to gateway")
            raise WiliotCloudError(
                "Failed to send action to gateway. Received the following error: {}".format(e.args[0]))

    def enter_custom_mqtt(self, gateway_id, mqtt_mode:Literal['automatic', 'manual' ,'legacy'] = 'automatic'):
        """
        enter GW Dev Mode
        :type gateway_id: string
        :param gateway_id: gateway id
        :type mqtt_mode: string
        :param mqtt_mode: 'automatic', 'manual' or 'legacy'
        :return: True if sent successfully to GW
        :rtype: bool
        """
        if mqtt_mode == 'legacy':
            return self.send_action_to_gateway(gateway_id, GatewayAction.ENTER_DEV_MODE)
        elif mqtt_mode == 'automatic':
            dev_mode = {
                    "customBroker": True,
                    "brokerUrl": "mqtts://broker.hivemq.com",
                    "port": 8883,
                    "username": "",
                    "password": "",
                    "updateTopic": f"update/{self.owner_id}/{gateway_id}",
                    "statusTopic": f"status/{self.owner_id}/{gateway_id}",
                    "dataTopic": f"data/{self.owner_id}/{gateway_id}"
                    }
            return self.send_custom_message_to_gateway(gateway_id, dev_mode)
        elif mqtt_mode == 'manual':
                debug_print(f"Make sure GW {gateway_id} is set to HiveMQ MQTT broker")
                return True

    def send_uart_packet_through_gw(self, gateway_id,packet_type,raw_packet,repetitions = 1000,delay_ms = 10):
        """
        send uart upstream packet to gate
        :param gateway_id: 
        :param packet_type: must be one of UartPacketOrigin
        :raw_packet: raw packet to send, without adva
        :param repetitions: repetitions of evety packet
        :param delay_ms: time interval between packets
        :return: True if sent successfully to GW
        :rtype: bool
        """
        if not self.check_uart_sim_support(gateway_id):
            debug_print(f"gateway:{gateway_id} doesn't support uart simulator")
            return False
        if not any(packet_type == item for item in UartPacketOrigin):
            debug_print("Invalid argument for packet_type, munst be a value of UartPacketOrigin")
            return False
        packet_args_dict = {}
        packet_args_dict['repetitions'] = repetitions
        packet_args_dict['delay_ms'] = delay_ms
        packet_args_dict['packet_type'] = packet_type.value
        packet_args_dict['raw_packet'] = raw_packet

        return self.send_action_to_gateway(gateway_id=gateway_id, action=GatewayAction.UART_UP_STREAM,**packet_args_dict)
        

    
    def send_packet_through_gw(self, gateway_id, raw_packet, is_ota=False, brg_id=None,
                               repetitions=8, tx_rate=None, tx_max_duration = None, debug=False, return_payload=False):
        """
        send packet through GW
        :param gateway_id: gateway ID
        :type gateway_id: str

        :param raw_packet: raw packet
        :type raw_packet: str
        :type is_ota: bool, optional
        :param is_ota: start OTA with bridge, defaults to False
        :type brg_id: bridge ID, optional
        :param brg_id: str, defaults to None
        :type repetitions: int, optional
        :param repetitions: number of times to send the packet, defaults to 8
        :type tx_rate: int, optional
        :param tx_rate: tx rate to send the packet (used to calculate txMaxDurationMs):
                        ANDROID GW - 140ms
                        ERM GW - 50ms
        :type tx_max_duration: int
        :param tx_max_duration: tx max duration to encode in the packet. 
                                if this parameter is given the tx_rate and repetitions will be ignored
        :type debug: bool
        :param debug: if True, debug_print payload
        :type return_payload: bool
        :param return_payload: if True, return sent payload as dict
        :return: True if successful / False if not, payload(dict) if return_payload is True
        :rtype: bool
        """
        
        if len(raw_packet) < 62:
            if len(raw_packet) == 54:
                raw_packet = 'C6FC' + raw_packet
            if len(raw_packet) == 58:
                raw_packet = '1E16' + raw_packet
        if len(raw_packet) > 62:
            raw_packet = raw_packet[-62:]
        
        assert len(raw_packet) == 62, 'Raw Packet must be 62 chars long!'
        # Android tx rate - 140ms
        # ERM StarLink tx rate - 50ms
        if tx_rate is None:
            if self.get_gateway_type(gateway_id) == GatewayType.MOBILE:
                tx_rate = 140
            elif self.get_gateway_type(gateway_id) == GatewayType.LTE:
                tx_rate = 50
            else:
                tx_rate = 140
        payload = {'txPacket': raw_packet,
                   'txMaxDurationMs': tx_rate * repetitions,
                   'txMaxRetries': repetitions,
                   'action': 0}
        if tx_max_duration is not None:
            payload['txMaxDurationMs'] = tx_max_duration
        if is_ota:
            payload.update({'action': 1, 'bridgeId': brg_id})
        if debug:
            debug_print(f'{payload} sent to {gateway_id}')
        res = self.send_custom_message_to_gateway(gateway_id, payload)
        if return_payload:
            return payload
        return res
    
    @staticmethod
    def generate_bridge_action_packet(action_type, payload='0', bridge_id=None, broadcast=False):
        assert action_type in BridgeThroughGatewayAction, 'Not valid action type'
        assert (bridge_id is not None and broadcast is False) or (bridge_id is None and broadcast is True), \
            'Must supply bridgeId / set broadcast to True'
        assert len(bridge_id) == 12
        if broadcast:
            bridge_id = BROADCAST_DST_MAC
        payload = str(payload).ljust(28, '0')
        # Packet Header: 0-5 ADVA, 6 Length, 7 AD Type, 8-9 UUID, 10-12 Group ID, 13 MSG type, 14 API Ver.
        header = '1E16C6FC0000ED0707'
        # Randomize Sequence ID
        seq_id = random.getrandbits(8).to_bytes(1, 'big').hex().upper()
        # Assemble raw packet
        return f'{header}{seq_id}{bridge_id}{action_type.value}{payload}'
    
    def send_bridge_action_through_gw(self, gateway_id, action_type, payload=None, bridge_id=None, broadcast=False, reps=8):
        """
        Send an action to a bridge through a gateway
        :param broadcast: whether to broadcast
        :param gateway_id: String - the ID of the gateway to send the action Through
        :param bridge_id: String - the ID of the bridge to send the action to
        :param action_type: BridgeThroughGatewayAction - Required
        :param payload: 28 bytes (hex string)
        :param reps: repetitions to send
        :return: True if the cloud successfully sent the action to the gateway, False otherwise
        """
        if payload is None:
            payload = '0'
        raw_packet = self.generate_bridge_action_packet(action_type, payload, bridge_id, broadcast)
        self.send_packet_through_gw(gateway_id, raw_packet, repetitions=reps)
    
    def reboot_gateway(self, gateway_id):
        """
        Reboots specified GW
        :param gateway_id: Gateway ID
        :return: True if the cloud successfully sent the action to the gateway, False otherwise
        """
        return self.send_action_to_gateway(gateway_id, GatewayAction.REBOOT_GW)

    def reboot_bridge(self, bridge_id):
        """
        Reboots specified GW
        :param bridge_id: Bridge ID
        :return: True if the cloud successfully sent the action to the gateway, False otherwise
        """
        return self.send_action_to_bridge(bridge_id, BridgeAction.REBOOT)

    # Logs & Acks
    def fetch_logs(self, gateway_id, hrs_back=24):
        """
        fetches gateway logs from cloud
        :param gateway_id: String - the ID of the gateway
        :param hrs_back: Int - How many hours back to query
        :return: List of Dicts of gateway log entries
        """
        assert hrs_back < 144, 'Cannot query for more than 144 hours back!'
        end_timestamp = int(datetime.datetime.now().timestamp())
        start_timestamp = int((datetime.datetime.now() - datetime.timedelta(hours=hrs_back)).timestamp())
        path = f'gateway/{gateway_id}/logs?' + urllib.parse.urlencode(
            {"start": start_timestamp, "end": end_timestamp, 'step': 60})
        try:
            res = self._get(path)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to fetch gateway logs")
            raise WiliotCloudError(
                "Failed to fetch gateway logs. Received the following error: {}".format(e.args[0]))

    def get_gateway_logs(self, gateway_id, hours_back=24):
        """
        fetches gateway logs from gateway
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type hours_back: int
        :param hours_back: How many hours back to query
        :rtype: Pandas DataFrame
        :return: Gateway Logs
        """

        logs = pd.DataFrame.from_dict(self.fetch_logs(gateway_id, hours_back))
        if len(logs) == 0:
            return None
        logs['type'] = logs['message'].apply(lambda x: x.split(':')[0])
        logs['message'] = logs['message'].apply(lambda x: ''.join(x.split(':')[1:]))
        return logs

    def print_gateway_logs(self, gateway_id):
        """
        prints gateway logs nicely
        :type gateway_id: str
        :param gateway_id: Gateway ID
        """
        logs = self.get_gateway_logs(gateway_id)
        if logs is None:
            print(f'---No logs for GW {gateway_id}---')
            return None
        logs = logs.reindex(index=logs.index[::-1])
        logs = logs.reset_index()
        datetime_format = "%Y-%m-%dT%H:%M:%SZ"

        for row in logs.itertuples():
            timestamp = datetime.datetime.strptime(row.timestamp, datetime_format).replace(tzinfo=pytz.UTC).timestamp()
            local_datetime = datetime.datetime.fromtimestamp(timestamp)
            print(f'---Log No. {row.Index} | {row.level} | {local_datetime}---')
            print(f'*{row.message}')
            print(f'')
    
    def get_gateway_info(self, gateway_id):
        """
        get gateway info from gateway
        :param gateway_id: Gateway ID
        :type gateway_id: str
        :return: gateway info
        :rtype: dict
        """
        res = self.get_gateway(gateway_id)
        return res['gatewayInfo']
                
    def get_acks(self, gateway_id, hours_back=3):
        """
        function gets latest acknowledge packets for each bridge ID (after sending GW action)
        :type gateway_id: str
        :param gateway_id: gateway ID
        :type hours_back: int
        :param hours_back: hours back to query
        :return: last acknowledge packet
        """

        try:
            logs = self.get_gateway_logs(gateway_id, hours_back=hours_back)
        except Exception as e:
            debug_print(f'Exception {e} Caught when getting Acks from GW {gateway_id}')
            logs = None
        if logs is None:
            return None
        gw_type = self.get_gateway_type(gateway_id)
        if gw_type == GatewayType.MOBILE:
            logs = logs[list(map(lambda x: x.startswith(' ReceivedAction'), logs['message']))]
            logs['rawPacket'] = logs['message'].apply(lambda x: x.split('=')[1][16:-1]).str.upper()
        else:
            logs = logs[list(map(lambda x: x.startswith(' RecievedAction') or x.startswith(' ReceivedAction'), logs['message']))]
            logs['rawPacket'] = logs['message'].apply(lambda x: x.split('=')[1][6:-1])
        logs['bridgeId'] = logs['rawPacket'].apply(lambda x: x[:12])
        logs['actionType'] = logs['rawPacket'].apply(lambda x: BridgeThroughGatewayAction(str(x[12:14])))
        logs['payload'] = logs['rawPacket'].apply(lambda x: x[14:])
        return logs

    # Versions & Version-Dependent
    def get_gw_version(self, gw_id):
        """
        :type gw_id: string
        :param gw_id: gateway id
        """
        # TODO - version bug
        cnt = 0
        while cnt <= 30:
            gw = self.get_gateway(gw_id)
            if 'version' in gw['reportedConf']:
                return gw['reportedConf']['version']
            else:
                debug_print('version not in GW reported conf! sleeping for 10 seconds...')
                sleep(10)

    def get_gw_ble_version(self, gw_id):
        """
        :type gw_id: string
        :param gw_id: gateway id
        """
        gw = self.get_gateway(gw_id)
        return gw["reportedConf"]["bleChipSwVersion"]
    
    def get_gw_interface_version(self, gw_id):
        """
        :type gw_id: string
        :param gw_id: gateway id
        """
        gw = self.get_gateway(gw_id)
        return gw["reportedConf"]["interfaceChipSwVersion"]

    def get_brg_ble_version(self, brg_id):
        """
        :type brg_id: string
        :param brg_id: bridge id
        """
        brg = self.get_bridge(brg_id)
        return brg["version"]

    def check_energous_ble_reboot_needed(self, brg_id):
        """
        checks if energous reboot after config change is needed for BLE version
        :rtype: bool
        :return: True if supported, False otherwise
        """
        ble_ver = self.get_brg_ble_version(brg_id).split('.')
        # TODO - use packaging lib
        if ((int(ble_ver[0]) > 3) or (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 11) or \
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 10 and int(ble_ver[2]) > 38)):
            return False
        else:
            return True

    def check_gw_datasource_name(self, gw_id):
        interface_ver = version.parse(self.get_gw_interface_version(gw_id))
        FIRST_SUPPORTED = version.parse('3.15.38')
        if interface_ver >= FIRST_SUPPORTED:
            return GW_DATA_MODE
        else:
            return GW_DATA_SRC
        


    def get_max_sub1ghzoutputpower(self, brg_id):
        brg = self.get_bridge(brg_id)
        version = brg["version"].split(".")
        # TODO - use packaging lib
        if (int(version[0]) > 3) or (int(version[0]) > 2 and int(version[1]) > 7) or \
                (int(version[0]) > 2 and int(version[1]) > 6 and int(version[2]) > 65):
            return 32
        return None


    def is_global_pacing_zone(self, brg_id):
        """
        check if bridge supports global pacing by zone
        :param brg_id: bridge ID
        :type brg_id: str
        :return: True if supports, False if not
        :rtype: bool
        """
        brg = self.get_bridge(brg_id)
        version = brg["version"].split(".")
        # TODO - use packaging lib
        if (int(version[0]) > 3) or ((int(version[0]) == 3) and int(version[1]) > 12) or \
                (int(version[0]) == 3 and int(version[1]) == 12 and int(version[2]) > 35):
            return True
        return False


    def get_pacing_param_name(self, gw_id):
        """
        gets name of global pacing / pacing group parameter name in platform
        :rtype: str
        :return: parameter name
        """
        ble_ver = self.get_gw_ble_version(gw_id).split('.')
        # TODO - use packaging lib
        if ((int(ble_ver[0]) > 3) or (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 12) or \
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 11 and int(ble_ver[2]) > 34)):
            return 'globalPacingGroup'
        else:
            return 'globalPacingEnabled'

    def print_brgs_versions(brg_list, ignore_bridges=None):
        """
        :type brg_list: list of dictionaries
        :param brg_list: bridges to print
        :type ignore_bridges: list
        :param ignore_bridges: list of bridges ID to ignore
        """
        ignore_bridges = ignore_bridges if ignore_bridges is not None else []
        debug_print(SEP)
        debug_print("Bridges versions:")
        for brg in brg_list:
            if brg["id"] in ignore_bridges:
                continue
            debug_print("{} : {}".format(brg["id"], brg["version"]))
        debug_print(SEP)

    def get_tx_period(self, brg_id, rx_tx_period, d_c, is_single=False):
        if is_single:
            return math.ceil(d_c * rx_tx_period + 0.45)
        brg = self.get_bridge(brg_id)
        version = brg["version"].split(".")
        # TODO - use packaging lib
        if (int(version[0]) > 3) or (int(version[0]) > 2 and int(version[1]) > 7) or \
                (int(version[0]) > 2 and int(version[1]) > 6 and int(version[2]) > 56):
            return math.ceil(d_c * rx_tx_period)
        return math.ceil(d_c * rx_tx_period + 1.5)

    def is_brg_updated_to_ble_ver(self, brg_id, ble_ver):
        """
        :type brg_id: str
        :param brg_id: bridge ID
        :type ble_ver: str
        :param ble_ver: BLE version
        :rtype: bool
        :return: True if bridge is updated to BLE version, False otherwise
        """
        brg_ble_ver = self.get_brg_ble_version(brg_id)
        if brg_ble_ver == ble_ver:
            return True
        else:
            return False

    def is_brg_updated_to_gw_ver(self, gw_id, brg_id):
        """
        :type gw_id: str
        :param gw_id: gateway id
        :type brg_id: str
        :param brg_id: bridge id
        :rtype: bool
        :returns: true if bridge is updated to gw version, else returns false
        """
        gw_ver = self.get_gw_ble_version(gw_id)
        brg_ver = self.get_brg_ble_version(brg_id)
        if gw_ver == brg_ver:
            debug_print(f'GW {gw_id} and BRG {brg_id} are both updated to version {self.get_gw_version(gw_id)}')
            return True
        else:
            debug_print(f'GW {gw_id} ver. {gw_ver}, BRG {brg_id} ver. {brg_ver}')
            return False

    def check_thin_gw_support(self, gw_id):
        if self.get_gateway_type(gw_id) == GatewayType.WIFI:
            return self.check_ble_thin_gw_support(self.get_gw_ble_version(gw_id))
        else:
            return True

    @staticmethod
    def check_ble_thin_gw_support(ble_ver):
        """
        checks if thin GW is supported for BLE version
        :rtype: bool
        :return: True if supported, False otherwise
        """
        ble_ver = ble_ver.split('.')
        # TODO - use packaging lib
        if not ((int(ble_ver[0]) > 3) or
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 11) or \
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 10 and int(ble_ver[2]) > 39)):
            return False
        else:
            return True
        
    def check_brg_mel_mod_supprt(self,brg_id):
        """
        checks if thin brg is support mel modules
        :rtype: bool
        :return: True if supported, False otherwise
        """
        brg_ble_ver = version.parse(self.get_brg_ble_version(brg_id))
        FIRST_SUPPORTED_BLE = version.parse('3.16.00')
        if brg_ble_ver >= FIRST_SUPPORTED_BLE:
            return True
        return False

    def check_brg_ver4(self,brg_id):
        """
        checks if GW is at ver 4 or above
        :rtype: bool
        :return: True if supported, False otherwise
        """
        brg_ble_ver = version.parse(self.get_brg_ble_version(brg_id))
        FIRST_SUPPORTED_BLE = version.parse('4.0.0')
        if brg_ble_ver >= FIRST_SUPPORTED_BLE:
            return True
        return False
    
    def check_gw_ver4(self,gateway_id):
        """
        checks if GW is at ver 4 or above
        :rtype: bool
        :return: True if supported, False otherwise
        """
        gw_ble_ver = version.parse(self.get_gw_ble_version(gateway_id))
        FIRST_SUPPORTED_WIFI = version.parse('4.0.0')
        if gw_ble_ver >= FIRST_SUPPORTED_WIFI:
            return True
        return False

    def check_uart_sim_support(self,gateway_id):
        """
        checks if thin GW is support uart_sim
        :rtype: bool
        :return: True if supported, False otherwise
        """
        gw_type = self.get_gateway_type(gateway_id)
        if not gw_type == GatewayType.WIFI:
            debug_print(f"gateway type: {gw_type} doesn't support uart simulator")
            return False
        gw_ble_ver = version.parse(self.get_gw_ble_version(gateway_id))
        interface_ver = version.parse(self.get_gw_interface_version(gateway_id))
        debug_print(f'gw_ble_ver={gw_ble_ver} interface_ver={interface_ver}')
        FIRST_SUPPORTED_WIFI = version.parse('3.15.0')
        FIRST_SUPPORTED_BLE = version.parse('3.16.20')
        if interface_ver >= FIRST_SUPPORTED_WIFI and gw_ble_ver >= FIRST_SUPPORTED_BLE:
            return True
        else:
            debug_print('Error! gateway versions do not support uart simulator')
        return False

    @staticmethod
    def ep_36_exist(version):
        """
        :type version: string
        :param version: FW version of bridge
        """
        major, minor, build = [int(v) for v in version]
        # TODO - use packaging lib
        if major > 3 or major == 3 and minor > 6 or major == 3 and minor == 6 and build > 28:
            return True
        else:
            return False

    # Configuration Changes
    def change_gw_config(self, gws_list, config_dict, minutes_timeout=5, ignore_missing_params=False, validate=True):
        """
            change configuration for multiple GWs
            :type gws_list: every iterable type
            :param gws_list: desired gateways to configure
            :type config_dict: dict
            :param config_dict: dictionary of parameters and values to configure
            :type ignore_missing_params: bool
            :param ignore_missing_params: if True, will return all GWs as updated as long as all available params have been changed
        """
        if not config_dict:  # check there are parameters to configure
            return gws_list

        def check_updated(gw_id, config_dict):
            """
            :param gw_id: Gateway ID
            :param config_dict: config dictionary
            """
            gw = self.get_gateway(gw_id)
            if 'version' in config_dict.keys():
                try:
                    gw_version = gw['version']
                    if gw_version != config_dict['version']:
                        return False
                except KeyError:
                    debug_print(f'Version not yet updated for {gw_id}... sleeping for 30 seconds')
                    sleep(30)
            if 'additional' in gw['reportedConf'].keys():
                gw_dict = gw['reportedConf']['additional']
            else:
                gw_dict = {}
            relevant_dict = {}
            missing_keys = []
            if GW_DATA_MODE in config_dict or GW_DATA_SRC in config_dict:
                if GW_DATA_MODE in config_dict:
                    config_dict[GW_DATA_SRC] = config_dict[GW_DATA_MODE]
                else:
                    config_dict[GW_DATA_MODE] = config_dict[GW_DATA_SRC]
                if self.check_gw_datasource_name(gw_id) == GW_DATA_SRC:
                    config_dict.pop(GW_DATA_MODE)
                else:
                    config_dict.pop(GW_DATA_SRC)
            for key in config_dict.keys():
                if key not in gw_dict.keys():
                    missing_keys.append(key)
                else:
                    relevant_dict.update({key: gw_dict[key]})
            if relevant_dict == config_dict:
                return True
            if len(missing_keys) > 0:
                if ignore_missing_params:
                    relevant_config_dict = config_dict.copy()
                    for key in missing_keys:
                        relevant_config_dict.pop(key)
                    if relevant_dict == relevant_config_dict:
                        return True
                    return False
                raise ParamMissingError(
                    f"{missing_keys} not in GW {gw_id} Parameters! Check FW Version or change desired config")
            return False

        desired_version = None
        if 'version' in config_dict.keys():
            desired_version = config_dict.pop('version')
        config_dict_altered = {'additional': config_dict}
        if desired_version is not None:
            config_dict_altered.update({'version': desired_version})
        updated_gws = []
        params_missing = []
        config_sent = False
        timeout = datetime.datetime.now() + datetime.timedelta(minutes=minutes_timeout)
        sleep_needed = False
        while datetime.datetime.now() <= timeout and set(updated_gws) != set(gws_list):
            if sleep_needed:
                sleep(10)
                sleep_needed = False
            # Configure Gateways
            if not config_sent:
                try:
                    self.update_gateways_configuration(gws_list, config_dict_altered)
                    debug_print(f'Configuration sent to {gws_list}')
                    config_sent = True
                    if not validate:
                        updated_gws = gws_list
                except EXCEPTIONS_TO_CATCH as e:
                    debug_print(f'{gws_list}: {e}')
                    sleep_needed = True

            # Check if GWs updated
            for gw_id in set(gws_list) - set(updated_gws):
                try:
                    gw_updated = check_updated(gw_id, config_dict.copy())
                    if gw_updated:
                        updated_gws.append(gw_id)
                except EXCEPTIONS_TO_CATCH as e:
                    debug_print(f'{gw_id}: {e}')
                    sleep_needed = True
                except ParamMissingError as e:
                    params_missing.append((e, gw_id))
                    updated_gws.append(gw_id)
        for error, gw in params_missing:
            debug_print(error)
            updated_gws.remove(gw)
        debug_print(f'{updated_gws} updated to desired configuration:')
        debug_print(config_dict, pretty=True)
        return updated_gws

    def change_brg_config(self, connected_bridges, config_dict, minutes_timeout=5, ignore_bridges=[None]):
        """
            change configuration for all bridge in connected_bridges
            hange configuration to all in connected_bridges
            :type connected_bridges: every iterable type
            :param connected_bridges: desired bridges to configure
            :type config_dict: dict
            :param config_dict: dictionary of parameters and values to configure
            :type ignore_bridges: list
            :param ignore_bridges: list of bridges ID to ignore
            :rtype: list
            :return: list of updated bridges
        """
        brgs_list = list(set(connected_bridges) - set(ignore_bridges))
        updated_brgs = []
        if len(brgs_list) == 0:
            return updated_brgs
        if not config_dict:
            return brgs_list
        
        def is_dict_subset_of_dict(dict1, dict2, path=""):
            """
            Checks if dict1 is a subset of dict2. If not, returns the missing keys.
            """
            missing_keys = []
            
            def helper(d1, d2, p):
                nonlocal missing_keys
                
                for key in d1:
                    full_key = f"{p}.{key}" if p else key
                    
                    if key not in d2:
                        missing_keys.append(full_key)
                    else:
                        value1 = d1[key]
                        value2 = d2[key]
                        if isinstance(value1, dict) and isinstance(value2, dict):
                            helper(value1, value2, full_key)
                        elif value1 != value2:
                            missing_keys.append(full_key)

            helper(dict1, dict2, path)
            
            is_subset = len(missing_keys) == 0
            return is_subset, missing_keys

        def update_bridge(brg_id, config_dict):
            """
            :param brg_id: Bridge ID
            :param config_dict: config dictionary
            """
            res = self.update_bridge_configuration(brg_id, config_dict) 
            if self.get_bridge_board(brg_id) == BoardTypes.ENERGOUS.value and self.check_energous_ble_reboot_needed(
                    brg_id):
                debug_print(f'Rebooting energous Bridge {brg_id}...')
                self.send_action_to_bridge(brg_id, BridgeAction.REBOOT)
            return res

        def get_brg_cfg_of_brg_info(bridge_info):
            """
            Extracting bridge configuration for a bridge id while supporing mel modules and previouse versions
            :param bridge_id: String - the ID of the bridge to get information about
            :return: A dictionary containing bridge configuration
            """
            bridge_info_received = bridge_info
            brg_config = {}
            def recursive_extract_config(dictionary):
                if "config" in dictionary:
                    brg_config.update(dictionary["config"])
                for key, value in dictionary.items():
                    if isinstance(value, dict):
                        recursive_extract_config(value)

            recursive_extract_config(bridge_info)
            if not brg_config:
                return bridge_info
            return brg_config

        def check_updated(brg_id, config_dict):
            """
            :param brg_id: Bridge ID
            :param config_dict: config dictionary
            """
            return True
            # bridge_info = self.get_bridge(brg_id)
            # if 'modules' in bridge_info and len(bridge_info['config'])>0:
            #     is_subset, keys_missing = is_dict_subset_of_dict(config_dict, bridge_info['config'])
            # elif 'modules' in bridge_info:
            #     is_subset, keys_missing = is_dict_subset_of_dict(config_dict, bridge_info['modules'])
            # if is_subset:
            #     debug_print(f'{brg_id} updated')
            #     return True
            # if len(keys_missing) > 0:
            #     print(bridge_info)
            #     raise ParamMissingError(
            #         f"{keys_missing} not in BRG {brg_id} Parameters! Check FW Version or change desired config")
            # return False

        timeout = datetime.datetime.now() + datetime.timedelta(minutes=minutes_timeout)
        brgs_to_config = {brg: True for brg in brgs_list}
        params_missing = []
        sleep_needed = False
        while datetime.datetime.now() <= timeout and set(updated_brgs) != set(brgs_list):
            if sleep_needed:
                sleep(10)
                sleep_needed = False
            # Update bridges
            for brg_id in filter(brgs_to_config.get, brgs_to_config):
                try:
                    res = update_bridge(brg_id, config_dict)
                    debug_print(f'Sent configuration to bridge {brg_id}')
                    brgs_to_config[brg_id] = not res
                except EXCEPTIONS_TO_CATCH as e:
                    debug_print(f'{brg_id}: {e}')
                    ueded = True
            # Check if bridges updated
            for brg_id in set(brgs_list) - set(updated_brgs):
                try:
                    brg_updated = check_updated(brg_id, config_dict)
                    if brg_updated:
                        updated_brgs.append(brg_id)
                    else:
                        pass
                        ## TODO TEMP
                        # debug_print(f'Sending configuration again to bridge {brg_id}')
                        # sleep(3)
                        # update_bridge(brg_id, config_dict)
                except (EXCEPTIONS_TO_CATCH) as e:
                    debug_print(f'{brg_id}: {e}')
                    sleep_needed = True
                except ParamMissingError as e:
                    params_missing.append((e, brg_id))
                    updated_brgs.append(brg_id)
        for error, brg in params_missing:
            debug_print(error)
            updated_brgs.remove(brg)
        if minutes_timeout>0:
            if updated_brgs:
                debug_print(f'{(updated_brgs)} updated to desired configuration:')
            else:
                debug_print('No bridge is updated to desired configuration:')
        else:
            debug_print(f'{brgs_list} will update to desired configuration when back online:')
        debug_print(config_dict, pretty=True)
        return updated_brgs

    # Connect & Brownout
    def change_to_brownout(self, connected_bridges, seconds_in_bo=0, ignore_bridges=None):
        """
            change all bridges in connected_bridges to brownout mode and sleeps for seconds_in_bo seconds.
            :type connected_bridges: every iterable type
            :param connected_bridges: desired bridges to configure
            :type seconds_in_bo: int
            :param seconds_in_bo: time to sleep in brownout [seconds]
            :type ignore_bridges: list
            :param ignore_bridges: list of bridges ID to ignore
            example:
            wiliot.change_to_brownout(["4CEE79FA3523", "D0269CFEB518"], seconds_in_bo=300)
        """
        ignore_bridges = list() if ignore_bridges is None else ignore_bridges
        relevant_brgs = list(set(connected_bridges) - set(ignore_bridges))
        ver4_support_brgs = [brg for brg in relevant_brgs if self.check_brg_ver4(brg)]
        not_ver4_support_brgs = [brg for brg in relevant_brgs if not self.check_brg_ver4(brg)]
        brgs_ver4_updated = self.change_brg_config(ver4_support_brgs, BO_DICT)
        brgs_not_ver4_updated = self.change_brg_config(not_ver4_support_brgs, {'energyPattern': 36})
        if seconds_in_bo > 0:
            debug_print(f'Sleeping for {datetime.timedelta(seconds=seconds_in_bo)}')
            sleep(seconds_in_bo)
        return brgs_ver4_updated + brgs_not_ver4_updated

    def connect_gw_bridges(self, gw_ids=None, minutes_timeout=5, expected_num_brgs=None, ignore_bridges=None,
                           do_brown_out=True, expected_brgs=None):
        """
            Iteratively connects to bridges and change them to brownout.
            Function can take either GW IDs as input and then connect to all brgs connected to them 
            and if needed change them to brownout, 
            OR takes expected brgs and then connect to those and if needed change them to brownout.
            brgs listed in ignore bridges will be completely ignored.
            :type gw_ids: list
            :param gw_ids: list of GW ids
            :type minutes_timeout: int
            :param minutes_timeout: timeout to connect to bridges
            :type expected_num_brgs: int
            :param expected_num_brgs: maximum bridges in the deployment.
                                      if None, the function will scan for new bridges until minutes_timeout is over / wait for all expected brgs
            :type ignore_bridges: list
            :param ignore_bridges: list of bridges ID to ignore
            :type do_brown_out: bool
            :param do_brown_out: brown out bridges (change to EP 36)
            :type expected_brgs: list
            :param expected_brgs: list of expected BRG ids
            :rtype board_type_dict: dict
            :return board_type_dict: dictionary of bridge and board type
            :rtype connected_brgs type: list
            :return connected_brgs param: list of all connected bridges from csv
        """
        
        def get_bridge_type(brg_dict):
            if 'single' in brg_dict['boardType'].lower():
                return 'single'
            return 'dual'

        def get_connected_bridges(gw_ids, ignore_bridges, expected_brgs, timeout):
            connected_bridges = list()
            connected_bridges_dicts = None
            sleep_needed = False
            while connected_bridges_dicts is None and datetime.datetime.now() < timeout:
                if sleep_needed:
                    sleep(5)
                try:
                    connected_bridges_dicts = self.get_bridges(online=True, gateway_id=gw_ids)
                except EXCEPTIONS_TO_CATCH as e:
                    print(e)
                    sleep_needed = True
            board_type_dict = {'dual': [], 'single': []}
            for brg_dict in connected_bridges_dicts:
                brg_id = brg_dict['id']
                # skip ignore bridges
                if brg_id in ignore_bridges:
                    continue
                # skip bridges not in expected brgs
                if len(expected_brgs) > 0:
                    if brg_id not in expected_brgs:
                        continue
                # claim unclaimed bridges
                if not brg_dict['claimed']:
                    self.claim_bridge(brg_id)
                board_type_dict[get_bridge_type(brg_dict)].append(brg_id)
                connected_bridges.append(brg_id)
            return connected_bridges, board_type_dict
        if gw_ids is None:
            if len(expected_brgs) > 0:
                gw_ids = list(self.get_gateways_from_bridges(expected_brgs).keys())
            else:
                raise ValueError('Must input either GW IDs or expected bridges!')
        ignore_bridges = list() if ignore_bridges is None else ignore_bridges
        expected_brgs = list() if expected_brgs is None else expected_brgs
        # remove ignore bridges from expected_brgs
        expected_brgs = list(set(expected_brgs) - set(ignore_bridges))
        expected_num_brgs = -1 if expected_num_brgs is None else expected_num_brgs
        timeout = datetime.datetime.now() + datetime.timedelta(minutes=minutes_timeout)
        connected_bridges, board_type_dict = get_connected_bridges(
            gw_ids, ignore_bridges, expected_brgs, timeout)
        brgs_brownout_status = dict()
        if do_brown_out:
            brgs_brownout_status = dict(map(lambda x: (x, False), connected_bridges))
        if expected_num_brgs < 0:
            debug_print(
                f'Connecting bridges | Timeout at {timeout.time()}')
        else:
            debug_print(
                f'Connecting{" and browning out" if do_brown_out else ""} {expected_num_brgs} bridges | Timeout at {timeout.time()}')
        if len(expected_brgs) > 0:
            debug_print(f'Expecting bridges {expected_brgs}')
            if expected_num_brgs == -1:
                expected_num_brgs = len(expected_brgs)
        last_print = datetime.datetime.now() - datetime.timedelta(minutes=1)
        while (datetime.datetime.now() < timeout and \
               (False in brgs_brownout_status.values() or (len(connected_bridges) < expected_num_brgs
                                                           and not (set(expected_brgs) <= set(connected_bridges))))):
            connected_bridges, board_type_dict = get_connected_bridges(
                gw_ids, ignore_bridges, expected_brgs, timeout)
            # update new brgs to brownout
            new_brgs = list(set(connected_bridges) - set(brgs_brownout_status.keys()))
            brgs_brownout_status.update({brg: False for brg in new_brgs})
            if (datetime.datetime.now() - last_print).total_seconds() > 5:
                debug_print(
                    f'{len(connected_bridges)}{(" / " + str(expected_num_brgs)) if expected_num_brgs > 0 else ""} connected bridges')
                last_print = datetime.datetime.now()
            # do brown out for needed bridges
            if do_brown_out and False in brgs_brownout_status.values():
                # update only needed bridges
                brgs_to_update = [brg for brg, status in brgs_brownout_status.items() if status is False]
                brgs_updated = self.change_to_brownout(brgs_to_update)
                # change brownout status to true
                brgs_brownout_status.update({brg: True for brg in brgs_updated})
        if False in brgs_brownout_status.values():
            browned_out_brgs = list(filter(brgs_brownout_status.get, brgs_brownout_status))
            non_browned_out_brgs = list(set(connected_bridges) - set(browned_out_brgs))
            raise WiliotCloudError(f'Cannot change connected BRGs {non_browned_out_brgs} to brownout! Check deployment!')
        
        debug_print(f'{len(gw_ids)} GWs {gw_ids} Connected')
        debug_print(f'{len(connected_bridges)} BRGs {connected_bridges} Connected')
        return connected_bridges, board_type_dict
    
    
    def check_gw_compatible_for_action(self, gateway_id):
        """
        checks if gateway is compatible to send and receive power management configurations
        :type gateway_id: str
        :param gateway_id: gateway ID
        :rtype: bool
        """
        gateway_type = self.get_gateway_type(gateway_id)
        if gateway_type != GatewayType.WIFI:
            if gateway_type == GatewayType.MOBILE: 
                return True
            else:
                return False
        gw_dict = self.get_gateway(gateway_id)        
        ble_ver = gw_dict["reportedConf"]["bleChipSwVersion"]
        if gw_dict['online']:
            if 'gwMgmtMode' in gw_dict['reportedConf']['additional']:
                if gw_dict['reportedConf']['additional']['gwMgmtMode'] == 'transparent':
                    support = self.check_gw_ble_transparent_support(ble_ver)
                    if not support:
                        debug_print(f'Please update GW {gateway_id} or change to active mode for power management support!')
                    return support
                return True
            return True
        return False
    
    @staticmethod
    def check_gw_ble_transparent_support(ble_ver):
        """
        checks if power management is supported for transparent GW BLE version
        :rtype: bool
        :return: True if supported, False otherwise
        """
        ble_ver = ble_ver.split('.')
        # TODO - use packaging lib
        if not ((int(ble_ver[0]) > 3) or
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 14) or \
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 13 and int(ble_ver[2]) > 27)):
            return False
        else:
            return True
    
    def brg_cfg_to_mel_module_v4(self,cfg_dict):
        def remove_empty(dict={}):
            res = {}
            for k,v in dict.items():
                if v != None:
                    res[k] = v 
            return res
        energy2400  = {}
        datapath    = {}
        energySub1g = {}
        calibration = {}
        powerManagement = {}
        externalSensor = {}
        energy2400['dutyCycle']          =   cfg_dict.get("dutyCycle2400")
        energy2400['outputPower']        =   cfg_dict.get("outputPower2400")
        energy2400['energyPattern2400']       =   cfg_dict.get("energyPattern2400")
        energy2400 = remove_empty(energy2400)
        calibrationParams = ['calibPattern','calibInterval','calibOutputPower']
        for param in calibrationParams:
            calibration[param] = cfg_dict.get(param)
        calibration = remove_empty(calibration)
        datapathParams = ['pktFilter','txRepetition','adaptivePacer','pacerInterval','unifiedEchoPkt','commOutputPower','globalPacingGroup']
        for param in datapathParams:
            datapath[param] = cfg_dict.get(param)
        datapath = remove_empty(datapath)
        energySub1g['cycle']        =   cfg_dict.get("cycle")
        energySub1g['dutyCycle']        =   cfg_dict.get("sub1gdutyCycle")
        energySub1g['sub1gEnergyPattern']        =   cfg_dict.get("sub1gEnergyPattern")
        energySub1g['outputPower']      =  cfg_dict.get("sub1GhzOutputPower")
        energySub1g = remove_empty(energySub1g)
        powerManagementParams = ['staticLedsOn','dynamicLedsOn','staticOnDuration','dynamicOnDuration',
                                 'staticKeepAliveScan','staticSleepDuration','dynamicKeepAliveScan',
                                 'dynamicSleepDuration','staticKeepAlivePeriod','dynamicKeepAlivePeriod']
        externalSensorParams = ['adType0','adType1','uuidLsb0','uuidLsb1','uuidMsb0','uuidMsb1','sensor0Scramble','sensor1Scramble']
        for param in powerManagementParams:
            powerManagement[param] = cfg_dict.get(param)
        powerManagement = remove_empty(powerManagement)
        for param in externalSensorParams:
            externalSensor[param] = cfg_dict.get(param)
        externalSensor = remove_empty(externalSensor)


        mel_mod_cfg = {
            "energy2400": {
                "config": energy2400   
            },
            "energySub1g": {
                "config": energySub1g
            },
            "datapath": {
                "config": datapath
            },
            "powerManagement": {
                "config": powerManagement
            },
            "externalSensor": {
                "config": externalSensor
            },
            "calibration": {
                "config": calibration
            }
        }
        return mel_mod_cfg
    
    def firmware_update(self, timeout_minutes=3,gws=None, brgs=None, version=None):
        """
        Update firmware for a gateway or a list of bridges.

        Args:
            timeout_minutes (int, optional): Maximum time to approve a gateway. Defaults to 3.
            gw (str, optional): Gateway ID. Defaults to None.
            brgs (list, optional): List of bridge IDs. Defaults to None.
            version (str, optional): Desired version to update to. Defaults to None.
            api_version (str, optional): Desired gateway API version. Defaults to None.

        Raises:
            ValueError: If neither or both gateway and bridge are provided.
            TypeError: If bridges are not provided as a list.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        def compare_versions(version1, version2):
            # Split the version strings into parts
            parts1 = version1.split('.')
            parts2 = version2.split('.')
            
            length = max(len(parts1), len(parts2))
            int_parts1 = [int(parts1[i]) if i < len(parts1) else 0 for i in range(length)]
            int_parts2 = [int(parts2[i]) if i < len(parts2) else 0 for i in range(length)]
            
            for v1, v2 in zip(int_parts1, int_parts2):
                if v1 < v2:
                    return False
                elif v1 > v2:
                    return True
            # If all parts are equal, return 0
            return 0
        
        if gws is None and brgs is None:
            raise KeyError("Must enter Gateway or Bridge!")
        elif gws is not None and brgs is not None:
            raise KeyError("Enter only Gateway or only Bridge!")
        elif gws is not None:
            if not isinstance(gws, list):
                raise TypeError("Gateways must be entered as a list")
            for gw in gws:
                debug_print(f"Updating Gateway '{gw}' to version '{version}'")
                gw_conf = self.get_gateway(gw)
                if compare_versions(gw_conf['reportedConf']['version'], version):
                    debug_print(f"Cannot downgrade {gw}, not supported")
                    return False
                res = self.update_gateway_configuration(gw, {"version": version})
                if res:
                    debug_print(f"Gateway '{gw}' updated to desired configuration")
                    return True
                else:
                    debug_print(f"Failed to update '{gw}'")
        elif brgs is not None:
            if not isinstance(brgs, list):
               raise TypeError("Bridges must be entered as a list")
            for bridge in brgs:
                path = "bridge/{}".format(bridge)
                payload = {'desiredVersion' : version}
                try:
                    res = self._put(path, payload)
                    return res["message"].lower().find("updated bridge success") != -1
                except Exception as e:
                    print(f"Failed to update bridge configuration: {e}")  

class ExtendedPlatformClient(PlatformClient):
    def __init__(self, api_key, owner_id, env='prod', region='us-east-2', cloud='', log_file=None, logger_=None):
        super().__init__(api_key=api_key, owner_id=owner_id, env=env, region=region, cloud=cloud, log_file=log_file, logger_=logger_)

    def get_locations(self, locations=None):
        """
        :rtype: dict
        :return: Dictionary of locations and zones with relevant associations for each
        """
        in_locations = locations
        locations = super().get_locations()
        res = []
        for location in locations:
            if in_locations is not None and location['name'] not in in_locations:
                continue
            loc_id = location['id']
            location['associations'] = super().get_location_associations(loc_id)
            zones = super().get_zones(loc_id)
            for zone in zones:
                zone_id = zone['id']
                zone['associations'] = super().get_zone_associations(zone_id)
            location['zones'] = zones
            res.append(location)
        return res

    def get_locations_bridges(self, locations=None):
        """
            change a list of bridges associated to location
            if location is None, reffer all owner's locations
            :type locations: every iterable type
            :param locations: desired locations
            returns a list of dictionaries
            Each dictionary includes bridgeId, location properties and zone properties if a bridge is associated to zone
        """
        locations = self.get_locations(locations=locations)
        bridges = []
        for location in locations:
            # Add bridges directly associated with location
            for bridge in location['associations']:
                if bridge['associationType'] == 'bridge':
                    bridges.append({'bridgeId': bridge['associationValue'],
                                    'locationId': location['id'],
                                    'locationName': location['name'],
                                    'locationType': location['locationType']})
                    if 'location' in location.keys():
                        bridges[-1].update({
                            'locationLat': location['lat'],
                            'locationLng': location['lng'],
                            'location': location['location'],
                            'locationAddress': location['address']})
            # add bridges associated to zone (inside location)
            for zone in location['zones']:
                for bridge in zone['associations']:
                    if bridge['associationType'] == 'bridge':
                        bridges.append({'bridgeId': bridge['associationValue'],
                                        'locationId': location['id'],
                                        'locationName': location['name'],
                                        'zoneId': zone['id'],
                                        'zoneName': zone['name'],
                                        'locationType': location['locationType']})
                        if 'location' in location.keys():
                            bridges[-1].update({
                                'locationLat': location['lat'],
                                'locationLng': location['lng'],
                                'location': location['location'],
                                'locationAddress': location['address']})
        return bridges

    def get_location_id(self, location_name):
        locations = self.get_locations()
        for loc_dict in locations:
            if loc_dict['name'] == location_name:
                return loc_dict['id']

    def get_location_bridges(self, location_name):
        """
        get brgs from location name
        :param location_name: name of location
        :type location_name: str
        :return: list of brgs in location
        :rtype: list
        """
        location_id = self.get_location_id(location_name)
        loc_associations = self.get_location_associations(location_id)
        brgs_list = [assoc['associationValue'] for assoc in loc_associations if (assoc['associationType'] == 'bridge')]
        return brgs_list

    def get_locations_names(self):
        locations = super().get_locations()
        names = []
        for loc in locations:
            names.append(loc['name'])
        return names 