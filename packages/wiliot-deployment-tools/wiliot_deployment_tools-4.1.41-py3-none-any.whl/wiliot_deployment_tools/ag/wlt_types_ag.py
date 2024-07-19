import bitstruct
import binascii

# This is auto generated file! Don't edit this file manually!!!

GROUP_ID_SIDE_INFO_SENSOR = 0xEB
GROUP_ID_SIDE_INFO = 0xEC
GROUP_ID_GW2BRG = 0xED
GROUP_ID_BRG2GW = 0xEE
GROUP_ID_UNIFIED_PKT = 0x3F

ACTION_EMPTY = 0
ACTION_REBOOT = 1
ACTION_BLINK = 2
ACTION_GET_MODULE = 3
ACTION_RESTORE_DEFAULTS = 4
ACTION_SEND_HB = 5
ACTION_EXT_SENSOR_DEPRECATED = 6
ACTION_SPARSE_37_DEPRECATED = 7
ACTION_GW_HB = 8
ACTION_GET_BATTERY_SENSOR = 9
ACTION_GET_POF_DATA = 10

BRG2BRG_ACTION_EMPTY = 0
BRG2BRG_ACTION_CFG = 1
BRG2BRG_ACTION_OTA = 2

RSSI_VAL_MIN = 40
RSSI_VAL_MAX = 103 # min val + 63 (6 bits)

API_VERSION_V0 = 0
API_VERSION_V1 = 1
API_VERSION_V2 = 2
API_VERSION_V5 = 5 # Because of backward compatabilty issue we jumped from V2 to V5
API_VERSION_V6 = 6
API_VERSION_V7 = 7
API_VERSION_V8 = 8
API_VERSION_V9 = 9
API_VERSION_V10 = 10
API_VERSION_LATEST = 10

API_VERSION_SENSOR_V0 = 0
API_VERSION_SENSOR_LATEST = 0

MODULE_EMPTY = 0
MODULE_GLOBAL = 0
MODULE_IF = 1
MODULE_DATAPATH = 2
MODULE_ENERGY_2400 = 3
MODULE_ENERGY_SUB1G = 4
MODULE_CALIBRATION = 5
MODULE_PWR_MGMT = 6
MODULE_EXT_SENSORS = 7
MODULE_CUSTOM = 8

SUB1G_ENERGY_PATTERN_NO_ENERGIZING = 0x00
SUB1G_ENERGY_PATTERN_SINGLE_TONE_915000 = 0x01
SUB1G_ENERGY_PATTERN_FCC_HOPPING = 0x02
SUB1G_ENERGY_PATTERN_JAPAN_1W = 0x03
SUB1G_ENERGY_PATTERN_JAPAN_350MW = 0x04
SUB1G_ENERGY_PATTERN_KOREA = 0x05
SUB1G_ENERGY_PATTERN_SINGLE_TONE_916300 = 0x06
SUB1G_ENERGY_PATTERN_SINGLE_TONE_917500 = 0x07
SUB1G_ENERGY_PATTERN_AUSTRALIA = 0x08
SUB1G_ENERGY_PATTERN_ISRAEL = 0x09
SUB1G_ENERGY_PATTERN_NZ_HOPPING = 0x0A
SUB1G_ENERGY_PATTERN_LAST = SUB1G_ENERGY_PATTERN_NZ_HOPPING

CHANNEL_FREQ_37 = 2402
CHANNEL_FREQ_38 = 2426
CHANNEL_FREQ_39 = 2480

CHANNEL_37 = 37
CHANNEL_38 = 38
CHANNEL_39 = 39

FREQUENCY_BAND_EDGE_2480 = 2480
FREQUENCY_BAND_EDGE_2475 = 2475

RADIO_TX_POWER_POS_2_DBM = 2
RADIO_TX_POWER_POS_3_DBM = 3
RADIO_TX_POWER_POS_6_DBM = 6
RADIO_TX_POWER_POS_8_DBM = 8

OUTPUT_POWER_2_4_GHZ_NEG_12 = -12
OUTPUT_POWER_2_4_GHZ_NEG_8 = -8
OUTPUT_POWER_2_4_GHZ_NEG_4 = -4
OUTPUT_POWER_2_4_GHZ_0 = 0
OUTPUT_POWER_2_4_GHZ_2 = 2
OUTPUT_POWER_2_4_GHZ_3 = 3
OUTPUT_POWER_2_4_GHZ_4 = 4
OUTPUT_POWER_2_4_GHZ_5 = 5
OUTPUT_POWER_2_4_GHZ_6 = 6
OUTPUT_POWER_2_4_GHZ_7 = 7
OUTPUT_POWER_2_4_GHZ_8 = 8

ENERGY_PATTERN_2_4_NO_ENERGIZING = 0x00
ENERGY_PATTERN_2_4_CHANNEL_37 = 0x01
ENERGY_PATTERN_2_4_CHANNEL_38 = 0x02
ENERGY_PATTERN_2_4_CHANNEL_39 = 0x03
ENERGY_PATTERN_2_4_FREQ_2450 = 0x04
ENERGY_PATTERN_2_4_FREQ_2454 = 0x05
ENERGY_PATTERN_2_4_LAST = ENERGY_PATTERN_2_4_FREQ_2454

SUB1G_FREQ_915000 = 915000
SUB1G_FREQ_916300 = 916300
SUB1G_FREQ_917500 = 917500
SUB1G_FREQ_918000 = 918000
SUB1G_FREQ_919100 = 919100
SUB1G_FREQ_905000 = 905000
SUB1G_FREQ_920000 = 920000

SUB1G_FREQ_PROFILE_915000 = 0
SUB1G_FREQ_PROFILE_916300 = 2
SUB1G_FREQ_PROFILE_917500 = 3
SUB1G_FREQ_PROFILE_918000 = 4
SUB1G_FREQ_PROFILE_919100 = 5
SUB1G_FREQ_PROFILE_920000 = 6

SUB1G_OUTPUT_POWER_11 = 11
SUB1G_OUTPUT_POWER_14 = 14
SUB1G_OUTPUT_POWER_17 = 17
SUB1G_OUTPUT_POWER_19 = 19
SUB1G_OUTPUT_POWER_20 = 20
SUB1G_OUTPUT_POWER_23 = 23
SUB1G_OUTPUT_POWER_25 = 25
SUB1G_OUTPUT_POWER_26 = 26
SUB1G_OUTPUT_POWER_27 = 27
SUB1G_OUTPUT_POWER_29 = 29
SUB1G_OUTPUT_POWER_32 = 32

SUB1G_OUTPUT_POWER_PROFILE_14 = 0
SUB1G_OUTPUT_POWER_PROFILE_17 = 1
SUB1G_OUTPUT_POWER_PROFILE_20 = 2
SUB1G_OUTPUT_POWER_PROFILE_23 = 3
SUB1G_OUTPUT_POWER_PROFILE_26 = 4
SUB1G_OUTPUT_POWER_PROFILE_29 = 5
SUB1G_OUTPUT_POWER_PROFILE_32 = 6

PKT_FILTER_RANDOM_FIRST_ARRIVING_PKT = 0x00
PKT_FILTER_DISABLE_FORWARDING = 0x10
PKT_FILTER_TEMP_PKT = 0x11
PKT_FILTER_ADVANCED_PKT = 0x12
PKT_FILTER_TEMP_AND_ADVANCED_PKTS = 0x13
PKT_FILTER_DEBUG_PKT = 0x14
PKT_FILTER_TEMP_AND_DEBUG_PKTS = 0x15
PKT_FILTER_TEMP_ADVANCED_AND_DEBUG_PKTS = 0x17

CALIB_PATTERN_STANDARD = 0x00
CALIB_PATTERN_38_38_39 = 0x01
CALIB_PATTERN_EU_PATTERN = 0x02
CALIB_PATTERN_DISABLE_BEACON = 0x03

COMM_PATTERN_STANDARD = 0x00
COMM_PATTERN_38_38_39 = 0x01
COMM_PATTERN_EU_PATTERN = 0x02
COMM_PATTERN_DISABLE_BEACON = 0x03

UNIFIED_ECHO_PKT_STATE_OFF = 0
UNIFIED_ECHO_PKT_STATE_ON = 1

ADAPTIVE_PACER_OFF = 0
ADAPTIVE_PACER_ON = 1

HDR_DEFAULT_PKT_SIZE = 0x1E
HDR_DEFAULT_AD_TYPE = 0x16
HDR_DEFAULT_BRG_UUID_MSB = 0xC6
HDR_DEFAULT_BRG_UUID_LSB = 0xFC
HDR_DEFAULT_BRG_SENSOR_UUID_MSB = 0x90
HDR_DEFAULT_BRG_SENSOR_UUID_LSB = 0xFC
HDR_DEFAULT_TAG_UUID_MSB = 0xAF
HDR_DEFAULT_TAG_UUID_LSB = 0xFD

BRG_DEFAULT_GLOBAL_PACING_GROUP = 0
BRG_DEFAULT_SCAN_CH = CHANNEL_37
BRG_DEFAULT_BRG_ENERGOUS_V1_OUTPUT_POWER_SUB1G = SUB1G_OUTPUT_POWER_29
BRG_DEFAULT_OUTPUT_POWER_SUB1G = SUB1G_OUTPUT_POWER_32
BRG_DEFAULT_BRG_ENERGOUS_V1_OUTPUT_POWER_SUB1G_PROFILE = SUB1G_OUTPUT_POWER_PROFILE_29
BRG_DEFAULT_OUTPUT_POWER_SUB1G_PROFILE = SUB1G_OUTPUT_POWER_PROFILE_32
BRG_DEFAULT_BRG_ENERGOUS_V1_TX_PERIOD = 40
BRG_DEFAULT_TX_PERIOD = 0
BRG_DEFAULT_ENERGIZE_FREQUENCY_2_4 = FREQUENCY_BAND_EDGE_2480
BRG_DEFAULT_BRG_ENERGOUS_V0_OUTPUT_POWER_2_4 = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_BRG_ENERGOUS_V1_OUTPUT_POWER_2_4 = RADIO_TX_POWER_POS_6_DBM
BRG_DEFAULT_BRG_ENERGOUS_V2_OUTPUT_POWER_2_4 = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_OUTPUT_POWER_2_4 = RADIO_TX_POWER_POS_2_DBM
BRG_DEFAULT_PACER_INTERVAL = 15
BRG_DEFAULT_PKT_FILTER = PKT_FILTER_TEMP_AND_ADVANCED_PKTS
BRG_DEFAULT_TX_REPETITION = 0
BRG_DEFAULT_TRANSMIT_TIME_SUB1G = 0
BRG_DEFAULT_SUB1G_FREQ = SUB1G_FREQ_915000
BRG_DEFAULT_SUB1G_FREQ_PROFILE = SUB1G_FREQ_PROFILE_915000
BRG_DEFAULT_CALIB_INTERVAL = 10
BRG_DEFAULT_CALIB_PATTERN = CALIB_PATTERN_38_38_39
BRG_DEFAULT_BRG_ENERGOUS_V0_CALIB_OUTPUT_POWER = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_BRG_ENERGOUS_V1_CALIB_OUTPUT_POWER = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_BRG_ENERGOUS_V2_CALIB_OUTPUT_POWER = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_CALIB_OUTPUT_POWER = RADIO_TX_POWER_POS_2_DBM
BRG_DEFAULT_BRG_ENERGOUS_V0_COMM_OUTPUT_POWER = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_BRG_ENERGOUS_V1_COMM_OUTPUT_POWER = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_BRG_ENERGOUS_V2_COMM_OUTPUT_POWER = RADIO_TX_POWER_POS_3_DBM
BRG_DEFAULT_COMM_OUTPUT_POWER = RADIO_TX_POWER_POS_2_DBM
BRG_DEFAULT_COMM_PATTERN = COMM_PATTERN_STANDARD
BRG_DEFAULT_ENERGY_DUTY_CYCLE_2_4 = 30
BRG_DEFAULT_ENERGY_PATTERN_2_4 = ENERGY_PATTERN_2_4_NO_ENERGIZING
BRG_DEFAULT_UNIFIED_ECHO_PKT = UNIFIED_ECHO_PKT_STATE_OFF
BRG_DEFAULT_ADAPTIVE_PACER = ADAPTIVE_PACER_OFF
BRG_DEFAULT_BRG_ENERGOUS_V0_SUB1G_ENERGY_PATTERN = SUB1G_ENERGY_PATTERN_SINGLE_TONE_915000
BRG_DEFAULT_BRG_ENERGOUS_V1_SUB1G_ENERGY_PATTERN = SUB1G_ENERGY_PATTERN_JAPAN_1W
BRG_DEFAULT_BRG_ENERGOUS_V2_SUB1G_ENERGY_PATTERN = SUB1G_ENERGY_PATTERN_SINGLE_TONE_915000
BRG_DEFAULT_SUB1G_ENERGY_PATTERN = SUB1G_ENERGY_PATTERN_NO_ENERGIZING
BRG_DEFAULT_BRG_ENERGOUS_V1_SUB1G_CYCLE = 100
BRG_DEFAULT_SUB1G_CYCLE = 15
BRG_DEFAULT_BRG_ENERGOUS_V1_SUB1G_DUTY_CYCLE = 40
BRG_DEFAULT_SUB1G_DUTY_CYCLE = 30
BRG_DEFAULT_BRG_ENERGOUS_V1_ENERGY_PATTERN_IDX_OLD = 71
BRG_DEFAULT_ENERGY_PATTERN_IDX_OLD = 50
BRG_DEFAULT_BRG_ENERGOUS_V1_RXTX_PERIOD = 100
BRG_DEFAULT_RXTX_PERIOD = 15
BRG_DEFAULT_PKT_TYPES_MASK = 0

INTERNAL_BRG_DEFAULT_INVALID_CFG = 0
INTERNAL_BRG_DEFAULT_SCAN_CH = CHANNEL_39
INTERNAL_BRG_DEFAULT_TX_PERIOD = 0
INTERNAL_BRG_DEFAULT_COMM_OUTPUT_POWER = RADIO_TX_POWER_POS_8_DBM
INTERNAL_BRG_DEFAULT_COMM_PATTERN = COMM_PATTERN_STANDARD
INTERNAL_BRG_DEFAULT_PACER_INTERVAL = 15
INTERNAL_BRG_DEFAULT_PKT_FILTER = PKT_FILTER_TEMP_AND_ADVANCED_PKTS
INTERNAL_BRG_DEFAULT_UNIFIED_ECHO_PKT = UNIFIED_ECHO_PKT_STATE_OFF
INTERNAL_BRG_DEFAULT_ADAPTIVE_PACER = ADAPTIVE_PACER_OFF

BRG_MGMT_MSG_TYPE_CFG_INFO = 1
BRG_MGMT_MSG_TYPE_OTA_UPDATE = 1
BRG_MGMT_MSG_TYPE_HB = 2
BRG_MGMT_MSG_TYPE_REBOOT = 3
BRG_MGMT_MSG_TYPE_LED_BLINK = 4
BRG_MGMT_MSG_TYPE_CFG_SET = 5
BRG_MGMT_MSG_TYPE_ACTION = 7 # msg_type cfg_get(6) was deprecated
BRG_MGMT_MSG_TYPE_BRG2BRG = 8

PWR_MGMT_DEFAULTS_LEDS_ON = 1
PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD = 20
PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN = 300
PWR_MGMT_DEFAULTS_ON_DURATION = 0
PWR_MGMT_DEFAULTS_SLEEP_DURATION = 0

BOARD_TYPE_FANSTEL_SINGLE_BAND_V0 = 0
BOARD_TYPE_FIRST = 0
BOARD_TYPE_FANSTEL_DUAL_BAND_V0 = 1
BOARD_TYPE_MINEW_SINGLE_BAND_V0 = 2
BOARD_TYPE_MINEW_DUAL_BAND_V0 = 3
BOARD_TYPE_ENERGOUS_V0 = 4
BOARD_TYPE_ENERGOUS_V1 = 5
BOARD_TYPE_ENERGOUS_V2 = 6
BOARD_TYPE_ERM_V0 = 7
BOARD_TYPE_ERM_V1 = 8
BOARD_TYPE_COGNIAN_V0 = 9
BOARD_TYPE_KOAMTAC_V0 = 10
BOARD_TYPE_INTERNAL_BRG = 11
BOARD_TYPE_LAST = 11
BOARD_TYPE_UN_INIT = 0xffffffff

ANT_SEL_MODE_RANDOM_TOGGLE = 0
ANT_SEL_MODE_CLEAR = 1
ANT_SEL_MODE_SET = 2
ANT_SEL_MODE_TOGGLE = 3

CUSTOM_ID_EMPTY = 0
CUSTOM_ID_LIS2DW12 = 1
CUSTOM_ID_BATTERY_SENSOR = 2
CUSTOM_ID_LAST = 2

SENSOR_SERVICE_ID_EMPTY = 0
SENSOR_SERVICE_ID_LIS2DW12 = 0x000001
SENSOR_SERVICE_ID_BATTERY_SENSOR = 0x000002
SENSOR_SERVICE_ID_POF_DATA = 0x800303

LIS2DW12_PACKET_VERSION_V1 = 1
LIS2DW12_PACKET_VERSION_LATEST = 1

LIS2DW12_DEFAULTS_CFG_PACKET_VERSION = LIS2DW12_PACKET_VERSION_LATEST
LIS2DW12_DEFAULTS_STATE_THRESHOLD = 1953
LIS2DW12_DEFAULTS_WAKE_UP_DURATION = 189
LIS2DW12_DEFAULTS_SLEEP_DURATION = 75

BATTERY_SENSOR_PACKET_VERSION_V1 = 1
BATTERY_SENSOR_PACKET_VERSION_LATEST = 1

POF_DATA_PACKET_VERSION_V1 = 1
POF_DATA_PACKET_VERSION_LATEST = 1

class UnifiedEchoPkt():
    def __init__(self, raw='', nonce_n_unique_id=0, nfpkt=0, rssi=0, brg_latency=0, global_pacing_group=0, mic=0, data=0):
        self.nonce_n_unique_id = nonce_n_unique_id
        self.nfpkt = nfpkt
        self.rssi = rssi
        self.brg_latency = brg_latency
        self.global_pacing_group = global_pacing_group
        self.mic = mic
        self.data = data
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, UnifiedEchoPkt):
            return (
                self.nonce_n_unique_id == other.nonce_n_unique_id and
                self.nfpkt == other.nfpkt and
                self.rssi == other.rssi and
                self.brg_latency == other.brg_latency and
                self.global_pacing_group == other.global_pacing_group and
                self.mic == other.mic and
                self.data == other.data
            )
        return False

    def dump(self):
        string = bitstruct.pack("u80u8u6u6u4u24u64", self.nonce_n_unique_id, self.nfpkt, ((self.rssi-40)//1), self.brg_latency, self.global_pacing_group, self.mic, self.data)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u80u8u6u6u4u24u64", binascii.unhexlify(string))
        self.nonce_n_unique_id = d[0]
        self.nfpkt = d[1]
        self.rssi = ((d[2]*1)+40)
        self.brg_latency = d[3]
        self.global_pacing_group = d[4]
        self.mic = d[5]
        self.data = d[6]

class Hdr():
    def __init__(self, raw='', pkt_size=HDR_DEFAULT_PKT_SIZE, ad_type=HDR_DEFAULT_AD_TYPE, uuid_msb=HDR_DEFAULT_BRG_UUID_MSB, uuid_lsb=HDR_DEFAULT_BRG_UUID_LSB, group_id=0):
        self.pkt_size = pkt_size
        self.ad_type = ad_type
        self.uuid_msb = uuid_msb
        self.uuid_lsb = uuid_lsb
        self.group_id = group_id
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Hdr):
            return (
                self.pkt_size == other.pkt_size and
                self.ad_type == other.ad_type and
                self.uuid_msb == other.uuid_msb and
                self.uuid_lsb == other.uuid_lsb and
                self.group_id == other.group_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u8u24", self.pkt_size, self.ad_type, self.uuid_msb, self.uuid_lsb, self.group_id)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u8u24", binascii.unhexlify(string))
        self.pkt_size = d[0]
        self.ad_type = d[1]
        self.uuid_msb = d[2]
        self.uuid_lsb = d[3]
        self.group_id = d[4]

class DataHdr():
    def __init__(self, raw='', pkt_size=HDR_DEFAULT_PKT_SIZE, ad_type=HDR_DEFAULT_AD_TYPE, uuid_msb=HDR_DEFAULT_BRG_UUID_MSB, uuid_lsb=HDR_DEFAULT_BRG_UUID_LSB, group_id_minor=0, pkt_type=0, group_id_major=0):
        self.pkt_size = pkt_size
        self.ad_type = ad_type
        self.uuid_msb = uuid_msb
        self.uuid_lsb = uuid_lsb
        self.group_id_minor = group_id_minor
        self.pkt_type = pkt_type
        self.group_id_major = group_id_major
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, DataHdr):
            return (
                self.pkt_size == other.pkt_size and
                self.ad_type == other.ad_type and
                self.uuid_msb == other.uuid_msb and
                self.uuid_lsb == other.uuid_lsb and
                self.group_id_minor == other.group_id_minor and
                self.pkt_type == other.pkt_type and
                self.group_id_major == other.group_id_major
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u8u16u2u6", self.pkt_size, self.ad_type, self.uuid_msb, self.uuid_lsb, self.group_id_minor, self.pkt_type, self.group_id_major)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u8u16u2u6", binascii.unhexlify(string))
        self.pkt_size = d[0]
        self.ad_type = d[1]
        self.uuid_msb = d[2]
        self.uuid_lsb = d[3]
        self.group_id_minor = d[4]
        self.pkt_type = d[5]
        self.group_id_major = d[6]

class GenericV10():
    def __init__(self, raw='', module_type=0, msg_type=0, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, unused=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, GenericV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u120", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u120", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused = d[5]

class GenericV9():
    def __init__(self, raw='', module_type=0, msg_type=0, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, unused=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, GenericV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u120", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u120", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused = d[5]

class GenericV8():
    def __init__(self, raw='', module_type=0, msg_type=0, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, unused=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, GenericV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u120", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u120", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused = d[5]

class GenericV7():
    def __init__(self, raw='', module_type=0, msg_type=0, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, unused=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, GenericV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u120", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u120", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused = d[5]

class GenericV1():
    def __init__(self, raw='', msg_type=0, unused0=0, seq_id=0, unused1=0, brg_mac=0, unused2=0):
        self.msg_type = msg_type
        self.unused0 = unused0
        self.seq_id = seq_id
        self.unused1 = unused1
        self.brg_mac = brg_mac
        self.unused2 = unused2
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, GenericV1):
            return (
                self.msg_type == other.msg_type and
                self.brg_mac == other.brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u48u72", self.msg_type, self.unused0, self.seq_id, self.unused1, self.brg_mac, self.unused2)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u48u72", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.unused0 = d[1]
        self.seq_id = d[2]
        self.unused1 = d[3]
        self.brg_mac = d[4]
        self.unused2 = d[5]

class ActionGenericV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=0, action_params=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.action_params = action_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGenericV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.action_params == other.action_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.action_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.action_params = d[5]

class ActionGenericV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=0, action_params=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.action_params = action_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGenericV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.action_params == other.action_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.action_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.action_params = d[5]

class ActionGenericV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=0, action_params=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.action_params = action_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGenericV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.action_params == other.action_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.action_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.action_params = d[5]

class ActionGenericV7():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V7, seq_id=0, brg_mac=ACTION_EMPTY, action_id=0, action_params=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.action_params = action_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGenericV7):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.action_params == other.action_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.action_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.action_params = d[5]

class ActionGwHbV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GW_HB, gw_id=0, rssi=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.gw_id = gw_id
        self.rssi = rssi
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGwHbV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.gw_id == other.gw_id and
                self.rssi == other.rssi
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u104u8", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.gw_id, self.rssi)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u104u8", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.gw_id = d[5]
        self.rssi = d[6]

class ActionGwHbV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GW_HB, gw_id=0, rssi=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.gw_id = gw_id
        self.rssi = rssi
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGwHbV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.gw_id == other.gw_id and
                self.rssi == other.rssi
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u104u8", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.gw_id, self.rssi)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u104u8", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.gw_id = d[5]
        self.rssi = d[6]

class ActionGwHbV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GW_HB, gw_id=0, rssi=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.gw_id = gw_id
        self.rssi = rssi
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGwHbV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.gw_id == other.gw_id and
                self.rssi == other.rssi
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u104u8", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.gw_id, self.rssi)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u104u8", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.gw_id = d[5]
        self.rssi = d[6]

class ActionRebootV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_REBOOT, gw_id=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.gw_id = gw_id
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionRebootV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.gw_id == other.gw_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.gw_id)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.gw_id = d[5]

class ActionRebootV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_REBOOT, gw_id=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.gw_id = gw_id
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionRebootV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.gw_id == other.gw_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.gw_id)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.gw_id = d[5]

class ActionRebootV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_REBOOT, gw_id=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.gw_id = gw_id
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionRebootV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.gw_id == other.gw_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.gw_id)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.gw_id = d[5]

class ActionBlinkV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_BLINK, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionBlinkV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionBlinkV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_BLINK, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionBlinkV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionBlinkV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_BLINK, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionBlinkV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionGetModuleV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_MODULE, interface=0, datapath=0, energy2400=0, energy_sub1g=0, calibration=0, pwr_mgmt=0, ext_sensors=0, custom=0, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.interface = interface
        self.datapath = datapath
        self.energy2400 = energy2400
        self.energy_sub1g = energy_sub1g
        self.calibration = calibration
        self.pwr_mgmt = pwr_mgmt
        self.ext_sensors = ext_sensors
        self.custom = custom
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetModuleV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.interface == other.interface and
                self.datapath == other.datapath and
                self.energy2400 == other.energy2400 and
                self.energy_sub1g == other.energy_sub1g and
                self.calibration == other.calibration and
                self.pwr_mgmt == other.pwr_mgmt and
                self.ext_sensors == other.ext_sensors and
                self.custom == other.custom
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u1u1u1u1u1u1u1u1u104", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.interface, self.datapath, self.energy2400, self.energy_sub1g, self.calibration, self.pwr_mgmt, self.ext_sensors, self.custom, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u1u1u1u1u1u1u1u1u104", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.interface = d[5]
        self.datapath = d[6]
        self.energy2400 = d[7]
        self.energy_sub1g = d[8]
        self.calibration = d[9]
        self.pwr_mgmt = d[10]
        self.ext_sensors = d[11]
        self.custom = d[12]
        self.unused0 = d[13]

class ActionGetModuleV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_MODULE, interface=0, datapath=0, energy2400=0, energy_sub1g=0, calibration=0, pwr_mgmt=0, ext_sensors=0, custom=0, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.interface = interface
        self.datapath = datapath
        self.energy2400 = energy2400
        self.energy_sub1g = energy_sub1g
        self.calibration = calibration
        self.pwr_mgmt = pwr_mgmt
        self.ext_sensors = ext_sensors
        self.custom = custom
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetModuleV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.interface == other.interface and
                self.datapath == other.datapath and
                self.energy2400 == other.energy2400 and
                self.energy_sub1g == other.energy_sub1g and
                self.calibration == other.calibration and
                self.pwr_mgmt == other.pwr_mgmt and
                self.ext_sensors == other.ext_sensors and
                self.custom == other.custom
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u1u1u1u1u1u1u1u1u104", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.interface, self.datapath, self.energy2400, self.energy_sub1g, self.calibration, self.pwr_mgmt, self.ext_sensors, self.custom, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u1u1u1u1u1u1u1u1u104", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.interface = d[5]
        self.datapath = d[6]
        self.energy2400 = d[7]
        self.energy_sub1g = d[8]
        self.calibration = d[9]
        self.pwr_mgmt = d[10]
        self.ext_sensors = d[11]
        self.custom = d[12]
        self.unused0 = d[13]

class ActionGetModuleV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_MODULE, interface=0, datapath=0, energy2400=0, energy_sub1g=0, calibration=0, pwr_mgmt=0, ext_sensors=0, custom=0, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.interface = interface
        self.datapath = datapath
        self.energy2400 = energy2400
        self.energy_sub1g = energy_sub1g
        self.calibration = calibration
        self.pwr_mgmt = pwr_mgmt
        self.ext_sensors = ext_sensors
        self.custom = custom
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetModuleV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id and
                self.interface == other.interface and
                self.datapath == other.datapath and
                self.energy2400 == other.energy2400 and
                self.energy_sub1g == other.energy_sub1g and
                self.calibration == other.calibration and
                self.pwr_mgmt == other.pwr_mgmt and
                self.ext_sensors == other.ext_sensors and
                self.custom == other.custom
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u1u1u1u1u1u1u1u1u104", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.interface, self.datapath, self.energy2400, self.energy_sub1g, self.calibration, self.pwr_mgmt, self.ext_sensors, self.custom, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u1u1u1u1u1u1u1u1u104", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.interface = d[5]
        self.datapath = d[6]
        self.energy2400 = d[7]
        self.energy_sub1g = d[8]
        self.calibration = d[9]
        self.pwr_mgmt = d[10]
        self.ext_sensors = d[11]
        self.custom = d[12]
        self.unused0 = d[13]

class ActionRestoreDefaultsV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_RESTORE_DEFAULTS, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionRestoreDefaultsV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionRestoreDefaultsV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_RESTORE_DEFAULTS, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionRestoreDefaultsV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionRestoreDefaultsV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_RESTORE_DEFAULTS, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionRestoreDefaultsV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionSendHbV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_SEND_HB, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionSendHbV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionSendHbV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_SEND_HB, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionSendHbV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionSendHbV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_SEND_HB, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionSendHbV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionGetBatterySensorV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_BATTERY_SENSOR, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetBatterySensorV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionGetBatterySensorV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_BATTERY_SENSOR, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetBatterySensorV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionGetBatterySensorV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_BATTERY_SENSOR, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetBatterySensorV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionGetPofDataV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V10, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_POF_DATA, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetPofDataV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionGetPofDataV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V9, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_POF_DATA, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetPofDataV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class ActionGetPofDataV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_ACTION, api_version=API_VERSION_V8, seq_id=0, brg_mac=ACTION_EMPTY, action_id=ACTION_GET_POF_DATA, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.action_id = action_id
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ActionGetPofDataV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.action_id == other.action_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u112", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.action_id, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u112", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.action_id = d[4]
        self.unused0 = d[5]

class Brg2BrgOtaV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_BRG2BRG, api_version=API_VERSION_V10, seq_id=0, src_brg_mac=ACTION_EMPTY, action_id=BRG2BRG_ACTION_OTA, dest_brg_mac=ACTION_EMPTY, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.src_brg_mac = src_brg_mac
        self.action_id = action_id
        self.dest_brg_mac = dest_brg_mac
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2BrgOtaV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.src_brg_mac == other.src_brg_mac and
                self.action_id == other.action_id and
                self.dest_brg_mac == other.dest_brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u48u64", self.msg_type, self.api_version, self.seq_id, self.src_brg_mac, self.action_id, self.dest_brg_mac, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u48u64", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.src_brg_mac = d[3]
        self.action_id = d[4]
        self.dest_brg_mac = d[5]
        self.unused0 = d[6]

class Brg2BrgOtaV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_BRG2BRG, api_version=API_VERSION_V9, seq_id=0, src_brg_mac=ACTION_EMPTY, action_id=BRG2BRG_ACTION_OTA, dest_brg_mac=ACTION_EMPTY, unused0=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.src_brg_mac = src_brg_mac
        self.action_id = action_id
        self.dest_brg_mac = dest_brg_mac
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2BrgOtaV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.src_brg_mac == other.src_brg_mac and
                self.action_id == other.action_id and
                self.dest_brg_mac == other.dest_brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u48u64", self.msg_type, self.api_version, self.seq_id, self.src_brg_mac, self.action_id, self.dest_brg_mac, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u48u64", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.src_brg_mac = d[3]
        self.action_id = d[4]
        self.dest_brg_mac = d[5]
        self.unused0 = d[6]

class Brg2BrgCfgV10():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_BRG2BRG, api_version=API_VERSION_V10, seq_id=0, src_brg_mac=ACTION_EMPTY, action_id=BRG2BRG_ACTION_CFG, dest_brg_mac=ACTION_EMPTY, module_type=MODULE_EMPTY, unused0=0, unused1=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.src_brg_mac = src_brg_mac
        self.action_id = action_id
        self.dest_brg_mac = dest_brg_mac
        self.module_type = module_type
        self.unused0 = unused0
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2BrgCfgV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.src_brg_mac == other.src_brg_mac and
                self.action_id == other.action_id and
                self.dest_brg_mac == other.dest_brg_mac and
                self.module_type == other.module_type
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u48u4u4u56", self.msg_type, self.api_version, self.seq_id, self.src_brg_mac, self.action_id, self.dest_brg_mac, self.module_type, self.unused0, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u48u4u4u56", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.src_brg_mac = d[3]
        self.action_id = d[4]
        self.dest_brg_mac = d[5]
        self.module_type = d[6]
        self.unused0 = d[7]
        self.unused1 = d[8]

class Brg2BrgCfgV9():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_BRG2BRG, api_version=API_VERSION_V9, seq_id=0, src_brg_mac=ACTION_EMPTY, action_id=BRG2BRG_ACTION_CFG, dest_brg_mac=ACTION_EMPTY, module_type=MODULE_EMPTY, unused0=0, unused1=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.src_brg_mac = src_brg_mac
        self.action_id = action_id
        self.dest_brg_mac = dest_brg_mac
        self.module_type = module_type
        self.unused0 = unused0
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2BrgCfgV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.src_brg_mac == other.src_brg_mac and
                self.action_id == other.action_id and
                self.dest_brg_mac == other.dest_brg_mac and
                self.module_type == other.module_type
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u8u48u4u4u56", self.msg_type, self.api_version, self.seq_id, self.src_brg_mac, self.action_id, self.dest_brg_mac, self.module_type, self.unused0, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u8u48u4u4u56", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.src_brg_mac = d[3]
        self.action_id = d[4]
        self.dest_brg_mac = d[5]
        self.module_type = d[6]
        self.unused0 = d[7]
        self.unused1 = d[8]

GW2BRG_CFG_V8_OUTPUT_POWER_SUB1G_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
GW2BRG_CFG_V8_OUTPUT_POWER_SUB1G_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
GW2BRG_CFG_V8_SUB1G_FREQ_PROFILE_ENC = {SUB1G_FREQ_915000:SUB1G_FREQ_PROFILE_915000, SUB1G_FREQ_916300:SUB1G_FREQ_PROFILE_916300, SUB1G_FREQ_917500:SUB1G_FREQ_PROFILE_917500, SUB1G_FREQ_918000:SUB1G_FREQ_PROFILE_918000, SUB1G_FREQ_919100:SUB1G_FREQ_PROFILE_919100}
GW2BRG_CFG_V8_SUB1G_FREQ_PROFILE_DEC = {SUB1G_FREQ_PROFILE_915000:SUB1G_FREQ_915000, SUB1G_FREQ_PROFILE_916300:SUB1G_FREQ_916300, SUB1G_FREQ_PROFILE_917500:SUB1G_FREQ_917500, SUB1G_FREQ_PROFILE_918000:SUB1G_FREQ_918000, SUB1G_FREQ_PROFILE_919100:SUB1G_FREQ_919100}
class Gw2BrgCfgV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, output_power_sub1g=BRG_DEFAULT_OUTPUT_POWER_SUB1G, seq_id=0, brg_mac=0, unused0=0, pkt_types_mask=BRG_DEFAULT_PKT_TYPES_MASK, unused1=0, rx_tx_period_ms=BRG_DEFAULT_RXTX_PERIOD, tx_period_ms=BRG_DEFAULT_TX_PERIOD, energy_pattern_idx=BRG_DEFAULT_ENERGY_PATTERN_IDX_OLD, output_power_2_4=BRG_DEFAULT_OUTPUT_POWER_2_4, pacer_interval=BRG_DEFAULT_PACER_INTERVAL, unused2=0, tx_repetition=BRG_DEFAULT_TX_REPETITION, transmit_time_sub1g=BRG_DEFAULT_TRANSMIT_TIME_SUB1G, sub1g_freq_profile=BRG_DEFAULT_SUB1G_FREQ):
        self.msg_type = msg_type
        self.global_pacing_group = global_pacing_group
        self.output_power_sub1g = output_power_sub1g
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused0 = unused0
        self.pkt_types_mask = pkt_types_mask
        self.unused1 = unused1
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        self.unused2 = unused2
        self.tx_repetition = tx_repetition
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, (Gw2BrgCfgV8, Brg2GwCfgV8)):
            return (
                self.msg_type == other.msg_type and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.brg_mac == other.brg_mac and
                self.pkt_types_mask == other.pkt_types_mask and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval and
                self.tx_repetition == other.tx_repetition and
                self.sub1g_freq_profile == other.sub1g_freq_profile
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u4u4u8u48u3u5u48u8u8u8s8u16u4u4u4u4", self.msg_type, self.global_pacing_group, GW2BRG_CFG_V8_OUTPUT_POWER_SUB1G_ENC[self.output_power_sub1g], self.seq_id, self.brg_mac, self.unused0, self.pkt_types_mask, self.unused1, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval, self.unused2, self.tx_repetition, self.transmit_time_sub1g, GW2BRG_CFG_V8_SUB1G_FREQ_PROFILE_ENC[self.sub1g_freq_profile])
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u4u4u8u48u3u5u48u8u8u8s8u16u4u4u4u4", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.global_pacing_group = d[1]
        self.output_power_sub1g = GW2BRG_CFG_V8_OUTPUT_POWER_SUB1G_DEC[d[2]]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused0 = d[5]
        self.pkt_types_mask = d[6]
        self.unused1 = d[7]
        self.rx_tx_period_ms = d[8]
        self.tx_period_ms = d[9]
        self.energy_pattern_idx = d[10]
        self.output_power_2_4 = d[11]
        self.pacer_interval = d[12]
        self.unused2 = d[13]
        self.tx_repetition = d[14]
        self.transmit_time_sub1g = d[15]
        self.sub1g_freq_profile = GW2BRG_CFG_V8_SUB1G_FREQ_PROFILE_DEC[d[16]]

GW2BRG_CFG_V7_OUTPUT_POWER_SUB1G_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
GW2BRG_CFG_V7_OUTPUT_POWER_SUB1G_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
GW2BRG_CFG_V7_SUB1G_FREQ_PROFILE_ENC = {SUB1G_FREQ_915000:SUB1G_FREQ_PROFILE_915000, SUB1G_FREQ_916300:SUB1G_FREQ_PROFILE_916300, SUB1G_FREQ_917500:SUB1G_FREQ_PROFILE_917500, SUB1G_FREQ_918000:SUB1G_FREQ_PROFILE_918000, SUB1G_FREQ_919100:SUB1G_FREQ_PROFILE_919100}
GW2BRG_CFG_V7_SUB1G_FREQ_PROFILE_DEC = {SUB1G_FREQ_PROFILE_915000:SUB1G_FREQ_915000, SUB1G_FREQ_PROFILE_916300:SUB1G_FREQ_916300, SUB1G_FREQ_PROFILE_917500:SUB1G_FREQ_917500, SUB1G_FREQ_PROFILE_918000:SUB1G_FREQ_918000, SUB1G_FREQ_PROFILE_919100:SUB1G_FREQ_919100}
class Gw2BrgCfgV7():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, output_power_sub1g=BRG_DEFAULT_OUTPUT_POWER_SUB1G, seq_id=0, brg_mac=0, unused1=0, rx_tx_period_ms=BRG_DEFAULT_RXTX_PERIOD, tx_period_ms=BRG_DEFAULT_TX_PERIOD, energy_pattern_idx=BRG_DEFAULT_ENERGY_PATTERN_IDX_OLD, output_power_2_4=BRG_DEFAULT_OUTPUT_POWER_2_4, pacer_interval=BRG_DEFAULT_PACER_INTERVAL, unused2=0, tx_probability=50, tx_repetition=BRG_DEFAULT_TX_REPETITION, transmit_time_sub1g=BRG_DEFAULT_TRANSMIT_TIME_SUB1G, sub1g_freq_profile=BRG_DEFAULT_SUB1G_FREQ):
        self.msg_type = msg_type
        self.global_pacing_group = global_pacing_group
        self.output_power_sub1g = output_power_sub1g
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused1 = unused1
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        self.unused2 = unused2
        self.tx_probability = tx_probability
        self.tx_repetition = tx_repetition
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, (Gw2BrgCfgV7, Brg2GwCfgV7)):
            return (
                self.msg_type == other.msg_type and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval and
                self.tx_probability == other.tx_probability and
                self.tx_repetition == other.tx_repetition and
                self.sub1g_freq_profile == other.sub1g_freq_profile
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u4u4u8u48u56u8u8u8s8u16u1u3u4u4u4", self.msg_type, self.global_pacing_group, GW2BRG_CFG_V7_OUTPUT_POWER_SUB1G_ENC[self.output_power_sub1g], self.seq_id, self.brg_mac, self.unused1, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval, self.unused2, ((self.tx_probability-30)//10), self.tx_repetition, self.transmit_time_sub1g, GW2BRG_CFG_V7_SUB1G_FREQ_PROFILE_ENC[self.sub1g_freq_profile])
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u4u4u8u48u56u8u8u8s8u16u1u3u4u4u4", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.global_pacing_group = d[1]
        self.output_power_sub1g = GW2BRG_CFG_V7_OUTPUT_POWER_SUB1G_DEC[d[2]]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused1 = d[5]
        self.rx_tx_period_ms = d[6]
        self.tx_period_ms = d[7]
        self.energy_pattern_idx = d[8]
        self.output_power_2_4 = d[9]
        self.pacer_interval = d[10]
        self.unused2 = d[11]
        self.tx_probability = ((d[12]*10)+30)
        self.tx_repetition = d[13]
        self.transmit_time_sub1g = d[14]
        self.sub1g_freq_profile = GW2BRG_CFG_V7_SUB1G_FREQ_PROFILE_DEC[d[15]]

class Gw2BrgCfgV6():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, global_pacing_group=0, output_power_sub1g=0, seq_id=0, brg_mac=0, unused0=0, unused1=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power_2_4=0, pacer_interval=0, unused2=0, tx_probability=0, tx_repetition=0, transmit_time_sub1g=0, sub1g_freq_profile=0):
        self.msg_type = msg_type
        self.global_pacing_group = global_pacing_group
        self.output_power_sub1g = output_power_sub1g
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused0 = unused0
        self.unused1 = unused1
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        self.unused2 = unused2
        self.tx_probability = tx_probability
        self.tx_repetition = tx_repetition
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, (Gw2BrgCfgV6, Brg2GwCfgV6)):
            return (
                self.msg_type == other.msg_type and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval and
                self.tx_probability == other.tx_probability and
                self.tx_repetition == other.tx_repetition and
                self.sub1g_freq_profile == other.sub1g_freq_profile
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u4u4u8u48u8u48u8u8u8s8u16u1u3u4u4u4", self.msg_type, self.global_pacing_group, self.output_power_sub1g, self.seq_id, self.brg_mac, self.unused0, self.unused1, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval, self.unused2, self.tx_probability, self.tx_repetition, self.transmit_time_sub1g, self.sub1g_freq_profile)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u4u4u8u48u8u48u8u8u8s8u16u1u3u4u4u4", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.global_pacing_group = d[1]
        self.output_power_sub1g = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused0 = d[5]
        self.unused1 = d[6]
        self.rx_tx_period_ms = d[7]
        self.tx_period_ms = d[8]
        self.energy_pattern_idx = d[9]
        self.output_power_2_4 = d[10]
        self.pacer_interval = d[11]
        self.unused2 = d[12]
        self.tx_probability = d[13]
        self.tx_repetition = d[14]
        self.transmit_time_sub1g = d[15]
        self.sub1g_freq_profile = d[16]

class Gw2BrgCfgV5():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, unused0=0, output_power_sub1g=0, seq_id=0, brg_mac=0, unused1=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power_2_4=0, pacer_interval=0, global_pacing=0, tx_probability=0, stat_freq=0, transmit_time_sub1g=0, sub1g_freq_profile=0):
        self.msg_type = msg_type
        self.unused0 = unused0
        self.output_power_sub1g = output_power_sub1g
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused1 = unused1
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        self.global_pacing = global_pacing
        self.tx_probability = tx_probability
        self.stat_freq = stat_freq
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, (Gw2BrgCfgV5, Brg2GwCfgV5)):
            return (
                self.msg_type == other.msg_type and
                self.output_power_sub1g == other.output_power_sub1g and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval and
                self.global_pacing == other.global_pacing and
                self.tx_probability == other.tx_probability and
                self.stat_freq == other.stat_freq and
                self.sub1g_freq_profile == other.sub1g_freq_profile
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u4u4u8u48u56u8u8u8s8u16u1u3u4u4u4", self.msg_type, self.unused0, self.output_power_sub1g, self.seq_id, self.brg_mac, self.unused1, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval, self.global_pacing, self.tx_probability, self.stat_freq, self.transmit_time_sub1g, self.sub1g_freq_profile)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u4u4u8u48u56u8u8u8s8u16u1u3u4u4u4", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.unused0 = d[1]
        self.output_power_sub1g = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused1 = d[5]
        self.rx_tx_period_ms = d[6]
        self.tx_period_ms = d[7]
        self.energy_pattern_idx = d[8]
        self.output_power_2_4 = d[9]
        self.pacer_interval = d[10]
        self.global_pacing = d[11]
        self.tx_probability = d[12]
        self.stat_freq = d[13]
        self.transmit_time_sub1g = d[14]
        self.sub1g_freq_profile = d[15]

class Gw2BrgCfgV2():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, unused=0, output_power_sub1g=0, seq_id=0, brg_mac=0, gw_mac=0, rx_rssi=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power_2_4=0, pacer_interval=0, global_pacing=0, tx_probability=0, stat_freq=0, transmit_time_sub1g=0, sub1g_freq_profile=0):
        self.msg_type = msg_type
        self.unused = unused
        self.output_power_sub1g = output_power_sub1g
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.gw_mac = gw_mac
        self.rx_rssi = rx_rssi
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        self.global_pacing = global_pacing
        self.tx_probability = tx_probability
        self.stat_freq = stat_freq
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, (Gw2BrgCfgV2, Brg2GwCfgV2)):
            return (
                self.msg_type == other.msg_type and
                self.output_power_sub1g == other.output_power_sub1g and
                self.brg_mac == other.brg_mac and
                self.gw_mac == other.gw_mac and
                self.rx_rssi == other.rx_rssi and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval and
                self.global_pacing == other.global_pacing and
                self.tx_probability == other.tx_probability and
                self.stat_freq == other.stat_freq and
                self.sub1g_freq_profile == other.sub1g_freq_profile
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u4u4u8u48u48u8u8u8u8s8u16u1u3u4u4u4", self.msg_type, self.unused, self.output_power_sub1g, self.seq_id, self.brg_mac, self.gw_mac, self.rx_rssi, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval, self.global_pacing, self.tx_probability, self.stat_freq, self.transmit_time_sub1g, self.sub1g_freq_profile)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u4u4u8u48u48u8u8u8u8s8u16u1u3u4u4u4", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.unused = d[1]
        self.output_power_sub1g = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.gw_mac = d[5]
        self.rx_rssi = d[6]
        self.rx_tx_period_ms = d[7]
        self.tx_period_ms = d[8]
        self.energy_pattern_idx = d[9]
        self.output_power_2_4 = d[10]
        self.pacer_interval = d[11]
        self.global_pacing = d[12]
        self.tx_probability = d[13]
        self.stat_freq = d[14]
        self.transmit_time_sub1g = d[15]
        self.sub1g_freq_profile = d[16]

class Gw2BrgCfgV1():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, unused0=0, seq_id=0, brg_mac=0, gw_mac=0, rx_rssi=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power=0, pacer_interval=0, tx_probability=0, unused1=0):
        self.msg_type = msg_type
        self.unused0 = unused0
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.gw_mac = gw_mac
        self.rx_rssi = rx_rssi
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power = output_power
        self.pacer_interval = pacer_interval
        self.tx_probability = tx_probability
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, (Gw2BrgCfgV1, Brg2GwCfgV1)):
            return (
                self.msg_type == other.msg_type and
                self.brg_mac == other.brg_mac and
                self.gw_mac == other.gw_mac and
                self.rx_rssi == other.rx_rssi and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power == other.output_power and
                self.pacer_interval == other.pacer_interval and
                self.tx_probability == other.tx_probability
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u48u8u8u8u8s8u16u8u8", self.msg_type, self.unused0, self.seq_id, self.brg_mac, self.gw_mac, self.rx_rssi, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power, self.pacer_interval, self.tx_probability, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u48u8u8u8u8s8u16u8u8", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.unused0 = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.gw_mac = d[4]
        self.rx_rssi = d[5]
        self.rx_tx_period_ms = d[6]
        self.tx_period_ms = d[7]
        self.energy_pattern_idx = d[8]
        self.output_power = d[9]
        self.pacer_interval = d[10]
        self.tx_probability = d[11]
        self.unused1 = d[12]

BRG2GW_CFG_V8_OUTPUT_POWER_SUB1G_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
BRG2GW_CFG_V8_OUTPUT_POWER_SUB1G_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
BRG2GW_CFG_V8_SUB1G_FREQ_PROFILE_ENC = {SUB1G_FREQ_915000:SUB1G_FREQ_PROFILE_915000, SUB1G_FREQ_916300:SUB1G_FREQ_PROFILE_916300, SUB1G_FREQ_917500:SUB1G_FREQ_PROFILE_917500, SUB1G_FREQ_918000:SUB1G_FREQ_PROFILE_918000, SUB1G_FREQ_919100:SUB1G_FREQ_PROFILE_919100}
BRG2GW_CFG_V8_SUB1G_FREQ_PROFILE_DEC = {SUB1G_FREQ_PROFILE_915000:SUB1G_FREQ_915000, SUB1G_FREQ_PROFILE_916300:SUB1G_FREQ_916300, SUB1G_FREQ_PROFILE_917500:SUB1G_FREQ_917500, SUB1G_FREQ_PROFILE_918000:SUB1G_FREQ_918000, SUB1G_FREQ_PROFILE_919100:SUB1G_FREQ_919100}
class Brg2GwCfgV8():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, unused0=0, tx_repetition=BRG_DEFAULT_TX_REPETITION, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, output_power_sub1g=BRG_DEFAULT_OUTPUT_POWER_SUB1G, transmit_time_sub1g=BRG_DEFAULT_TRANSMIT_TIME_SUB1G, sub1g_freq_profile=BRG_DEFAULT_SUB1G_FREQ, bl_version=0, board_type=0, unused1=0, pkt_types_mask=BRG_DEFAULT_PKT_TYPES_MASK, brg_mac=0, major_ver=0, minor_ver=0, build_ver=0, rx_tx_period_ms=BRG_DEFAULT_RXTX_PERIOD, tx_period_ms=BRG_DEFAULT_TX_PERIOD, energy_pattern_idx=BRG_DEFAULT_ENERGY_PATTERN_IDX_OLD, output_power_2_4=BRG_DEFAULT_OUTPUT_POWER_2_4, pacer_interval=BRG_DEFAULT_PACER_INTERVAL):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.unused0 = unused0
        self.tx_repetition = tx_repetition
        self.global_pacing_group = global_pacing_group
        self.output_power_sub1g = output_power_sub1g
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        self.bl_version = bl_version
        self.board_type = board_type
        self.unused1 = unused1
        self.pkt_types_mask = pkt_types_mask
        self.brg_mac = brg_mac
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.build_ver = build_ver
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwCfgV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.tx_repetition == other.tx_repetition and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.bl_version == other.bl_version and
                self.board_type == other.board_type and
                self.pkt_types_mask == other.pkt_types_mask and
                self.brg_mac == other.brg_mac and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.build_ver == other.build_ver and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        if isinstance(other, Gw2BrgCfgV8):
            return (
                self.msg_type == other.msg_type and
                self.tx_repetition == other.tx_repetition and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.pkt_types_mask == other.pkt_types_mask and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u4u4u4u4u4u4u8u8u3u5u48u8u8u8u8u8u8s8u16", self.msg_type, self.api_version, self.seq_id, self.unused0, self.tx_repetition, self.global_pacing_group, BRG2GW_CFG_V8_OUTPUT_POWER_SUB1G_ENC[self.output_power_sub1g], self.transmit_time_sub1g, BRG2GW_CFG_V8_SUB1G_FREQ_PROFILE_ENC[self.sub1g_freq_profile], self.bl_version, self.board_type, self.unused1, self.pkt_types_mask, self.brg_mac, self.major_ver, self.minor_ver, self.build_ver, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u4u4u4u4u4u4u8u8u3u5u48u8u8u8u8u8u8s8u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.unused0 = d[3]
        self.tx_repetition = d[4]
        self.global_pacing_group = d[5]
        self.output_power_sub1g = BRG2GW_CFG_V8_OUTPUT_POWER_SUB1G_DEC[d[6]]
        self.transmit_time_sub1g = d[7]
        self.sub1g_freq_profile = BRG2GW_CFG_V8_SUB1G_FREQ_PROFILE_DEC[d[8]]
        self.bl_version = d[9]
        self.board_type = d[10]
        self.unused1 = d[11]
        self.pkt_types_mask = d[12]
        self.brg_mac = d[13]
        self.major_ver = d[14]
        self.minor_ver = d[15]
        self.build_ver = d[16]
        self.rx_tx_period_ms = d[17]
        self.tx_period_ms = d[18]
        self.energy_pattern_idx = d[19]
        self.output_power_2_4 = d[20]
        self.pacer_interval = d[21]

BRG2GW_CFG_V7_OUTPUT_POWER_SUB1G_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
BRG2GW_CFG_V7_OUTPUT_POWER_SUB1G_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
BRG2GW_CFG_V7_SUB1G_FREQ_PROFILE_ENC = {SUB1G_FREQ_915000:SUB1G_FREQ_PROFILE_915000, SUB1G_FREQ_916300:SUB1G_FREQ_PROFILE_916300, SUB1G_FREQ_917500:SUB1G_FREQ_PROFILE_917500, SUB1G_FREQ_918000:SUB1G_FREQ_PROFILE_918000, SUB1G_FREQ_919100:SUB1G_FREQ_PROFILE_919100}
BRG2GW_CFG_V7_SUB1G_FREQ_PROFILE_DEC = {SUB1G_FREQ_PROFILE_915000:SUB1G_FREQ_915000, SUB1G_FREQ_PROFILE_916300:SUB1G_FREQ_916300, SUB1G_FREQ_PROFILE_917500:SUB1G_FREQ_917500, SUB1G_FREQ_PROFILE_918000:SUB1G_FREQ_918000, SUB1G_FREQ_PROFILE_919100:SUB1G_FREQ_919100}
class Brg2GwCfgV7():
    def __init__(self, raw='', msg_type=0, api_version=API_VERSION_V7, seq_id=0, unused0=0, tx_probability=50, tx_repetition=BRG_DEFAULT_TX_REPETITION, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, output_power_sub1g=BRG_DEFAULT_OUTPUT_POWER_SUB1G, transmit_time_sub1g=BRG_DEFAULT_TRANSMIT_TIME_SUB1G, sub1g_freq_profile=BRG_DEFAULT_SUB1G_FREQ, bl_version=0, board_type=0, unused1=0, brg_mac=0, major_ver=0, minor_ver=0, build_ver=0, rx_tx_period_ms=BRG_DEFAULT_RXTX_PERIOD, tx_period_ms=BRG_DEFAULT_TX_PERIOD, energy_pattern_idx=BRG_DEFAULT_ENERGY_PATTERN_IDX_OLD, output_power_2_4=BRG_DEFAULT_OUTPUT_POWER_2_4, pacer_interval=BRG_DEFAULT_PACER_INTERVAL):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.unused0 = unused0
        self.tx_probability = tx_probability
        self.tx_repetition = tx_repetition
        self.global_pacing_group = global_pacing_group
        self.output_power_sub1g = output_power_sub1g
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        self.bl_version = bl_version
        self.board_type = board_type
        self.unused1 = unused1
        self.brg_mac = brg_mac
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.build_ver = build_ver
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwCfgV7):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.tx_probability == other.tx_probability and
                self.tx_repetition == other.tx_repetition and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.bl_version == other.bl_version and
                self.board_type == other.board_type and
                self.brg_mac == other.brg_mac and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.build_ver == other.build_ver and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        if isinstance(other, Gw2BrgCfgV7):
            return (
                self.msg_type == other.msg_type and
                self.tx_probability == other.tx_probability and
                self.tx_repetition == other.tx_repetition and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u1u3u4u4u4u4u4u8u8u8u48u8u8u8u8u8u8s8u16", self.msg_type, self.api_version, self.seq_id, self.unused0, ((self.tx_probability-30)//10), self.tx_repetition, self.global_pacing_group, BRG2GW_CFG_V7_OUTPUT_POWER_SUB1G_ENC[self.output_power_sub1g], self.transmit_time_sub1g, BRG2GW_CFG_V7_SUB1G_FREQ_PROFILE_ENC[self.sub1g_freq_profile], self.bl_version, self.board_type, self.unused1, self.brg_mac, self.major_ver, self.minor_ver, self.build_ver, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u1u3u4u4u4u4u4u8u8u8u48u8u8u8u8u8u8s8u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.unused0 = d[3]
        self.tx_probability = ((d[4]*10)+30)
        self.tx_repetition = d[5]
        self.global_pacing_group = d[6]
        self.output_power_sub1g = BRG2GW_CFG_V7_OUTPUT_POWER_SUB1G_DEC[d[7]]
        self.transmit_time_sub1g = d[8]
        self.sub1g_freq_profile = BRG2GW_CFG_V7_SUB1G_FREQ_PROFILE_DEC[d[9]]
        self.bl_version = d[10]
        self.board_type = d[11]
        self.unused1 = d[12]
        self.brg_mac = d[13]
        self.major_ver = d[14]
        self.minor_ver = d[15]
        self.build_ver = d[16]
        self.rx_tx_period_ms = d[17]
        self.tx_period_ms = d[18]
        self.energy_pattern_idx = d[19]
        self.output_power_2_4 = d[20]
        self.pacer_interval = d[21]

class Brg2GwCfgV6():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V6, seq_id=0, unused0=0, tx_probability=0, tx_repetition=0, global_pacing_group=0, output_power_sub1g=0, transmit_time_sub1g=0, sub1g_freq_profile=0, bl_version=0, board_type=0, unused1=0, brg_mac=0, major_ver=0, minor_ver=0, build_ver=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power_2_4=0, pacer_interval=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.unused0 = unused0
        self.tx_probability = tx_probability
        self.tx_repetition = tx_repetition
        self.global_pacing_group = global_pacing_group
        self.output_power_sub1g = output_power_sub1g
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        self.bl_version = bl_version
        self.board_type = board_type
        self.unused1 = unused1
        self.brg_mac = brg_mac
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.build_ver = build_ver
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwCfgV6):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.tx_probability == other.tx_probability and
                self.tx_repetition == other.tx_repetition and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.bl_version == other.bl_version and
                self.board_type == other.board_type and
                self.brg_mac == other.brg_mac and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.build_ver == other.build_ver and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        if isinstance(other, Gw2BrgCfgV6):
            return (
                self.msg_type == other.msg_type and
                self.tx_probability == other.tx_probability and
                self.tx_repetition == other.tx_repetition and
                self.global_pacing_group == other.global_pacing_group and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u1u3u4u4u4u4u4u8u8u8u48u8u8u8u8u8u8s8u16", self.msg_type, self.api_version, self.seq_id, self.unused0, self.tx_probability, self.tx_repetition, self.global_pacing_group, self.output_power_sub1g, self.transmit_time_sub1g, self.sub1g_freq_profile, self.bl_version, self.board_type, self.unused1, self.brg_mac, self.major_ver, self.minor_ver, self.build_ver, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u1u3u4u4u4u4u4u8u8u8u48u8u8u8u8u8u8s8u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.unused0 = d[3]
        self.tx_probability = d[4]
        self.tx_repetition = d[5]
        self.global_pacing_group = d[6]
        self.output_power_sub1g = d[7]
        self.transmit_time_sub1g = d[8]
        self.sub1g_freq_profile = d[9]
        self.bl_version = d[10]
        self.board_type = d[11]
        self.unused1 = d[12]
        self.brg_mac = d[13]
        self.major_ver = d[14]
        self.minor_ver = d[15]
        self.build_ver = d[16]
        self.rx_tx_period_ms = d[17]
        self.tx_period_ms = d[18]
        self.energy_pattern_idx = d[19]
        self.output_power_2_4 = d[20]
        self.pacer_interval = d[21]

class Brg2GwCfgV5():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V5, seq_id=0, global_pacing_enabled=0, tx_probability=0, stat_freq=0, unused0=0, output_power_sub1g=0, transmit_time_sub1g=0, sub1g_freq_profile=0, bl_version=0, board_type=0, unused1=0, brg_mac=0, major_ver=0, minor_ver=0, build_ver=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power_2_4=0, pacer_interval=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.global_pacing_enabled = global_pacing_enabled
        self.tx_probability = tx_probability
        self.stat_freq = stat_freq
        self.unused0 = unused0
        self.output_power_sub1g = output_power_sub1g
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        self.bl_version = bl_version
        self.board_type = board_type
        self.unused1 = unused1
        self.brg_mac = brg_mac
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.build_ver = build_ver
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwCfgV5):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.global_pacing_enabled == other.global_pacing_enabled and
                self.tx_probability == other.tx_probability and
                self.stat_freq == other.stat_freq and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.bl_version == other.bl_version and
                self.board_type == other.board_type and
                self.brg_mac == other.brg_mac and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.build_ver == other.build_ver and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        if isinstance(other, Gw2BrgCfgV5):
            return (
                self.msg_type == other.msg_type and
                self.global_pacing_enabled == other.global_pacing_enabled and
                self.tx_probability == other.tx_probability and
                self.stat_freq == other.stat_freq and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u1u3u4u4u4u4u4u8u8u8u48u8u8u8u8u8u8s8u16", self.msg_type, self.api_version, self.seq_id, self.global_pacing_enabled, self.tx_probability, self.stat_freq, self.unused0, self.output_power_sub1g, self.transmit_time_sub1g, self.sub1g_freq_profile, self.bl_version, self.board_type, self.unused1, self.brg_mac, self.major_ver, self.minor_ver, self.build_ver, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u1u3u4u4u4u4u4u8u8u8u48u8u8u8u8u8u8s8u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.global_pacing_enabled = d[3]
        self.tx_probability = d[4]
        self.stat_freq = d[5]
        self.unused0 = d[6]
        self.output_power_sub1g = d[7]
        self.transmit_time_sub1g = d[8]
        self.sub1g_freq_profile = d[9]
        self.bl_version = d[10]
        self.board_type = d[11]
        self.unused1 = d[12]
        self.brg_mac = d[13]
        self.major_ver = d[14]
        self.minor_ver = d[15]
        self.build_ver = d[16]
        self.rx_tx_period_ms = d[17]
        self.tx_period_ms = d[18]
        self.energy_pattern_idx = d[19]
        self.output_power_2_4 = d[20]
        self.pacer_interval = d[21]

class Brg2GwCfgV2():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, board_type=0, seq_id=0, global_pacing_enabled=0, tx_probability=0, stat_freq=0, unused0=0, output_power_sub1g=0, transmit_time_sub1g=0, sub1g_freq_profile=0, bl_version=0, unused1=0, brg_mac=0, major_ver=0, minor_ver=0, build_ver=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power_2_4=0, pacer_interval=0):
        self.msg_type = msg_type
        self.board_type = board_type
        self.seq_id = seq_id
        self.global_pacing_enabled = global_pacing_enabled
        self.tx_probability = tx_probability
        self.stat_freq = stat_freq
        self.unused0 = unused0
        self.output_power_sub1g = output_power_sub1g
        self.transmit_time_sub1g = transmit_time_sub1g
        self.sub1g_freq_profile = sub1g_freq_profile
        self.bl_version = bl_version
        self.unused1 = unused1
        self.brg_mac = brg_mac
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.build_ver = build_ver
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power_2_4 = output_power_2_4
        self.pacer_interval = pacer_interval
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwCfgV2):
            return (
                self.msg_type == other.msg_type and
                self.board_type == other.board_type and
                self.global_pacing_enabled == other.global_pacing_enabled and
                self.tx_probability == other.tx_probability and
                self.stat_freq == other.stat_freq and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.bl_version == other.bl_version and
                self.brg_mac == other.brg_mac and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.build_ver == other.build_ver and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        if isinstance(other, Gw2BrgCfgV2):
            return (
                self.msg_type == other.msg_type and
                self.global_pacing_enabled == other.global_pacing_enabled and
                self.tx_probability == other.tx_probability and
                self.stat_freq == other.stat_freq and
                self.output_power_sub1g == other.output_power_sub1g and
                self.sub1g_freq_profile == other.sub1g_freq_profile and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power_2_4 == other.output_power_2_4 and
                self.pacer_interval == other.pacer_interval
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u1u3u4u4u4u4u4u8u16u48u8u8u8u8u8u8s8u16", self.msg_type, self.board_type, self.seq_id, self.global_pacing_enabled, self.tx_probability, self.stat_freq, self.unused0, self.output_power_sub1g, self.transmit_time_sub1g, self.sub1g_freq_profile, self.bl_version, self.unused1, self.brg_mac, self.major_ver, self.minor_ver, self.build_ver, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power_2_4, self.pacer_interval)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u1u3u4u4u4u4u4u8u16u48u8u8u8u8u8u8s8u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.board_type = d[1]
        self.seq_id = d[2]
        self.global_pacing_enabled = d[3]
        self.tx_probability = d[4]
        self.stat_freq = d[5]
        self.unused0 = d[6]
        self.output_power_sub1g = d[7]
        self.transmit_time_sub1g = d[8]
        self.sub1g_freq_profile = d[9]
        self.bl_version = d[10]
        self.unused1 = d[11]
        self.brg_mac = d[12]
        self.major_ver = d[13]
        self.minor_ver = d[14]
        self.build_ver = d[15]
        self.rx_tx_period_ms = d[16]
        self.tx_period_ms = d[17]
        self.energy_pattern_idx = d[18]
        self.output_power_2_4 = d[19]
        self.pacer_interval = d[20]

class Brg2GwCfgV1():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, unused0=0, seq_id=0, gw_mac=0, brg_mac=0, major_ver=0, minor_ver=0, build_ver=0, unused1=0, tx_probability=0, is_dual_band=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power=0, pacer_interval=0):
        self.msg_type = msg_type
        self.unused0 = unused0
        self.seq_id = seq_id
        self.gw_mac = gw_mac
        self.brg_mac = brg_mac
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.build_ver = build_ver
        self.unused1 = unused1
        self.tx_probability = tx_probability
        self.is_dual_band = is_dual_band
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power = output_power
        self.pacer_interval = pacer_interval
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwCfgV1):
            return (
                self.msg_type == other.msg_type and
                self.gw_mac == other.gw_mac and
                self.brg_mac == other.brg_mac and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.build_ver == other.build_ver and
                self.tx_probability == other.tx_probability and
                self.is_dual_band == other.is_dual_band and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power == other.output_power and
                self.pacer_interval == other.pacer_interval
            )
        if isinstance(other, Gw2BrgCfgV1):
            return (
                self.msg_type == other.msg_type and
                self.gw_mac == other.gw_mac and
                self.brg_mac == other.brg_mac and
                self.tx_probability == other.tx_probability and
                self.is_dual_band == other.is_dual_band and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power == other.output_power and
                self.pacer_interval == other.pacer_interval
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u48u4u4u4u4u7u1u8u8u8s8u16", self.msg_type, self.unused0, self.seq_id, self.gw_mac, self.brg_mac, self.major_ver, self.minor_ver, self.build_ver, self.unused1, self.tx_probability, self.is_dual_band, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power, self.pacer_interval)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u48u4u4u4u4u7u1u8u8u8s8u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.unused0 = d[1]
        self.seq_id = d[2]
        self.gw_mac = d[3]
        self.brg_mac = d[4]
        self.major_ver = d[5]
        self.minor_ver = d[6]
        self.build_ver = d[7]
        self.unused1 = d[8]
        self.tx_probability = d[9]
        self.is_dual_band = d[10]
        self.rx_tx_period_ms = d[11]
        self.tx_period_ms = d[12]
        self.energy_pattern_idx = d[13]
        self.output_power = d[14]
        self.pacer_interval = d[15]

class Brg2GwCfgV0():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, bridge_id=0, seq_id=0, gw_mac=0, brg_mac=0, major_ver=0, minor_ver=0, build_ver=0, rx_tx_period_ms=0, tx_period_ms=0, energy_pattern_idx=0, output_power=0, pacer_interval=0):
        self.msg_type = msg_type
        self.bridge_id = bridge_id
        self.seq_id = seq_id
        self.gw_mac = gw_mac
        self.brg_mac = brg_mac
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.build_ver = build_ver
        self.rx_tx_period_ms = rx_tx_period_ms
        self.tx_period_ms = tx_period_ms
        self.energy_pattern_idx = energy_pattern_idx
        self.output_power = output_power
        self.pacer_interval = pacer_interval
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwCfgV0):
            return (
                self.msg_type == other.msg_type and
                self.bridge_id == other.bridge_id and
                self.gw_mac == other.gw_mac and
                self.brg_mac == other.brg_mac and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.build_ver == other.build_ver and
                self.rx_tx_period_ms == other.rx_tx_period_ms and
                self.tx_period_ms == other.tx_period_ms and
                self.energy_pattern_idx == other.energy_pattern_idx and
                self.output_power == other.output_power and
                self.pacer_interval == other.pacer_interval
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u48u8u8u8u8u8u8s8u16", self.msg_type, self.bridge_id, self.seq_id, self.gw_mac, self.brg_mac, self.major_ver, self.minor_ver, self.build_ver, self.rx_tx_period_ms, self.tx_period_ms, self.energy_pattern_idx, self.output_power, self.pacer_interval)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u48u8u8u8u8u8u8s8u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.bridge_id = d[1]
        self.seq_id = d[2]
        self.gw_mac = d[3]
        self.brg_mac = d[4]
        self.major_ver = d[5]
        self.minor_ver = d[6]
        self.build_ver = d[7]
        self.rx_tx_period_ms = d[8]
        self.tx_period_ms = d[9]
        self.energy_pattern_idx = d[10]
        self.output_power = d[11]
        self.pacer_interval = d[12]

class Gw2BrgHbV1():
    def __init__(self, raw='', msg_type=0, unused0=0, seq_id=0, brg_mac=0, gw_mac=0, rx_rssi=0, unused1=0):
        self.msg_type = msg_type
        self.unused0 = unused0
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.gw_mac = gw_mac
        self.rx_rssi = rx_rssi
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Gw2BrgHbV1):
            return (
                self.msg_type == other.msg_type and
                self.brg_mac == other.brg_mac and
                self.gw_mac == other.gw_mac and
                self.rx_rssi == other.rx_rssi
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u48u8u64", self.msg_type, self.unused0, self.seq_id, self.brg_mac, self.gw_mac, self.rx_rssi, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u48u8u64", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.unused0 = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.gw_mac = d[4]
        self.rx_rssi = d[5]
        self.unused1 = d[6]

class Brg2GwHbV10():
    def __init__(self, raw='', msg_type=0, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, non_wlt_rx_pkts_ctr=0, bad_crc_pkts_ctr=0, wlt_rx_pkts_ctr=0, wlt_tx_pkts_ctr=0, tags_ctr=0, tx_queue_watermark=0, effective_pacer_increment=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.non_wlt_rx_pkts_ctr = non_wlt_rx_pkts_ctr
        self.bad_crc_pkts_ctr = bad_crc_pkts_ctr
        self.wlt_rx_pkts_ctr = wlt_rx_pkts_ctr
        self.wlt_tx_pkts_ctr = wlt_tx_pkts_ctr
        self.tags_ctr = tags_ctr
        self.tx_queue_watermark = tx_queue_watermark
        self.effective_pacer_increment = effective_pacer_increment
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwHbV10):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.non_wlt_rx_pkts_ctr == other.non_wlt_rx_pkts_ctr and
                self.bad_crc_pkts_ctr == other.bad_crc_pkts_ctr and
                self.wlt_rx_pkts_ctr == other.wlt_rx_pkts_ctr and
                self.wlt_tx_pkts_ctr == other.wlt_tx_pkts_ctr and
                self.tags_ctr == other.tags_ctr and
                self.tx_queue_watermark == other.tx_queue_watermark and
                self.effective_pacer_increment == other.effective_pacer_increment
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u24u24u24u16u16u8u8", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.non_wlt_rx_pkts_ctr, self.bad_crc_pkts_ctr, self.wlt_rx_pkts_ctr, self.wlt_tx_pkts_ctr, self.tags_ctr, self.tx_queue_watermark, self.effective_pacer_increment)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u24u24u24u16u16u8u8", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.non_wlt_rx_pkts_ctr = d[4]
        self.bad_crc_pkts_ctr = d[5]
        self.wlt_rx_pkts_ctr = d[6]
        self.wlt_tx_pkts_ctr = d[7]
        self.tags_ctr = d[8]
        self.tx_queue_watermark = d[9]
        self.effective_pacer_increment = d[10]

class Brg2GwHbV9():
    def __init__(self, raw='', msg_type=0, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, non_wlt_rx_pkts_ctr=0, bad_crc_pkts_ctr=0, wlt_rx_pkts_ctr=0, wlt_tx_pkts_ctr=0, tags_ctr=0, tx_queue_watermark=0, effective_pacer_increment=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.non_wlt_rx_pkts_ctr = non_wlt_rx_pkts_ctr
        self.bad_crc_pkts_ctr = bad_crc_pkts_ctr
        self.wlt_rx_pkts_ctr = wlt_rx_pkts_ctr
        self.wlt_tx_pkts_ctr = wlt_tx_pkts_ctr
        self.tags_ctr = tags_ctr
        self.tx_queue_watermark = tx_queue_watermark
        self.effective_pacer_increment = effective_pacer_increment
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwHbV9):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.non_wlt_rx_pkts_ctr == other.non_wlt_rx_pkts_ctr and
                self.bad_crc_pkts_ctr == other.bad_crc_pkts_ctr and
                self.wlt_rx_pkts_ctr == other.wlt_rx_pkts_ctr and
                self.wlt_tx_pkts_ctr == other.wlt_tx_pkts_ctr and
                self.tags_ctr == other.tags_ctr and
                self.tx_queue_watermark == other.tx_queue_watermark and
                self.effective_pacer_increment == other.effective_pacer_increment
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u24u24u24u16u16u8u8", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.non_wlt_rx_pkts_ctr, self.bad_crc_pkts_ctr, self.wlt_rx_pkts_ctr, self.wlt_tx_pkts_ctr, self.tags_ctr, self.tx_queue_watermark, self.effective_pacer_increment)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u24u24u24u16u16u8u8", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.non_wlt_rx_pkts_ctr = d[4]
        self.bad_crc_pkts_ctr = d[5]
        self.wlt_rx_pkts_ctr = d[6]
        self.wlt_tx_pkts_ctr = d[7]
        self.tags_ctr = d[8]
        self.tx_queue_watermark = d[9]
        self.effective_pacer_increment = d[10]

class Brg2GwHbV8():
    def __init__(self, raw='', msg_type=0, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, non_wlt_rx_pkts_ctr=0, bad_crc_pkts_ctr=0, wlt_rx_pkts_ctr=0, wlt_tx_pkts_ctr=0, tags_ctr=0, tx_queue_watermark=0, unused=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.non_wlt_rx_pkts_ctr = non_wlt_rx_pkts_ctr
        self.bad_crc_pkts_ctr = bad_crc_pkts_ctr
        self.wlt_rx_pkts_ctr = wlt_rx_pkts_ctr
        self.wlt_tx_pkts_ctr = wlt_tx_pkts_ctr
        self.tags_ctr = tags_ctr
        self.tx_queue_watermark = tx_queue_watermark
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwHbV8):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.non_wlt_rx_pkts_ctr == other.non_wlt_rx_pkts_ctr and
                self.bad_crc_pkts_ctr == other.bad_crc_pkts_ctr and
                self.wlt_rx_pkts_ctr == other.wlt_rx_pkts_ctr and
                self.wlt_tx_pkts_ctr == other.wlt_tx_pkts_ctr and
                self.tags_ctr == other.tags_ctr and
                self.tx_queue_watermark == other.tx_queue_watermark
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u24u24u24u16u16u8u8", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.non_wlt_rx_pkts_ctr, self.bad_crc_pkts_ctr, self.wlt_rx_pkts_ctr, self.wlt_tx_pkts_ctr, self.tags_ctr, self.tx_queue_watermark, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u24u24u24u16u16u8u8", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.non_wlt_rx_pkts_ctr = d[4]
        self.bad_crc_pkts_ctr = d[5]
        self.wlt_rx_pkts_ctr = d[6]
        self.wlt_tx_pkts_ctr = d[7]
        self.tags_ctr = d[8]
        self.tx_queue_watermark = d[9]
        self.unused = d[10]

class Brg2GwHbV7():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_HB, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, non_wlt_rx_pkts_ctr=0, bad_crc_pkts_ctr=0, wlt_rx_pkts_ctr=0, wlt_tx_pkts_ctr=0, tags_ctr=0, unused=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.non_wlt_rx_pkts_ctr = non_wlt_rx_pkts_ctr
        self.bad_crc_pkts_ctr = bad_crc_pkts_ctr
        self.wlt_rx_pkts_ctr = wlt_rx_pkts_ctr
        self.wlt_tx_pkts_ctr = wlt_tx_pkts_ctr
        self.tags_ctr = tags_ctr
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwHbV7):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.non_wlt_rx_pkts_ctr == other.non_wlt_rx_pkts_ctr and
                self.bad_crc_pkts_ctr == other.bad_crc_pkts_ctr and
                self.wlt_rx_pkts_ctr == other.wlt_rx_pkts_ctr and
                self.wlt_tx_pkts_ctr == other.wlt_tx_pkts_ctr and
                self.tags_ctr == other.tags_ctr
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u24u24u24u16u16u16", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.non_wlt_rx_pkts_ctr, self.bad_crc_pkts_ctr, self.wlt_rx_pkts_ctr, self.wlt_tx_pkts_ctr, self.tags_ctr, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u24u24u24u16u16u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.non_wlt_rx_pkts_ctr = d[4]
        self.bad_crc_pkts_ctr = d[5]
        self.wlt_rx_pkts_ctr = d[6]
        self.wlt_tx_pkts_ctr = d[7]
        self.tags_ctr = d[8]
        self.unused = d[9]

class Brg2GwHbV6():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_HB, api_version=API_VERSION_V6, seq_id=0, brg_mac=0, non_wlt_rx_pkts_ctr=0, bad_crc_pkts_ctr=0, wlt_rx_pkts_ctr=0, wlt_tx_pkts_ctr=0, tags_ctr=0, unused=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.non_wlt_rx_pkts_ctr = non_wlt_rx_pkts_ctr
        self.bad_crc_pkts_ctr = bad_crc_pkts_ctr
        self.wlt_rx_pkts_ctr = wlt_rx_pkts_ctr
        self.wlt_tx_pkts_ctr = wlt_tx_pkts_ctr
        self.tags_ctr = tags_ctr
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwHbV6):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.non_wlt_rx_pkts_ctr == other.non_wlt_rx_pkts_ctr and
                self.bad_crc_pkts_ctr == other.bad_crc_pkts_ctr and
                self.wlt_rx_pkts_ctr == other.wlt_rx_pkts_ctr and
                self.wlt_tx_pkts_ctr == other.wlt_tx_pkts_ctr and
                self.tags_ctr == other.tags_ctr
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u24u24u24u16u16u16", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.non_wlt_rx_pkts_ctr, self.bad_crc_pkts_ctr, self.wlt_rx_pkts_ctr, self.wlt_tx_pkts_ctr, self.tags_ctr, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u24u24u24u16u16u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.non_wlt_rx_pkts_ctr = d[4]
        self.bad_crc_pkts_ctr = d[5]
        self.wlt_rx_pkts_ctr = d[6]
        self.wlt_tx_pkts_ctr = d[7]
        self.tags_ctr = d[8]
        self.unused = d[9]

class Brg2GwHbV5():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_HB, api_version=API_VERSION_V6, seq_id=0, brg_mac=0, non_wlt_rx_pkts_ctr=0, bad_crc_pkts_ctr=0, wlt_rx_pkts_ctr=0, wlt_tx_pkts_ctr=0, tags_ctr=0, unused=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.non_wlt_rx_pkts_ctr = non_wlt_rx_pkts_ctr
        self.bad_crc_pkts_ctr = bad_crc_pkts_ctr
        self.wlt_rx_pkts_ctr = wlt_rx_pkts_ctr
        self.wlt_tx_pkts_ctr = wlt_tx_pkts_ctr
        self.tags_ctr = tags_ctr
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwHbV5):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.non_wlt_rx_pkts_ctr == other.non_wlt_rx_pkts_ctr and
                self.bad_crc_pkts_ctr == other.bad_crc_pkts_ctr and
                self.wlt_rx_pkts_ctr == other.wlt_rx_pkts_ctr and
                self.wlt_tx_pkts_ctr == other.wlt_tx_pkts_ctr and
                self.tags_ctr == other.tags_ctr
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u24u24u24u16u16u16", self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.non_wlt_rx_pkts_ctr, self.bad_crc_pkts_ctr, self.wlt_rx_pkts_ctr, self.wlt_tx_pkts_ctr, self.tags_ctr, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u24u24u24u16u16u16", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.brg_mac = d[3]
        self.non_wlt_rx_pkts_ctr = d[4]
        self.bad_crc_pkts_ctr = d[5]
        self.wlt_rx_pkts_ctr = d[6]
        self.wlt_tx_pkts_ctr = d[7]
        self.tags_ctr = d[8]
        self.unused = d[9]

class Brg2GwHbV1():
    def __init__(self, raw='', msg_type=BRG_MGMT_MSG_TYPE_HB, api_version=API_VERSION_V1, seq_id=0, gw_mac=0, brg_mac=0, sent_pkts_ctr=0, non_wlt_pkts_ctr=0, tags_ctr=0, unused1=0):
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.gw_mac = gw_mac
        self.brg_mac = brg_mac
        self.sent_pkts_ctr = sent_pkts_ctr
        self.non_wlt_pkts_ctr = non_wlt_pkts_ctr
        self.tags_ctr = tags_ctr
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Brg2GwHbV1):
            return (
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.gw_mac == other.gw_mac and
                self.brg_mac == other.brg_mac and
                self.sent_pkts_ctr == other.sent_pkts_ctr and
                self.non_wlt_pkts_ctr == other.non_wlt_pkts_ctr and
                self.tags_ctr == other.tags_ctr
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u8u48u48u16u16u16u24", self.msg_type, self.api_version, self.seq_id, self.gw_mac, self.brg_mac, self.sent_pkts_ctr, self.non_wlt_pkts_ctr, self.tags_ctr, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u8u48u48u16u16u16u24", binascii.unhexlify(string))
        self.msg_type = d[0]
        self.api_version = d[1]
        self.seq_id = d[2]
        self.gw_mac = d[3]
        self.brg_mac = d[4]
        self.sent_pkts_ctr = d[5]
        self.non_wlt_pkts_ctr = d[6]
        self.tags_ctr = d[7]
        self.unused1 = d[8]

class SideInfo():
    def __init__(self, raw='', brg_mac=0, nfpkt=0, rssi=0, global_pacing_group=0, unused0=0, unused1=0, pkt_id=0):
        self.brg_mac = brg_mac
        self.nfpkt = nfpkt
        self.rssi = rssi
        self.global_pacing_group = global_pacing_group
        self.unused0 = unused0
        self.unused1 = unused1
        self.pkt_id = pkt_id
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, SideInfo):
            return (
                self.brg_mac == other.brg_mac and
                self.nfpkt == other.nfpkt and
                self.rssi == other.rssi and
                self.global_pacing_group == other.global_pacing_group and
                self.pkt_id == other.pkt_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u48u16u8u4u4u80u32", self.brg_mac, self.nfpkt, self.rssi, self.global_pacing_group, self.unused0, self.unused1, self.pkt_id)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u48u16u8u4u4u80u32", binascii.unhexlify(string))
        self.brg_mac = d[0]
        self.nfpkt = d[1]
        self.rssi = d[2]
        self.global_pacing_group = d[3]
        self.unused0 = d[4]
        self.unused1 = d[5]
        self.pkt_id = d[6]

class SideInfoSensor():
    def __init__(self, raw='', brg_mac=0, nfpkt=0, rssi=0, global_pacing_group=0, unused0=0, sensor_mac=0, sensor_ad_type=0, sensor_uuid_msb=0, sensor_uuid_lsb=0, api_version=0, unused1=0, is_scrambled=0, is_sensor_embedded=0, is_sensor=0, pkt_id=0):
        self.brg_mac = brg_mac
        self.nfpkt = nfpkt
        self.rssi = rssi
        self.global_pacing_group = global_pacing_group
        self.unused0 = unused0
        self.sensor_mac = sensor_mac
        self.sensor_ad_type = sensor_ad_type
        self.sensor_uuid_msb = sensor_uuid_msb
        self.sensor_uuid_lsb = sensor_uuid_lsb
        self.api_version = api_version
        self.unused1 = unused1
        self.is_scrambled = is_scrambled
        self.is_sensor_embedded = is_sensor_embedded
        self.is_sensor = is_sensor
        self.pkt_id = pkt_id
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, SideInfoSensor):
            return (
                self.brg_mac == other.brg_mac and
                self.nfpkt == other.nfpkt and
                self.rssi == other.rssi and
                self.global_pacing_group == other.global_pacing_group and
                self.sensor_mac == other.sensor_mac and
                self.sensor_ad_type == other.sensor_ad_type and
                self.sensor_uuid_msb == other.sensor_uuid_msb and
                self.sensor_uuid_lsb == other.sensor_uuid_lsb and
                self.api_version == other.api_version and
                self.is_scrambled == other.is_scrambled and
                self.is_sensor_embedded == other.is_sensor_embedded and
                self.is_sensor == other.is_sensor and
                self.pkt_id == other.pkt_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u48u16u8u4u4u48u8u8u8u4u1u1u1u1u32", self.brg_mac, self.nfpkt, self.rssi, self.global_pacing_group, self.unused0, self.sensor_mac, self.sensor_ad_type, self.sensor_uuid_msb, self.sensor_uuid_lsb, self.api_version, self.unused1, self.is_scrambled, self.is_sensor_embedded, self.is_sensor, self.pkt_id)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u48u16u8u4u4u48u8u8u8u4u1u1u1u1u32", binascii.unhexlify(string))
        self.brg_mac = d[0]
        self.nfpkt = d[1]
        self.rssi = d[2]
        self.global_pacing_group = d[3]
        self.unused0 = d[4]
        self.sensor_mac = d[5]
        self.sensor_ad_type = d[6]
        self.sensor_uuid_msb = d[7]
        self.sensor_uuid_lsb = d[8]
        self.api_version = d[9]
        self.unused1 = d[10]
        self.is_scrambled = d[11]
        self.is_sensor_embedded = d[12]
        self.is_sensor = d[13]
        self.pkt_id = d[14]

class PktFilterStruct():
    def __init__(self, raw='', unused=0, mask_enable=0, p3_pacing=0, p2_pacing=0, p1_pacing=0, p0_pacing=0):
        self.unused = unused
        self.mask_enable = mask_enable
        self.p3_pacing = p3_pacing
        self.p2_pacing = p2_pacing
        self.p1_pacing = p1_pacing
        self.p0_pacing = p0_pacing
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, PktFilterStruct):
            return (
                self.mask_enable == other.mask_enable and
                self.p3_pacing == other.p3_pacing and
                self.p2_pacing == other.p2_pacing and
                self.p1_pacing == other.p1_pacing and
                self.p0_pacing == other.p0_pacing
            )
        return False

    def dump(self):
        string = bitstruct.pack("u3u1u1u1u1u1", self.unused, self.mask_enable, self.p3_pacing, self.p2_pacing, self.p1_pacing, self.p0_pacing)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u3u1u1u1u1u1", binascii.unhexlify(string))
        self.unused = d[0]
        self.mask_enable = d[1]
        self.p3_pacing = d[2]
        self.p2_pacing = d[3]
        self.p1_pacing = d[4]
        self.p0_pacing = d[5]

class PwrMgmt():
    def __init__(self, raw='', leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, unused=0):
        self.leds_on = leds_on
        self.keep_alive_scan = keep_alive_scan # 10 [msec] resolution
        self.keep_alive_period = keep_alive_period # 5 [sec] resolution
        self.on_duration = on_duration # 30 [sec] resolution
        self.sleep_duration = sleep_duration # 60 [sec] resolution
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, PwrMgmt):
            return (
                self.leds_on == other.leds_on and
                self.keep_alive_scan == other.keep_alive_scan and
                self.keep_alive_period == other.keep_alive_period and
                self.on_duration == other.on_duration and
                self.sleep_duration == other.sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u1u6u5u7u11u2", self.leds_on, self.keep_alive_scan, self.keep_alive_period, self.on_duration, self.sleep_duration, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u1u6u5u7u11u2", binascii.unhexlify(string))
        self.leds_on = d[0]
        self.keep_alive_scan = d[1]
        self.keep_alive_period = d[2]
        self.on_duration = d[3]
        self.sleep_duration = d[4]
        self.unused = d[5]

class Lis2Dw12Cfg():
    def __init__(self, raw='', version=LIS2DW12_DEFAULTS_CFG_PACKET_VERSION, state_threshold=LIS2DW12_DEFAULTS_STATE_THRESHOLD, wake_up_duration=LIS2DW12_DEFAULTS_WAKE_UP_DURATION, sleep_duration=LIS2DW12_DEFAULTS_SLEEP_DURATION, unused=0):
        self.version = version
        self.state_threshold = state_threshold # 31 [mg] resolution
        self.wake_up_duration = wake_up_duration # 3 [sec] resolution
        self.sleep_duration = sleep_duration # 5 [sec] resolution
        self.unused = unused
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Lis2Dw12Cfg):
            return (
                self.version == other.version and
                self.state_threshold == other.state_threshold and
                self.wake_up_duration == other.wake_up_duration and
                self.sleep_duration == other.sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u6u6u4u8", self.version, self.state_threshold, self.wake_up_duration, self.sleep_duration, self.unused)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u6u6u4u8", binascii.unhexlify(string))
        self.version = d[0]
        self.state_threshold = d[1]
        self.wake_up_duration = d[2]
        self.sleep_duration = d[3]
        self.unused = d[4]

class ModuleIfV10():
    def __init__(self, raw='', module_type=MODULE_IF, msg_type=0, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, board_type=0, bl_version=0, major_ver=0, minor_ver=0, patch_ver=0, sup_cap_glob=0, sup_cap_datapath=0, sup_cap_energy2400=0, sup_cap_energy_sub1g=0, sup_cap_calibration=0, sup_cap_pwr_mgmt=0, sup_cap_sensors=0, sup_cap_custom=0, cfg_hash=0, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.board_type = board_type
        self.bl_version = bl_version
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.patch_ver = patch_ver
        self.sup_cap_glob = sup_cap_glob
        self.sup_cap_datapath = sup_cap_datapath
        self.sup_cap_energy2400 = sup_cap_energy2400
        self.sup_cap_energy_sub1g = sup_cap_energy_sub1g
        self.sup_cap_calibration = sup_cap_calibration
        self.sup_cap_pwr_mgmt = sup_cap_pwr_mgmt
        self.sup_cap_sensors = sup_cap_sensors
        self.sup_cap_custom = sup_cap_custom
        self.cfg_hash = cfg_hash
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleIfV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.board_type == other.board_type and
                self.bl_version == other.bl_version and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.patch_ver == other.patch_ver and
                self.sup_cap_glob == other.sup_cap_glob and
                self.sup_cap_datapath == other.sup_cap_datapath and
                self.sup_cap_energy2400 == other.sup_cap_energy2400 and
                self.sup_cap_energy_sub1g == other.sup_cap_energy_sub1g and
                self.sup_cap_calibration == other.sup_cap_calibration and
                self.sup_cap_pwr_mgmt == other.sup_cap_pwr_mgmt and
                self.sup_cap_sensors == other.sup_cap_sensors and
                self.sup_cap_custom == other.sup_cap_custom and
                self.cfg_hash == other.cfg_hash
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u32u40", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.board_type, self.bl_version, self.major_ver, self.minor_ver, self.patch_ver, self.sup_cap_glob, self.sup_cap_datapath, self.sup_cap_energy2400, self.sup_cap_energy_sub1g, self.sup_cap_calibration, self.sup_cap_pwr_mgmt, self.sup_cap_sensors, self.sup_cap_custom, self.cfg_hash, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u32u40", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.board_type = d[5]
        self.bl_version = d[6]
        self.major_ver = d[7]
        self.minor_ver = d[8]
        self.patch_ver = d[9]
        self.sup_cap_glob = d[10]
        self.sup_cap_datapath = d[11]
        self.sup_cap_energy2400 = d[12]
        self.sup_cap_energy_sub1g = d[13]
        self.sup_cap_calibration = d[14]
        self.sup_cap_pwr_mgmt = d[15]
        self.sup_cap_sensors = d[16]
        self.sup_cap_custom = d[17]
        self.cfg_hash = d[18]
        self.unused0 = d[19]

class ModuleIfV9():
    def __init__(self, raw='', module_type=MODULE_IF, msg_type=0, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, board_type=0, bl_version=0, major_ver=0, minor_ver=0, patch_ver=0, sup_cap_glob=0, sup_cap_datapath=0, sup_cap_energy2400=0, sup_cap_energy_sub1g=0, sup_cap_calibration=0, sup_cap_pwr_mgmt=0, sup_cap_sensors=0, sup_cap_custom=0, cfg_hash=0, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.board_type = board_type
        self.bl_version = bl_version
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.patch_ver = patch_ver
        self.sup_cap_glob = sup_cap_glob
        self.sup_cap_datapath = sup_cap_datapath
        self.sup_cap_energy2400 = sup_cap_energy2400
        self.sup_cap_energy_sub1g = sup_cap_energy_sub1g
        self.sup_cap_calibration = sup_cap_calibration
        self.sup_cap_pwr_mgmt = sup_cap_pwr_mgmt
        self.sup_cap_sensors = sup_cap_sensors
        self.sup_cap_custom = sup_cap_custom
        self.cfg_hash = cfg_hash
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleIfV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.board_type == other.board_type and
                self.bl_version == other.bl_version and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.patch_ver == other.patch_ver and
                self.sup_cap_glob == other.sup_cap_glob and
                self.sup_cap_datapath == other.sup_cap_datapath and
                self.sup_cap_energy2400 == other.sup_cap_energy2400 and
                self.sup_cap_energy_sub1g == other.sup_cap_energy_sub1g and
                self.sup_cap_calibration == other.sup_cap_calibration and
                self.sup_cap_pwr_mgmt == other.sup_cap_pwr_mgmt and
                self.sup_cap_sensors == other.sup_cap_sensors and
                self.sup_cap_custom == other.sup_cap_custom and
                self.cfg_hash == other.cfg_hash
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u32u40", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.board_type, self.bl_version, self.major_ver, self.minor_ver, self.patch_ver, self.sup_cap_glob, self.sup_cap_datapath, self.sup_cap_energy2400, self.sup_cap_energy_sub1g, self.sup_cap_calibration, self.sup_cap_pwr_mgmt, self.sup_cap_sensors, self.sup_cap_custom, self.cfg_hash, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u32u40", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.board_type = d[5]
        self.bl_version = d[6]
        self.major_ver = d[7]
        self.minor_ver = d[8]
        self.patch_ver = d[9]
        self.sup_cap_glob = d[10]
        self.sup_cap_datapath = d[11]
        self.sup_cap_energy2400 = d[12]
        self.sup_cap_energy_sub1g = d[13]
        self.sup_cap_calibration = d[14]
        self.sup_cap_pwr_mgmt = d[15]
        self.sup_cap_sensors = d[16]
        self.sup_cap_custom = d[17]
        self.cfg_hash = d[18]
        self.unused0 = d[19]

class ModuleIfV8():
    def __init__(self, raw='', module_type=MODULE_IF, msg_type=0, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, board_type=0, bl_version=0, major_ver=0, minor_ver=0, patch_ver=0, sup_cap_glob=0, sup_cap_datapath=0, sup_cap_energy2400=0, sup_cap_energy_sub1g=0, sup_cap_calibration=0, sup_cap_pwr_mgmt=0, sup_cap_sensors=0, sup_cap_custom=0, cfg_hash=0, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.board_type = board_type
        self.bl_version = bl_version
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.patch_ver = patch_ver
        self.sup_cap_glob = sup_cap_glob
        self.sup_cap_datapath = sup_cap_datapath
        self.sup_cap_energy2400 = sup_cap_energy2400
        self.sup_cap_energy_sub1g = sup_cap_energy_sub1g
        self.sup_cap_calibration = sup_cap_calibration
        self.sup_cap_pwr_mgmt = sup_cap_pwr_mgmt
        self.sup_cap_sensors = sup_cap_sensors
        self.sup_cap_custom = sup_cap_custom
        self.cfg_hash = cfg_hash
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleIfV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.board_type == other.board_type and
                self.bl_version == other.bl_version and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.patch_ver == other.patch_ver and
                self.sup_cap_glob == other.sup_cap_glob and
                self.sup_cap_datapath == other.sup_cap_datapath and
                self.sup_cap_energy2400 == other.sup_cap_energy2400 and
                self.sup_cap_energy_sub1g == other.sup_cap_energy_sub1g and
                self.sup_cap_calibration == other.sup_cap_calibration and
                self.sup_cap_pwr_mgmt == other.sup_cap_pwr_mgmt and
                self.sup_cap_sensors == other.sup_cap_sensors and
                self.sup_cap_custom == other.sup_cap_custom and
                self.cfg_hash == other.cfg_hash
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u32u40", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.board_type, self.bl_version, self.major_ver, self.minor_ver, self.patch_ver, self.sup_cap_glob, self.sup_cap_datapath, self.sup_cap_energy2400, self.sup_cap_energy_sub1g, self.sup_cap_calibration, self.sup_cap_pwr_mgmt, self.sup_cap_sensors, self.sup_cap_custom, self.cfg_hash, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u32u40", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.board_type = d[5]
        self.bl_version = d[6]
        self.major_ver = d[7]
        self.minor_ver = d[8]
        self.patch_ver = d[9]
        self.sup_cap_glob = d[10]
        self.sup_cap_datapath = d[11]
        self.sup_cap_energy2400 = d[12]
        self.sup_cap_energy_sub1g = d[13]
        self.sup_cap_calibration = d[14]
        self.sup_cap_pwr_mgmt = d[15]
        self.sup_cap_sensors = d[16]
        self.sup_cap_custom = d[17]
        self.cfg_hash = d[18]
        self.unused0 = d[19]

class ModuleIfV7():
    def __init__(self, raw='', module_type=MODULE_IF, msg_type=0, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, board_type=0, bl_version=0, major_ver=0, minor_ver=0, patch_ver=0, sup_cap_glob=0, sup_cap_datapath=0, sup_cap_energy2400=0, sup_cap_energy_sub1g=0, sup_cap_calibration=0, sup_cap_pwr_mgmt=0, sup_cap_sensors=0, sup_cap_custom=0, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.board_type = board_type
        self.bl_version = bl_version
        self.major_ver = major_ver
        self.minor_ver = minor_ver
        self.patch_ver = patch_ver
        self.sup_cap_glob = sup_cap_glob
        self.sup_cap_datapath = sup_cap_datapath
        self.sup_cap_energy2400 = sup_cap_energy2400
        self.sup_cap_energy_sub1g = sup_cap_energy_sub1g
        self.sup_cap_calibration = sup_cap_calibration
        self.sup_cap_pwr_mgmt = sup_cap_pwr_mgmt
        self.sup_cap_sensors = sup_cap_sensors
        self.sup_cap_custom = sup_cap_custom
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleIfV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.board_type == other.board_type and
                self.bl_version == other.bl_version and
                self.major_ver == other.major_ver and
                self.minor_ver == other.minor_ver and
                self.patch_ver == other.patch_ver and
                self.sup_cap_glob == other.sup_cap_glob and
                self.sup_cap_datapath == other.sup_cap_datapath and
                self.sup_cap_energy2400 == other.sup_cap_energy2400 and
                self.sup_cap_energy_sub1g == other.sup_cap_energy_sub1g and
                self.sup_cap_calibration == other.sup_cap_calibration and
                self.sup_cap_pwr_mgmt == other.sup_cap_pwr_mgmt and
                self.sup_cap_sensors == other.sup_cap_sensors and
                self.sup_cap_custom == other.sup_cap_custom
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u72", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.board_type, self.bl_version, self.major_ver, self.minor_ver, self.patch_ver, self.sup_cap_glob, self.sup_cap_datapath, self.sup_cap_energy2400, self.sup_cap_energy_sub1g, self.sup_cap_calibration, self.sup_cap_pwr_mgmt, self.sup_cap_sensors, self.sup_cap_custom, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u1u1u1u1u1u1u1u1u72", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.board_type = d[5]
        self.bl_version = d[6]
        self.major_ver = d[7]
        self.minor_ver = d[8]
        self.patch_ver = d[9]
        self.sup_cap_glob = d[10]
        self.sup_cap_datapath = d[11]
        self.sup_cap_energy2400 = d[12]
        self.sup_cap_energy_sub1g = d[13]
        self.sup_cap_calibration = d[14]
        self.sup_cap_pwr_mgmt = d[15]
        self.sup_cap_sensors = d[16]
        self.sup_cap_custom = d[17]
        self.unused0 = d[18]

class ModuleCalibrationV10():
    def __init__(self, raw='', module_type=MODULE_CALIBRATION, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, calib_interval=BRG_DEFAULT_CALIB_INTERVAL, calib_output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, calib_pattern=BRG_DEFAULT_CALIB_PATTERN, unused0=0, unused1=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.calib_interval = calib_interval
        self.calib_output_power = calib_output_power
        self.calib_pattern = calib_pattern
        self.unused0 = unused0
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCalibrationV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.calib_interval == other.calib_interval and
                self.calib_output_power == other.calib_output_power and
                self.calib_pattern == other.calib_pattern
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8s8u4u4u96", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.calib_interval, self.calib_output_power, self.calib_pattern, self.unused0, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8s8u4u4u96", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.calib_interval = d[5]
        self.calib_output_power = d[6]
        self.calib_pattern = d[7]
        self.unused0 = d[8]
        self.unused1 = d[9]

class ModuleCalibrationV9():
    def __init__(self, raw='', module_type=MODULE_CALIBRATION, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, calib_interval=BRG_DEFAULT_CALIB_INTERVAL, calib_output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, calib_pattern=BRG_DEFAULT_CALIB_PATTERN, unused0=0, unused1=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.calib_interval = calib_interval
        self.calib_output_power = calib_output_power
        self.calib_pattern = calib_pattern
        self.unused0 = unused0
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCalibrationV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.calib_interval == other.calib_interval and
                self.calib_output_power == other.calib_output_power and
                self.calib_pattern == other.calib_pattern
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8s8u4u4u96", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.calib_interval, self.calib_output_power, self.calib_pattern, self.unused0, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8s8u4u4u96", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.calib_interval = d[5]
        self.calib_output_power = d[6]
        self.calib_pattern = d[7]
        self.unused0 = d[8]
        self.unused1 = d[9]

class ModuleCalibrationV8():
    def __init__(self, raw='', module_type=MODULE_CALIBRATION, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCalibrationV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u120", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u120", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused0 = d[5]

class ModuleCalibrationV7():
    def __init__(self, raw='', module_type=MODULE_CALIBRATION, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCalibrationV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u120", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u120", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.unused0 = d[5]

class ModuleDatapathV10():
    def __init__(self, raw='', module_type=MODULE_DATAPATH, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, unused0=0, adaptive_pacer=BRG_DEFAULT_ADAPTIVE_PACER, unified_echo_pkt=BRG_DEFAULT_UNIFIED_ECHO_PKT, pacer_interval=BRG_DEFAULT_PACER_INTERVAL, pkt_filter=BRG_DEFAULT_PKT_FILTER, tx_repetition=BRG_DEFAULT_TX_REPETITION, comm_output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, comm_pattern=BRG_DEFAULT_COMM_PATTERN, unused1=0, unused2=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.global_pacing_group = global_pacing_group
        self.unused0 = unused0
        self.adaptive_pacer = adaptive_pacer
        self.unified_echo_pkt = unified_echo_pkt
        self.pacer_interval = pacer_interval
        self.pkt_filter = pkt_filter
        self.tx_repetition = tx_repetition
        self.comm_output_power = comm_output_power
        self.comm_pattern = comm_pattern
        self.unused1 = unused1
        self.unused2 = unused2
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleDatapathV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.global_pacing_group == other.global_pacing_group and
                self.adaptive_pacer == other.adaptive_pacer and
                self.unified_echo_pkt == other.unified_echo_pkt and
                self.pacer_interval == other.pacer_interval and
                self.pkt_filter == other.pkt_filter and
                self.tx_repetition == other.tx_repetition and
                self.comm_output_power == other.comm_output_power and
                self.comm_pattern == other.comm_pattern
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u4u2u1u1u16u5u3s8u4u4u72", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.global_pacing_group, self.unused0, self.adaptive_pacer, self.unified_echo_pkt, self.pacer_interval, self.pkt_filter, self.tx_repetition, self.comm_output_power, self.comm_pattern, self.unused1, self.unused2)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u4u2u1u1u16u5u3s8u4u4u72", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.global_pacing_group = d[5]
        self.unused0 = d[6]
        self.adaptive_pacer = d[7]
        self.unified_echo_pkt = d[8]
        self.pacer_interval = d[9]
        self.pkt_filter = d[10]
        self.tx_repetition = d[11]
        self.comm_output_power = d[12]
        self.comm_pattern = d[13]
        self.unused1 = d[14]
        self.unused2 = d[15]

class ModuleDatapathV9():
    def __init__(self, raw='', module_type=MODULE_DATAPATH, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, unused0=0, adaptive_pacer=BRG_DEFAULT_ADAPTIVE_PACER, unified_echo_pkt=BRG_DEFAULT_UNIFIED_ECHO_PKT, pacer_interval=BRG_DEFAULT_PACER_INTERVAL, pkt_filter=BRG_DEFAULT_PKT_FILTER, tx_repetition=BRG_DEFAULT_TX_REPETITION, comm_output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, comm_pattern=BRG_DEFAULT_COMM_PATTERN, unused1=0, unused2=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.global_pacing_group = global_pacing_group
        self.unused0 = unused0
        self.adaptive_pacer = adaptive_pacer
        self.unified_echo_pkt = unified_echo_pkt
        self.pacer_interval = pacer_interval
        self.pkt_filter = pkt_filter
        self.tx_repetition = tx_repetition
        self.comm_output_power = comm_output_power
        self.comm_pattern = comm_pattern
        self.unused1 = unused1
        self.unused2 = unused2
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleDatapathV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.global_pacing_group == other.global_pacing_group and
                self.adaptive_pacer == other.adaptive_pacer and
                self.unified_echo_pkt == other.unified_echo_pkt and
                self.pacer_interval == other.pacer_interval and
                self.pkt_filter == other.pkt_filter and
                self.tx_repetition == other.tx_repetition and
                self.comm_output_power == other.comm_output_power and
                self.comm_pattern == other.comm_pattern
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u4u2u1u1u16u5u3s8u4u4u72", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.global_pacing_group, self.unused0, self.adaptive_pacer, self.unified_echo_pkt, self.pacer_interval, self.pkt_filter, self.tx_repetition, self.comm_output_power, self.comm_pattern, self.unused1, self.unused2)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u4u2u1u1u16u5u3s8u4u4u72", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.global_pacing_group = d[5]
        self.unused0 = d[6]
        self.adaptive_pacer = d[7]
        self.unified_echo_pkt = d[8]
        self.pacer_interval = d[9]
        self.pkt_filter = d[10]
        self.tx_repetition = d[11]
        self.comm_output_power = d[12]
        self.comm_pattern = d[13]
        self.unused1 = d[14]
        self.unused2 = d[15]

class ModuleDatapathV8():
    def __init__(self, raw='', module_type=MODULE_DATAPATH, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, unused0=0, pacer_interval=BRG_DEFAULT_PACER_INTERVAL, pkt_types_mask=BRG_DEFAULT_PKT_TYPES_MASK, tx_repetition=BRG_DEFAULT_TX_REPETITION, unused1=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.global_pacing_group = global_pacing_group
        self.unused0 = unused0
        self.pacer_interval = pacer_interval
        self.pkt_types_mask = pkt_types_mask
        self.tx_repetition = tx_repetition
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleDatapathV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.global_pacing_group == other.global_pacing_group and
                self.pacer_interval == other.pacer_interval and
                self.pkt_types_mask == other.pkt_types_mask and
                self.tx_repetition == other.tx_repetition
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u4u4u16u5u3u88", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.global_pacing_group, self.unused0, self.pacer_interval, self.pkt_types_mask, self.tx_repetition, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u4u4u16u5u3u88", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.global_pacing_group = d[5]
        self.unused0 = d[6]
        self.pacer_interval = d[7]
        self.pkt_types_mask = d[8]
        self.tx_repetition = d[9]
        self.unused1 = d[10]

class ModuleDatapathV7():
    def __init__(self, raw='', module_type=MODULE_DATAPATH, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, global_pacing_group=BRG_DEFAULT_GLOBAL_PACING_GROUP, unused0=0, pacer_interval=BRG_DEFAULT_PACER_INTERVAL, unsued2=0, tx_repetition=BRG_DEFAULT_TX_REPETITION, unused1=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.global_pacing_group = global_pacing_group
        self.unused0 = unused0
        self.pacer_interval = pacer_interval
        self.unsued2 = unsued2
        self.tx_repetition = tx_repetition
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleDatapathV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.global_pacing_group == other.global_pacing_group and
                self.pacer_interval == other.pacer_interval and
                self.unsued2 == other.unsued2 and
                self.tx_repetition == other.tx_repetition
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u4u4u16u5u3u88", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.global_pacing_group, self.unused0, self.pacer_interval, self.unsued2, self.tx_repetition, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u4u4u16u5u3u88", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.global_pacing_group = d[5]
        self.unused0 = d[6]
        self.pacer_interval = d[7]
        self.unsued2 = d[8]
        self.tx_repetition = d[9]
        self.unused1 = d[10]

class ModuleEnergy2400V10():
    def __init__(self, raw='', module_type=MODULE_ENERGY_2400, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, duty_cycle=BRG_DEFAULT_ENERGY_DUTY_CYCLE_2_4, energy_pattern_2400=BRG_DEFAULT_ENERGY_PATTERN_2_4, output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.duty_cycle = duty_cycle
        self.energy_pattern_2400 = energy_pattern_2400
        self.output_power = output_power
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergy2400V10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.duty_cycle == other.duty_cycle and
                self.energy_pattern_2400 == other.energy_pattern_2400 and
                self.output_power == other.output_power
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8s8u96", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.duty_cycle, self.energy_pattern_2400, self.output_power, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8s8u96", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.duty_cycle = d[5]
        self.energy_pattern_2400 = d[6]
        self.output_power = d[7]
        self.unused0 = d[8]

class ModuleEnergy2400V9():
    def __init__(self, raw='', module_type=MODULE_ENERGY_2400, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, duty_cycle=BRG_DEFAULT_ENERGY_DUTY_CYCLE_2_4, energy_pattern_2400=BRG_DEFAULT_ENERGY_PATTERN_2_4, output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.duty_cycle = duty_cycle
        self.energy_pattern_2400 = energy_pattern_2400
        self.output_power = output_power
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergy2400V9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.duty_cycle == other.duty_cycle and
                self.energy_pattern_2400 == other.energy_pattern_2400 and
                self.output_power == other.output_power
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8s8u96", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.duty_cycle, self.energy_pattern_2400, self.output_power, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8s8u96", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.duty_cycle = d[5]
        self.energy_pattern_2400 = d[6]
        self.output_power = d[7]
        self.unused0 = d[8]

class ModuleEnergy2400V8():
    def __init__(self, raw='', module_type=MODULE_ENERGY_2400, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, rx_tx_period=BRG_DEFAULT_RXTX_PERIOD, tx_period=BRG_DEFAULT_TX_PERIOD, energy_pattern=BRG_DEFAULT_ENERGY_PATTERN_IDX_OLD, output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.rx_tx_period = rx_tx_period
        self.tx_period = tx_period
        self.energy_pattern = energy_pattern
        self.output_power = output_power
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergy2400V8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period == other.rx_tx_period and
                self.tx_period == other.tx_period and
                self.energy_pattern == other.energy_pattern and
                self.output_power == other.output_power
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8s8u88", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.rx_tx_period, self.tx_period, self.energy_pattern, self.output_power, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8s8u88", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.rx_tx_period = d[5]
        self.tx_period = d[6]
        self.energy_pattern = d[7]
        self.output_power = d[8]
        self.unused0 = d[9]

class ModuleEnergy2400V7():
    def __init__(self, raw='', module_type=MODULE_ENERGY_2400, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, rx_tx_period=BRG_DEFAULT_RXTX_PERIOD, tx_period=BRG_DEFAULT_TX_PERIOD, energy_pattern=BRG_DEFAULT_ENERGY_PATTERN_IDX_OLD, output_power=BRG_DEFAULT_OUTPUT_POWER_2_4, tx_probability=50, unused0=0, unused1=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.rx_tx_period = rx_tx_period
        self.tx_period = tx_period
        self.energy_pattern = energy_pattern
        self.output_power = output_power
        self.tx_probability = tx_probability
        self.unused0 = unused0
        self.unused1 = unused1
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergy2400V7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.rx_tx_period == other.rx_tx_period and
                self.tx_period == other.tx_period and
                self.energy_pattern == other.energy_pattern and
                self.output_power == other.output_power and
                self.tx_probability == other.tx_probability
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8s8u3u5u80", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.rx_tx_period, self.tx_period, self.energy_pattern, self.output_power, ((self.tx_probability-30)//10), self.unused0, self.unused1)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8s8u3u5u80", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.rx_tx_period = d[5]
        self.tx_period = d[6]
        self.energy_pattern = d[7]
        self.output_power = d[8]
        self.tx_probability = ((d[9]*10)+30)
        self.unused0 = d[10]
        self.unused1 = d[11]

MODULE_ENERGY_SUB1G_V10_OUTPUT_POWER_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
MODULE_ENERGY_SUB1G_V10_OUTPUT_POWER_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
class ModuleEnergySub1GV10():
    def __init__(self, raw='', module_type=MODULE_ENERGY_SUB1G, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, output_power=BRG_DEFAULT_OUTPUT_POWER_SUB1G, sub1g_energy_pattern=BRG_DEFAULT_SUB1G_ENERGY_PATTERN, cycle=BRG_DEFAULT_SUB1G_CYCLE, duty_cycle=BRG_DEFAULT_SUB1G_DUTY_CYCLE, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.output_power = output_power
        self.sub1g_energy_pattern = sub1g_energy_pattern
        self.cycle = cycle
        self.duty_cycle = duty_cycle
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergySub1GV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.output_power == other.output_power and
                self.sub1g_energy_pattern == other.sub1g_energy_pattern and
                self.cycle == other.cycle and
                self.duty_cycle == other.duty_cycle
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u88", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, MODULE_ENERGY_SUB1G_V10_OUTPUT_POWER_ENC[self.output_power], self.sub1g_energy_pattern, self.cycle, self.duty_cycle, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u88", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.output_power = MODULE_ENERGY_SUB1G_V10_OUTPUT_POWER_DEC[d[5]]
        self.sub1g_energy_pattern = d[6]
        self.cycle = d[7]
        self.duty_cycle = d[8]
        self.unused0 = d[9]

MODULE_ENERGY_SUB1G_V9_OUTPUT_POWER_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
MODULE_ENERGY_SUB1G_V9_OUTPUT_POWER_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
class ModuleEnergySub1GV9():
    def __init__(self, raw='', module_type=MODULE_ENERGY_SUB1G, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, output_power=BRG_DEFAULT_OUTPUT_POWER_SUB1G, sub1g_energy_pattern=BRG_DEFAULT_SUB1G_ENERGY_PATTERN, cycle=BRG_DEFAULT_SUB1G_CYCLE, duty_cycle=BRG_DEFAULT_SUB1G_DUTY_CYCLE, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.output_power = output_power
        self.sub1g_energy_pattern = sub1g_energy_pattern
        self.cycle = cycle
        self.duty_cycle = duty_cycle
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergySub1GV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.output_power == other.output_power and
                self.sub1g_energy_pattern == other.sub1g_energy_pattern and
                self.cycle == other.cycle and
                self.duty_cycle == other.duty_cycle
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u88", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, MODULE_ENERGY_SUB1G_V9_OUTPUT_POWER_ENC[self.output_power], self.sub1g_energy_pattern, self.cycle, self.duty_cycle, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u88", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.output_power = MODULE_ENERGY_SUB1G_V9_OUTPUT_POWER_DEC[d[5]]
        self.sub1g_energy_pattern = d[6]
        self.cycle = d[7]
        self.duty_cycle = d[8]
        self.unused0 = d[9]

MODULE_ENERGY_SUB1G_V8_OUTPUT_POWER_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
MODULE_ENERGY_SUB1G_V8_OUTPUT_POWER_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
MODULE_ENERGY_SUB1G_V8_FREQUENCY_ENC = {SUB1G_FREQ_915000:SUB1G_FREQ_PROFILE_915000, SUB1G_FREQ_916300:SUB1G_FREQ_PROFILE_916300, SUB1G_FREQ_917500:SUB1G_FREQ_PROFILE_917500, SUB1G_FREQ_918000:SUB1G_FREQ_PROFILE_918000, SUB1G_FREQ_919100:SUB1G_FREQ_PROFILE_919100}
MODULE_ENERGY_SUB1G_V8_FREQUENCY_DEC = {SUB1G_FREQ_PROFILE_915000:SUB1G_FREQ_915000, SUB1G_FREQ_PROFILE_916300:SUB1G_FREQ_916300, SUB1G_FREQ_PROFILE_917500:SUB1G_FREQ_917500, SUB1G_FREQ_PROFILE_918000:SUB1G_FREQ_918000, SUB1G_FREQ_PROFILE_919100:SUB1G_FREQ_919100}
class ModuleEnergySub1GV8():
    def __init__(self, raw='', module_type=MODULE_ENERGY_SUB1G, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, output_power=BRG_DEFAULT_OUTPUT_POWER_SUB1G, frequency=BRG_DEFAULT_SUB1G_FREQ, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.output_power = output_power
        self.frequency = frequency
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergySub1GV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.output_power == other.output_power and
                self.frequency == other.frequency
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u104", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, MODULE_ENERGY_SUB1G_V8_OUTPUT_POWER_ENC[self.output_power], MODULE_ENERGY_SUB1G_V8_FREQUENCY_ENC[self.frequency], self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u104", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.output_power = MODULE_ENERGY_SUB1G_V8_OUTPUT_POWER_DEC[d[5]]
        self.frequency = MODULE_ENERGY_SUB1G_V8_FREQUENCY_DEC[d[6]]
        self.unused0 = d[7]

MODULE_ENERGY_SUB1G_V7_OUTPUT_POWER_ENC = {SUB1G_OUTPUT_POWER_14:SUB1G_OUTPUT_POWER_PROFILE_14, SUB1G_OUTPUT_POWER_17:SUB1G_OUTPUT_POWER_PROFILE_17, SUB1G_OUTPUT_POWER_20:SUB1G_OUTPUT_POWER_PROFILE_20, SUB1G_OUTPUT_POWER_23:SUB1G_OUTPUT_POWER_PROFILE_23, SUB1G_OUTPUT_POWER_26:SUB1G_OUTPUT_POWER_PROFILE_26, SUB1G_OUTPUT_POWER_29:SUB1G_OUTPUT_POWER_PROFILE_29, SUB1G_OUTPUT_POWER_32:SUB1G_OUTPUT_POWER_PROFILE_32}
MODULE_ENERGY_SUB1G_V7_OUTPUT_POWER_DEC = {SUB1G_OUTPUT_POWER_PROFILE_14:SUB1G_OUTPUT_POWER_14, SUB1G_OUTPUT_POWER_PROFILE_17:SUB1G_OUTPUT_POWER_17, SUB1G_OUTPUT_POWER_PROFILE_20:SUB1G_OUTPUT_POWER_20, SUB1G_OUTPUT_POWER_PROFILE_23:SUB1G_OUTPUT_POWER_23, SUB1G_OUTPUT_POWER_PROFILE_26:SUB1G_OUTPUT_POWER_26, SUB1G_OUTPUT_POWER_PROFILE_29:SUB1G_OUTPUT_POWER_29, SUB1G_OUTPUT_POWER_PROFILE_32:SUB1G_OUTPUT_POWER_32}
MODULE_ENERGY_SUB1G_V7_FREQUENCY_ENC = {SUB1G_FREQ_915000:SUB1G_FREQ_PROFILE_915000, SUB1G_FREQ_916300:SUB1G_FREQ_PROFILE_916300, SUB1G_FREQ_917500:SUB1G_FREQ_PROFILE_917500, SUB1G_FREQ_918000:SUB1G_FREQ_PROFILE_918000, SUB1G_FREQ_919100:SUB1G_FREQ_PROFILE_919100}
MODULE_ENERGY_SUB1G_V7_FREQUENCY_DEC = {SUB1G_FREQ_PROFILE_915000:SUB1G_FREQ_915000, SUB1G_FREQ_PROFILE_916300:SUB1G_FREQ_916300, SUB1G_FREQ_PROFILE_917500:SUB1G_FREQ_917500, SUB1G_FREQ_PROFILE_918000:SUB1G_FREQ_918000, SUB1G_FREQ_PROFILE_919100:SUB1G_FREQ_919100}
class ModuleEnergySub1GV7():
    def __init__(self, raw='', module_type=MODULE_ENERGY_SUB1G, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, output_power=BRG_DEFAULT_OUTPUT_POWER_SUB1G, frequency=BRG_DEFAULT_SUB1G_FREQ, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.output_power = output_power
        self.frequency = frequency
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleEnergySub1GV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.output_power == other.output_power and
                self.frequency == other.frequency
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u104", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, MODULE_ENERGY_SUB1G_V7_OUTPUT_POWER_ENC[self.output_power], MODULE_ENERGY_SUB1G_V7_FREQUENCY_ENC[self.frequency], self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u104", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.output_power = MODULE_ENERGY_SUB1G_V7_OUTPUT_POWER_DEC[d[5]]
        self.frequency = MODULE_ENERGY_SUB1G_V7_FREQUENCY_DEC[d[6]]
        self.unused0 = d[7]

class ModulePwrMgmtV10():
    def __init__(self, raw='', module_type=MODULE_PWR_MGMT, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, static_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, static_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, static_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, static_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, static_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, dynamic_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, dynamic_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, dynamic_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, dynamic_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, dynamic_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.static_leds_on = static_leds_on
        self.static_keep_alive_period = static_keep_alive_period # 5sec resolution
        self.static_keep_alive_scan = static_keep_alive_scan # 10msec resolution
        self.static_on_duration = static_on_duration # 30sec resolution
        self.static_sleep_duration = static_sleep_duration # 60sec resolution
        self.dynamic_leds_on = dynamic_leds_on
        self.dynamic_keep_alive_period = dynamic_keep_alive_period # 5sec resolution
        self.dynamic_keep_alive_scan = dynamic_keep_alive_scan # 10msec resolution
        self.dynamic_on_duration = dynamic_on_duration # 30sec resolution
        self.dynamic_sleep_duration = dynamic_sleep_duration # 60sec resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModulePwrMgmtV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.static_leds_on == other.static_leds_on and
                self.static_keep_alive_period == other.static_keep_alive_period and
                self.static_keep_alive_scan == other.static_keep_alive_scan and
                self.static_on_duration == other.static_on_duration and
                self.static_sleep_duration == other.static_sleep_duration and
                self.dynamic_leds_on == other.dynamic_leds_on and
                self.dynamic_keep_alive_period == other.dynamic_keep_alive_period and
                self.dynamic_keep_alive_scan == other.dynamic_keep_alive_scan and
                self.dynamic_on_duration == other.dynamic_on_duration and
                self.dynamic_sleep_duration == other.dynamic_sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.static_leds_on, ((self.static_keep_alive_period-0)//5), ((self.static_keep_alive_scan-0)//10), ((self.static_on_duration-0)//30), ((self.static_sleep_duration-0)//60), self.dynamic_leds_on, ((self.dynamic_keep_alive_period-0)//5), ((self.dynamic_keep_alive_scan-0)//10), ((self.dynamic_on_duration-0)//30), ((self.dynamic_sleep_duration-0)//60), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.static_leds_on = d[5]
        self.static_keep_alive_period = ((d[6]*5)+0)
        self.static_keep_alive_scan = ((d[7]*10)+0)
        self.static_on_duration = ((d[8]*30)+0)
        self.static_sleep_duration = ((d[9]*60)+0)
        self.dynamic_leds_on = d[10]
        self.dynamic_keep_alive_period = ((d[11]*5)+0)
        self.dynamic_keep_alive_scan = ((d[12]*10)+0)
        self.dynamic_on_duration = ((d[13]*30)+0)
        self.dynamic_sleep_duration = ((d[14]*60)+0)
        self.unused0 = d[15]

class ModulePwrMgmtV9():
    def __init__(self, raw='', module_type=MODULE_PWR_MGMT, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, static_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, static_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, static_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, static_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, static_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, dynamic_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, dynamic_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, dynamic_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, dynamic_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, dynamic_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.static_leds_on = static_leds_on
        self.static_keep_alive_period = static_keep_alive_period # 5sec resolution
        self.static_keep_alive_scan = static_keep_alive_scan # 10msec resolution
        self.static_on_duration = static_on_duration # 30sec resolution
        self.static_sleep_duration = static_sleep_duration # 60sec resolution
        self.dynamic_leds_on = dynamic_leds_on
        self.dynamic_keep_alive_period = dynamic_keep_alive_period # 5sec resolution
        self.dynamic_keep_alive_scan = dynamic_keep_alive_scan # 10msec resolution
        self.dynamic_on_duration = dynamic_on_duration # 30sec resolution
        self.dynamic_sleep_duration = dynamic_sleep_duration # 60sec resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModulePwrMgmtV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.static_leds_on == other.static_leds_on and
                self.static_keep_alive_period == other.static_keep_alive_period and
                self.static_keep_alive_scan == other.static_keep_alive_scan and
                self.static_on_duration == other.static_on_duration and
                self.static_sleep_duration == other.static_sleep_duration and
                self.dynamic_leds_on == other.dynamic_leds_on and
                self.dynamic_keep_alive_period == other.dynamic_keep_alive_period and
                self.dynamic_keep_alive_scan == other.dynamic_keep_alive_scan and
                self.dynamic_on_duration == other.dynamic_on_duration and
                self.dynamic_sleep_duration == other.dynamic_sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.static_leds_on, ((self.static_keep_alive_period-0)//5), ((self.static_keep_alive_scan-0)//10), ((self.static_on_duration-0)//30), ((self.static_sleep_duration-0)//60), self.dynamic_leds_on, ((self.dynamic_keep_alive_period-0)//5), ((self.dynamic_keep_alive_scan-0)//10), ((self.dynamic_on_duration-0)//30), ((self.dynamic_sleep_duration-0)//60), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.static_leds_on = d[5]
        self.static_keep_alive_period = ((d[6]*5)+0)
        self.static_keep_alive_scan = ((d[7]*10)+0)
        self.static_on_duration = ((d[8]*30)+0)
        self.static_sleep_duration = ((d[9]*60)+0)
        self.dynamic_leds_on = d[10]
        self.dynamic_keep_alive_period = ((d[11]*5)+0)
        self.dynamic_keep_alive_scan = ((d[12]*10)+0)
        self.dynamic_on_duration = ((d[13]*30)+0)
        self.dynamic_sleep_duration = ((d[14]*60)+0)
        self.unused0 = d[15]

class ModulePwrMgmtV8():
    def __init__(self, raw='', module_type=MODULE_PWR_MGMT, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, static_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, static_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, static_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, static_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, static_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, dynamic_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, dynamic_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, dynamic_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, dynamic_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, dynamic_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.static_leds_on = static_leds_on
        self.static_keep_alive_period = static_keep_alive_period # 5sec resolution
        self.static_keep_alive_scan = static_keep_alive_scan # 10msec resolution
        self.static_on_duration = static_on_duration # 30sec resolution
        self.static_sleep_duration = static_sleep_duration # 60sec resolution
        self.dynamic_leds_on = dynamic_leds_on
        self.dynamic_keep_alive_period = dynamic_keep_alive_period # 5sec resolution
        self.dynamic_keep_alive_scan = dynamic_keep_alive_scan # 10msec resolution
        self.dynamic_on_duration = dynamic_on_duration # 30sec resolution
        self.dynamic_sleep_duration = dynamic_sleep_duration # 60sec resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModulePwrMgmtV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.static_leds_on == other.static_leds_on and
                self.static_keep_alive_period == other.static_keep_alive_period and
                self.static_keep_alive_scan == other.static_keep_alive_scan and
                self.static_on_duration == other.static_on_duration and
                self.static_sleep_duration == other.static_sleep_duration and
                self.dynamic_leds_on == other.dynamic_leds_on and
                self.dynamic_keep_alive_period == other.dynamic_keep_alive_period and
                self.dynamic_keep_alive_scan == other.dynamic_keep_alive_scan and
                self.dynamic_on_duration == other.dynamic_on_duration and
                self.dynamic_sleep_duration == other.dynamic_sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.static_leds_on, ((self.static_keep_alive_period-0)//5), ((self.static_keep_alive_scan-0)//10), ((self.static_on_duration-0)//30), ((self.static_sleep_duration-0)//60), self.dynamic_leds_on, ((self.dynamic_keep_alive_period-0)//5), ((self.dynamic_keep_alive_scan-0)//10), ((self.dynamic_on_duration-0)//30), ((self.dynamic_sleep_duration-0)//60), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.static_leds_on = d[5]
        self.static_keep_alive_period = ((d[6]*5)+0)
        self.static_keep_alive_scan = ((d[7]*10)+0)
        self.static_on_duration = ((d[8]*30)+0)
        self.static_sleep_duration = ((d[9]*60)+0)
        self.dynamic_leds_on = d[10]
        self.dynamic_keep_alive_period = ((d[11]*5)+0)
        self.dynamic_keep_alive_scan = ((d[12]*10)+0)
        self.dynamic_on_duration = ((d[13]*30)+0)
        self.dynamic_sleep_duration = ((d[14]*60)+0)
        self.unused0 = d[15]

class ModulePwrMgmtV7():
    def __init__(self, raw='', module_type=MODULE_PWR_MGMT, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, static_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, static_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, static_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, static_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, static_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, dynamic_leds_on=PWR_MGMT_DEFAULTS_LEDS_ON, dynamic_keep_alive_period=PWR_MGMT_DEFAULTS_KEEP_ALIVE_PERIOD, dynamic_keep_alive_scan=PWR_MGMT_DEFAULTS_KEEP_ALIVE_SCAN, dynamic_on_duration=PWR_MGMT_DEFAULTS_ON_DURATION, dynamic_sleep_duration=PWR_MGMT_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.static_leds_on = static_leds_on
        self.static_keep_alive_period = static_keep_alive_period # 5sec resolution
        self.static_keep_alive_scan = static_keep_alive_scan # 10msec resolution
        self.static_on_duration = static_on_duration # 30sec resolution
        self.static_sleep_duration = static_sleep_duration # 60sec resolution
        self.dynamic_leds_on = dynamic_leds_on
        self.dynamic_keep_alive_period = dynamic_keep_alive_period # 5sec resolution
        self.dynamic_keep_alive_scan = dynamic_keep_alive_scan # 10msec resolution
        self.dynamic_on_duration = dynamic_on_duration # 30sec resolution
        self.dynamic_sleep_duration = dynamic_sleep_duration # 60sec resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModulePwrMgmtV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.static_leds_on == other.static_leds_on and
                self.static_keep_alive_period == other.static_keep_alive_period and
                self.static_keep_alive_scan == other.static_keep_alive_scan and
                self.static_on_duration == other.static_on_duration and
                self.static_sleep_duration == other.static_sleep_duration and
                self.dynamic_leds_on == other.dynamic_leds_on and
                self.dynamic_keep_alive_period == other.dynamic_keep_alive_period and
                self.dynamic_keep_alive_scan == other.dynamic_keep_alive_scan and
                self.dynamic_on_duration == other.dynamic_on_duration and
                self.dynamic_sleep_duration == other.dynamic_sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.static_leds_on, ((self.static_keep_alive_period-0)//5), ((self.static_keep_alive_scan-0)//10), ((self.static_on_duration-0)//30), ((self.static_sleep_duration-0)//60), self.dynamic_leds_on, ((self.dynamic_keep_alive_period-0)//5), ((self.dynamic_keep_alive_scan-0)//10), ((self.dynamic_on_duration-0)//30), ((self.dynamic_sleep_duration-0)//60), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u16u8u8u8u8u16u24", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.static_leds_on = d[5]
        self.static_keep_alive_period = ((d[6]*5)+0)
        self.static_keep_alive_scan = ((d[7]*10)+0)
        self.static_on_duration = ((d[8]*30)+0)
        self.static_sleep_duration = ((d[9]*60)+0)
        self.dynamic_leds_on = d[10]
        self.dynamic_keep_alive_period = ((d[11]*5)+0)
        self.dynamic_keep_alive_scan = ((d[12]*10)+0)
        self.dynamic_on_duration = ((d[13]*30)+0)
        self.dynamic_sleep_duration = ((d[14]*60)+0)
        self.unused0 = d[15]

class ModuleExtSensorsV10():
    def __init__(self, raw='', module_type=MODULE_EXT_SENSORS, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, ad_type0=0, uuid_msb0=0, uuid_lsb0=0, ad_type1=0, uuid_msb1=0, uuid_lsb1=0, sensor0_scramble=0, sensor1_scramble=0, unused1=0, unused2=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.ad_type0 = ad_type0
        self.uuid_msb0 = uuid_msb0
        self.uuid_lsb0 = uuid_lsb0
        self.ad_type1 = ad_type1
        self.uuid_msb1 = uuid_msb1
        self.uuid_lsb1 = uuid_lsb1
        self.sensor0_scramble = sensor0_scramble
        self.sensor1_scramble = sensor1_scramble
        self.unused1 = unused1
        self.unused2 = unused2
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleExtSensorsV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.ad_type0 == other.ad_type0 and
                self.uuid_msb0 == other.uuid_msb0 and
                self.uuid_lsb0 == other.uuid_lsb0 and
                self.ad_type1 == other.ad_type1 and
                self.uuid_msb1 == other.uuid_msb1 and
                self.uuid_lsb1 == other.uuid_lsb1 and
                self.sensor0_scramble == other.sensor0_scramble and
                self.sensor1_scramble == other.sensor1_scramble
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.ad_type0, self.uuid_msb0, self.uuid_lsb0, self.ad_type1, self.uuid_msb1, self.uuid_lsb1, self.sensor0_scramble, self.sensor1_scramble, self.unused1, self.unused2)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.ad_type0 = d[5]
        self.uuid_msb0 = d[6]
        self.uuid_lsb0 = d[7]
        self.ad_type1 = d[8]
        self.uuid_msb1 = d[9]
        self.uuid_lsb1 = d[10]
        self.sensor0_scramble = d[11]
        self.sensor1_scramble = d[12]
        self.unused1 = d[13]
        self.unused2 = d[14]

class ModuleExtSensorsV9():
    def __init__(self, raw='', module_type=MODULE_EXT_SENSORS, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, ad_type0=0, uuid_msb0=0, uuid_lsb0=0, ad_type1=0, uuid_msb1=0, uuid_lsb1=0, sensor0_scramble=0, sensor1_scramble=0, unused1=0, unused2=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.ad_type0 = ad_type0
        self.uuid_msb0 = uuid_msb0
        self.uuid_lsb0 = uuid_lsb0
        self.ad_type1 = ad_type1
        self.uuid_msb1 = uuid_msb1
        self.uuid_lsb1 = uuid_lsb1
        self.sensor0_scramble = sensor0_scramble
        self.sensor1_scramble = sensor1_scramble
        self.unused1 = unused1
        self.unused2 = unused2
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleExtSensorsV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.ad_type0 == other.ad_type0 and
                self.uuid_msb0 == other.uuid_msb0 and
                self.uuid_lsb0 == other.uuid_lsb0 and
                self.ad_type1 == other.ad_type1 and
                self.uuid_msb1 == other.uuid_msb1 and
                self.uuid_lsb1 == other.uuid_lsb1 and
                self.sensor0_scramble == other.sensor0_scramble and
                self.sensor1_scramble == other.sensor1_scramble
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.ad_type0, self.uuid_msb0, self.uuid_lsb0, self.ad_type1, self.uuid_msb1, self.uuid_lsb1, self.sensor0_scramble, self.sensor1_scramble, self.unused1, self.unused2)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.ad_type0 = d[5]
        self.uuid_msb0 = d[6]
        self.uuid_lsb0 = d[7]
        self.ad_type1 = d[8]
        self.uuid_msb1 = d[9]
        self.uuid_lsb1 = d[10]
        self.sensor0_scramble = d[11]
        self.sensor1_scramble = d[12]
        self.unused1 = d[13]
        self.unused2 = d[14]

class ModuleExtSensorsV8():
    def __init__(self, raw='', module_type=MODULE_EXT_SENSORS, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, ad_type0=0, uuid_msb0=0, uuid_lsb0=0, ad_type1=0, uuid_msb1=0, uuid_lsb1=0, sensor0_scramble=0, sensor1_scramble=0, unused1=0, unused2=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.ad_type0 = ad_type0
        self.uuid_msb0 = uuid_msb0
        self.uuid_lsb0 = uuid_lsb0
        self.ad_type1 = ad_type1
        self.uuid_msb1 = uuid_msb1
        self.uuid_lsb1 = uuid_lsb1
        self.sensor0_scramble = sensor0_scramble
        self.sensor1_scramble = sensor1_scramble
        self.unused1 = unused1
        self.unused2 = unused2
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleExtSensorsV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.ad_type0 == other.ad_type0 and
                self.uuid_msb0 == other.uuid_msb0 and
                self.uuid_lsb0 == other.uuid_lsb0 and
                self.ad_type1 == other.ad_type1 and
                self.uuid_msb1 == other.uuid_msb1 and
                self.uuid_lsb1 == other.uuid_lsb1 and
                self.sensor0_scramble == other.sensor0_scramble and
                self.sensor1_scramble == other.sensor1_scramble
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.ad_type0, self.uuid_msb0, self.uuid_lsb0, self.ad_type1, self.uuid_msb1, self.uuid_lsb1, self.sensor0_scramble, self.sensor1_scramble, self.unused1, self.unused2)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.ad_type0 = d[5]
        self.uuid_msb0 = d[6]
        self.uuid_lsb0 = d[7]
        self.ad_type1 = d[8]
        self.uuid_msb1 = d[9]
        self.uuid_lsb1 = d[10]
        self.sensor0_scramble = d[11]
        self.sensor1_scramble = d[12]
        self.unused1 = d[13]
        self.unused2 = d[14]

class ModuleExtSensorsV7():
    def __init__(self, raw='', module_type=MODULE_EXT_SENSORS, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, ad_type0=0, uuid_msb0=0, uuid_lsb0=0, ad_type1=0, uuid_msb1=0, uuid_lsb1=0, sensor0_scramble=0, sensor1_scramble=0, unused1=0, unused2=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.ad_type0 = ad_type0
        self.uuid_msb0 = uuid_msb0
        self.uuid_lsb0 = uuid_lsb0
        self.ad_type1 = ad_type1
        self.uuid_msb1 = uuid_msb1
        self.uuid_lsb1 = uuid_lsb1
        self.sensor0_scramble = sensor0_scramble
        self.sensor1_scramble = sensor1_scramble
        self.unused1 = unused1
        self.unused2 = unused2
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleExtSensorsV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.ad_type0 == other.ad_type0 and
                self.uuid_msb0 == other.uuid_msb0 and
                self.uuid_lsb0 == other.uuid_lsb0 and
                self.ad_type1 == other.ad_type1 and
                self.uuid_msb1 == other.uuid_msb1 and
                self.uuid_lsb1 == other.uuid_lsb1 and
                self.sensor0_scramble == other.sensor0_scramble and
                self.sensor1_scramble == other.sensor1_scramble
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.ad_type0, self.uuid_msb0, self.uuid_lsb0, self.ad_type1, self.uuid_msb1, self.uuid_lsb1, self.sensor0_scramble, self.sensor1_scramble, self.unused1, self.unused2)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u8u1u1u6u64", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.ad_type0 = d[5]
        self.uuid_msb0 = d[6]
        self.uuid_lsb0 = d[7]
        self.ad_type1 = d[8]
        self.uuid_msb1 = d[9]
        self.uuid_lsb1 = d[10]
        self.sensor0_scramble = d[11]
        self.sensor1_scramble = d[12]
        self.unused1 = d[13]
        self.unused2 = d[14]

class ModuleCustomV10():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, custom_id=CUSTOM_ID_EMPTY, custom_params=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.custom_params = custom_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomV10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.custom_params == other.custom_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u112", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.custom_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u112", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.custom_params = d[6]

class ModuleCustomV9():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, custom_id=CUSTOM_ID_EMPTY, custom_params=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.custom_params = custom_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomV9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.custom_params == other.custom_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u112", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.custom_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u112", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.custom_params = d[6]

class ModuleCustomV8():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, custom_id=CUSTOM_ID_EMPTY, custom_params=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.custom_params = custom_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomV8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.custom_params == other.custom_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u112", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.custom_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u112", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.custom_params = d[6]

class ModuleCustomV7():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, custom_id=0, custom_params=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.custom_params = custom_params
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomV7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.custom_params == other.custom_params
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u112", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.custom_params)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u112", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.custom_params = d[6]

class ModuleCustomLis2Dw12V10():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V10, seq_id=0, brg_mac=0, custom_id=CUSTOM_ID_LIS2DW12, version=LIS2DW12_DEFAULTS_CFG_PACKET_VERSION, state_threshold=LIS2DW12_DEFAULTS_STATE_THRESHOLD, wake_up_duration=LIS2DW12_DEFAULTS_WAKE_UP_DURATION, sleep_duration=LIS2DW12_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.version = version
        self.state_threshold = state_threshold # 31 [mg] resolution
        self.wake_up_duration = wake_up_duration # 3 [sec] resolution
        self.sleep_duration = sleep_duration # 5 [sec] resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomLis2Dw12V10):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.version == other.version and
                self.state_threshold == other.state_threshold and
                self.wake_up_duration == other.wake_up_duration and
                self.sleep_duration == other.sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u80", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.version, ((self.state_threshold-0)//31), ((self.wake_up_duration-0)//3), ((self.sleep_duration-0)//5), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u80", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.version = d[6]
        self.state_threshold = ((d[7]*31)+0)
        self.wake_up_duration = ((d[8]*3)+0)
        self.sleep_duration = ((d[9]*5)+0)
        self.unused0 = d[10]

class ModuleCustomLis2Dw12V9():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V9, seq_id=0, brg_mac=0, custom_id=CUSTOM_ID_LIS2DW12, version=LIS2DW12_DEFAULTS_CFG_PACKET_VERSION, state_threshold=LIS2DW12_DEFAULTS_STATE_THRESHOLD, wake_up_duration=LIS2DW12_DEFAULTS_WAKE_UP_DURATION, sleep_duration=LIS2DW12_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.version = version
        self.state_threshold = state_threshold # 31 [mg] resolution
        self.wake_up_duration = wake_up_duration # 3 [sec] resolution
        self.sleep_duration = sleep_duration # 5 [sec] resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomLis2Dw12V9):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.version == other.version and
                self.state_threshold == other.state_threshold and
                self.wake_up_duration == other.wake_up_duration and
                self.sleep_duration == other.sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u80", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.version, ((self.state_threshold-0)//31), ((self.wake_up_duration-0)//3), ((self.sleep_duration-0)//5), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u80", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.version = d[6]
        self.state_threshold = ((d[7]*31)+0)
        self.wake_up_duration = ((d[8]*3)+0)
        self.sleep_duration = ((d[9]*5)+0)
        self.unused0 = d[10]

class ModuleCustomLis2Dw12V8():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V8, seq_id=0, brg_mac=0, custom_id=CUSTOM_ID_LIS2DW12, version=LIS2DW12_DEFAULTS_CFG_PACKET_VERSION, state_threshold=LIS2DW12_DEFAULTS_STATE_THRESHOLD, wake_up_duration=LIS2DW12_DEFAULTS_WAKE_UP_DURATION, sleep_duration=LIS2DW12_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.version = version
        self.state_threshold = state_threshold # 31 [mg] resolution
        self.wake_up_duration = wake_up_duration # 3 [sec] resolution
        self.sleep_duration = sleep_duration # 5 [sec] resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomLis2Dw12V8):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.version == other.version and
                self.state_threshold == other.state_threshold and
                self.wake_up_duration == other.wake_up_duration and
                self.sleep_duration == other.sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u80", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.version, ((self.state_threshold-0)//31), ((self.wake_up_duration-0)//3), ((self.sleep_duration-0)//5), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u80", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.version = d[6]
        self.state_threshold = ((d[7]*31)+0)
        self.wake_up_duration = ((d[8]*3)+0)
        self.sleep_duration = ((d[9]*5)+0)
        self.unused0 = d[10]

class ModuleCustomLis2Dw12V7():
    def __init__(self, raw='', module_type=MODULE_CUSTOM, msg_type=BRG_MGMT_MSG_TYPE_CFG_SET, api_version=API_VERSION_V7, seq_id=0, brg_mac=0, custom_id=CUSTOM_ID_LIS2DW12, version=LIS2DW12_DEFAULTS_CFG_PACKET_VERSION, state_threshold=LIS2DW12_DEFAULTS_STATE_THRESHOLD, wake_up_duration=LIS2DW12_DEFAULTS_WAKE_UP_DURATION, sleep_duration=LIS2DW12_DEFAULTS_SLEEP_DURATION, unused0=0):
        self.module_type = module_type
        self.msg_type = msg_type
        self.api_version = api_version
        self.seq_id = seq_id
        self.brg_mac = brg_mac
        self.custom_id = custom_id
        self.version = version
        self.state_threshold = state_threshold # 31 [mg] resolution
        self.wake_up_duration = wake_up_duration # 3 [sec] resolution
        self.sleep_duration = sleep_duration # 5 [sec] resolution
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, ModuleCustomLis2Dw12V7):
            return (
                self.module_type == other.module_type and
                self.msg_type == other.msg_type and
                self.api_version == other.api_version and
                self.brg_mac == other.brg_mac and
                self.custom_id == other.custom_id and
                self.version == other.version and
                self.state_threshold == other.state_threshold and
                self.wake_up_duration == other.wake_up_duration and
                self.sleep_duration == other.sleep_duration
            )
        return False

    def dump(self):
        string = bitstruct.pack("u4u4u8u8u48u8u8u8u8u8u80", self.module_type, self.msg_type, self.api_version, self.seq_id, self.brg_mac, self.custom_id, self.version, ((self.state_threshold-0)//31), ((self.wake_up_duration-0)//3), ((self.sleep_duration-0)//5), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u4u4u8u8u48u8u8u8u8u8u80", binascii.unhexlify(string))
        self.module_type = d[0]
        self.msg_type = d[1]
        self.api_version = d[2]
        self.seq_id = d[3]
        self.brg_mac = d[4]
        self.custom_id = d[5]
        self.version = d[6]
        self.state_threshold = ((d[7]*31)+0)
        self.wake_up_duration = ((d[8]*3)+0)
        self.sleep_duration = ((d[9]*5)+0)
        self.unused0 = d[10]

class Lis2Dw12Data():
    def __init__(self, raw='', version=LIS2DW12_PACKET_VERSION_LATEST, state=0, temperature=0, unused0=0):
        self.version = version
        self.state = state
        self.temperature = temperature # Multiplied by 100
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, Lis2Dw12Data):
            return (
                self.version == other.version and
                self.state == other.state and
                self.temperature == other.temperature
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u16u184", self.version, self.state, ((self.temperature-0)//0.01), self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u16u184", binascii.unhexlify(string))
        self.version = d[0]
        self.state = d[1]
        self.temperature = ((d[2]*0.01)+0)
        self.unused0 = d[3]

class BatterySensorData():
    def __init__(self, raw='', version=BATTERY_SENSOR_PACKET_VERSION_LATEST, power_source=0, battery_level=0, unused0=0):
        self.version = version
        self.power_source = power_source
        self.battery_level = battery_level # In [mV]
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, BatterySensorData):
            return (
                self.version == other.version and
                self.power_source == other.power_source and
                self.battery_level == other.battery_level
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u16u184", self.version, self.power_source, self.battery_level, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u16u184", binascii.unhexlify(string))
        self.version = d[0]
        self.power_source = d[1]
        self.battery_level = d[2]
        self.unused0 = d[3]

class PofData():
    def __init__(self, raw='', version=POF_DATA_PACKET_VERSION_LATEST, power_source=0, voltage_thr=0, unused0=0):
        self.version = version
        self.power_source = power_source
        self.voltage_thr = voltage_thr
        self.unused0 = unused0
        if raw:
            self.set(raw)

    def __eq__(self, other):
        if isinstance(other, PofData):
            return (
                self.version == other.version and
                self.power_source == other.power_source and
                self.voltage_thr == other.voltage_thr
            )
        return False

    def dump(self):
        string = bitstruct.pack("u8u8u16u184", self.version, self.power_source, self.voltage_thr, self.unused0)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u8u8u16u184", binascii.unhexlify(string))
        self.version = d[0]
        self.power_source = d[1]
        self.voltage_thr = d[2]
        self.unused0 = d[3]

MODULES_LIST = [ModuleIfV10, ModuleIfV9, ModuleIfV8, ModuleIfV7, ModuleCalibrationV10, ModuleCalibrationV9, ModuleCalibrationV8, ModuleCalibrationV7, ModuleDatapathV10, ModuleDatapathV9, ModuleDatapathV8, ModuleDatapathV7, ModuleEnergy2400V10, ModuleEnergy2400V9, ModuleEnergy2400V8, ModuleEnergy2400V7, ModuleEnergySub1GV10, ModuleEnergySub1GV9, ModuleEnergySub1GV8, ModuleEnergySub1GV7, ModulePwrMgmtV10, ModulePwrMgmtV9, ModulePwrMgmtV8, ModulePwrMgmtV7, ModuleExtSensorsV10, ModuleExtSensorsV9, ModuleExtSensorsV8, ModuleExtSensorsV7, ModuleCustomV10, ModuleCustomV9, ModuleCustomV8, ModuleCustomV7]
MODULES_DICT = {MODULE_IF:'ModuleIfV', MODULE_CALIBRATION:'ModuleCalibrationV', MODULE_DATAPATH:'ModuleDatapathV', MODULE_ENERGY_2400:'ModuleEnergy2400V', MODULE_ENERGY_SUB1G:'ModuleEnergySub1GV', MODULE_PWR_MGMT:'ModulePwrMgmtV', MODULE_EXT_SENSORS:'ModuleExtSensorsV', MODULE_CUSTOM:'ModuleCustomV'}
ACTIONS_DICT = {ACTION_EMPTY:'ActionGenericV', ACTION_GW_HB:'ActionGwHbV', ACTION_REBOOT:'ActionRebootV', ACTION_BLINK:'ActionBlinkV', ACTION_GET_MODULE:'ActionGetModuleV', ACTION_RESTORE_DEFAULTS:'ActionRestoreDefaultsV', ACTION_SEND_HB:'ActionSendHbV', ACTION_GET_BATTERY_SENSOR:'ActionGetBatterySensorV', ACTION_GET_POF_DATA:'ActionGetPofDataV'}
WLT_PKT_TYPES = [UnifiedEchoPkt, ActionGenericV10, ActionGenericV9, ActionGenericV8, ActionGenericV7, ActionGwHbV10, ActionGwHbV9, ActionGwHbV8, ActionRebootV10, ActionRebootV9, ActionRebootV8, ActionBlinkV10, ActionBlinkV9, ActionBlinkV8, ActionGetModuleV10, ActionGetModuleV9, ActionGetModuleV8, ActionRestoreDefaultsV10, ActionRestoreDefaultsV9, ActionRestoreDefaultsV8, ActionSendHbV10, ActionSendHbV9, ActionSendHbV8, ActionGetBatterySensorV10, ActionGetBatterySensorV9, ActionGetBatterySensorV8, ActionGetPofDataV10, ActionGetPofDataV9, ActionGetPofDataV8, Brg2BrgOtaV10, Brg2BrgOtaV9, Brg2BrgCfgV10, Brg2BrgCfgV9, Gw2BrgCfgV8, Gw2BrgCfgV7, Brg2GwCfgV8, Brg2GwCfgV7, Brg2GwCfgV6, Brg2GwCfgV5, Brg2GwCfgV2, Brg2GwHbV10, Brg2GwHbV9, Brg2GwHbV8, Brg2GwHbV7, Brg2GwHbV6, Brg2GwHbV5, Brg2GwHbV1, SideInfo, SideInfoSensor, ModuleIfV10, ModuleIfV9, ModuleIfV8, ModuleIfV7, ModuleCalibrationV10, ModuleCalibrationV9, ModuleCalibrationV8, ModuleCalibrationV7, ModuleDatapathV10, ModuleDatapathV9, ModuleDatapathV8, ModuleDatapathV7, ModuleEnergy2400V10, ModuleEnergy2400V9, ModuleEnergy2400V8, ModuleEnergy2400V7, ModuleEnergySub1GV10, ModuleEnergySub1GV9, ModuleEnergySub1GV8, ModuleEnergySub1GV7, ModulePwrMgmtV10, ModulePwrMgmtV9, ModulePwrMgmtV8, ModulePwrMgmtV7, ModuleExtSensorsV10, ModuleExtSensorsV9, ModuleExtSensorsV8, ModuleExtSensorsV7, ModuleCustomV10, ModuleCustomV9, ModuleCustomV8, ModuleCustomV7, ModuleCustomLis2Dw12V10, ModuleCustomLis2Dw12V9, ModuleCustomLis2Dw12V8, ModuleCustomLis2Dw12V7]