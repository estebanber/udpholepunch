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
        sock.sendto(b'OKOK', addr)
        logger.info("connection from: %s - %s", addr, data)
        addresses.append(addr)
        for a in addresses:
            sock.sendto(b'LIST\n'+list_of_addresses(addresses), a)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    main(*addr_from_args(sys.argv))
