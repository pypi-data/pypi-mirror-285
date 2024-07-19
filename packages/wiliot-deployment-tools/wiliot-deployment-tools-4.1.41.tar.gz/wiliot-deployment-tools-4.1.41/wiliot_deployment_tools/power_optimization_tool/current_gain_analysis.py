import argparse
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
import pandas as pd
import math
import pkg_resources
from enum import Enum
import sys

CSV_NAME = 'current_gain_data_set.csv'
PACKET_TABLE_CSV_PATH = pkg_resources.resource_filename(__name__, CSV_NAME)

class BridgeType(Enum):
    MINEW = {
        "avg_beacon_current": 208,
        "beacon_tx_time": 1.5,
        "avg_rx_current": 17.5,
        "max_output_power": 27.1
    }
    FANSTEL = {
        "avg_beacon_current": 101,
        "beacon_tx_time": 1.52,
        "avg_rx_current": 42.5,
        "max_output_power": 27.6
    }

class OptimalPowerConfiguration:
    def __init__(self, bridge_type, dc, rxtx_period):
        self.bridge_type = bridge_type
        self.dc_list = dc
        self.rxtx_period_list = rxtx_period
        self.avg_beacon_current = None
        self.beacon_tx_time = None
        self.avg_rx_current = None
        self.max_output_power = None
        self.data_df = None
        self.dc_rxtx_dict = None
        self.data_array = None
        self.dc_to_color = None

    def generate_current_gain_plot(self):
        self.load_csv_data_base()
        self.match_const_val_to_board_type()
        self.create_dc_rxtx_dict()
        self.calculate_data_create_np_array()
        self.create_color_mapping()
        self.plot_data()

    def load_csv_data_base(self):
        self.data_df = pd.read_csv(PACKET_TABLE_CSV_PATH)
        
    def match_const_val_to_board_type(self):
        try:
            bridge_type = BridgeType[self.bridge_type.upper()]  
            bridge_data = bridge_type.value
            self.avg_beacon_current = bridge_data["avg_beacon_current"]
            self.beacon_tx_time = bridge_data["beacon_tx_time"]
            self.avg_rx_current = bridge_data["avg_rx_current"]
            self.max_output_power = bridge_data["max_output_power"]
        except KeyError:
            print(f"Invalid bridge type: {self.bridge_type}. Please choose from the following bridge types: {', '.join(member.name.lower() for member in BridgeType)}.")
            sys.exit(1)

    def create_dc_rxtx_dict(self):
        self.dc_rxtx_dict = {}
        if len(self.dc_list) != len(self.rxtx_period_list):
            print("The number of 'dc' arguments must match the number of 'rxtx_perid' argument")
            sys.exit(1)
        for i, element in enumerate(self.dc_list):
            self.dc_rxtx_dict[element] = self.rxtx_period_list[i]

    def calculate_data_create_np_array(self):
        data = []
        self.data_df = self.data_df[self.data_df['bridge_type'] == self.bridge_type]
        for key in self.dc_rxtx_dict:
            for idx, row in self.data_df.iterrows():
                cfg_power = row['cfg_power']
                register_cfg = row['register_changed']
                avg_current = round(
                    key * row['X_current'] +
                    self.avg_beacon_current * (self.beacon_tx_time / self.dc_rxtx_dict[key]) +
                    self.avg_rx_current * ((self.dc_rxtx_dict[key] - self.beacon_tx_time) / self.dc_rxtx_dict[key]), 2)
                relative_gain = round((row['output_power'] - self.max_output_power) +
                                       10 * math.log10(key / 0.33), 2)
                pa = row['PA']
                data.append([key, cfg_power, avg_current, relative_gain, pa, register_cfg])
        self.data_array = np.array(data)

    def create_color_mapping(self):
        unique_dc_values = np.unique(self.data_array[:, 0])
        num_colors = len(unique_dc_values)
        custom_cmap = plt.get_cmap('viridis', num_colors)
        self.dc_to_color = {dc: custom_cmap(i) for i, dc in enumerate(unique_dc_values)}

    def plot_data(self):
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(self.data_array[:, 3], self.data_array[:, 2],
                            c=[self.dc_to_color[dc] for dc in self.data_array[:, 0]], marker='o', alpha=0.7)
        labels = ['DC: {:.2f}\nCfg Value: {}\nAvg Current: {:.2f}\nRelative Gain: {:.2f}\nPA: {}\nReg. changed: {}'.format(
            dc, cfg_power, avg_current, relative_gain, pa,register_cfg) for dc, cfg_power, avg_current, relative_gain, pa, register_cfg in self.data_array]

        mplcursors.cursor(scatter, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(labels[sel.index]))

        plt.xlabel('Relative Gain [dBm]')
        plt.ylabel('Avg Current [mA]')
        plt.title(f'Avg Current vs. Relative Gain for {self.bridge_type}')
        plt.grid()

        # Create a legend for the registers configurations
        legend_labels = [
        'Reg. cfg 1: pa_duty_cycle = 0x02; hp_max = 0x02;',
        'Reg. cfg 2: pa_duty_cycle = 0x02; hp_max = 0x03;',
        'Reg. cfg 3: pa_duty_cycle = 0x03; hp_max = 0x05;',
        'Reg. cfg 4: pa_duty_cycle = 0x04; hp_max = 0x07;']

        proxy_artists = [plt.Line2D([0], [0], marker='o', color='w', label=label,
                                    markerfacecolor='k', markersize=10) for label in legend_labels]

        plt.legend(handles=proxy_artists, title="Register configuration table:", loc='best')

        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate and plot Avg Current vs. Relative Gain")
    required = parser.add_argument_group('required arguments')
    required.add_argument("-bridge_type", type=str, help="Bridge type (minew or fanstel)", required=True)
    required.add_argument("-dc", nargs="+", type=float, help="The values of the duty cycles to compare. The order of insertion must match the order of the corresponding rxtx period", required=True)
    required.add_argument("-rxtx_period", nargs="+", type=int, help="The value of rxtx period. The order of insertion must match the order of the corresponding duty cycle", required=True)
    args = parser.parse_args()

    opt_power_cfg = OptimalPowerConfiguration(args.bridge_type, args.dc, args.rxtx_period)
    opt_power_cfg.generate_current_gain_plot()
















