import sys
import serial.tools.list_ports

def get_uart_ports(silent=True):
    ports = serial.tools.list_ports.comports()
    uart_ports = []
    if not silent:
        sys.stdout.write('[')
    for port, desc, hwid in sorted(ports):
        if 'USB to UART' not in desc:
            continue
        if not silent:
            sys.stdout.write(f'("{port}", "{desc}", "{hwid}"),') 
        uart_ports.append(port)
    if not silent: 
        sys.stdout.write(']')
    return uart_ports

if __name__ == '__main__':
    get_uart_ports(silent=False)