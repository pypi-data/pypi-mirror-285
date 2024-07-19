import datetime
import subprocess
import serial
import serial.tools.list_ports
import time
import os.path
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.interface.if_defines import *
from packaging import version
import pkg_resources

LATEST_VERSION = '4.2.115'
LATEST_VERSION_FILE = f'{LATEST_VERSION}_app.zip'
LATEST_VERSION_PATH = pkg_resources.resource_filename(__name__, LATEST_VERSION_FILE)

LATEST_VERSION_SNIFFING_KIT = '4.1.19'
LATEST_VERSION_FILE_SNIFFING_KIT = f'{LATEST_VERSION_SNIFFING_KIT}_app.zip'
LATEST_VERSION_PATH_SNIFFING_KIT = pkg_resources.resource_filename(__name__, LATEST_VERSION_FILE_SNIFFING_KIT)

class UARTError(Exception):
    pass

class UARTInterface:
    def __init__(self, comport, update_fw=True, sniffing_kit_flag=False):
        self.comport = comport
        self.serial = serial.Serial(port=comport, baudrate=921600, timeout=SERIAL_TIMEOUT)
        self.serial.flushInput()
        self.gw_app_rx = None
        self.sniffing_kit_flag = sniffing_kit_flag
        version_supported = self.check_fw_supported()
        if not version_supported and update_fw:
            update_status = self.update_firmware()
            if not update_status:
                raise UARTError('Update Failed! Update FW manually using NRF Tools')
            if self.fw_version >= version.Version('3.17.0'):
                self.write_ble_command(GATEWAY_APP)
                self.flush()
        debug_print(f'Serial Connection {comport} Initialized')

    @staticmethod
    def get_comports():
        ports = serial.tools.list_ports.comports()
        debug_print(SEP + "\nAvailable ports:")
        for port, desc, hwid in sorted(ports):
            debug_print("{}: {} [{}]".format(port, desc, hwid))
        debug_print(SEP + "\n")
        return ports

    def read_line(self):
        # This reads a line from the ble device (from the serial connection using ble_ser),
        # strips it from white spaces and then decodes to string from bytes using the "utf-8" protocol.
        answer = self.serial.readline().strip().decode("utf-8", "ignore")
        if len(answer) == 0:
            return None
        return answer

    def write_ble_command(self, cmd, read=False):
        # This function writes a command (cmd) to the ble using a serial connection (ble_ser) that are provided to it beforehand.. and returns the answer from the device as string
        debug_print("Write to BLE: {}".format(cmd))
        # Shows on terminal what command is about to be printed to the BLE device
        bytes_to_write = bytes(cmd.encode("utf-8")) + b'\r\n'
        self.serial.write(bytes_to_write)
        answer = None
        if read:
            # The "bytes" function converts the command from string to bytes by the specified "utf-8" protocol then we use .write to send the byte sequence to the ble device using the serial connection that we have for this port (ble_ser)
            # Pauses the program for execution for 0.01sec. This is done to allow the device to process the command and provide a response before reading the response.
            time.sleep(1)
            answer = self.read_line()
            debug_print(answer)
        return answer
    
    def flush(self):
        self.serial.close()
        self.serial.open()
        self.serial.flushInput()
        self.serial.flush()
        self.serial.reset_output_buffer()

    def reset_gw(self):
        self.flush()
        self.write_ble_command(RESET_GW)
        self.gw_app_rx = None
        time.sleep(3)
        self.write_ble_command(STOP_ADVERTISING)
        time.sleep(3)


    def cancel(self):
        self.write_ble_command(CANCEL)

    def set_rx(self, rx_channel):
        if self.sniffing_kit_flag:
            assert rx_channel in RX_CHANNELS_SNIFFING_KIT
        else:
            assert rx_channel in RX_CHANNELS
        if self.gw_app_rx is None:
            self.reset_gw()

        if self.fw_version >= version.Version('3.17.0'):
            # from 3.17.0, only full_cfg can be used to configure channels. sending it with:
            # Data coupling(DC) off, wifi(NW) and mqtt(MQ) on.
            rx_ch_to_fw_enums = {37: 2, 38: 3, 39: 4}
            if self.sniffing_kit_flag:
                my_dict = {i: 5 + i for i in range(37)}
                rx_ch_to_fw_enums.update(my_dict)
            cmd = f'!full_cfg DM {rx_ch_to_fw_enums[rx_channel]} DC 0 NW 1 MQ 1 CH {rx_channel}'
            # cmd = '!gateway_app'
        else:
            cmd = f'!gateway_app {rx_channel} 30 0 17'

        self.write_ble_command(cmd)
        self.gw_app_rx = rx_channel

    def set_sniffer(self, rx_channel):
        self.set_rx(rx_channel)
        self.flush()
        time.sleep(1)
        self.write_ble_command(f'{SET_SNIFFER} {rx_channel}')
        self.flush()
        time.sleep(1)

    def cancel_sniffer(self):
        self.write_ble_command(CANCEL_SNIFFER)
        self.flush()

    def get_version(self):
        self.reset_gw()
        self.flush()
        timeout = datetime.datetime.now() + datetime.timedelta(seconds=15)
        while datetime.datetime.now() < timeout:
            raw_version = self.write_ble_command(VERSION, read=True)
            if raw_version is not None:
                if GW_APP_VERSION_HEADER in raw_version:
                    return raw_version.split(' ')[0].split('=')[1]
        return None
    
    def check_fw_supported(self):
        current_version = self.get_version()
        if current_version is None:
            raise UARTError("Cannot initialize board! Please try disconnecting and connecting USB cable")
        current_version = version.parse(current_version)
        hex_version = version.parse(os.path.splitext(os.path.basename(LATEST_VERSION_PATH))[0].split('_')[0])
        self.fw_version = current_version
        if current_version >= hex_version:
            debug_print(f'GW Running version {current_version}')
            self.fw_version = current_version
            return True
        return False

    def update_firmware(self):
        self.write_ble_command('!reset', read=True)
        self.write_ble_command('!move_to_bootloader', read=True)
        self.serial.close()
        p = None
        if self.sniffing_kit_flag:
            p = subprocess.Popen(f'nrfutil dfu serial --package "{LATEST_VERSION_PATH_SNIFFING_KIT}" -p {self.comport} -fc 0 -b 115200 -t 10', shell=True)
        else:
            p = subprocess.Popen(f'nrfutil dfu serial --package "{LATEST_VERSION_PATH}" -p {self.comport} -fc 0 -b 115200 -t 10', shell=True)
        p.wait()
        return_code = p.returncode
        debug_print('Waiting for device to update...')
        timeout = datetime.datetime.now() + datetime.timedelta(minutes=2)
        current_ver = ''
        time.sleep(15)
        self.serial.open()
        self.flush()
        while GW_APP_VERSION_HEADER not in current_ver and datetime.datetime.now() < timeout:
            current_ver = self.write_ble_command(VERSION, read=True)
            if current_ver is None:
                current_ver = ''
            time.sleep(1)
        if self.sniffing_kit_flag:
            if current_ver.split(' ')[0].split('=')[1] != LATEST_VERSION_SNIFFING_KIT:
                return False
        else:
            if current_ver.split(' ')[0].split('=')[1] != LATEST_VERSION:
                return False
        if return_code == 0:
            self.fw_version = version.parse(current_ver.split(' ')[0].split('=')[1])
            return True
        return False

        ### TODO: Sequence List