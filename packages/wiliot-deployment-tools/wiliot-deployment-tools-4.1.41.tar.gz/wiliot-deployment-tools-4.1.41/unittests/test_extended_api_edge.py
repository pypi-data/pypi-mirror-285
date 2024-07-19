import unittest
from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient
from api_secrets import *
class TestExtendedEdge(unittest.TestCase):

    def test_init(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        self.assertIsInstance(edge, ExtendedEdgeClient)
        
    def test_get_connected_bridges(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        self.assertEquals(list(map(lambda x: x['id'], edge.get_connected_brgs(HOME_GW))), [HOME_BRG])
        
    def test_get_seen_bridges(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        self.assertEquals(edge.get_seen_bridges(HOME_GW), [HOME_BRG])
    
    def test_check_gw_online(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        self.assertTrue(edge.check_gw_online([HOME_GW]))

    def test_test_if_bridge_connected(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        self.assertTrue(edge.test_if_bridge_connected(edge.get_bridge(HOME_BRG)))

    def test_get_bridge_dict(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        self.assertIsInstance(edge.get_bridge(HOME_BRG), dict)

    def test_get_bridge_board(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        self.assertIsInstance(edge.get_bridge_board(HOME_BRG), str)

    def test_version_functions(self):
        edge = ExtendedEdgeClient(WH_EDGE, WH_OWNERID)
        home_gw_ver = edge.get_gw_version(HOME_GW)
        home_gw_ble_ver = edge.get_gw_ble_version(HOME_GW)
        home_brg_ble_ver = edge.get_brg_ble_version(HOME_BRG)
        self.assertIsInstance(home_gw_ver, str)
        self.assertIsInstance(home_gw_ble_ver, str)
        self.assertIsInstance(home_brg_ble_ver, str)
        self.assertFalse(edge.check_energous_ble_reboot_needed(HOME_BRG))
        self.assertEquals(edge.get_max_sub1ghzoutputpower(HOME_BRG), 32)
        self.assertEquals(edge.get_pacing_param_name(HOME_GW), 'globalPacingGroup')
        self.assertTrue(edge.is_brg_updated_to_ble_ver(HOME_BRG, home_brg_ble_ver))
        self.assertTrue(edge.is_brg_updated_to_gw_ver(HOME_GW, HOME_BRG))
        self.assertTrue(edge.check_thin_gw_support(HOME_GW))
        
if __name__ == '__main__':
    unittest.main()
