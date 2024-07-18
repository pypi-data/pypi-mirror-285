from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient, GatewayAction
from wiliot_deployment_tools.common.debug import debug_print

class GatewaySsidControl(ExtendedEdgeClient):
    def toggle_gw_ssid(self, gateway_id):
        """
        Toggles gateway preferred SSID (if a new SSID was not added, function will have no effect)
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :return: True if the cloud successfully sent the action to the gateway, False otherwise
        """
        res = self.send_action_to_gateway(gateway_id, GatewayAction.TOGGLE_SSID)
        debug_print(f'Rebooting GW {gateway_id}')
        return res

    def add_ssid_to_gw(self, gateway_id, ssid, pswd=None):
        """
        Adds SSID/PSWD pair to gateway
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type ssid: str
        :param ssid: SSID
        :type pswd: str
        :param pswd: Password
        :rtype: bool
        :return: True if the cloud successfully sent the action to the gateway, False otherwise
        """
        return self.send_action_to_gateway(gateway_id, GatewayAction.ADD_SSID, ssid=ssid, pswd=pswd)
