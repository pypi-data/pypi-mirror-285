from wiliot_deployment_tools.internal.kafka_consumer.kafka_consumer import WiliotKafkaClient
from wiliot_deployment_tools.api.extended_api import BridgeThroughGatewayAction, ExtendedEdgeClient, GatewayType,ExtendedPlatformClient,EXCEPTIONS_TO_CATCH,BoardTypes
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.common.utils_defines import  SEC_TO_SEND,BROADCAST_DST_MAC
import json


class ConnectivtyAnalyzer():
    def __init__(self, edge_api_key, owner ,brgs = None, gws = None, env='prod', cloud="", region="us-east-2"):
        
        self.edge = ExtendedEdgeClient(edge_api_key, owner, env, cloud=cloud, region=region)
        self.gws = gws
        self.brgs = brgs
        self.kc = WiliotKafkaClient(env, cloud, keys=gws)
    
    def is_hexadecimal(self, char):
        """
        Check if a character is a hexadecimal digit.
        """
        return char.isdigit() or ('a' <= char.lower() <= 'f')
        
        
    def process_payload(self, input_string):
        """
        Process the string and extract the first 12 hexadecimal characters.
        """
        result = ''
        count = 0
        for char in input_string:
            if self.is_hexadecimal(char):
                result += char
                count += 1
                if count == 12:
                    break
        return result
    
    def send_hb_action(self, gateways):
        '''
        :param gateways: list of gateways to send action from
        Sends HB action from gateways to all seen bridges
        '''
        gw_payloads = []
        bridgeId = BROADCAST_DST_MAC
        for gw in gateways:
            try:
                gw_type = self.edge.get_gateway_type(gw)
                if gw_type is not GatewayType.ANDROID and gw_type is not GatewayType.MOBILE:
                    payload = self.process_payload(gw)
                    gw_payloads.append(payload)
                    try:
                        res = self.edge.send_bridge_action_through_gw(gw, BridgeThroughGatewayAction.GW_HB, payload, bridgeId)
                        debug_print(f'Sending HB packet through WIFI GW {gw}')
                    except Exception as e:
                        continue
                else:
                    debug_print(f'Gateway {gw} is a mobile gateway - not supported!')
            except Exception as e:
                if "not owned" in str(e):
                        debug_print(f"Warning!! gateway {gw} is not owned")
        return gw_payloads
    
    def check_ack(self, gw_payloads, bridges, gws):
        '''
        :param gw_payloads: A list of the payloads sent in the HB action by the gateway.
        :param bridges: A list of all bridges seen by the gateways.
        :return: A list of dictionaries with gw_payload, bridgeId and rssi as recieved in the gateway from
        that brideId's ack to the HB action.
        '''
        num_msgs_to_retreive = 500
        data = []
        messages = self.kc.get_last_messages_by_key(gws, num_msgs_to_retreive)
        for message in messages:
            value_str = message['value']
            try:
                value_dict = json.loads(value_str)
            except json.JSONDecodeError as e:
                debug_print(f"Error decoding value string: {e}")
                continue  # Skip to the next message if value_str is not in JSON format
            for key, value in value_dict.items():
                if key == 'packets':
                    parsed_data = {}
                    for packet in value:
                        remove_prefix_1E16 = lambda variable: str(variable)[4:] if str(variable).startswith("1E16") else variable
                        packet['payload'] = remove_prefix_1E16(packet['payload'])
                        payload_brg = packet['payload'][16:28]
                        payload_action_id = packet['payload'][28:30]
                        payload_gw = packet['payload'][30:42]
                        payload_rssi = int(packet['payload'][-2:], 16)
                        if payload_action_id == BridgeThroughGatewayAction.GW_HB.value and payload_gw in gw_payloads and payload_brg in bridges:
                            parsed_data = {'gw_payload' : payload_gw, 'bridge' : payload_brg, 'rssi' : payload_rssi}
                            data.append(parsed_data)   
        return data 
    
    def get_brgs_connected_gws(self, brgs):
        gws = []
        try:
            gws_dic = self.edge.get_gateways_from_bridges(brgs)
            for key, value in gws_dic.items():
                gws.append(key)
        except Exception as e:
            debug_print(f'Bridges not owned!; exception raised: {e}')
        return gws
    
    def get_gws_connected_brgs(self, gws):
        bridges = []
        for gw in gws:
            try:
                brgs_dic = self.edge.get_bridges(True, gw)
                for dic in brgs_dic:
                    bridges.append(dic['id'])
            except Exception as e:
                debug_print(f'Gateway {gw} is not owned!')
                continue
        return bridges
    
    def create_dic(self, gws, brgs):
        gw_brg_payload_dicts = []
        for gw in gws:
            brg_check_gw_list = []
            try:            
                gw_type = self.edge.get_gateway_type(gw)
                brg_check_gw_list.append(gw)
                brg_check = self.get_gws_connected_brgs(brg_check_gw_list)
                if gw_type is not GatewayType.ANDROID and gw_type is not GatewayType.MOBILE:
                    payload = self.process_payload(gw)
                else:
                    debug_print(f'Gateway {gw} is a mobile gateway - not supported!')
                for brg in brgs:
                    if brg in brg_check:
                        gw_brg_payload_dict = {'gw' : gw, 'bridge' : brg, 'gw_payload' : payload, 'rssi' : []}
                        gw_brg_payload_dicts.append(gw_brg_payload_dict)                    
            except Exception as e:
                if "not owned" in str(e):
                    debug_print(f"Warning!! gateway {gw} is not owned")
                    continue
        return gw_brg_payload_dicts
        
    def connectivity_analyzer(self):
        if self.gws and self.brgs:
            debug_print('Enter only brgs or gws')
            return None
        
        if self.gws:
            gws = self.gws
            gws_online = self.edge.check_gw_online(gws)
            if gws_online:
                brgs = self.get_gws_connected_brgs(gws)
                if brgs:
                    gw_brg_payload_dicts = self.create_dic(gws, brgs)
                else:
                    debug_print('No bridges connected to gateways for testing!')
            else:
                debug_print('Gateways offline!')
    
        elif self.brgs:
            brgs = self.brgs
            for brg in brgs:
                brg_online = self.edge.get_bridge_status(brg)
                if brg_online == 'offline':
                    brgs.remove(brg)
                    debug_print(f'Bridge {brg} is offline!')
            gws = self.get_brgs_connected_gws(brgs)
            if brgs and gws:
                gw_brg_payload_dicts = self.create_dic(gws, brgs)
            else:
                debug_print('No compatible gateways connected for running the test!')
                
        if gw_brg_payload_dicts:    
            gw_payloads = self.send_hb_action(gws)
            data = self.check_ack(gw_payloads, brgs, gws)
            brgs_with_good_uplink = []
            brgs_with_bad_uplink = []
            
            for dic_keys in gw_brg_payload_dicts:
                for dic_data in data:
                    if dic_data['gw_payload'] == dic_keys['gw_payload'] and dic_data['bridge'] == dic_keys['bridge']:
                        dic_keys['rssi'].append(dic_data['rssi'])
                if dic_keys['rssi'] and min(dic_keys['rssi']) < 76:
                    debug_print(f"Bridge {dic_keys['bridge']} has good connection to GW {dic_keys['gw']} with RSSIs {dic_keys['rssi']}")
                    brgs_with_good_uplink.append(dic_keys['bridge'])
                else:
                    debug_print(f"Bridge {dic_keys['bridge']} doesn't have a good connection to GW {dic_keys['gw']} with rssi {dic_keys['rssi']}")
                    brgs_with_bad_uplink.append(dic_keys['bridge'])
                    
            if brgs_with_good_uplink:
                for brg in list(set(brgs_with_good_uplink)):
                    debug_print(f'Bridge {brg} has a good downlink')
            if brgs_with_bad_uplink:
                for brg in list(set(brgs_with_bad_uplink)):
                    if brg not in brgs_with_good_uplink:
                        debug_print(f'Bridge {brg} has a bad downlink')
            return gw_brg_payload_dicts