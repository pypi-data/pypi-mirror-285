import unittest
from wiliot_deployment_tools.internal.alert_service.databricks_alert_server import DatabricksAlertServer
from wiliot_deployment_tools.common.analysis_data_bricks import get_packet_table_name, get_spark, get_statistics_table_name
from db_secrets import DEBUG_SLACKCHANNEL, DEBUG_WEBHOOK
from ut_secrets import owners
from wiliot_deployment_tools.common.utils import timestamp_timedelta

class TestAlerts(unittest.TestCase):

    def test_init(self):
        alerts = DatabricksAlertServer(get_spark(), reset_owners=True)
        self.assertIsInstance(alerts, DatabricksAlertServer)

    def test_slackmessage(self):
        alerts = DatabricksAlertServer(get_spark(), reset_owners=True)
        self.assertTrue(alerts.send_to_slack('UnitTest Slack Message Test!', DEBUG_SLACKCHANNEL))
        
    def test_teamsmessage(self):
        alerts = DatabricksAlertServer(get_spark(), reset_owners=True)
        self.assertTrue(alerts.send_to_teams('UnitTest Teams Message Test!', DEBUG_WEBHOOK))

    def test_warehouse_alerts(self):
        das = DatabricksAlertServer(get_spark(), owners, reset_owners=True)
        packet_table = get_packet_table_name(owners[0]['ownerId'], 'prod', True)
        statistics_table = get_statistics_table_name('prod')
        data_1 = das.wdb.get_seen_edge_devices_from_packets(packet_table, timestamp_timedelta(hours=1.5),
                                                            timestamp_timedelta(hours=1))
        data_2 = das.wdb.get_seen_edge_devices_from_packets(packet_table, timestamp_timedelta(hours=1),
                                                            timestamp_timedelta(hours=0.5))
        data_3 = das.wdb.get_seen_edge_devices_from_packets(packet_table, timestamp_timedelta(hours=0.5),
                                                            timestamp_timedelta())
        seq_data_1 = das.wdb.get_sequence_id_loss(packet_table, statistics_table, timestamp_timedelta(hours=1.5),
                                                timestamp_timedelta(hours=1))
        seq_data_2 = das.wdb.get_sequence_id_loss(packet_table, statistics_table, timestamp_timedelta(hours=1),
                                                timestamp_timedelta(hours=0.5))
        seq_data_3 = das.wdb.get_sequence_id_loss(
            packet_table, statistics_table, timestamp_timedelta(hours=0.5), timestamp_timedelta())

        self.assertTrue(das.generate_owner_alert(owners[0], data_1, seq_data_1), 'Alerts #1')
        self.assertTrue(das.generate_owner_alert(owners[0], data_2, seq_data_2), 'Alerts #2')
        self.assertTrue(das.generate_owner_alert(owners[0], data_3, seq_data_3), 'Alerts #3')



if __name__ == '__main__':
    unittest.main()
