from threading import Thread
from logger import getlogger
from time import sleep
from client import get_server_proxy


PKG = 'raft.raft'
LOGGER = getlogger(PKG)

# States
CANDIDATE = 'candidate'
FOLLOWER = 'follower'
LEADER = 'leader'


class ElectionTimeoutChecker(Thread):
    def __init__(self, peergroup, timeout):
        super(ElectionTimeoutChecker, self).__init__()
        self.peergroup = peergroup
        self.heartbeat_event = peergroup.heartbeat_event
        self.vote_event = peergroup.vote_event
        # election timeout
        self.timeout = timeout
        self.is_stop = False

    def run(self):
        LOGGER.info('Election Timeout Checker Start')
        while True:
            if self.peergroup.state == FOLLOWER:
                result = self.heartbeat_event.wait(timeout=self.timeout)
                if result is True:
                    LOGGER.info('Get Heartbeat.')
                else:
                    LOGGER.info('Election Timeout')
                    self.peergroup.state = CANDIDATE
                    self.heartbeat_event.clear()
                    self.vote_event.set()
            elif self.peergroup.state == CANDIDATE:
                LOGGER.info('Do Noting as CANDIDATE')
                sleep(1)
            elif self.peergroup.state == LEADER:
                LOGGER.info('Do Noting as LEADER')
                sleep(1)

            if self.is_stop is True:
                break

    def stop(self):
        self.is_stop = True


class ElectionChecker(Thread):
    def __init__(self, peergroup, timeout):
        super(ElectionChecker, self).__init__()
        self.peergroup = peergroup
        self.vote_event = peergroup.vote_event
        self.timeout = timeout  #Vote Timeout
        self.is_stop = False

    def run(self):
        while True:
            if self.is_stop is True:
                break
            self.vote_event.wait()
            if self.is_stop is True:
                break
            LOGGER.info('ElectionChecker Start')

            # Send vote (Threads)
            peers = self.peergroup.other_peers.get_peers()
            peer_threads = []
            peer_results = [None] * len(peers)
            for i, peer in enumerate(peers):
                voter = Voter(peer, peer_results, i, self.timeout) # Election Timeout
                peer_threads.append(voter)

            for peer_thread in peer_threads:
                peer_thread.start()
            for peer_thread in peer_threads:
                peer_thread.join()

            for i, peer_result in enumerate(peer_results):
                LOGGER.info("i:{}, peer_result:{}".format(i, peer_result))

            majority = len(peer_results)+1/2
            votes = len(filter(lambda x: x == 'OK', peer_results))
            if majority <= votes:
                # Elected.
                self.peergroup.state = LEADER
                LOGGER.info("{} is Leader!".format(
                    self.peergroup.me_peer.get_ip_port()))
            else:
                self.peergroup.state = FOLLOWER
                LOGGER.info("{} is FOLLOWER!".format(
                    self.peergroup.me_peer.get_ip_port()))
            self.vote_event.clear()

    def stop(self):
        self.vote_event.set()
        self.is_stop = True


class Voter(Thread):
    def __init__(self, peer, result, index, timeout):
        super(Voter, self).__init__()
        self.peer = peer
        self.result = result
        self.index = index
        self.timeout = timeout

    def run(self):
        try:
            server = get_server_proxy(self.peer, self.timeout)
            ret = server.vote()
        except BaseException as e:
            LOGGER.error(e)
            ret = None

        ip_port = self.peer.get_ip_port()
        LOGGER.info("ip_port:{}'s Vote:{}".format(ip_port, ret))
        self.result[self.index] = ret

    def stop(self):
        self.is_stop = True
