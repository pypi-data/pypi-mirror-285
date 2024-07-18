import binascii
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import pkg_resources
import os
import subprocess
import shutil
from wiliot_deployment_tools.gw_certificate.tests.static.coupling_defines import *
from wiliot_deployment_tools.interface.ble_simulator import BLESimulator
from wiliot_deployment_tools.interface.pkt_generator import TagPktGenerator
from wiliot_deployment_tools.interface.uart_if import UARTInterface

if __name__ == "__main_____":
    test_name = 'zebra_screenoff'
    CSV_NAME = test_name
    CSV_PATH = pkg_resources.resource_filename(__name__, f'{test_name}/{CSV_NAME}.csv')
    ANDROID_LOG_PATH = pkg_resources.resource_filename(__name__, f'{test_name}/{CSV_NAME}.log')
    HTML_PATH_BAR = pkg_resources.resource_filename(__name__, f'{test_name}/{test_name}_bar.html')
    HTML_PATH_SCATTER = pkg_resources.resource_filename(__name__, f'{test_name}/{test_name}_scatter.html')
    
    os.makedirs(pkg_resources.resource_filename(__name__, f'{test_name}'), exist_ok=True)
    
    subprocess.run('adb -d logcat -c', shell=True)
    subprocess.Popen(f'adb -d logcat --format="epoch" > {ANDROID_LOG_PATH}', shell=True)
    pkts = []
    
    pkt_gen = TagPktGenerator(adva=INCREMENTAL_STAGE_ADVA)
    uart = UARTInterface('/dev/cu.usbserial-0001')
    ble_sim = BLESimulator(uart)
    ble_sim.set_sim_mode(True)
    for time_delay in INCREMENTAL_TIME_DELAYS:
        for pkt in INCREMENTAL_PACKETS:
            data = pkt_gen.get_packet()
            # expected_pkt = self.pkt_gen.get_expected_mqtt()
            # expected_pkt.update({'duplication': duplication, 'time_delay': DEFAULT_DELAY,
            # 'si_rawpacket': si, 'data_rawpacket': data})
            # self.local_pkts.append(expected_pkt)
            ble_sim.send_packet(raw_packet=data, duplicates=1, delay=15)
            pkt_id_bytes, pkt_id_int = pkt_gen.get_pkt_id()
            pkt_gen.set_pkt_id(pkt_id_int + 1)
            pkts.append({PAYLOAD: data, 'time_delay':time_delay,
                        'time': datetime.datetime.now(), 'source':'ble',
                        'rssi': 0})
    pkts = pd.DataFrame().from_dict(pkts)
    pkts.to_csv(CSV_PATH)
            
    # Parse android logs
    android_data = []
    with open(ANDROID_LOG_PATH) as f:
        loglines = f.readlines()
        
    for line in loglines:
        if 'AdvA' not in line:
            continue
        line = line.split()
        time = datetime.datetime.fromtimestamp(float(line[0]))
        adva = line[7]
        rssi = float(line[8].split(':')[-1])
        payload = line[9].split('[')[-1]+':'+line[11].split(']')[0]
        android_data.append({'source': 'android', 'time': time,
                                'adva': adva, 'rssi': rssi, 'payload': payload})
    android_data = pd.DataFrame().from_dict(android_data)
    
    all_data = pd.concat([pkts, android_data])
    all_data['pkt_counter'] = all_data['payload'].apply(lambda x: int.from_bytes(binascii.unhexlify(str(x)[-4:]), 'big'))
    percentages = []
    for delay in INCREMENTAL_TIME_DELAYS:
        relevant_pkt_ids = all_data[(all_data['source']=='ble') & (all_data['time_delay']==delay)]['pkt_counter']
        num_sent = len(relevant_pkt_ids.unique())
        num_received = len(all_data[(all_data['source']=='android') & (all_data['pkt_counter'].isin(relevant_pkt_ids))]['payload'].unique())
        percentages.append({'time_delay': delay, 'source': 'ble', 'num_pkts':num_sent, 'percent': num_sent/num_sent})
        percentages.append({'time_delay': delay, 'source': 'android', 'num_pkts':num_received, 'percent': num_received/num_sent})
    percentages = pd.DataFrame().from_dict(percentages)
    trace1 = px.scatter(all_data, x='time', y='pkt_counter', render_mode='svg', color='source', hover_data=['rssi'], title=test_name)
    trace2 = px.bar(percentages, x='time_delay', y='num_pkts', color='source', barmode='group', hover_data=['percent'])
    trace2.update_xaxes(type='category')

    trace1.write_html(HTML_PATH_SCATTER)
    trace2.write_html(HTML_PATH_BAR)
    # fig.show()
    # fig.write_html(HTML_PATH)