import rlhpProtocol as hp
import logging
import socket
import sys
from time import sleep
from threading import Event, Thread


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()
myData={
    'myid':0xFFFF,
    'myip':[]
}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

STOP = Event()

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

def accept(port):
    logger.info("accept %s", port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('', port))
    s.listen(1)
    s.settimeout(5)
    while not STOP.is_set():
        try:
            conn, addr = s.accept()
        except socket.timeout:
            continue
        else:
            logger.info("Accept %s connected!", port)
            # STOP.set()


def connect(local_addr, addr):
    logger.info("connect from %s to %s", local_addr, addr)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(local_addr)
    while not STOP.is_set():
        try:
            s.connect(addr)
        except socket.error:
            continue
        # except Exception as exc:
        #     logger.exception("unexpected exception encountered")
        #     break
        else:
            pass
            #logger.info("connected from %s to %s success!", local_addr, addr)
            # STOP.set()

def tcpPunchHole(addresses,host,port):
    sleep(0.1)
    sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sa.connect((host, port))
    priv_addr = sa.getsockname()
    threads = {
        '0_accept': Thread(target=accept, args=(priv_addr[1],)),
        '1_accept': Thread(target=accept, args=(addresses['public_port'],)),
        '2_connect': Thread(target=connect, args=(priv_addr, (addresses['public_ip'],addresses['public_port']))),
        '3_connect': Thread(target=connect, args=(priv_addr, (addresses['private_ip'],addresses['private_port']),)),
    }

    for name in sorted(threads.keys()):
        logger.info('start thread %s', name)
        threads[name].start()

    while threads:
        keys = list(threads.keys())
        for name in keys:
            try:
                threads[name].join(1)
            except TimeoutError:
                continue
            if not threads[name].is_alive():
                threads.pop(name)

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
        if packet['command'] == hp.Command.CONFIGURAR:
            if packet['protocol'] == 1: #TCP
                lastConfigProtocol = 1
                new_host = packet['server_ip']
                new_port = packet['server_port']
                sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sa.connect((new_host, new_port))
                priv_tcp_addr = sa.getsockname()
                packet={
                    'command':hp.Command.CONFIGURAROK,
                    'private_ip': priv_tcp_addr[0],
                    'private_port':priv_tcp_addr[1]
                }
                data= hp.createRlhpPacket(myData['myid'],555,packet)
                sock.sendto(data, (host, port))
                sa.sendall(data)
                print('enviado')

            elif packet['protocol'] == 2: #UDP:
                lastConfigProtocol = 2

        elif packet['command'] == hp.Command.INTERCAMBIAR:
            if lastConfigProtocol == 1: #TCP
                print('aqui')
                peerAddr = tcpPunchHole(packet,new_host,new_port)
            elif lastConfigProtocol == 2: #UDP
                peerAddr = udpPunchHole(packet)
            print('Dirección del peer: ',peerAddr)
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
                'remotePeer': int(comm[4]),
                'connections':1,
                'protocol':int(comm[5])
            }
            data= hp.createRlhpPacket(myData['myid'],555,packet)
            sock.sendto(data, (host, port))
            lastConfigProtocol = 0
            new_host = ''
            new_port = 0
            while True:
                data, addr = sock.recvfrom(1024)
                packet = hp.processRlhpPacket(data)
                if packet['command'] == hp.Command.CONFIGURAR:
                    if packet['protocol'] == 1: #TCP
                        lastConfigProtocol = 1
                        new_host = packet['server_ip']
                        new_port = packet['server_port']
                        sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        sa.connect((new_host, new_port))
                        priv_tcp_addr = sa.getsockname()
                        packet={
                            'command':hp.Command.CONFIGURAROK,
                            'private_ip': priv_tcp_addr[0],
                            'private_port':priv_tcp_addr[1]
                        }
                        data= hp.createRlhpPacket(myData['myid'],555,packet)
                        sock.sendto(data, (host, port))
                        sa.sendall(data)
                        print('enviado')
                    elif packet['protocol'] == 2: #UDP:
                        lastConfigProtocol = 2

                elif packet['command'] == hp.Command.INTERCAMBIAR:
                    if lastConfigProtocol == 1: #TCP
                        print('aqui')
                        peerAddr = tcpPunchHole(packet,new_host,new_port)
                    elif lastConfigProtocol == 2: #UDP
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



