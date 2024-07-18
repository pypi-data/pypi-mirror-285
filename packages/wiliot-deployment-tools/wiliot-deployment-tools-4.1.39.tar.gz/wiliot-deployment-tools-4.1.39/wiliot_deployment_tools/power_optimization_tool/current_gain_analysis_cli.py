from argparse import ArgumentParser
from wiliot_deployment_tools.power_optimization_tool.current_gain_analysis import OptimalPowerConfiguration

def main():
    parser = ArgumentParser(description="Calculate and plot Avg Current vs. Relative Gain")
    required = parser.add_argument_group('required arguments')
    required.add_argument("-bridge_type", type=str, help="Bridge type (minew or fanstel)", required=True)
    required.add_argument("-dc", nargs="+", type=float, help="The values of the duty cycles to compare. The order of insertion must match the order of the corresponding rxtx period", required=True)
    required.add_argument("-rxtx_period", nargs="+", type=int, help="The value of rxtx period. The order of insertion must match the order of the corresponding duty cycle", required=True)
    
    args = parser.parse_args()
    b = OptimalPowerConfiguration(args.bridge_type, args.dc, args.rxtx_period)
    b.generate_current_gain_plot()
    
def main_cli():
    main()

if __name__ == '__main__':
    main()