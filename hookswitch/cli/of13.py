import os
import logging
from hookswitch.openflow import OF13Hook
from hookswitch.internal import LOG


class _OF13Hook(OF13Hook):

    """
    should be called from ryu-manager
    """

    def get_args(self):
        zmq_addr = os.getenv('HOOKSWITCH_ZMQ_ADDR')
        tcp_ports_str = os.getenv('HOOKSWITCH_TCP_PORTS')
        udp_ports_str = os.getenv('HOOKSWITCH_UDP_PORTS')
        debug = os.getenv('HOOKSWITCH_DEBUG')
        tcp_ports = []
        udp_ports = []

        if not zmq_addr:
            raise RuntimeError('ZMQ address is not specified')

        if tcp_ports_str:
            try:
                tcp_ports = [int(x) for x in tcp_ports_str.split(',')]
            except ValueError as ve:
                raise RuntimeError('Bad tcp ports', ve)

        if udp_ports_str:
            try:
                udp_ports = [int(x) for x in udp_ports_str.split(',')]
            except ValueError as ve:
                raise RuntimeError('Bad udp ports', ve)

        if not tcp_ports and not udp_ports:
            raise RuntimeError('No port is specified')

        return {'zmq_addr': zmq_addr,
                'tcp_ports': tcp_ports,
                'udp_ports': udp_ports,
                'debug': debug}

    def __init__(self, *ryu_args, **ryu_kwargs):
        args = self.get_args()
        if not args['debug']:
            LOG.setLevel(logging.INFO)
        LOG.debug('Args: %s', args)

        super(_OF13Hook, self).__init__(tcp_ports=args['tcp_ports'],
                                        udp_ports=args['udp_ports'],
                                        zmq_addr=args['zmq_addr'],
                                        *ryu_args, **ryu_kwargs)
