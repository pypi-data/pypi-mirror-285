# Files
UT_MQTT_LOG_FILE = "ut_mqtt_log.json"

# GW defines
GW_ID =                         "gatewayId"
ADDITIONAL =                    "additional"
REPORTED_CONF =                 "reportedConf"
GW_CONF =                       "gatewayConf"
GW_NAME =                       "gatewayName"
GW_API_VERSION =                "apiVersion"
LAT =                           "lat"
LNG =                           "lng"
WLT_SERVER =                    "wiliotServer"
PACER_INTERVAL =                "pacerInterval"
PKT_TYPES_MASK =                "packetTypesMask"
RX_TX_PERIOD =                  "rxTxPeriodMs"
TX_PERIOD =                     "txPeriodMs"
ENERGY_PATTERN =                "energyPattern"
OUTPUT_POWER_2_4 =              "2.4GhzOutputPower"
NFPKT =                         "nfpkt"
RSSI =                          "rssi"
SRC_ID =                        "src_id"

MUL_BRG_TEST_MIN =              2
INTERNAL_BRG_RSSI =             1
BRIDGE_ID =                     "bridgeId"
ALIAS_BRIDGE_ID =               "aliasBridgeId"
GROUP_ID =                      "group_id"
BRG_ACTION =                    "bridgeAction"
INTERNAL_BRG_STR =              "internal_brg"
INTERNAL =                      "INTERNAL"

GW_DATA_MODE =                  "gwDataMode"
TAGS_AND_BRGS =                 "Tags & Bridges"
TAGS_ONLY =                     "Tags only"
BRGS_ONLY_37 =                  "Bridges only (ch37)"
BRGS_ONLY_38 =                  "Bridges only (ch38)"
BRGS_ONLY_39 =                  "Bridges only (ch39)"
HIBERNATE =                     "Hibernate"

BLE_WIFI =                      "ble_wifi"
BLE_LAN =                       "ble_lan"

WLT_SERVER =                    "wiliotServer"
PACER_INTERVAL =                "pacerInterval"
OUTPUT_POWER_2_4 =              "2.4GhzOutputPower"
USE_STAT_LOC =                  "useStaticLocation"
GW_ENERGY_PATTERN =             "energizingPattern"
VERSION =                       "version"
WIFI_VERSION =                  "interfaceChipSwVersion"
BLE_VERSION =                   "bleChipSwVersion"
DATA_COUPLING =                 "dataCoupling"
GW_MODE =                       "gwMode"
PROD =                          "prod"

GET_INFO_ACTION =               "getGwInfo"
REBOOT_GW_ACTION =              "rebootGw"
LOG_PERIOD_ACTION =             "LogPeriodSet"
GET_LOGS =                      "getLogs"
GW_INFO =                       "gatewayInfo"
GW_LOGS =                       "gatewayLogs"
GW_LATITUDE =                   "Latitude"
GW_LONGITUDE =                  "Longitude"
GW_LOG_PERIOD =                 30

# Thin gw defines
THIN_GW_PROTOCOL_VERSION =      "protocolVersion"
TX_PKT =                        "txPacket"
TX_MAX_DURATION_MS =            "txMaxDurationMs"
TX_MAX_RETRIES =                "txMaxRetries"
TRANPARENT_PKT_LEN =            31 * 2
COUPLED_DATA_PKT_LEN =          29 * 2 # No 1E16

# Configurable brg fields' names
BRG_TX_REPETITION =             "tx_repetition"
BRG_GLOBAL_PACING_GROUP =       "global_pacing_group"
BRG_OUTPUT_POWER =              "output_power"
BRG_CALIB_OUTPUT_POWER =        "calib_output_power"
BRG_COMM_OUTPUT_POWER =         "comm_output_power"
BRG_CALIB_INTERVAL =            "calib_interval"
BRG_CALIB_PATTERN =             "calib_pattern"
BRG_RXTX_PERIOD =               "rx_tx_period" # rx_tx_period_ms in Brg2GwCfg & Gw2BrgCfg
BRG_TX_PERIOD =                 "tx_period" # tx_period_ms in Brg2GwCfg & Gw2BrgCfg
BRG_DUTY_CYCLE =                "duty_cycle"
BRG_CYCLE =                     "cycle"
BRG_PACER_INTERVAL =            "pacer_interval"
BRG_PKT_FILTER =                "pkt_filter"
BRG_ENERGY_PATTERN_2_4 =        "energy_pattern_2400"
BRG_SUB1GHZ_ENERGY_PATTERN =    "sub1g_energy_pattern"
BRG_ADAPTIVE_PACER =            "adaptive_pacer"
BRG_UNIFIED_ECHO_PKT =          "unified_echo_pkt"
BRG_COMM_PATTERN =              "comm_pattern"

# Common defines
PACKETS =                       "packets"
TIMESTAMP =                     "timestamp"
ACTION =                        "action"
PAYLOAD =                       "payload"
SEQUENCE_ID =                   "sequenceId"
MODULE_IF =                     "module IF"
HB =                            "HB"
DATETIME =                      "datetime"
TIME =                          "time"
TIMESTAMP_DELTA =               "timestamp_delta"
TAGS_COUNT =                    "tags_count"
NEW_TAGS =                      "new_tags"
TTFP =                          "ttfp"

# External Sensors
IS_SENSOR =                      "isSensor"
IS_EMBEDDED =                    "isEmbedded"
IS_SCRAMBLED =                   "isScrambled"
SENSOR_UUID =                    "sensorServiceId"
SENSOR_ID =                      "sensorId"

# OTA
STATUS_CODE_STR =                "statusCode"
IMG_DIR_URL =                    "imageDirUrl"
UPGRADE_BLSD =                   "upgradeBlSd"
VER_UUID_STR =                   "versionUUID"
VER_MAX_LEN =                    31

# Versions
VERSIONS = {
    "1.5.0" : {WIFI_VERSION: "3.5.32", BLE_VERSION: "3.7.25"},
    "1.5.2" : {WIFI_VERSION: "3.5.132", BLE_VERSION: "3.7.25"},
    "1.6.1" : {WIFI_VERSION: "3.5.51", BLE_VERSION: "3.8.18"},
    "1.7.0" : {WIFI_VERSION: "3.9.8", BLE_VERSION: "3.9.24"},
    "1.7.1" : {WIFI_VERSION: "3.10.6", BLE_VERSION: "3.10.13"},
    "1.8.0" : {WIFI_VERSION: "3.11.36", BLE_VERSION: "3.11.40"},
    "1.8.2" : {WIFI_VERSION: "3.11.36", BLE_VERSION: "3.11.42"},
    "1.9.0" : {WIFI_VERSION: "3.12.10", BLE_VERSION: "3.12.36"},
    "1.10.1" : {WIFI_VERSION: "3.13.29", BLE_VERSION: "3.13.25"},
    "3.14.0" : {WIFI_VERSION: "3.14.33", BLE_VERSION: "3.14.64"},
    "3.15.0" : {WIFI_VERSION: "3.15.38", BLE_VERSION: "3.15.72"},
    "3.16.3" : {WIFI_VERSION: "3.16.20", BLE_VERSION: "3.16.96"},
    "3.17.0" : {WIFI_VERSION: "3.17.25", BLE_VERSION: "3.17.90"},
    "4.0.0" : {WIFI_VERSION: "4.0.8", BLE_VERSION: "4.0.65"},
    "4.1.0" : {WIFI_VERSION: "4.1.8", BLE_VERSION: "4.1.33"}
}

# Tests defines
DEFAULT_GW_FIELD_UPDATE_TIMEOUT =   10
DEFAULT_BRG_FIELD_UPDATE_TIMEOUT =  10
HB_PERIOD =                         30
VER_UPDATE_TIMEOUT =                300
GW_LATITUDE_DEFAULT =               33.0222
GW_LONGITUDE_DEFAULT =              -117.0839
# Set to work with default when versions tests only pass through new api ver
GW_API_VER_DEFAULT =                "201"
GW_API_VER_OLD =                    "200"
BRG_CFG_HAS_LEN =                   2
CLEAR_DATA_PATH_TIMEOUT =           10
BRG_ADVERTISEMENT_TIMEOUT =         30 + 2 # First 30 for wlt app start & 2 extra for brg to settle to recieve its get module action
BRG_OTA_TIMEOUT =                   100
ACTION_LONG_TIMEOUT =               120
ACTION_SI_PKT_TIMEOUT =             10
ACTION_SHORT_TIMEOUT =              5

# Internal python ut defines - used only in ut
PACER_INTERVAL_THRESHOLD_HIGH =                     0.90
PACER_INTERVAL_THRESHOLD =                          0.80
GLOBAL_PACING_GROUP_THRESHOLD =                     0.70
PACKETS_ECHO_OFF =                                  16
TEST_PASSED =                                       0
TEST_FAILED =                                       -1
NO_RESPONSE =                                       "NO_RESPONSE"
DONE =                                              "DONE"
TEST_SUCCESS =                                      ":)"
MGMT_PKT =                                          "mgmt_pkt"
UNIFIED_PKT =                                       "unified_pkt"
SIDE_INFO_PKT =                                     "side_info_pkt"
DECODED_DATA =                                      "decoded_data"
TAG_ID =                                            "tag_id"
PACKET_CNTR =                                       "packet_cntr"
PACKET_TYPE =                                       "packet_type"
PACKET_DATA =                                       "packet_data"
PKTS =                                              "pkts"
MQTT_LOG_PRE_STR =                                  "mqtt_log_"
GW_DATA =                                           "gw_data"
GW_ID =                                             "gw_id"
CER =                                               "cer"
PKT_CNTR_DIFF =                                     "packet_cntr_diff"
AVG =                                               "avg_"
CER_PER_TAG =                                       "cer_per_tag"
AWS =                                               "aws"
TEST =                                              "test"

# test reasons
BRG_VER_SUCCESS =           "SUCCESS - BRG version matches expected version!"
WANTED_VER_SAME =           "Wanted version is same as original one!"
WANTED_VER_SAME_MUL =       "Wanted versions is same as original ones!"
VER_UPDATE_PASSED =         "Version Update Ran Successfully!"
VER_UPDATE_FAILED =         "The Update Process Has Been Interrupted!"

# Non Default defines
BRG_NON_DEFAULT_DUTY_CYCLE =                        15
BRG_NON_DEFAULT_OP_2_4 =                            6
BRG_NON_DEFAULT_EP_2_4 =                            1
BRG_NON_DEFAULT_OUTPUT_POWER_SUB1G =                26
BRG_NON_DEFAULT_CYCLE_SUB1G =                       40
BRG_NON_DEFAULT_PWR_MGMT_KEEP_ALIVE_SCAN =          0
BRG_NON_DEFAULT_TX_REPETITION =                     2
BRG_NON_DEFAULT_PACER_INTERVAL =                    20
BRG_NON_DEFAULT_CALIB_OUTPUT_POWER =                8
BRG_NON_DEFAULT_PKT_FILTER =                        17
BRG_NON_DEFAULT_CALIB_PATTERN =                     2
BRG_NON_DEFAULT_CALIB_INTERVAL =                    15

LIS2DW12_NON_DEFAULT_STATE_THRESHOLD =              93
LIS2DW12_NON_DEFAULT_WAKE_UP_DURATION =             120
LIS2DW12_NON_DEFAULT_SLEEP_DURATION =               35

# ---------------------------------------------------RTSA defines---------------------------------------------------
# common defines
TRACE_LOG_FILE_NAME =                   "TRACELOG"
TRACE_LOG_FILE_PATH =                   "C:/SignalVu-PC Files/" + TRACE_LOG_FILE_NAME + ".TOV"

# freq defines
FREQ_2_4_GHZ =                          {'37':2.402, '38':2.426, '39':2.480}
FREQ_SUB1G_MHZ =                        {'865_7':865.700, '915':915.000, '916_3':916.300, '917_5':917.500, '918':918.000, '919_1':919.100}

# SignalVu API commands defines
TRACE_DETECTION =                       {'average':'AVERage', 'positive':'POSitive', 'negative':'NEGative', 'positive-negative':'POSNegative', 'sample':'SAMPle'}
MAX_TRACE_POINTS =                      {'1K':'ONEK', '10K':'TENK', '100K':'HUNDredk', 'never_decimate':'NEVerdecimate' }

# default values
DEFAULT_LENGTH_MS =                     30
DEFAULT_TIME_PER_DIVISION_SEC =         5
DEFAULT_RX_TX_PERIOD_SEC =              0.015
BEACON_MIN_LENGTH_SEC =                 375e-6
BEACON_MAX_LENGTH_SEC =                 500e-6
ENERGIZING_TIME_THRESHOLD =             0.3
BEACON_POWER_THRESHOLD =                0.9
BEACON_POWER_CURVE_38 =                 0.7
BEACON_POWER_CURVE_39 =                 0.625
DEFAULT_SPAN_MHZ =                      5
RXTX_MAX_CFG =                          255
RXTX_CFG_DEFAULT =                      100

# test times
FREQ_BEACONS_ANALYSIS_TIME_DELTA =      10

# structured energizing patterns information
class energizingPattern:
    def __init__(self, ble_calibration_beacons = [], ble_energy = {}, ble_post_energy_beacons = [], sub1G_energy = False, info = ""):
        self.ble_calibration_beacons = ble_calibration_beacons
        self.ble_energy = ble_energy
        self.ble_post_energy_beacons = ble_post_energy_beacons
        self.sub1G_energy = sub1G_energy
        self.info = info

EP_INFO = {
        '17' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']]),
        '18' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['39'] : 1.0}),
        '20' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['37'] : 0.2, FREQ_2_4_GHZ['39'] : 0.8}),
        '24' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['37'] : 1.0}),
        '25' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['38'] : 1.0}),
        '26' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={2.454 : 1.0}),
        '27' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39'], FREQ_2_4_GHZ['39']]),
        '29' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['38'] : 0.3333, 2.454 : 0.3333, FREQ_2_4_GHZ['39'] : 0.3333}),
        '36' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'],FREQ_2_4_GHZ['38'],FREQ_2_4_GHZ['39']], info="idle"),
        '37' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], 2.415, FREQ_2_4_GHZ['39'], 2.441, 2.428, 2.454, 2.467], ble_energy={2.450 : 1.0}, info="euro"),
        '50' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], sub1G_energy=True),
        '51' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['39'] : 1.0}, sub1G_energy=True),
        '52' : energizingPattern(sub1G_energy=True),
        '55' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['37'] : 1.0}, sub1G_energy=True),
        '56' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={FREQ_2_4_GHZ['38'] : 1.0}, sub1G_energy=True),
        '57' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], FREQ_2_4_GHZ['38'], FREQ_2_4_GHZ['39']], ble_energy={2.454 : 1.0}, sub1G_energy=True),
        '61' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], 2.415, FREQ_2_4_GHZ['39'], 2.441, 2.428, 2.454, 2.467], sub1G_energy=True, info="euro"),
        '62' : energizingPattern(ble_calibration_beacons=[FREQ_2_4_GHZ['37'], 2.415, FREQ_2_4_GHZ['39'], 2.441, 2.428, 2.454, 2.467], ble_energy={2.475 : 1.0}, sub1G_energy=True, info="euro"),
        '99' : energizingPattern(ble_calibration_beacons=[i/1000.0 for i in range(2402, 2481, 2)])
                }

EP_FREQ_BREAKDOWN_COUNTER_SETUP = {
    2.402 : {'beacons':0, 'energy_in_ms': 0.0},
    2.426 : {'beacons':0, 'energy_in_ms': 0.0},
    2.480 : {'beacons':0, 'energy_in_ms': 0.0},
    2.403 : {'beacons':0, 'energy_in_ms': 0.0},
    2.427 : {'beacons':0, 'energy_in_ms': 0.0},
    2.483 : {'beacons':0, 'energy_in_ms': 0.0},
    2.454 : {'beacons':0, 'energy_in_ms': 0.0},
    2.481 : {'beacons':0, 'energy_in_ms': 0.0},
    2.415 : {'beacons':0, 'energy_in_ms': 0.0},
    2.441 : {'beacons':0, 'energy_in_ms': 0.0},
    2.428 : {'beacons':0, 'energy_in_ms': 0.0},
    2.467 : {'beacons':0, 'energy_in_ms': 0.0},
    2.475 : {'beacons':0, 'energy_in_ms': 0.0},
    0.8657 : {'beacons':0, 'energy_in_ms': 0.0},
    0.915 : {'beacons':0, 'energy_in_ms': 0.0},
    0.9163 : {'beacons':0, 'energy_in_ms': 0.0},
    0.9175 : {'beacons':0, 'energy_in_ms': 0.0},
    0.918 : {'beacons':0, 'energy_in_ms': 0.0},
    0.9191 : {'beacons':0, 'energy_in_ms': 0.0}
}

# Tag IDs for setup 1 & 4 - private setups in a chamber
# Added to support tag count in versions_analysis_test
NO_TAGS_STR = "no_tags"
SETUP_1_STR = "setup_1"
SETUP_4_STR = "setup_4"

PRIVATE_SETUP_CHOICES = [NO_TAGS_STR,
                         SETUP_1_STR,
                         SETUP_4_STR]

SETUP_1_TAG_IDS = [
    "000d40174823",
    "000d401747df",
    "000d401747f2",
    "000d40174862",
    "000d4017483d",
    "000d40174843",
    "000d401747f1",
    "000d4017482a",
    "000d401747f7",
    "000d40174869",
    "000d40174824",
    "000d40174829",
    "000d40174810",
    "000d4017480b",
    "000d401747d1",
    "000d4017480a",
    "000d401747f8",
    "000d401747cc",
    "000d40174882",
    "000d40174863",
    "000d4017483b",
    "000d401747cb",
    "000d40174842",
    "000d4017487c",
    "000d40174811",
    "000d401747e0",
    "000d40174881"
]
SETUP_4_TAG_IDS = [
    "000d40ce912e",
    "000d40ce9107",
    "000d40ce9233",
    "000d40ce9240",
    "000d40ce9219",
    "000d40ce912d",
    "000d40ce9120",
    "000d40ce9228",
    "000d40ce9146",
    "000d40ce9138",
    "000d40ce9200",
    "000d40ce9229",
    "000d40ce921a",
    "000d40ce9148",
    "000d40ce911f",
    "000d40ce920e",
    "000d40ce9232",
    "000d40ce9201",
    "000d40ce9137"
]

TAG_IDS = {
    SETUP_1_STR: SETUP_1_TAG_IDS,
    SETUP_4_STR: SETUP_4_TAG_IDS
}