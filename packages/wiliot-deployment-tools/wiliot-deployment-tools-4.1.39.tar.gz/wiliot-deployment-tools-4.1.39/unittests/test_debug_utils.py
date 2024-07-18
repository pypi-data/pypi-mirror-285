import unittest
from wiliot_deployment_tools.common.debug import *


class TestDebuggingUtils(unittest.TestCase):

    def test_print_git_info(self):
        self.assertTrue(print_package_gitinfo())
    
    def test_if_databricks(self):
        self.assertFalse(is_databricks())


if __name__ == '__main__':
    unittest.main()
