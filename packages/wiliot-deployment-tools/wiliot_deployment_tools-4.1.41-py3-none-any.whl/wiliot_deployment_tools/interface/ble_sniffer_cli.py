from argparse import ArgumentParser
import datetime
import os
import time
from wiliot_core.utils.utils import WiliotDir
from wiliot_deployment_tools.interface.ble_sniffer import BLESniffer
from wiliot_deployment_tools.interface.uart_if import UARTInterface
from wiliot_deployment_tools.interface.uart_ports import get_uart_ports

def main():
    parser = ArgumentParser(prog='wlt-sniffer',
                            description='BLE Sniffer - CLI Tool to Sniff BLE Packets')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-p', type=str, required=True, help=f'UART Port. Available ports: {str(get_uart_ports())}')
    required.add_argument('-c', type=int, help="channel", required=True, choices=[37, 38, 39])

    env_dirs = WiliotDir()
    current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    sniffer_dir = os.path.join(env_dirs.get_wiliot_root_app_dir(), 'ble-sniffer', current_datetime)
    env_dirs.create_dir(sniffer_dir)
    start_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    sniffer_logger_filepath = os.path.join(sniffer_dir, f'{start_timestamp}_sniffer.log')

    
    args = parser.parse_args()
    uart = UARTInterface(args.p, update_fw=True)
    sniffer = BLESniffer(uart, print_pkt=True, logger_filepath=sniffer_logger_filepath)
    sniffer.start_sniffer(args.c)
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            sniffer.stop_sniffer()
            break
        
def main_cli():
    main()


if __name__ == '__main__':
    main()
