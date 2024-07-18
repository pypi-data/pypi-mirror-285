# External Imports
import time
import datetime
import os
from typing import Literal
import webbrowser
from jinja2 import Environment, FileSystemLoader
import pkg_resources
import time

# Internal Imports
from wiliot_deployment_tools.common.analysis_data_bricks import initialize_logger
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_core.utils.utils import WiliotDir
from wiliot_deployment_tools.interface.ble_sniffer import BLESniffer
from wiliot_deployment_tools.interface.uart_if import UARTError, UARTInterface
from wiliot_deployment_tools.interface.ble_simulator import BLESimulator
from wiliot_deployment_tools.interface.mqtt import MqttClient
from wiliot_deployment_tools.gw_certificate.tests import *
from wiliot_deployment_tools.interface.uart_ports import get_uart_ports
from wiliot_deployment_tools.gw_certificate.api_if.gw_capabilities import GWCapabilities
class GWCertificateError(Exception):
    pass


class TemplateEngine:
    def __init__(self):
        self.template_dir = pkg_resources.resource_filename(__name__, 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def get_template(self, template_name):
        return self.env.get_template(template_name)

    def render_template(self, template_name, **kwargs):
        template = self.get_template(template_name)
        return template.render(**kwargs)


class GWCertificate:
    def __init__(self, gw_id, owner_id, tests:list = [], topic_suffix=''):
        # Runtime
        self.env_dirs = WiliotDir()
        self.current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.certificate_dir = os.path.join(self.env_dirs.get_wiliot_root_app_dir(), 'gw-certificate', self.current_datetime)
        self.env_dirs.create_dir(self.certificate_dir)
        self.start_timestamp = initialize_logger(self.certificate_dir)
        self.logger_filepath = os.path.join(self.certificate_dir, f'{self.start_timestamp}.log')
        self.mqtt_logger_filepath = os.path.join(self.certificate_dir, f'{self.start_timestamp}_mqtt.log')
        self.sniffer_logger_filepath = os.path.join(self.certificate_dir, f'{self.start_timestamp}_sniffer.log')
        self.result_html_path = os.path.join(self.certificate_dir, f'results_{self.current_datetime}.html')
        self.template_engine = TemplateEngine()

        # Version 
        self.gw_cert_version = "1.1.0"
        
        # GW-related
        self.gw_id = gw_id
        self.owner_id = owner_id
        self.topic_suffix = topic_suffix
        self.mqttc = MqttClient(gw_id, owner_id, self.mqtt_logger_filepath, topic_suffix=topic_suffix)
        self.gw_capabilities = GWCapabilities()
        
        # UART-related
        self.uart_comports = get_uart_ports()
        debug_print(f'UART Ports:{self.uart_comports}')
        if len(self.uart_comports) < 1:
            raise GWCertificateError('A Wiliot tester board must be connected to USB!')
        self.uart = None
        
        for port in self.uart_comports:
            try:
                # TODO Fix UARTInterface firmware update and then call it with the flag set to True
                self.uart = UARTInterface(port, update_fw=True)
                break
            except UARTError as e:
                debug_print(f'Port: {port} - {e}')
        if type(self.uart) is not UARTInterface:
            raise GWCertificateError("Cannot initialize any port!")
        self.ble_sim = BLESimulator(self.uart)
        self.sniffer = BLESniffer(self.uart, logger_filepath=self.sniffer_logger_filepath)
        
        tests_to_init = TESTS if tests == [] else tests
        # Tests
        self.tests = [t(**self.__dict__) for t in tests_to_init]
        debug_print(f'Running Tests: {self.tests}')
    
    def run_tests(self):
        debug_print("Sleeping 20 seconds after mqtt connect")
        time.sleep(20)

        # capabilities_received = ConnectionTest in self.tests
        for test in self.tests:
            # if capabilities_received:
            #     if (type(test) == DownlinkTest and self.gw_capabilities.downlinkSupported == False):
            #         debug_print(f'# Skipping {type(test)} since it is not a supported capability. #')
            #         continue
            test.run()
            test.end_test()
        
    def create_results_html(self):
        with open(self.logger_filepath, 'r') as f:
            log = f.read().split('\n')
        with open(self.mqtt_logger_filepath, 'r') as f:
            mqtt_log = f.read().split('\n')
        with open(self.sniffer_logger_filepath, 'r') as f:
            sniffer_log = f.read().split('\n')

        
        html = self.template_engine.render_template('results.html', tests=self.tests,
                                                    log = log,
                                                    mqtt_log = mqtt_log,
                                                    sniffer_log = sniffer_log,
                                                    gw_id = self.gw_id,
                                                    version = self.gw_cert_version,
                                                    datetime = self.current_datetime)
        with open(self.result_html_path, 'w', encoding="utf-8") as f:
            f.write(html)
        debug_print("Test Finished. Results HTML Saved: " + self.result_html_path)
        webbrowser.open('file://' + os.path.realpath(self.result_html_path))

if __name__ == "__main__":
    from api_secrets import *
    gw_id = 'gw_id'
    owner_id = 'owner_id'
    gwc = GWCertificate(gw_id=gw_id,owner_id=owner_id, topic_suffix='-test', tests=[ConnectionTest,])
    gwc.run_tests()
    gwc.create_results_html()