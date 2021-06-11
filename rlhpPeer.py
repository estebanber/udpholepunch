import rlhpProtocol as hp
import logging
import socket
import sys
from time import sleep


myData={
    'myid':0xFFFF,
    'myip':[]
}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


def udpPunchHole(addresses):
    packet={'command':hp.Command.HANDSHAKE }
    data= hp.createRlhpPacket(myData['myid'],555,packet)
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
            packet={'command':hp.Command.HANDSHAKEOK }
            data= hp.createRlhpPacket(myData['myid'],555,packet)
            sock.sendto(data, addr)
        elif packet['command']==hp.Command.HANDSHAKEOK:
            hsok=True
        if hnsk and hsok:
            print('Ready')
            connReady = True
            return addr



def peerSender(host='127.0.0.1', port=9999):
    sock.sendto(b'0', (host, port))
    lanPort = int(sock.getsockname()[1])


    packet={
        'command':hp.Command.REGISTRAR,
        'type': 1,
        'private_port': lanPort,
        'private_ip': myData['myip'][0]
    }
    data= hp.createRlhpPacket(0xFFFF,555,packet)
    print(myData['myip'], lanPort)
    sock.sendto(data, (host, port))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    packet = hp.processRlhpPacket(data)
    myData['myid']=packet['identifier']
    while True:
        data, addr = sock.recvfrom(1024)
        packet = hp.processRlhpPacket(data)
        if packet['command'] == hp.Command.INTERCAMBIAR:
            addr = udpPunchHole(packet)
            print('Dirección del peer: ',addr)
        elif packet['command'] == hp.Command.SERVICE:
            count=0
            while True:
                sock.sendto(bytes(f'Dato {count}',encoding='utf-8'), addr)
                count=count+1
                sleep(1)

def peerReceiver(host='127.0.0.1', port=9999):

    while True:
        comm = input('Enter Command > ')
        if comm == 'LIST':
            sock.sendto(b'LIST', (host, port))
            data, addr = sock.recvfrom(1024)
            res = data[0:4].decode('utf-8')
            if res == 'LIST':
                print('List received from {}\n{}'.format(addr, data.decode('utf-8')))
                actualizarLista(addresses,data)
        elif comm[0:4] == 'CONN':
            sock.sendto(b'0', (host, port))
            lanPort = sock.getsockname()[1]
            packet={
                'command':hp.Command.REGISTRAR,
                'type':2,
                'private_port': lanPort,
                'private_ip': myData['myip'][0],
            }
            data= hp.createRlhpPacket(myData['myid'],555,packet)
            sock.sendto(data, (host, port))
            data, addr = sock.recvfrom(1024)
            packet = hp.processRlhpPacket(data)
            myData['myid']=packet['identifier']
            packet={
                'command':hp.Command.CONECTAR,
                'remotePeer': int(comm[4])
            }
            data= hp.createRlhpPacket(myData['myid'],555,packet)
            sock.sendto(data, (host, port))
            data, addr = sock.recvfrom(1024)
            packet = hp.processRlhpPacket(data)
            if packet['command'] == hp.Command.INTERCAMBIAR:
                peerAddr = udpPunchHole(packet)
                print('Dirección del peer: ',peerAddr)
        elif comm[0:4] == 'STRM':
            packet={'command':hp.Command.SERVICE }
            data= hp.createRlhpPacket(myData['myid'],555,packet)
            sock.sendto(data, peerAddr)
            while True:
                data, addr = sock.recvfrom(1024)
                print(data)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    myData['myip'] = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith('127.')][:1]
    if not myData['myip']:
        print("Check your connection")
        exit()

    if sys.argv[1] == 'R':
        argumentos= sys.argv[1:4]
        peerReceiver()
    elif sys.argv[1] == 'S':
        argumentos= sys.argv[1:4]
        peerSender()



