from wiliot_deployment_tools.interface.if_defines import *
from wiliot_deployment_tools.ag.ut_defines import *

UPLINK_BRG_ID = 'FFFFFFFFFFFF'
RECEIVED = 'received'
SEQ_ID = "sequenceId"
SHARED_COLUMNS = [PAYLOAD]
INT64_COLUMNS = [RSSI]
OBJECT_COLUMNS = [PAYLOAD]
INIT_STAGES_DUPLICATIONS = [i for i in range(2,9)]
REPORT_COLUMNS = ['pkt_id', 'duplication', 'time_delay']
INCREMENTAL_TIME_DELAYS = [10, 50, 100, 255]
TAG_STAGE_ADVA = '0000000000C0'
TAG_STAGE_PACKETS = range(40)
INCREMENTAL_PACKETS = range(255)