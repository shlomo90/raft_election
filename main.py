import sys
import argparse
from server import get_server_thread
from peergroup import Peers, Peer, get_peer_group_thread


PKG = 'raft.main'
IP = '172.17.0.2'
PORT = 3769


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--me', '-m', type=str, help='--me 192.168.100.1:3769')
    parser.add_argument('--peer', '-p', type=str, nargs='*', help='--peer 192.168.100.2:3769 192.168.100.3:3768')
    args = parser.parse_args()
    print(args.me)
    print(args.peer)

    ip, port = args.me.split(':')
    print("My IP:{}, Port:{}".format(ip, port))
    myself = Peer(ip, int(port))
    others = Peers()
    for peer in args.peer:
        ip, port = peer.split(':')
        print("Peer IP:{}, Port:{}".format(ip, port))
        others.add_new_peer(ip, int(port))

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
