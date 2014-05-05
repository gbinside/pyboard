__author__ = 'Roberto'

import threading
import socket
from board import Board, Pawn

HOST = ''
PORT = 5941

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(4)
clients = []  # list of clients connected
lock = threading.Lock()

board = Board()
board.map("""
**************************
*                 *      *
*                 D      *
****************  *      *
      *        *  ********
      *        *   *   * *
      *        *     *   *
      *        S  ********
      *        *  *      *
      **D*******  D      *
      *           *      *
      *           *      *
      ********************
""")
board.reduce_positions()
p1 = Pawn('1Player1', 1)
board.put(9, 1, p1)
p2 = Pawn('2Player2', 1)
board.put(1, 2, p2)
p3 = Pawn('3Player3', 1)
board.put(3, 2, p3)
p4 = Pawn('4Player4', 1)
board.put(3, 1, p4)
enemy = Pawn('Enemy', 2)
board.put(16, 3, enemy)
enemy2 = Pawn('Enemy2', 2)
board.put(17, 4, enemy2)


class BoardServer(threading.Thread):
    def __init__(self, (_socket, address)):
        threading.Thread.__init__(self)
        self.socket = _socket
        self.address = address

    def run(self):
        lock.acquire()
        clients.append(self)
        lock.release()
        print '%s:%s connected.' % self.address
        self.socket.send(str(board))
        self.socket.close()
        print '%s:%s disconnected.' % self.address
        lock.acquire()
        clients.remove(self)
        lock.release()


while True:  # wait for socket to connect
    # send socket to chatserver and start monitoring
    BoardServer(s.accept()).start()