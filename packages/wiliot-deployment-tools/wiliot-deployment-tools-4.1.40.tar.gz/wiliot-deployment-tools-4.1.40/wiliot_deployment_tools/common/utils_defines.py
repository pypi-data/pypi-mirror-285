# Brownout / OTA Defines
SEP = "#" * 50
MINUTES_TO_BROWN_OUT = 5
TABLES_SYNC_MINUTES = 70
MINUTES_FOR_LC = 2
LATEST_FW = "1.9.0"
SINGLE_BAT_BO_DICT = {"2.4GhzOutputPower": 2, 'txPeriodMs': 75, 'rxTxPeriodMs': 255, 'energyPattern': 25}
DUAL_BAT_BO_DICT = {"2.4GhzOutputPower": 2, 'txPeriodMs': 75, 'rxTxPeriodMs': 255, 'energyPattern': 50}
LEGACY_BO_DICT = {'energyPattern': 17, 'rxTxPeriodMs': 99}
# BO_DICT_PREV = {'energyPattern': 36}
BO_DICT = {
    'datapath': {'config': {'pktFilter': 'Disable forwarding'}},
    'energy2400': {'config': {'energyPattern2400': 'No Energizing'}},
    'energySub1g': {'config': {'sub1gEnergyPattern': 'No Energizing'}},
    'calibration': {'config': {'calibPattern': 'Disable calibration beaconing'}}
}


# Configuration tool / change Brg/Gw Defines
ATC_GW_CONFIG = {
    'wifi': {'gwDataSrc': 'Bridges only (ch38)',
             'pacerInterval': 60,
             'txPeriodMs': 3,
             'rxTxPeriodMs': 90,
             'energizingPattern': 17,
             "2.4GhzOutputPower": 8},
    'lte': {},
    'mobile': {},
    'unknown': {}}
ATC_REGION_DICT = {
    'IL': {
        'sub1GhzFrequency': 919100,
        'energyPattern': 50
    }
}

energy_patterns = [18, 25, 26]
energy_patterns_db = {17: 50, 18: 51, 25: 56, 26: 57}
gw_rx_channel = {17: "Bridges only (ch39)", 18: "Bridges only (ch38)", 24: "Bridges only (ch39)",
                 25: "Bridges only (ch39)", 26: "Bridges only (ch39)", 51: "Bridges only (ch38)",
                 55: "Bridges only (ch39)", 56: "Bridges only (ch39)", 57: "Bridges only (ch39)",
                 50: "Bridges only (ch39)"}
shifted_brg_energy_patterns = [33, 34, 35, 58, 59, 60]
shifted_gw_energizing_patterns = [33]
lc_output_powers = [14, 17, 20, 23, 26, 29, 32]
fp_duty_cycles = [0.1, 0.15, 0.2, 0.25, 0.3]

# Power Mgmt
EXIT_POWER_MGMT_GW_DICT = {
    'gwDataSrc': gw_rx_channel[17],
    'txPeriodMs': 3,
    'rxTxPeriodMs': 15,
    'energizingPattern': 17,
    'gwMgmtMode': 'active'
}
KEEP_ALIVE_PERIOD = 30  # seconds
KEEP_ALIVE_SCAN_DURATION = 300  # in millisecond
SEC_TO_SEND = 2
BROADCAST_DST_MAC = 'FFFFFFFFFFFF'

colors = ['red', 'blue', 'yellow', 'cyan', 'green', 'brown', 'orange', 'pink', 'purple', 'black']

# Test Tool
WH_OWNER = '832742983939'
INIT_GW_CONFIG = {
    'wifi':{'gwDataSrc': gw_rx_channel[18],
            'gwDataMode': gw_rx_channel[18]},
    'lte':{},
    'mobile':{},
    'unknown':{}}
INIT_BRG_CONFIG = {
	'calibration': {'config': {'calibPattern': 'Disable calibration beaconing', 'calibInterval': 10, 'calibOutputPower': 2}},
    'externalSensor': {'config': {'adType0': 0, 'adType1': 0, 'uuidLsb0': 0, 'uuidLsb1': 0, 'uuidMsb0': 0, 'uuidMsb1': 0, 'sensor0Scramble': 0, 'sensor1Scramble': 0}},
    'energy2400': {'config': {'dutyCycle': 30, 'outputPower': 2, 'energyPattern2400': 'No Energizing'}},
    'datapath': {'config': {'pktFilter': 'Disable forwarding', 'txRepetition': 0, 'adaptivePacer': 0, 'pacerInterval': 15, 'unifiedEchoPkt': 0, 'commOutputPower': 2, 'globalPacingGroup': 0}},
    'powerManagement': {'config': {'staticLedsOn': 1, 'dynamicLedsOn': 1, 'staticOnDuration': 0, 'dynamicOnDuration': 0, 'staticKeepAliveScan': 300, 'staticSleepDuration': 0, 'dynamicKeepAliveScan': 300, 'dynamicSleepDuration': 0, 'staticKeepAlivePeriod': 20, 'dynamicKeepAlivePeriod': 20}},
    'energySub1g': {'config': {'cycle': 15, 'dutyCycle': 30, 'outputPower': 29, 'sub1gEnergyPattern': 'No Energizing'}},
    }

# prev init cfg for prev brgs version (lower then version 4.0)
INIT_BRG_PREV_CONFIG = {
	'energy2400': {'config': {'txPeriod': 5, 'rxTxPeriod': 15, 'outputPower': 2, 'energyPattern': 36}},
	'datapath': {'config': {'txRepetition': 0, 'pacerInterval': 15, 'globalPacingGroup': 0}}, 
	'energySub1g': {'config': {'frequency': 919100, 'outputPower': 32}}
    }

BRG_KEYS = ['calibPattern','calibInterval','calibOutputPower',
            'adType0','adType1','uuidLsb0','uuidLsb1','uuidMsb0','uuidMsb1','sensor0Scramble','sensor1Scramble',
            'txPeriod','rxTxPeriod','2.4GhzOutputPower','energyPattern','sub1GhzFrequency','sub1GhzOutputPower',
            'dutyCycle','outputPower','energyPattern2400','pktFilter','txRepetition','adaptivePacer','pktTypesMask',
            'pacerInterval','unifiedEchoPkt','commOutputPower','globalPacingGroup',
            'staticLedsOn','dynamicLedsOn','staticOnDuration','dynamicOnDuration','staticKeepAliveScan','staticSleepDuration',
            'dynamicKeepAliveScan','dynamicSleepDuration','staticKeepAlivePeriod','dynamicKeepAlivePeriod',
            'cycle','dutyCycle','outputPower','sub1gEnergyPattern']
BRG_LOC_SIM_KEYS = ['X','Y','Z','brgDirectionX','brgDirectionY','brgDirectionZ','bridgeId','boardType']
BRG_KEYS_REQ = ['calibInterval','sub1GhzOutputPower','dutyCycle','pacerInterval','boardType','brgDirectionX','brgDirectionY','brgDirectionZ']
BRG_KEYS_OPTIONAL = ['commPattern','calibPattern','txRepetition']
BRG_KEYS_ALL = list(set(BRG_LOC_SIM_KEYS + BRG_KEYS_REQ + BRG_KEYS_OPTIONAL))
GW_KEYS = ['gwDataSrc', 'gwDataMode']
GW_KEYS = ['gwDataSrc', 'gwDataMode']
TAGS_SIM_KEYS_OPTIONAL = ['shadowing','speed','radius','center_x','center_y','center_z','rec_cor1','rec_cor2','rec_cor3','rec_cor4']
TAGS_SIM_KEYS_REQ = ['tags_in_group','tagDirection','tagNormal']
TEST_TAGS_SIM_KEYS_REQ = ['x_location','y_location','z_location','tagNormal','tagDirection']
TAGS_SIM_KEYS = list(set(TAGS_SIM_KEYS_REQ + TAGS_SIM_KEYS_OPTIONAL))
TEST_TAGS_SIM_KEYS = list(set(TEST_TAGS_SIM_KEYS_REQ + TAGS_SIM_KEYS_OPTIONAL))
WALLS_SIM_KEYS = ['wall_id','x_start','x_end','y_start','y_end']
GW_DATA_SRC = 'gwDataSrc'
GW_DATA_MODE = 'gwDataMode'
GW_KEYS_THIN = ['dataCoupling', 'useStaticLocation', 'gwMgmtMode']
GW_SHARED_KEYS = ['gw_2.4GhzOutputPower', 'gw_txPeriodMs', 'gw_pacerInterval', 'gw_energizingPattern',
                  'gw_rxTxPeriodMs']
TIME_COLUMNS = ['endTimestamp', 'startTimestamp', 'receivedTestConfigTimestamp']
TEST_CONFIG_COLUMNS = ['testId', 'testTimeMins', 'gatewaysIncluded', 'bridgesIncluded']
