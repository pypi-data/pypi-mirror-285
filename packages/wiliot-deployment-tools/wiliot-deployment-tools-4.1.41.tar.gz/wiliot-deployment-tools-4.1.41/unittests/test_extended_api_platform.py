import unittest
from wiliot_deployment_tools.api.extended_api import ExtendedPlatformClient
from api_secrets import *
class TestExtendedPlatform(unittest.TestCase):

    def test_init(self):
        plat = ExtendedPlatformClient(WH_ASSET, WH_OWNERID)
        self.assertIsInstance(plat, ExtendedPlatformClient)
    
    def test_get_locations(self):
        plat = ExtendedPlatformClient(WH_ASSET, WH_OWNERID)
        self.assertIsInstance(plat.get_locations(), list)
    
    def test_get_locations_bridges(self):
        plat = ExtendedPlatformClient(WH_ASSET, WH_OWNERID)
        self.assertIsInstance(plat.get_locations_bridges(), list)

    def test_get_location_id(self):
        plat = ExtendedPlatformClient(WH_ASSET, WH_OWNERID)
        for location in plat.get_locations():
            name = location['name']
            self.assertIsInstance(plat.get_location_id(name), str)
    
    def test_get_location_bridges(self):
        plat = ExtendedPlatformClient(WH_ASSET, WH_OWNERID)
        for location in plat.get_locations():
            name = location['name']
            self.assertIsInstance(plat.get_location_bridges(name), list)

if __name__ == '__main__':
    unittest.main()
