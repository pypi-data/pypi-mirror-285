import datetime
import unittest
from wiliot_deployment_tools.internal.Archive.power_mgmt.power_mgmt import PowerManagementClient, PowerManagementPacket
from api_secrets import *
class TestPowerManagement(unittest.TestCase):

    def test_init(self):
        mgmt = PowerManagementClient(WH_EDGE, WH_OWNERID)
        self.assertIsInstance(mgmt, PowerManagementClient)
        
    def test_check_gw_compatible(self):
        mgmt = PowerManagementClient(WH_EDGE, WH_OWNERID)
        self.assertTrue(mgmt.check_gw_compatible_for_pwr_mgmt(HOME_GW))
    
    def test_get_brg_relevant_gw(self):
        mgmt = PowerManagementClient(WH_EDGE, WH_OWNERID)
        self.assertEquals(mgmt.get_bridge_relevant_gw(HOME_BRG), HOME_GW)
        
    def test_get_relevant_bridges(self):
        mgmt = PowerManagementClient(WH_EDGE, WH_OWNERID)
        self.assertEquals(mgmt.get_relevant_bridges(HOME_GW), [HOME_BRG])
    
    def test_check_ble_power_mgmt_support(self):
        ble_vers = [('3.7.25', False), ('3.8.20', False), ('3.11.39', False), ('3.11.40', True), ('3.12.40', True), ('4.0.15', True), ('-1', False)]
        for ver, support in ble_vers:
            actual = PowerManagementClient.check_ble_power_mgmt_support(ver)
            self.assertEquals(actual, support, f'{ver}, {actual}, {support}')
        
    def test_power_mgmt_functionality(self):
        with self.subTest('init_client'):
            mgmt = PowerManagementClient(WH_EDGE, WH_OWNERID)
        with self.subTest('send_blank_packet'):
            now = datetime.datetime.now()
            self.assertTrue(mgmt.send_pwr_mgmt_pkt(bridge_id=DESK_BRG, packet=PowerManagementPacket.exit_packet(), gateway_id=DESK_GW))
        with self.subTest('send_until_ack'):
            self.assertEquals(mgmt.send_packet_until_ack(DESK_GW, DESK_BRG, PowerManagementPacket.exit_packet()), {DESK_BRG: True})    
        with self.subTest('exit_power_mgmt'):
            self.assertEquals(mgmt.exit_power_mgmt(DESK_GW, False, DESK_BRG, False), {DESK_BRG: True})
if __name__ == '__main__':
    unittest.main()
