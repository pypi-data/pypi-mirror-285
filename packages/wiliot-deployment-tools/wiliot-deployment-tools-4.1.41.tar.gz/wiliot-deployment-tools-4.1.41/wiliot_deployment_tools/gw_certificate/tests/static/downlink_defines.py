SANITY_STAGE = "SanityStage"
CORRELATION_STAGE = "CorrelationStage"
STAGE_CONFIGS = {
    SANITY_STAGE:([i for i in range(700, 901, 100)], range(3)),
    CORRELATION_STAGE:([i for i in range(100, 2001, 400)], range(3))}
TX_MAX_DURATIONS = range(100, 501, 100)
RETRIES = range(5)
MAX_RX_TX_PERIOD_SECS = 0.255
DEFAULT_BRG_ID = "FFFFFFFFFFFF"