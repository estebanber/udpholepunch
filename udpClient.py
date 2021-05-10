import threading
import logging
import socket
import sys
from utils import *
from time import sleep

logger = logging.getLogger()
addresses = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

def mainReciever(host='127.0.0.1', port=9999):
    sock.sendto(b'0', (host, port))
    while True:
        data=''
        data, addr = sock.recvfrom(1024)
        print(data)
        pck = data[0:4].decode('utf-8')
        if pck == 'LIST':
            print('list received from {}\n{}'.format(addr, data.decode('utf-8')))
            actualizarLista(addresses,data)
        elif pck == 'NEWC':
            addr = msg_to_addr(data)
            sock.sendto(b'0', addr)

def actualizarLista(lista,data):
    listaString = data.decode('utf-8')
    rows = listaString.split('\n')
    for r in rows:
            campos = r.split(' -> ')
            if len(campos)>=2:
                lista[campos[0].split(' ')[1]]=msg_to_addr(campos[1].encode('utf-8'))
    print(lista)


def getCommand():
    while True:
        comm = input('Select client> ')
        if comm == 'N':
            continue
        elif comm == 'S':
            comm = input('Select client> ')
            addr= addresses[comm]
            sock.sendto(b'STOP', addr)
        else:
            addr= addresses[comm]
            sock.sendto(b'STRM', addr)




def mainSender(host='127.0.0.1', port=9999):
    sock.sendto(b'0', (host, port))
    while True:
        data, addr = sock.recvfrom(1024)
        pck = data[0:4].decode('utf-8')
        if pck == 'NEWC':
            addr = msg_to_addr(data)
            sock.sendto(b'0', addr)
        elif pck == 'STRM': #Activate streaming
            count=0;
            while True:
                sleep(1)
                print(f'Sending to {addr}: Dato {count}')
                sock.sendto(bytes(f'Dato {count}\n','utf-8'), addr)
                count=count +1


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    if sys.argv[1] == 'R':
        hilo = threading.Thread(target=getCommand)
        hilo.start()
        argumentos= sys.argv[1:3]
        mainReciever(*addr_from_args(argumentos))
    elif sys.argv[1] == 'S':
        argumentos= sys.argv[1:3]
        mainSender(*addr_from_args(argumentos))

