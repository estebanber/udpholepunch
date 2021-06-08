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


def processRlhpPacket(packet):
    res={}
    command=Command(packet[0]);
    identifier=int.from_bytes(packet[1:3],byteorder='little',signed=False)
    sequence=int.from_bytes(packet[3:5],byteorder='little',signed=False)


    if command==Command.REGISTRAR:
        res['command'] = Command.REGISTRAR
        res['type'] = packet[5]
        res['private_ip']=f'{packet[9]}.{packet[8]}.{packet[7]}.{packet[6]}'
        res['private_port']=int.from_bytes(packet[10:12],byteorder='little',signed=False)
    elif command ==Command.KEEPALIVE:
        pass
    elif command == Command.OK:
        pass
    elif command == Command.INTERCAMBIAR:
        pass
    elif command == Command.HANDSHAKE:
        pass
    elif command == Command.HANDSHAKEOK:
        pass
    elif command == Command.KEEPALIVEPEER:
        pass
    else:
        print('Unknown command')

    return res

def createRlhpPacket(identifier,sequence, dataPacket):
    b1=dataPacket['command'].value.to_bytes(1,'little')
    b2=identifier.to_bytes(2,'little')
    b3=sequence.to_bytes(2,'little')

    if dataPacket['command']==Command.OK:
        b4 = dataPacket['identifier'].to_bytes(2,'little') 
        return b1+b2+b3+b4
    elif dataPacket['command']==Command.REGISTRAR:
        b4_1 = dataPacket['type'].to_bytes(1,'little') 
        b4_2 = bytes(map(int,dataPacket['private_ip'].split('.')[::-1]))
        b4_3 = dataPacket['private_port'].to_bytes(2,'little')
        b4=b4_1+b4_2+b4_3
        return b1+b2+b3+b4
    else:
        return b1+b2+b3

    

