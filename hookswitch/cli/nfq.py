import argparse
import logging
from hookswitch.nfq import NFQHook
from hookswitch.internal import LOG


def main():
    parser = argparse.ArgumentParser(
        description='HookSwitch for Linux netfilter queue')
    help_str = 'ZeroMQ connect address (e.g. ipc:///tmp/hookswitch-socket)'
    parser.add_argument('ZMQ_ADDR',
                        type=str,
                        help=help_str)
    parser.add_argument('-n', '--nfq-number',
                        required=True,
                        type=int,
                        help='netfilter queue number')
    parser.add_argument('--debug',
                        action='store_true',
                        help='print debug info')

    args = parser.parse_args()

    if not args.debug:
        LOG.setLevel(logging.INFO)

    hook = NFQHook(nfq_number=args.nfq_number, zmq_addr=args.ZMQ_ADDR)
    print('Starting for %s (NFQ %d)' % (args.ZMQ_ADDR, args.nfq_number))
    hook.start()

if __name__ == '__main__':
    import sys
    sys.exit(main())
