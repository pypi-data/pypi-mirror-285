from argparse import ArgumentParser
import datetime
import logging
import os
from wiliot_deployment_tools.common.analysis_data_bricks import initialize_logger

from wiliot_deployment_tools.interface.mqtt import MqttClient
from wiliot_core.utils.utils import WiliotDir

class MqttListener(MqttClient):
    def __init__(self, gw_id, owner_id, logger_filepath=None, topic_suffix=''):
        # Runtime
        self.env_dirs = WiliotDir()
        self.current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.mqtt_listener_dir = os.path.join(self.env_dirs.get_wiliot_root_app_dir(), 'mqtt_listener', self.current_datetime)
        self.env_dirs.create_dir(self.mqtt_listener_dir)
        self.mqtt_logger_filepath = os.path.join(self.mqtt_listener_dir, f'{self.current_datetime}_mqtt.log')
        super().__init__(gw_id, owner_id, self.mqtt_logger_filepath, topic_suffix)
        logging.getLogger('mqtt').addHandler(logging.StreamHandler())
        
    def listen(self):
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
        finally:
            print('MQTT Listener stopped')
            self.client.disconnect()
            self.client.loop_stop()

def main():
    parser = ArgumentParser(prog='wlt-mqtt',
                            description='MQTT Listener - CLI Tool to listen to Wiliot topics on external MQTT Broker')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-owner', type=str, help="Owner ID", required=True)
    required.add_argument('-gw', type=str, help="Gateway ID", required=True)
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-suffix', type=str, help="Topic suffix", default='', required=False)
    args = parser.parse_args()
    topic_suffix = '' if args.suffix == '' else '-'+args.suffix
    mqtt = MqttListener(gw_id=args.gw, owner_id=args.owner, topic_suffix=topic_suffix)
    mqtt.listen()

def main_cli():
    main()

if __name__ == '__main__':
    main()
    