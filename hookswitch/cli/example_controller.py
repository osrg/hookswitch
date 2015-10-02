import argparse
import hexdump
import json
import logging
import eventlet
from eventlet.green import zmq


def main():
    parser = argparse.ArgumentParser(
        description='HookSwitch Controller Example')
    help_str = 'ZeroMQ bind address (e.g. ipc:///tmp/hookswitch-socket)'
    parser.add_argument('ZMQ_ADDR',
                        type=str,
                        help=help_str)
    args = parser.parse_args()
    worker = Worker(args.ZMQ_ADDR)
    print('Starting for %s' % (args.ZMQ_ADDR))
    worker.start()


class Worker(object):

    def __init__(self, zmq_addr):
        self.zmq_addr = zmq_addr

    def start(self):
        self.zmq_ctx = zmq.Context()
        self.zs = self.zmq_ctx.socket(zmq.PAIR)
        self.zs.bind(self.zmq_addr)
        handle = eventlet.spawn(self._zmq_worker)
        handle.wait()
        raise RuntimeError('should not reach here')

    def _zmq_worker(self):
        while True:
            metadata_str, eth_bytes = self.zs.recv_multipart()
            metadata = json.loads(metadata_str)
            print('===== Packet: %s =====' % metadata)
            print('Ethernet Frame (%d bytes)' % len(eth_bytes))
            hexdump.hexdump(eth_bytes)
            self._accept(metadata)

    def _accept(self, metadata):
        assert isinstance(metadata, dict)
        resp_metadata = metadata.copy()
        resp_metadata['op'] = 'accept'
        resp_metadata_str = json.dumps(resp_metadata)
        self.zs.send_multipart((resp_metadata_str, ''))

if __name__ == '__main__':
    import sys
    sys.exit(main())
