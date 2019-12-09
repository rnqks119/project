import socketserver, pymysql
import threading

HOST = ''
PORT = 9009
lock = threading.Lock() # syncronized 동기화 진행하는 스레드 생성

class UserManager: # 사용자관리 및 채팅 메세지 전송을 담당하는 클래스
                   # ① 채팅 서버로 입장한 사용자의 등록
                   # ② 채팅을 종료하는 사용자의 퇴장 관리
                   # ③ 사용자가 입장하고 퇴장하는 관리
                   # ④ 사용자가 입력한 메세지를 채팅 서버에 접속한 모두에게 전송
    def __init__(self):
        self.users = {} # 사용자의 등록 정보를 담을 사전 {사용자 이름:(소켓,주소),...}

    def verityUser(self, username, password, conn, addr):
        if username in self.users.keys():
            if password in self.users[username]:
                self.users[username][0:2] = [conn,addr]
                self.users[username][3] = True
                # + conn, addr 로그는 찍어야함
                return 0;
        return 1;

    def addUser(self, username, conn, addr, password, login): # 사용자 ID를 self.users에 추가하는 함수
        if username in self.users: # 이미 등록된 사용자라면
            if self.verityUser(username, password, conn, addr) == 0:
                conn.send('로그인 성공!'.encode('utf-16'))
            else:
                conn.send('로그인 실패!'.encode('utf-16'))
                return
        else:
            # 새로운 사용자를 등록함
            lock.acquire() # 스레드 동기화를 막기위한 락
            self.users[username] = [conn, addr, password, login]
            lock.release() # 업데이트 후 락 해제

        self.sendMessageToAll('[%s]님이 입장했습니다.' %username)
        self.sendMessageToUser('안녕하세요', username)
        print('[%s]님이 입장했습니다.'%username)
        print('+++ 대화 참여자 수 [%d]' %self.userCount())

        return username

    def removeUser(self, username, login): #사용자를 제거하는 함수
        if username not in self.users:
            return
        """ 데이터 베이스 삭제 비활성화
        lock.acquire()
        del self.users[username]
        lock.release()
        """
        self.users[username][3] = login
        self.sendMessageToAll('[%s]님이 퇴장했습니다.' %username)
        print('--- 대화 참여자 수 [%d]' %self.userCount())

    def userCount(self): # 접속중인 사용자 카운팅
        count = 0
        for username in self.users.keys():
            if self.users[username][3] == 1:
                count+=1
        return count

    def messageHandler(self, username, msg): # 전송한 msg를 처리하는 부분
        if msg[0] != '/': # 보낸 메세지의 첫문자가 '/'가 아니면
            self.sendMessageToAll('[%s] %s' %(username, msg))
            return

        if msg.strip() == '/quit': # 보낸 메세지가 'quit'이면
            self.removeUser(username, False)
            return -1

    def sendMessageToAll(self, msg):
        for conn, addr, password, login in self.users.values():
            if login == True:
                conn.send(msg.encode('utf-16'))

    def sendMessageToUser(self, msg, username):
        self.users[username][0].send(msg.encode('utf-16'))

class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()

    def handle(self): # 클라이언트가 접속시 클라이언트 주소 출력
        print('[%s:%s] 연결됨' %(self.client_address[0],self.client_address[1]))
        try:
            username = self.registerUsername()
            msg = self.request.recv(1024)
            while msg:
                print('[%s] %s'%(username,msg.decode('utf-16')))
                if self.userman.messageHandler(username, msg.decode('utf-16')) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)

        except Exception as e:
            print(e)

        print('[%s] 접속종료' %self.client_address[0])
        self.userman.removeUser(username, False)

    def registerUsername(self):
        while True:
            self.request.send('로그인 해주세요'.encode('utf-16'))
            self.request.send('ID : '.encode('utf-16'))
            username = self.request.recv(1024)
            self.request.send('PASSWORD : '.encode('utf-16'))
            password = self.request.recv(1024)
            username = username.decode('utf-16').strip()
            password = password.decode('utf-16').strip()
            if self.userman.addUser(username, self.request, self.client_address, password, True):
                return username

class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def runServer():
    print('+++ 채팅 서버를 시작합니다.')
    print('+++ 채텅 서버를 끝내려면 Ctrl-C를 누르세요.')

    try:
        server = ChatingServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()
    except input() == "quit":
        print('--- 채팅 서버를 종료합니다.')
        server.shutdown()
        server.server_close()

runServer()