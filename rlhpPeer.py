import rlhpProtocol as hp
import logging
import socket
import sys


myip=[]
myid=0xFFFF
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


def udpPunchHole(addresses):
    packet={
        'command':hp.Command.HANDSHAKE,
    }
    data= hp.createRlhpPacket(myid,555,packet)
    sock.sendto(data, (addresses['public_ip'], addresses['public_port']))
    sock.sendto(data, (addresses['private_ip'], addresses['private_port']))
    hsok=False
    hnsk=False
    connReady=False
    while not connReady: 
        data, addr = sock.recvfrom(1024)
        packet = hp.processRlhpPacket(data)
        if packet['command']==hp.Command.HANDSHAKE:
            hnsk=True
            pass 
        elif packet['command']==hp.Command.HANDSHAKEOK:
            hsok=True
            pass
        if hnsk and hsok:
            print('Ready')
            connReady = True



def peerSender(host='127.0.0.1', port=9999):
    sock.sendto(b'0', (host, port))
    lanPort = int(sock.getsockname()[1])


    packet={
        'command':hp.Command.REGISTRAR,
        'type': 1,
        'private_port': lanPort,
        'private_ip': myip[0]
    }
    data= hp.createRlhpPacket(0xFFFF,555,packet)
    print(lanPort)
    print(myip)
    print(data)
    sock.sendto(data, (host, port))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    packet = hp.processRlhpPacket(data)
    myid=packet('identifier')
    print(data)
    while True:
        data, addr = sock.recvfrom(1024)
        packet = hp.processRlhpPacket(data)
        if packet['command'] == hp.Command.INTERCAMBIAR
            addr = udpPunchHole(packet)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    myip = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith('127.')][:1]
    if not myip:
        print("Check your connection")
        exit()

    
    if sys.argv[1] == 'R':
        argumentos= sys.argv[1:4]
        mainReciever(*addr_from_args(argumentos))
    elif sys.argv[1] == 'S':
        argumentos= sys.argv[1:4]
        peerSender()



