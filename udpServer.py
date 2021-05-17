import logging
import socket
import sys
from utils import *

logger = logging.getLogger()
addresses = []


def main(host='0.0.0.0', port=9999):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((host, port))
    logger.info("server - waiting connections in: %s:%s", host,port)
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        if data == b'0':
            sock.sendto(b'OK', addr)
            logger.info("connection from: %s - %s", addr, data)
            addresses.append(addr)
        elif data[0:4] == b'CONN':
            command= data.decode('utf-8')
            print(int(command[4]))
            print(addresses)
            sock.sendto(addr_to_msg(addresses[int(command[4])]), addr)
            sock.sendto(b'NEWC', addresses[int(command[4])])
            sock.sendto(addr_to_msg(addr), addresses[int(command[4])])
        elif data == b'LIST':
            sock.sendto(b'LIST\n'+list_of_addresses(addresses), addr)
            
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    main(*addr_from_args(sys.argv))
