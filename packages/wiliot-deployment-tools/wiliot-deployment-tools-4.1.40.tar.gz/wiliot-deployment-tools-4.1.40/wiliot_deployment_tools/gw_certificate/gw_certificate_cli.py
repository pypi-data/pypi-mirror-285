from argparse import ArgumentParser
from wiliot_deployment_tools.gw_certificate.gw_certificate import GWCertificate
from wiliot_deployment_tools.gw_certificate.tests import TESTS

def filter_tests(tests_names):
    chosen_tests = []
    if tests_names == []:
        return TESTS
    for test_class in TESTS:
        for test_name in tests_names:
            if test_name in test_class.__name__.lower() and test_class not in chosen_tests:
                chosen_tests.append(test_class)
    return chosen_tests

def main():
    usage = (
        "usage: wlt-gw-certificate [-h] -owner OWNER -gw GW\n"
        "                          [-tests {connection,uplink,downlink,stress}] [-update]"
        )

    parser = ArgumentParser(prog='wlt-gw-certificate',
                            description='Gateway Certificate - CLI Tool to test Wiliot GWs', usage=usage)

    required = parser.add_argument_group('required arguments')
    required.add_argument('-owner', type=str, help="Owner ID", required=True)
    required.add_argument('-gw', type=str, help="Gateway ID", required=True)
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-suffix', type=str, help="Topic suffix", default='', required=False)
    optional.add_argument('-tests', type=str, choices=['connection', 'uplink', 'downlink', 'stress'], help="Tests to run", required=False, nargs='+', default=[])
    optional.add_argument('-update', action='store_true', help='Update test board firmware', default=False, required=False)
    args = parser.parse_args()
    tests = filter_tests(args.tests)
    topic_suffix = '' if args.suffix == '' else '-'+args.suffix


    gwc = GWCertificate(gw_id=args.gw, owner_id=args.owner, topic_suffix=topic_suffix, tests=tests, update_fw=args.update)
    gwc.run_tests()
    gwc.create_results_html()

def main_cli():
    main()

if __name__ == '__main__':
    main()
    