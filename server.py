from logger import getlogger
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from peergroup import Peer


PKG = 'raft.server'
LOGGER = getlogger(PKG)


class SyncServerInterface():
    def __init__(self, peergroup_th):
        self.peers = {}
        self.peergroup_th = peergroup_th

    def vote(self):
        return 'OK'

    def heartbeat(self):
        LOGGER.info("Remote heartbeat event set!")
        peergroup_th.heartbeat_event.set()


class RequestHandler(SimpleXMLRPCRequestHandler):
    def log_request(self, code='-', size='-'):
        LOGGER.info('Received Request.')


class ServerThread(Thread):
    def __init__(self, myself, peergroup_th):
        super(ServerThread, self).__init__()
        self.myself = myself
        self.server = None
        self.peergroup_th = peergroup_th

    def run(self):
        server_interface = SyncServerInterface(self.peergroup_th)
        ip_port = self.myself.get_ip_port()
        LOGGER.info('start server:{}'.format(ip_port))
        server = SimpleXMLRPCServer(ip_port, requestHandler=RequestHandler,
            #???
            allow_none=True)
        server.register_instance(server_interface)
        self.server = server
        server.serve_forever()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.socket.close()


def get_server_thread(peer, peergroup_th):
    thread = ServerThread(peer, peergroup_th)
    return thread
