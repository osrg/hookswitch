from abc import ABCMeta, abstractmethod
import six
import socket
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.app.simple_switch_13 import SimpleSwitch13
from hookswitch.internal.zmqclient import ZMQClientBase


class OFHookZMQC(ZMQClientBase):

    def __init__(self, zmq_addr, ryu, datapath):
        super(OFHookZMQC, self).__init__(zmq_addr)
        self.ryu = ryu
        self.datapath = datapath

    def on_accept(self, packet_id_IGNORED, eth_bytes, metadata=None):
        ofp = self.datapath.ofproto
        parser = self.datapath.ofproto_parser
        in_port, out_port = self.ryu.determine_ports(self.datapath, eth_bytes)
        ofp_packet_out = parser.OFPPacketOut(datapath=self.datapath,
                                             buffer_id=ofp.OFP_NO_BUFFER,
                                             in_port=in_port,
                                             actions=[
                                                 parser.OFPActionOutput(
                                                     out_port)],
                                             data=eth_bytes)
        self.datapath.send_msg(ofp_packet_out)

    def on_drop(self, packet_id, eth_bytes, metadata=None):
        pass


@six.add_metaclass(ABCMeta)
class OF13HookBase(SimpleSwitch13):

    """
    Inherits ryu.app.SimpleSwitch13.
    Tested with ryu 3.20.2 + OVS 2.3.1.
    """
    OFP = ofproto_v1_3
    OFP_PARSER = ofproto_v1_3_parser  # used by child classes
    FLOW_PRIORITY_BASE = 10240

    def __init__(self, matches, zmq_addr, *args, **kwargs):
        super(OF13HookBase, self).__init__(*args, **kwargs)
        self.matches = matches
        self.zmq_client = None
        self.zmq_addr = zmq_addr
        self.current_packet_id = 0

    def determine_ports(self, datapath, data):
        ofp = datapath.ofproto
        in_port = ofp.OFPP_CONTROLLER
        out_port = ofp.OFPP_FLOOD

        pkt = packet.Packet(data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        # self.mac_to_port is managed by the parent class
        if eth.src in self.mac_to_port[datapath.id]:
            in_port = self.mac_to_port[datapath.id][eth.src]
        if eth.dst in self.mac_to_port[datapath.id]:
            out_port = self.mac_to_port[datapath.id][eth.dst]
        return (in_port, out_port)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(OF13HookBase, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser

        # increase miss_send_len to the max (OVS default: 128 bytes)
        conf = parser.OFPSetConfig(datapath, ofp.OFPC_FRAG_NORMAL, 0xFFFF)
        datapath.send_msg(conf)

        # install self.matches
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER,
                                          ofp.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
                                             actions)]
        for i, match in enumerate(self.matches):
            mod = parser.OFPFlowMod(datapath=datapath,
                                    priority=self.FLOW_PRIORITY_BASE + i,
                                    match=match,
                                    instructions=inst)
            # TODO: Check flow overlaps
            datapath.send_msg(mod)

        # initialize mac table (managed by the parent class)
        self.mac_to_port.setdefault(datapath.id, {})

        # Start ZMQ Worker
        assert self.zmq_client is None, 'multiple datapaths not supported'
        self.zmq_client = OFHookZMQC(self.zmq_addr, self, datapath)
        self.zmq_client_handle = self.zmq_client.start()

        self.logger.debug('Setup done for datapath %d', datapath.id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        # NOTE: too old OVS(<= 2.0?) returns OFPR_ACTION, not OFPR_NO_MATCH
        # http://git.openvswitch.org/cgi-bin/gitweb.cgi?p=openvswitch;a=commitdiff;h=cfa955b083c5617212a29a03423e063ff6cb350a
        # So we need OVS >= 2.1.
        if msg.reason == ev.msg.datapath.ofproto.OFPR_NO_MATCH:
            super(OF13HookBase, self)._packet_in_handler(ev)
        else:
            assert self.zmq_client, \
                'PKT-IN handler called before configuration'
            # NOTE: packet_id can conflict when packet_id = hash(ev)
            self.zmq_client.send(self.current_packet_id, msg.data)
            self.current_packet_id += 1


class OF13Hook(OF13HookBase):

    def __init__(self, tcp_ports, udp_ports, zmq_addr, *args, **kwargs):
        OFPMatch = self.OFP_PARSER.OFPMatch
        matches = []
        for port in tcp_ports:
            m = OFPMatch(
                eth_type=0x0800, ip_proto=socket.IPPROTO_TCP, tcp_dst=port)
            matches.append(m)
            m = OFPMatch(
                eth_type=0x0800, ip_proto=socket.IPPROTO_TCP, tcp_src=port)
            matches.append(m)
        for port in udp_ports:
            m = OFPMatch(
                eth_type=0x0800, ip_proto=socket.IPPROTO_UDP, udp_dst=port)
            matches.append(m)
            m = OFPMatch(
                eth_type=0x0800, ip_proto=socket.IPPROTO_UDP, udp_src=port)
            matches.append(m)
        super(OF13Hook, self).__init__(matches, zmq_addr, *args, **kwargs)
