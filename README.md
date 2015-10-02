# HookSwitch: A Usermode Packet Injection Library

[![PyPI version](https://badge.fury.io/py/hookswitch.svg)](http://badge.fury.io/py/hookswitch)

## Possible Recipes

* Fault Injection (Example: [Earthquake](https://github.com/osrg/earthquake))
* L7-aware firewall (Note that you might not get good performance. However, it's still useful for prototyping.)

and so on..

HookSwitch was originally developed for [Earthquake](https://github.com/osrg/earthquake), but we believe HookSwitch can be also used for other purposes.

## Supported Backends

* Openflow 1.3 compliant switches
* Linux netfilter queue (effective for loopback interfaces)

## Install
For Python 2:

    $ sudo pip install hookswitch

For Python 3 [NOT YET SUPPORTED]:

    $ sudo pip3 install hookswitch


## Usage (Openflow 1.3 implementation)
In this section, we suppose you have already set up Openflow switch (e.g. OVS) and Ryu Framework.
   
    $ hookswitch-example-controller ipc:///tmp/hookswitch-socket &
    $ hookswitch-of13 ipc:///tmp/hookswitch-socket --tcp-ports=4242,4243,4244


## Usage (Linux netfilter queue implementation)

    $ sudo iptables -A OUTPUT -p tcp -m owner --uid-owner johndoe -j NFQUEUE --queue-num 42
    $ hookswitch-example-controller ipc:///tmp/hookswitch-socket &
    $ sudo hookswitch-nfq ipc:///tmp/hookswitch-socket --nfq-number=42
    

## API Design
HookSwitch works as a ZeroMQ client.

You can implement your application ("Controller") as a ZeroMQ server in an arbitrary language.

ZeroMQ message format:
    
    +------------------------------+
    |         JSON metadata        |
    +------------------------------+
    |         Ethernet Frame       |
    +------------------------------+

NOTE: In Linux netfilter queue implementation, Ethernet header is always like this:

    FF FF FF FF FF FF 00 00 00 00 00 00 08 00

### JSON Metadata

HookSwitch -> Controller:

 - `id`(int): Ethernet frame ID

HookSwitch <- Controller:

 - `id`(int): Ethernet frame ID
 - `op`(string): either one of {`accept`, `drop`, `modify`}. If `op` is not `modify`, the Ethernet frame *must* be ignored.


## Related Projects
* [Earthquake](https://github.com/osrg/earthquake)
* [HookFS](https://github.com/osrg/hookfs)

## How to Contribute
We welcome your contribution to HookSwitch.
Please feel free to send your pull requests on github!

## Copyright
Copyright (C) 2015 [Nippon Telegraph and Telephone Corporation](http://www.ntt.co.jp/index_e.html).

Released under [Apache License 2.0](LICENSE).
