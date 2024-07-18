import pprint
from wiliot_deployment_tools.api.extended_api import AndroidGatewayAction, ExtendedEdgeClient
from argparse import ArgumentParser
from wiliot_core import check_user_config_is_ok
import colorama

def main():
    parser = ArgumentParser(prog='wlt-log',
                            description='Log Viewer - CLI Tool to view Wiliot Gateway logs')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-owner', type=str, help="Owner ID", required=True)
    required.add_argument('-gw', type=str, help="Gateway ID", required=True)
    parser.add_argument('-test', action='store_true',
                    help='If flag used, use test environment (prod is used by default)')
    parser.add_argument('--mobile_ble_logging', choices=['on', 'off'], help='set mobile BLE logging to on or off')
    
    args = parser.parse_args()
    if args.test:
        env = 'test'
    else:
        env = 'prod'

    owner_id = args.owner
    conf_env = env if env == 'prod' else 'non-prod'
    user_config_file_path, api_key, is_success = check_user_config_is_ok(owner_id, conf_env, 'edge')
    if is_success:
        print('credentials saved/upload from {}'.format(user_config_file_path))
    else:
        raise Exception('invalid credentials - please try again to login')

    colorama.init()

    e = ExtendedEdgeClient(api_key, args.owner, env)
    if args.mobile_ble_logging is not None:
        print(colorama.Fore.LIGHTBLACK_EX, end=None)
        print(colorama.Fore.GREEN +
          f'---Setting mobile BLE Logging {args.gw} to {args.mobile_ble_logging}---' + colorama.Style.RESET_ALL)        
        mode = {'on': AndroidGatewayAction.ENABLE_BLE_LOGS, 'off': AndroidGatewayAction.DISABLE_BLE_LOGS}
        res = e.send_action_to_gateway(args.gw, mode[args.mobile_ble_logging])
        print({args.gw: res})
    else:
        print(colorama.Fore.LIGHTBLACK_EX, end=None)
        print(colorama.Fore.GREEN +
            f'---Printing info for {args.gw}---' + colorama.Style.RESET_ALL)
        print(colorama.Style.RESET_ALL)
        try:
            print_gw(e, args.gw)
        except AttributeError as e:
            print(e)

def print_gw(e, gw):
    info = e.get_gateway_info(gw)

    print(colorama.Fore.GREEN +
        f'---Gateway Info---' + colorama.Style.RESET_ALL)
    pprint.pprint(info)
    print()
    print(colorama.Fore.GREEN +
        f'---Gateway Logs---' + colorama.Style.RESET_ALL)
    e.print_gateway_logs(gw)
    
def main_cli():
    main()


if __name__ == '__main__':
    main()
