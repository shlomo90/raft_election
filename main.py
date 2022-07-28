from server import get_server_thread
from peergroup import Peers, Peer, get_peer_group_thread


PKG = 'raft.main'
IP = '172.17.0.2'
PORT = 3769


if __name__ == "__main__":
    myself = Peer(IP, PORT)
    others = Peers()
    others.add_new_peer('172.17.0.3', PORT)
    others.add_new_peer('172.17.0.4', PORT)
    others.add_new_peer('172.17.0.5', PORT)

    peergroup_th = get_peer_group_thread(myself, others)
    server_th = get_server_thread(myself, peergroup_th)

    server_th.start()
    peergroup_th.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        peergroup_th.stop()
        peergroup_th.join()
        server_th.stop()
        server_th.join()
