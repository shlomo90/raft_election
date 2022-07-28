from time import sleep
from logger import getlogger
from threading import Thread, Lock, Event

from raft import CANDIDATE, FOLLOWER, LEADER, ElectionTimeoutChecker, ElectionChecker


PKG = 'raft.peergroup'
LOGGER = getlogger(PKG)


class Peer():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_ip_port(self):
        return ((self.ip, self.port))


class Peers():
    def __init__(self):
        self.peers = []

    def add_peer(self, peer):
        if isinstance(peer, Peer) is False:
            raise
        self.peers.append(Peer)

    def add_new_peer(self, ip, port):
        peer = Peer(ip, port)
        self.peers.append(peer)
        return peer

    def get_peers(self):
        peers = []
        for peer in self.peers:
            peers.append(peer)
        return peers

class PeerGroupThread(Thread):
    def __init__(self, me_peer, other_peers):
        super(PeerGroupThread, self).__init__()
        self.me_peer = me_peer
        self.other_peers = other_peers

        self.state = FOLLOWER
        self.state_lock = Lock()

        self.heartbeat_event = Event()
        self.vote_event = Event()

        self.is_stop = False

    def run(self):
        # Main Voting System Logic Here.
        # 3 threads
        LOGGER.info("self.me_peer:{}".format(self.me_peer.get_ip_port()))
        LOGGER.info("self.other_peers:{}".format(self.other_peers.get_peers()))

        LOGGER.info("create 3 threads")
        etc_th = ElectionTimeoutChecker(self, 3) #election timeout: 3sec
        # TODO: VOTE
        ec_th = ElectionChecker(self, 1)
        LOGGER.info("start run.")
        ec_th.start()
        etc_th.start()

        # Infinity loop.
        while True:
            sleep(5)
            LOGGER.info("5 seconds elapsed.")
            if self.is_stop is True:
                etc_th.stop()
                etc_th.join()
                ec_th.stop()
                ec_th.join()
                break

    def stop(self):
        self.is_stop = True


def get_peer_group_thread(me_peer, other_peers):
    return PeerGroupThread(me_peer, other_peers)
