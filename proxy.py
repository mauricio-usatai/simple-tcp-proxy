import socket
import sys
import select
import time


class TCPProxy:
  def __init__(self, local_port, local_addr, remote_port, remote_addr):
    self.local_port = local_port
    self.local_addr = local_addr
    self.remote_port = remote_port
    self.remote_addr = remote_addr

    self.msg_queue = {}
    self.lsock = []

  def tcp_server(self):
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:
          sock.setblocking(0)
          sock.bind((self.local_addr, int(self.local_port)))
          sock.listen()
          self.lsock.append(sock)
          print('[*] Listening on {0} {1}'  .format(self.local_addr,self.local_port))
          while True:
              readable, writable, exceptional = select.select(self.lsock, [], [])
              for s in readable:
                  if s == sock:
                      rserver =self.remote_conn()
                      if rserver:
                          client, addr = sock.accept()
                          print('Accepted connection {0} {1}'.format(addr[0], addr[1]))
                          self.store_sock(client, addr, rserver)
                          break
                      else:
                          print('the connection with the remote server can\'t be \
                          established')
                          print('Connection with {} is closed'.format(addr[0]))
                          client.close()
                  data = self.received_from(s, 10)
                  print('Adding timeout')
                  time.sleep(1)
                  self.msg_queue[s].send(data)
                  if len(data) == 0:
                      self.close_sock(s)
                      break
                  else:
                      print('Received {} bytes from client '.format(len(data)))
                      self.datadump(data)
      except KeyboardInterrupt:
          print ('Ending server')        
      except Exception as err:
          print('Failed to listen on {}:{} : error : {}'.format(self.local_addr, self.local_port, err))
          sys.exit(0)      
      finally:
          sys.exit(0)

  def remote_conn(self):
    try:
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.connect((self.remote_addr, int(self.remote_port)))
        return remote_sock
    except Exception as e:
        print(e)
        return False

  def store_sock(self, client, addr, rserver):
    self.lsock.append(client)
    self.lsock.append(rserver)
    self.msg_queue[client] = rserver
    self.msg_queue[rserver] = client

  def received_from(self, sock, timeout):
      data = ""
      sock.settimeout(timeout)
      try:
          while True:
              data = sock.recv(4096)
              if not data:
                  break
              data =+ data
      except:
          pass
      return data

  def datadump(self, data):
    print(data)
  
  def close_sock(self, sock):
    print ('End of connection with {}'.format(sock.getpeername()))
    self.lsock.remove(self.msg_queue[sock])
    self.lsock.remove(self.msg_queue[self.msg_queue[sock]])
    serv = self.msg_queue[sock]
    self.msg_queue[serv].close()
    self.msg_queue[sock].close()
    del self.msg_queue[sock]
    del self.msg_queue[serv]


if __name__ == '__main__':
  if len(sys.argv) != 5:
    print('Usage: python3 proxy.py local_port local_addr remote_port remote_addr')
    sys.exit(0)
  
  local_port = sys.argv[1]
  local_addr = sys.argv[2]
  remote_port = sys.argv[3]
  remote_addr = sys.argv[4]
  
  proxy = TCPProxy(local_port, local_addr, remote_port, remote_addr)
  proxy.tcp_server()
