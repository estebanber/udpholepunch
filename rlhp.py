import logging
import socket
import sys
from utils import *

import rlhpProtocol as hp

logger = logging.getLogger()
addresses = []
localAddr = []

class PeerRecords():
    data=[]
    def addRecord(self,rec):
        self.data.append(rec)
        return len(self.data)-1
    def getRecord(self,idn):
        pass
    def addInfo(self,rec):
        pass
    def getAddr(self,idn):
        pass
    def print(self):
        print('========================================================')
        for i,d in enumerate(self.data):
            print(f'{i}\t{d["type"]}\t{d["private_ip"]}:{d["private_port"]}\t{d["public_ip"]}:{d["public_port"]}')
        print('========================================================')
peers=PeerRecords()


def main(host='0.0.0.0', port=9999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((host, port))
    logger.info("server - waiting connections in: %s:%s", host,port)
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        if data == b'0': continue
        print(data,addr)
        processedData = hp.processRlhpPacket(data)
        print(processedData)        
        if processedData['command'] == hp.Command.REGISTRAR:
            newPeer = {
                'type':processedData['type'],
                'private_ip':processedData['private_ip'],
                'private_port':processedData['private_port'],
                'public_ip':addr[0],
                'public_port':addr[1]
            }
            ident = peers.addRecord(newPeer)
            peers.print()
            sock.sendto(hp.createRlhpPacket(0,666,{'command':hp.Command.OK,'identifier':ident}), addr)
            logger.info("connection from: %s - %s", addr, data)
        elif processedData.command == Command.INFO:
            peers.addInfo(processedData)
        elif processedData.command == Command.CONECTAR:
            oid=processedData.identifier
            pid=processedData.peerIdentifier
            sock.sendto(createRlhpPacket(0,666,{}), peers.getAddr(oid))
            sock.sendto(createRlhpPacket(0,666,{}), peers.getAddr(pid))
        elif processedData.command == Command.LISTAR:
            sock.sendto(createRlhpPacket(0,666,{}), addr)
        else:
            print(data)
            
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    main(*addr_from_args(sys.argv))
