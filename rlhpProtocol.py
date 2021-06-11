import enum

class Command(enum.Enum):
    REGISTRAR=1
    KEEPALIVE=2
    OK=3
    CONECTAR=4
    INTERCAMBIAR=5
    HANDSHAKE=6
    HANDSHAKEOK=7
    KEEPALIVEPEER=8
    SERVICE=9


def processRlhpPacket(packet):
    res={}
    command=Command(packet[0]);
    res['myid']=int.from_bytes(packet[1:3],byteorder='little',signed=False)
    res['sequence']=int.from_bytes(packet[3:5],byteorder='little',signed=False)
    res['command'] = command

    if command==Command.REGISTRAR:
        res['type'] = packet[5]
        res['private_ip']=f'{packet[9]}.{packet[8]}.{packet[7]}.{packet[6]}'
        res['private_port']=int.from_bytes(packet[10:12],byteorder='little',signed=False)
    elif command ==Command.KEEPALIVE:
        pass
    elif command == Command.OK:
        res['identifier'] = int.from_bytes(packet[5:7],byteorder='little',signed=False)
    elif command == Command.CONECTAR:
        res['remotePeer'] = int.from_bytes(packet[5:7],byteorder='little',signed=False)
    elif command == Command.INTERCAMBIAR:
        res['remotePeer'] = int.from_bytes(packet[5:7],byteorder='little',signed=False)
        res['private_ip']=f'{packet[10]}.{packet[9]}.{packet[8]}.{packet[7]}'
        res['private_port']=int.from_bytes(packet[11:13],byteorder='little',signed=False)
        res['public_ip']=f'{packet[16]}.{packet[15]}.{packet[14]}.{packet[13]}'
        res['public_port']=int.from_bytes(packet[17:19],byteorder='little',signed=False)
    elif command == Command.HANDSHAKE:
        pass
    elif command == Command.HANDSHAKEOK:
        pass
    elif command == Command.KEEPALIVEPEER:
        pass
    else:
        print('Unknown command')

    print('<-- ' + str(packet))
    print('<-- ' + str(res))
    return res

def createRlhpPacket(identifier,sequence, dataPacket):
    b1=dataPacket['command'].value.to_bytes(1,'little')
    b2=identifier.to_bytes(2,'little')
    b3=sequence.to_bytes(2,'little')

    if dataPacket['command']==Command.OK:
        b4 = dataPacket['identifier'].to_bytes(2,'little')
        res = b1+b2+b3+b4
    elif dataPacket['command']==Command.REGISTRAR:
        b4_1 = dataPacket['type'].to_bytes(1,'little')
        b4_2 = bytes(map(int,dataPacket['private_ip'].split('.')[::-1]))
        b4_3 = dataPacket['private_port'].to_bytes(2,'little')
        b4=b4_1+b4_2+b4_3
        res = b1+b2+b3+b4
    elif dataPacket['command']==Command.CONECTAR:
        b4 = dataPacket['remotePeer'].to_bytes(2,'little')
        res = b1+b2+b3+b4

    elif dataPacket['command']==Command.INTERCAMBIAR:
        b4_1 = dataPacket['remotePeer'].to_bytes(2,'little')
        b4_2 = bytes(map(int,dataPacket['private_ip'].split('.')[::-1]))
        b4_3 = dataPacket['private_port'].to_bytes(2,'little')
        b4_4 = bytes(map(int,dataPacket['public_ip'].split('.')[::-1]))
        b4_5 = dataPacket['public_port'].to_bytes(2,'little')
        b4=b4_1+b4_2+b4_3+b4_4+b4_5
        res = b1+b2+b3+b4
    else:
        res = b1+b2+b3


    print('--> ' + str(dataPacket))
    print('--> ' + str(res))
    return res
