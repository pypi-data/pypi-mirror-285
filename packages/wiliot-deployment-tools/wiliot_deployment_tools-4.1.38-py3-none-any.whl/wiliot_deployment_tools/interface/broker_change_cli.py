from argparse import ArgumentParser
import time
from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient
from wiliot_core import check_user_config_is_ok
from wiliot_deployment_tools.common.debug import debug_print

from wiliot_deployment_tools.interface.mqtt import MqttClient

def main(arguments):
    parser = ArgumentParser(prog='wlt-broker-change',
                            description='Wiliot Broker Change - Change MQTT broker for Wiliot GWs')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-broker', type=str, help="Broker to change to", choices=['wiliot', 'hivemq'], required=True)
    required.add_argument('-owner', type=str, help="Owner ID", required=True)
    required.add_argument('-gw', type=str, help="Gateway ID", required=True)
    required.add_argument('-env', choices=['prod', 'test', 'dev'], help='Environment', required=False, default='prod')
    required.add_argument('-cloud', choices=['aws', 'gcp'], help='Wiliot Cloud', required=False, default='aws')
    required.add_argument('-legacy', action='store_true', help='Legacy Broker Change')
    optional.add_argument('-suffix', type=str, help="Topic suffix", default='', required=False)

    args = parser.parse_args(args=arguments)
    owner_id = args.owner
    env = args.env
    conf_env = env if env == 'prod' else 'non-prod'
    user_config_file_path, api_key, is_success = check_user_config_is_ok(owner_id, conf_env, 'edge')
    if is_success:
        print('credentials saved/upload from {}'.format(user_config_file_path))
    else:
        raise Exception('invalid credentials - please try again to login')
    
    mqtt_mode = 'legacy' if args.legacy else 'automatic'
    
    if args.broker == 'wiliot':
        topic_suffix = '' if args.suffix == '' else '-'+args.suffix
        mqtt = MqttClient(args.gw, owner_id, topic_suffix=topic_suffix)
        mqtt.exit_custom_mqtt(mqtt_mode=mqtt_mode)
        debug_print(f'Broker for {args.gw} changed to Wiliot')
    elif args.broker == 'hivemq':
        edge = ExtendedEdgeClient(api_key=api_key, owner_id=owner_id, env=env, cloud=args.cloud)
        edge.enter_custom_mqtt(gateway_id=args.gw, mqtt_mode=mqtt_mode)
        debug_print(f'Broker for {args.gw} changed to HiveMQ')
    
def main_cli():
    main()
    
if __name__ == '__main__':
    args = [
        '-broker', 'hivemq',
        '-owner', '529063429343',
        '-gw', 'GW0CDC7EDB09AC',
        '-env', 'test',
        '-cloud', 'aws',
        '-legacy',
        '-suffix', 'test'
    ]
    main(args)