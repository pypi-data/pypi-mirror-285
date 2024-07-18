import os
import unittest
from wiliot_deployment_tools.internal.test_tool.test_tool import WiliotTestingUtils
from api_secrets import *
from wiliot_deployment_tools.common.analysis_data_bricks import get_spark


class TestTestingTool(unittest.TestCase):
    
    def test_init(self):
        self.test = WiliotTestingUtils(get_spark(), WH_EDGE, expected_num_brgs=1, working_directory=os.getcwd()+'/unittests/UTTest/')
        self.assertIsInstance(self.test, WiliotTestingUtils)
        folder = os.getcwd()+'/unittests/UTTest/'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def test_run_stages(self):
        with open(os.getcwd()+'/unittests/UTTest/testConfiguration.csv', 'x') as f:
            f.write("""
testId,testTimeMins,boTimeBeforeTestMins,gatewaysIncluded,bridgesIncluded,energyPattern,txPeriodMs,rxTxPeriodMs
1MinTest,1,0,GW98F4AB14DB4C,B7484419928A,63,5,15""")
        self.test = WiliotTestingUtils(get_spark(), WH_EDGE, expected_num_brgs=1, working_directory=os.getcwd()+'/unittests/UTTest/')
        self.assertTrue(self.test.init_gw_brgs())
        self.assertTrue(self.test.run_test())
        self.assertTrue(self.test.get_rawdata())
        self.assertTrue(self.test.get_tagstats())
        self.assertTrue(self.test.process_tagstats())

if __name__ == '__main__':
    unittest.main()
