import sys, webbrowser, requests, ctypes, socket
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from bs4 import BeautifulSoup
#from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QToolTip, QAction, qApp, QDesktopWidget, \
#    QHBoxLayout, QVBoxLayout, QWidget, QTextEdit, QTabWidget
#from PyQt5.QtGui import QIcon, QFont
#from PyQt5.QtCore import QCoreApplication, QDate, Qt

HOST = '13.209.174.89'
PORT = 9009

""" Lambda 연결(테스트는 클라이언트에서 하지만 실제론 서버에서 작동)
link = "https://rta2983gfl.execute-api.ap-northeast-2.amazonaws.com/default/myHelloWorld"
headers = {'auth':'v89uh45378uv4h3587vh34598ygh3458gyu43h5tu34'}
res = requests.get(link, headers=headers)
print(res.json())
"""

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.date = QDate.currentDate()
        self.initUI()

    def initUI(self):

        # 메인 탭 생성
        mainTabs = QTabWidget()
        mainTabs.addTab(FirstTab(), '홈')
        mainTabs.addTab(SecondTab(), '상품 작업')
        mainTabs.addTab(ThirdTab(), '상품 관리')
        mainTabs.setStyleSheet("QTabBar::tab {width: 100px; }")

        # ToolTip 폰트, 사이즈 지정
        QToolTip.setFont(QFont('SansSerif', 10))

        # 텍스트 에디터 생성
        self.te = QTextEdit()
        self.te.setText("https://detail.1688.com/offer/571298975261.html") # 테스트용
        self.te.setAcceptRichText(False)

        # 링크 추출 버튼
        btn_send = QPushButton('추출')
        btn_send.setToolTip('추출 버튼 입니다')
        btn_send.resize(btn_send.sizeHint())
        btn_send.clicked.connect(self.urlOut)

        # 종료 버튼
        btn = QPushButton('종료')
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QCoreApplication.instance().quit)

        # 환율
        country = '중국 위안 CNY'
        URL = 'https://finance.naver.com/marketindex/exchangeDetail.nhn?marketindexCd=FX_CNYKRW'
        page = requests.get(URL).text
        soup = BeautifulSoup(page, 'html.parser')
        ex_rate = soup.find('option', text=country).get('value')
        label1 = QLabel(self)
        label1.setText('환율: '+ex_rate+'원'+\
                       '\t\t접속자: n/n'+\
                       '\t\t사용만료: n일 n시간 n분 n초 남음')
        # 접속자, 사용기간만료는 네트워크 연동이 필요하므로 아직 추가 안함
        label1.setAlignment(Qt.AlignCenter)
        label1.repaint()

        # 세로박스
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_send)
        hbox.addWidget(btn)
        hbox.addStretch(1)

        # 가로박스
        grid = QGridLayout()
        grid.addWidget(mainTabs, 0, 0)
        grid.addWidget(label1, 1, 0)
        #vbox.addWidget(self.te) # 주소 입력 칸
        #vbox.addLayout(hbox) # 추출, 종료 버튼

        # 그리드 레이아웃 설정
        window = QWidget()
        window.setLayout(grid)
        self.setCentralWidget(window)

        # 프로그램 셋팅
        myappid = u'mycompany.myproduct.subproduct.version' # ~
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid) # 작업표시줄 아이콘 표시

        self.setWindowTitle('프로그램 개발')
        self.setWindowIcon(QIcon('web.png'))
        self.setGeometry(0, 0, 800, 500)
        self.statusBar().showMessage(self.date.toString(Qt.DefaultLocaleLongDate))
        self.center()
        self.show()

    # 프로그램 중앙 실행 함수
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 링크 추출 함수
    def urlOut(self):
        if 'http' is not self.te.toPlainText()[:5]:
            return

        url = self.te.toPlainText()
        r = requests.get(url)

        tx = r.text
        soup = BeautifulSoup(tx, 'html.parser')
        print("크롤링완료")
        fi = soup.find_all('div', attrs={'class': 'region-custom region-detail-feature region-takla ui-sortable region-vertical'})
        fi2 = soup.find_all('div', attrs={'class': 'desc-lazyload-container'})
        print("검색완료")
        filepath = open("hello.html", "w", encoding='utf-8')
        filepath.write(str(fi))
        print("쓰기완료")
        filepath.close()
        print("파일완료")
        webbrowser.open("file:///C:/Users/HJJ%20Sub/PycharmProjects/test01/hello.html")
        print("파일 띄우기 완료")


# 홈 탭
class FirstTab(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        subTabs = QTabWidget()
        subTabs.addTab(subFirstTab(), '공지사항')
        subTabs.addTab(subSecondTab(), '문의사항')
        subTabs.setStyleSheet("QTabBar::tab {width: 100px; }")

        grid = QGridLayout()
        grid.addWidget(subTabs)

        self.setLayout(grid)

# 공지사항 탭
class subFirstTab(FirstTab):
    def __init__(self):
        super().__init__()

    #@property
    def initUI(self):
        # 공지사항 테이블
        self.notice = QTableView()
        self.model = QStandardItemModel(self)
        self.notice.setModel(self.model)
        self.notice.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.notice.setSelectionMode(QAbstractItemView.SingleSelection)
        self.notice.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.notice.setShowGrid(True)
        self.notice.verticalHeader().setVisible(False)
        #notice.setFocusPolicy(Qt.NoFocus) 포커스 해제인데 궁극적으로 아래꺼가 짱
        self.notice.setStyle(Style())
        self.notice.setStyleSheet("margin-bottom: 1px;border-bottom:2px solid;font-weight:bold;")
        
        # 데이터 추가
        self.model.setHorizontalHeaderLabels(["번호", "제목", "날짜"])
        for i in range(20, 0, -1):
            row = []
            item = [QStandardItem(str(i)), QStandardItem("0.0.0."+str(i)+" 버전 패치 안내"), QStandardItem("날짜,시간"+str(i))]
            for j in range(0,3):
                item[j].setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter|Qt.AlignCenter)
            self.model.appendRow(item)
        #self.notice.clicked.connect(self.getNoticeData)
        self.notice.doubleClicked.connect(self.getNoticeData)

        self.notice.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.notice.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.notice.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)

        # 박스 레이아웃
        grid = QGridLayout()
        grid.addWidget(self.notice)
        self.setLayout(grid)
    #@initUI.setter

    # 공지에 데이터 넣기
    def getNoticeData(self, index):
        #indget = self.notice.currentIndex()
        data = self.notice.model().index(index.row(), 1)
        getData = self.notice.model().data(data)

        dig = QDialog(None, Qt.WindowTitleHint)

        label1 = QLabel(dig)
        label1.setText(getData)
        label1.setAlignment(Qt.AlignCenter)
        btn = QPushButton('종료')
        btn.resize(btn.sizeHint())
        btn.clicked.connect(dig.close)
        QWhatsThis.leaveWhatsThisMode()

        grid = QGridLayout()
        grid.addWidget(label1, 0, 0)
        grid.addWidget(btn, 1, 0)
        dig.setLayout(grid)

        dig.setWindowTitle(getData)
        dig.setGeometry(0, 0, 300, 300)

        MyApp.center(dig)
        dig.setWindowModality(Qt.ApplicationModal)
        dig.exec_()

# 문의사항 탭
class subSecondTab(FirstTab):
    def __init__(self):
        super().__init__()

    def initUI(self):
        lan_group = QGroupBox('Select Your Language')
        combo = QComboBox()
        list = ['Korean', 'English', 'Chinese']
        combo.addItems(list)

        vbox1 = QVBoxLayout()
        vbox1.addWidget(combo)
        lan_group.setLayout(vbox1)

        learn_group = QGroupBox('Select What You Want To Learn')
        korean = QCheckBox('Korean')
        english = QCheckBox('English')
        chinese = QCheckBox('Chinese')

        vbox2 = QVBoxLayout()
        vbox2.addWidget(korean)
        vbox2.addWidget(english)
        vbox2.addWidget(chinese)
        learn_group.setLayout(vbox2)

        button = QPushButton('전송하기')
        button.clicked.connect(self.msgSendButton)

        # 텍스트 에디터 생성
        self.te = QTextEdit()
        self.te.setAcceptRichText(False)

        grid = QGridLayout()
        grid.addWidget(self.te)
        grid.addWidget(button)
        self.setLayout(grid)

    def serverLogin(self): # 세션로그인
        id = "rnqks123"
        password = ""

    def msgSendButton(self): # 메시지전송(추후엔 펑션메시지 전송으로 대체)
        msg = self.te.toPlainText()
        #server.send(msg.encode('utf-16'))

# 상품 작업 탭
class SecondTab(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        lan_group = QGroupBox('Select Your Language')
        combo = QComboBox()
        list = ['Korean', 'English', 'Chinese']
        combo.addItems(list)

        vbox1 = QVBoxLayout()
        vbox1.addWidget(combo)
        lan_group.setLayout(vbox1)

        learn_group = QGroupBox('Select What You Want To Learn')
        korean = QCheckBox('Korean')
        english = QCheckBox('English')
        chinese = QCheckBox('Chinese')

        vbox2 = QVBoxLayout()
        vbox2.addWidget(korean)
        vbox2.addWidget(english)
        vbox2.addWidget(chinese)
        learn_group.setLayout(vbox2)

        vbox = QVBoxLayout()
        vbox.addWidget(lan_group)
        vbox.addWidget(learn_group)
        self.setLayout(vbox)

# 상품 관리 탭
class ThirdTab(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        lbl = QLabel('Terms and Conditions')
        text_browser = QTextBrowser()
        text_browser.setText('This is the terms and conditions')
        checkbox = QCheckBox('Check the terms and conditions.')

        vbox = QVBoxLayout()
        vbox.addWidget(lbl)
        vbox.addWidget(text_browser)
        vbox.addWidget(checkbox)

        self.setLayout(vbox)

# 마우스 포커싱 점선 해제 스타일
# QWidget.setStyle(Style())
# while True:
class Style(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget):
        if element == QStyle.PE_FrameFocusRect:
            return
        super().drawPrimitive(element, option, painter, widget)

def rcvMsg(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode('utf-16'))
        except:
            pass

class loginLogic(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        lbl = QLabel('Terms and Conditions')
        text_browser = QTextBrowser()
        text_browser.setText('This is the terms and conditions')
        checkbox = QCheckBox('Check the terms and conditions.')

        vbox = QVBoxLayout()
        vbox.addWidget(lbl)
        vbox.addWidget(text_browser)
        vbox.addWidget(checkbox)

        self.setLayout(vbox)
        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('web.png'))
    ex = loginLogic()
    sys.exit(app.exec_())


    # 서버 연결 부분
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((HOST, PORT))
    except Exception as e:
        print("Error : ", e)
        exit()
    else:
        t = Thread(target=rcvMsg, args=(server,))
        t.daemon = True
        t.start()
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon('web.png'))
        ex = MyApp()
        sys.exit(app.exec_())