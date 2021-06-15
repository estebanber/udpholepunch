import logging
import socket
import sys
from utils import *

import rlhpProtocol as hp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()
TCP_port = 20003
myPublicIP = '127.0.0.1'
addresses = []
localAddr = []

class PeerRecords():
    data=[]
    def __init__(self):
        self.data=[]
    def addRecord(self,rec):
        self.data.append(rec)
        return len(self.data)-1
    def setRecord(self, rec,recId):
        if (len(self.data) <= recId):
            self.data=self.data+['']*(recId-len(self.data)+1)
        self.data[recId]=rec

    def getRecord(self,idn):
        pass
    def addInfo(self,rec):
        pass
    def getAddr(self,idn):
        d=self.data[idn]
        return d["private_ip"],d["private_port"],d["public_ip"],d["public_port"]
    def print(self):
        print('========================================================')
        for i,d in enumerate(self.data):
            print(f'{i}\t{d["type"]}\t{d["private_ip"]}:{d["private_port"]}\t{d["public_ip"]}:{d["public_port"]}')
        print('========================================================')
peers=PeerRecords()
tcpPeers=PeerRecords()


def main(host='0.0.0.0', port=9999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((host, port))
    logger.info("server - waiting connections in: %s:%s", host,port)
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        if data == b'0': continue
        processedData = hp.processRlhpPacket(data)
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
            logger.info("connection from: %s - %s", addr, 'NUEVO PEER')
        elif processedData['command'] == hp.Command.CONECTAR:
            receiver_id=processedData['myid']
            sender_id=processedData['remotePeer']
            rpip, rpp, rPip, rPp = peers.getAddr(receiver_id)
            spip, spp, sPip, sPp = peers.getAddr(sender_id)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', TCP_port))
            s.listen(1)
            packet={
                'command':hp.Command.CONFIGURAR,
                'connections': 1,
                'protocol':1,
                'mode':1,
                'server_ip':myPublicIP,
                'server_port':TCP_port
            }
            sock.sendto(hp.createRlhpPacket(0,666,packet), (sPip,sPp))
            packet={
                'command':hp.Command.CONFIGURAR,
                'connections': 1,
                'protocol':1,
                'mode':2,
                'server_ip':myPublicIP,
                'server_port':TCP_port
            }
            sock.sendto(hp.createRlhpPacket(0,666,packet), (rPip,rPp))
            configurarok = 0
        elif processedData['command'] == hp.Command.CONFIGURAROK:
            configurarok = configurarok + 1
            if configurarok==2:
                conn1, addr = s.accept()
                print(addr)
                tcpData = conn1.recv(1024)
                processedTcpData = hp.processRlhpPacket(tcpData)
                newPeer = {
                    'type':0,
                    'private_ip':processedTcpData['private_ip'],
                    'private_port':processedTcpData['private_port'],
                    'public_ip':addr[0],
                    'public_port':addr[1]
                }
                ident = tcpPeers.setRecord(newPeer,processedTcpData['myid'])
                tcpPeers.print()
                conn2, addr = s.accept()
                print(addr)
                tcpData = conn2.recv(1024)
                processedTcpData = hp.processRlhpPacket(tcpData)
                newPeer = {
                    'type':0,
                    'private_ip':processedTcpData['private_ip'],
                    'private_port':processedTcpData['private_port'],
                    'public_ip':addr[0],
                    'public_port':addr[1]
                }
                ident = tcpPeers.setRecord(newPeer,processedTcpData['myid'])
                tcpPeers.print()

                receiver_id=0
                sender_id=1
                rpip, rpp, rPip, rPp = tcpPeers.getAddr(receiver_id)
                spip, spp, sPip, sPp = tcpPeers.getAddr(sender_id)

                _, _, rPipu, rPpu = peers.getAddr(receiver_id)
                _, _, sPipu, sPpu = peers.getAddr(sender_id)

                packet={
                    'command':hp.Command.INTERCAMBIAR,
                    'remotePeer': receiver_id,
                    'private_ip':rpip,
                    'private_port':rpp,
                    'public_ip':rPip,
                    'public_port':rPp
                }
                sock.sendto(hp.createRlhpPacket(0,666,packet), (sPipu,sPpu))
                packet={
                    'command':hp.Command.INTERCAMBIAR,
                    'remotePeer': sender_id,
                    'private_ip':spip,
                    'private_port':spp,
                    'public_ip':sPip,
                    'public_port':sPp
                }
                sock.sendto(hp.createRlhpPacket(0,666,packet), (rPipu,rPpu))
        elif processedData['command'] == hp.Command.UDP:
            receiver_id=processedData['myid']
            sender_id=processedData['remotePeer']
            rpip, rpp, rPip, rPp = peers.getAddr(receiver_id)
            spip, spp, sPip, sPp = peers.getAddr(sender_id)

            packet={
                'command':hp.Command.INTERCAMBIAR,
                'remotePeer': receiver_id,
                'private_ip':rpip,
                'private_port':rpp,
                'public_ip':rPip,
                'public_port':rPp
            }
            sock.sendto(hp.createRlhpPacket(0,666,packet), (sPip,sPp))
            packet={
                'command':hp.Command.INTERCAMBIAR,
                'remotePeer': sender_id,
                'private_ip':spip,
                'private_port':spp,
                'public_ip':sPip,
                'public_port':sPp
            }
            sock.sendto(hp.createRlhpPacket(0,666,packet), (rPip,rPp))
        elif processedData['command'] == hp.Command.LIST:
            sock.sendto(hp.createRlhpPacket(0,666,{}), addr)
        else:
            print(data)

if __name__ == '__main__':
    main(*addr_from_args(sys.argv))
