import threading
import logging
import socket
import sys
from utils import *
from time import sleep

logger = logging.getLogger()
myip=[]
addresses = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

def mainReciever(host='127.0.0.1', port=9999):
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
            sock.sendto(comm.encode('utf-8'), (host,port))
            lanPort = sock.getsockname()[1]
            sock.sendto(addr_to_msg((myip[0],lanPort)), (host, port))
            data, addr = sock.recvfrom(1024)
            print(data)
            loc_rem=data.decode('utf-8').split('|')
            addr1 = msg_to_addr(loc_rem[0].encode('utf-8'))
            addr2 = msg_to_addr(loc_rem[1].encode('utf-8'))
            print(addr1,addr2)
            hsok=False
            hnsk=False
            connReady=False
            while not connReady:
                sock.sendto(b'HNSK', addr1)
                sock.sendto(b'HNSK', addr2)
                data, addr = sock.recvfrom(1024)
                print(data)
                if data==b'HNSK':
                    sock.sendto(b'HSOK', addr)
                    hnsk=True;
                elif data==b'HSOK':
                    hsok=True
                if hnsk and hsok:
                    print('Ready')
                    connReady = True
            sleep(1)
            print(f'Asking streaming to {addr}')
            sock.sendto(b'STRM', addr)
            while True:
                data, addr = sock.recvfrom(1024)
                print(data)

def actualizarLista(lista,data):
    listaString = data.decode('utf-8')
    rows = listaString.split('\n')
    for r in rows:
            campos = r.split(' -> ')
            if len(campos)>=2:
                lista[campos[0].split(' ')[1]]=msg_to_addr(campos[1].encode('utf-8'))
    print(lista)



def mainSender(host='127.0.0.1', port=9999):
    sock.sendto(b'0', (host, port))
    lanPort = sock.getsockname()[1]
    sock.sendto(addr_to_msg((myip[0],lanPort)), (host, port))
    while True:
        data, addr = sock.recvfrom(1024)
        com = data[0:4].decode('utf-8')
        print(len(data))
        print(data)
        if com == 'HNSK':
            sock.sendto(b'HSOK', addr)

        if com == 'NEWC':
            data, addr = sock.recvfrom(1024)
            print(data)
            loc_rem=data.decode('utf-8').split('|')
            addr1 = msg_to_addr(loc_rem[0].encode('utf-8'))
            addr2 = msg_to_addr(loc_rem[1].encode('utf-8'))
            print(addr1,addr2)
            hsok=False
            hnsk=False
            connReady=False
            while not connReady:
                sock.sendto(b'HNSK', addr1)
                sock.sendto(b'HNSK', addr2)
                data, addr = sock.recvfrom(1024)
                print(data)
                if data==b'HNSK':
                    sock.sendto(b'HSOK', addr)
                    hnsk=True;
                elif data==b'HSOK':
                    hsok=True
                if hnsk and hsok:
                    print('Ready')
                    connReady = True
            sleep(1)
            data, addr = sock.recvfrom(1024)
            com = data[0:4].decode('utf-8')
            print(com)
        if com == 'STRM': #Activate streaming
            count=0;
            while True:
                sleep(1)
                print(f'Sending to {addr}: Dato {count}')
                sock.sendto(bytes(f'Dato {count}\n','utf-8'), addr)
                count=count +1


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
        mainSender(*addr_from_args(argumentos))

