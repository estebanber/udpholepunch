# R-link hole punch
## Caracteristicas
Datos: binarios

## Comandos

* Registro
    * inicia: cliente
    * Registrar, tipo, ipl:puertol, ipp:puertop
    * ok, identificador
    * info, identificador, data
* Keepalive
    * inicia: cliente
    * ka, identificador
* Conectar
    * Solicitar interconeccion con peer
    * conectar,identificador,indentificador,numero de conexiones,protocolo
*  Intercambiar:
    * inicia: servidor
    * interconectar, identificadorPeer, ipl:puertol,ipl:puertol (a ambos peers)
* Handshake:
    * inicia: peer
    * handshake,indentificador,l (ip local)
        Enviar cada 1 mS mientras no Handshake OK
        Esperar handshake y responder handshake OK,idnetificador
        Si timeout reintentar con ip publica

* KeepalivePeer
    * inicia: peer cliente

* Comando
    * inicia: peer cliente
    * solicitar servicio




