# xaal use multicast cnx too, so reuse it here. TODO : drop this 
from xaal.lib import network 

import logging
import json
import gevent

logger = logging.getLogger(__name__)

class AqaraConnector(gevent.Greenlet):
    """
    Aqara Device Report/Heartbeat connector, used only to receive event, if you want to send a command,
    you must send a unicast datagram to the right Aqara GW.
    """

    def __init__(self,gw):
        gevent.Greenlet.__init__(self)
        self.gw = gw
        self.nc = network.NetworkConnector('224.0.0.50',9898,10)
        self.nc.connect()

    def receive(self):
        buf = self.nc.receive()
        if buf:
            try:
                return json.loads(buf)
            except ValueError:
                logger.debug('JSON decoder Error %s' % buf)
        return None

    def _run(self):
        logger.info("AqaraConnector ready, waiting for hubs.")
        while 1:
            pkt = self.receive()
            if pkt:
                self.gw.on_receive(pkt)


class AqaraDiscovery(gevent.Greenlet):
    """ Aqara Hubs discovery."""

    def __init__(self,gw):
        gevent.Greenlet.__init__(self)
        self.gw = gw
        self.nc = network.NetworkConnector('224.0.0.50',4321,10)
        self.nc.connect()

    def receive(self):
        buf = self.nc.receive()
        if buf:
            try:
                return json.loads(buf)
            except ValueError:
                logger.debug('JSON decoder Error %s' % buf)
        return None

    def whois(self):
        """ forge and send a whois packet"""
        h = {"cmd":"whois"}
        self.nc.send(json.dumps(h).encode('utf-8'))
    
    def _run(self):
        logger.info("AqaraDiscovery ready, let's discover")
        self.whois()
        while 1:
            pkt = self.receive()
            if pkt:
                self.gw.on_receive(pkt)
