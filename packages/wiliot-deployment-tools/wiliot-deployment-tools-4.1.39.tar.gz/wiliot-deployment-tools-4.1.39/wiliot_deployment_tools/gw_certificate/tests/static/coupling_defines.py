from wiliot_deployment_tools.interface.if_defines import *
from wiliot_deployment_tools.ag.ut_defines import *

RECEIVED = 'received'
SHARED_COLUMNS = [PAYLOAD, BRIDGE_ID, NFPKT, RSSI]
INT64_COLUMNS = [NFPKT, RSSI]
OBJECT_COLUMNS = [PAYLOAD, BRIDGE_ID]
INIT_STAGES_DUPLICATIONS = [i for i in range(3,7)]
REPORT_COLUMNS = ['pkt_id', 'bridgeId', 'duplication', 'time_delay']
INCREMENTAL_TIME_DELAYS = [10, 50, 100, 255]
INCREMENTAL_STAGE_ADVA = '0000000000C0'
INCREMENTAL_PACKETS = range(255)