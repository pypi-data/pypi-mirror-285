import datetime
import os
from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.gw_certificate.api_if.gw_capabilities import GWCapabilities
from wiliot_deployment_tools.interface.ble_simulator import BLESimulator
from wiliot_deployment_tools.interface.if_defines import SEP
from wiliot_deployment_tools.interface.mqtt import MqttClient

PASS_STATUS = {True: 'PASS', False: 'FAIL'}

# Score values for pass/inconclusive/fail
PERFECT_SCORE = 100
PASS_MINIMUM = 80
INCONCLUSIVE_MINIMUM = 70
INIT_INCONCLUSIVE_MINIMUM = 40
MINIMUM_SCORE = 0

# Results indications for stages. Must always be synced with frontend. 
# 'score' shows as pass/inconclusive/fail. 'info' shows as info/warning.
SCORE_BASED = 'score'
INFORMATIVE = 'info'

class PassCriteria():
    def __init__(self):
        pass
        
    @staticmethod
    def to_string(pass_value:int) -> str:
        if pass_value >= PASS_MINIMUM:
            return 'Pass'
        elif pass_value >= INCONCLUSIVE_MINIMUM:
            return 'Inconclusive'
        else:
            return 'Fail'

    @staticmethod
    def missing_score(pass_value:int) -> int:
        return PERFECT_SCORE - pass_value

    @staticmethod
    def calc_for_stage_uplink(pass_value:int, stage_name:str) -> int:
        error_msg = "Insufficient amount of packets were scanned & uploaded by the gateway"
        return pass_value, error_msg

    @staticmethod
    def calc_for_stage_stress(pass_value: int, stage_name:str) -> int:
        return pass_value
    
    @staticmethod
    def calc_for_stage_downlink(rsquared, slope, stage_name:str):
        error_msg = ''
        if 'Sanity' in stage_name:
            if rsquared > 0:
                return PERFECT_SCORE, error_msg
            else:
                error_msg = 'No advertisements were received from the gateway.'
                return MINIMUM_SCORE, error_msg
        else:
            if rsquared > 0.8 and slope > 0.7:
                return PERFECT_SCORE, error_msg
            elif rsquared > 0.5 and slope > 0:
                error_msg = "The correlation between 'txMaxDuration' and the board advertisements is suboptimal."
                return INCONCLUSIVE_MINIMUM, error_msg
            else:
                error_msg = "The correlation between 'txMaxDuration' and the board advertisements is weak."
                return MINIMUM_SCORE, error_msg

    @staticmethod
    def calc_for_test(test_pass_value:int, stage) -> int:
        if stage.stage_pass < test_pass_value:
            if 'Geolocation' in stage.stage_name or 'info' in stage.result_indication:
                return test_pass_value
            else:
                return stage.stage_pass
        else:
            return test_pass_value


class GenericTest:
    def __init__(self, mqttc: MqttClient, ble_sim: BLESimulator, 
                 gw_capabilities:GWCapabilities, gw_id, owner_id, test_name, **kwargs):
        # Clients
        self.mqttc = mqttc
        self.ble_sim = ble_sim
        
        # Test-Related
        self.gw_capabilities = gw_capabilities
        self.report = ''
        self.report_html = ''
        self.test_pass = MINIMUM_SCORE
        self.pass_min = PASS_MINIMUM
        self.inconclusive_min = INCONCLUSIVE_MINIMUM
        self.start_time = None
        self.test_name = test_name
        self.test_dir = os.path.join(self.certificate_dir, self.test_name)
        self.env_dirs.create_dir(self.test_dir)
        self.stages = []
        self.test_tooltip = kwargs.get('test_tooltip', 'Missing tooltip')
        self.result_indication = kwargs.get('result_indication', SCORE_BASED)
        
    def __repr__(self):
        return self.test_name
    
    def run(self):
        self.start_time = datetime.datetime.now()
        debug_print(f"Starting Test {self.test_name} : {self.start_time}")
        
    def runtime(self):
        return datetime.datetime.now() - self.start_time
    
    def add_to_test_report(self, report):
        self.report += '\n' + report
    
    def create_test_html(self):
        self.report_html = self.template_engine.render_template('test.html', test=self,
                                                                running_time = self.runtime())
    
    def end_test(self):
        self.create_test_html()

class GenericStage():
    def __init__(self, stage_name, **kwargs):
        #Stage Params
        self.stage_name = stage_name
        self.result_indication = kwargs.get('result_indication', SCORE_BASED)
        self.stage_pass = MINIMUM_SCORE
        self.pass_min = kwargs.get('pass_min', PASS_MINIMUM)
        self.inconclusive_min = INCONCLUSIVE_MINIMUM
        self.report = ''
        self.report_html = ''
        self.start_time = None
        self.csv_path = os.path.join(self.test_dir, f'{self.stage_name}.csv')
        self.stage_tooltip = kwargs.get('stage_tooltip', 'Missing tooltip')
        self.error_summary = ''
        
    def __repr__(self):
        return self.stage_name
    
    def prepare_stage(self):
        debug_print(f'### Starting Stage: {self.stage_name}')

    def add_to_stage_report(self, report):
        self.report += f'{report}\n'
    
    def generate_stage_report(self):
        return self.report
