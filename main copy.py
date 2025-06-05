from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QTableWidgetItem,
    QTableWidget,
    QMenu,
    QSizePolicy,
    QTabWidget,
    QPushButton, 
    QLineEdit,
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QApplication,
    QRadioButton,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

import sys
import os
import shutil
import requests
from bs4 import BeautifulSoup
from glob import glob
from datetime import datetime

from seleniumbase import Driver
import time
import pyperclip


from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class MainMenu(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # .ui 파일 로드
        loader = QUiLoader()
        ui_file = QFile("ui/auto_upload.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # 방법 1: 고정 크기 설정
        self.resize(550, 600)  # 너비 800px, 높이 600px
        self.connect_widget()


    def connect_widget(self): 
        self.id = self.ui.findChild(QLineEdit, 'id')
        self.password = self.ui.findChild(QLineEdit, 'password')

        self.logs = self.ui.findChild(QWidget, 'logs')

        self.not_upload_files = self.ui.findChild(QLineEdit, 'not_upload_files_dirs')
        self.upload_files = self.ui.findChild(QLineEdit, 'upload_files_dirs')

        self.not_upload_btn = self.ui.findChild(QPushButton, 'not_upload_btn')
        self.upload_btn = self.ui.findChild(QPushButton, 'upload_btn')

        self.github_radio_btn = self.ui.findChild(QRadioButton, 'github')
        self.google_radio_btn = self.ui.findChild(QRadioButton, 'google')

        # self.github_radio_btn.clicked.coinnect(self.on_radio_selected)
        # self.google_radio_btn.clicked.coinnect(self.on_radio_selected)

        # 폴더 선택 버튼 이벤트 연결
        self.upload_btn.clicked.connect(self.select_upload_folder)
        self.not_upload_btn.clicked.connect(self.select_not_upload_folder)

        self.write_btn = self.ui.findChild(QPushButton, 'write_btn')
        self.write_btn.clicked.connect(self.write_content)

    # 라디오 버튼 기본 설정
    def set_default_radio(self):
        self.github_radio_btn.setChecked(True)
        self.google_radio_btn.setChecked(False)

    # 라디오 클릭하기
    def on_radio_selected(self):
        if self.github_radio_btn.isChecked():
            return 'github'
        if self.google_radio_btn.isChecked():
            return 'google'
        
        return None
    
    # 업로드할 코드들이 있는 폴더
    def select_not_upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "업로드할 코드들이 있는 폴더 선택", 
            "",  # 시작 디렉토리 (빈 문자열이면 현재 디렉토리)
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:  # 폴더가 선택되었으면
            self.not_upload_files.setText(folder_path)
            print(f"업로드 폴더 선택됨: {folder_path}")

    # 업로드한 코드들이 있는 폴더
    def select_upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "업로드한 코드들이 있는 폴더 선택", 
            "",  # 시작 디렉토리 (빈 문자열이면 현재 디렉토리)
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:  # 폴더가 선택되었으면
            self.upload_files.setText(folder_path)
            print(f"업로드 폴더 선택됨: {folder_path}")
    
    # 코드 데이터 가져오기
    def crawl_data(self):
        self.variables = {}
        
        file_paths = glob(os.path.join(self.not_upload_files.text(), '*'))
        print(file_paths)
        
        for id, file in enumerate(file_paths):
            file_name = os.path.basename(file)[:-3]
            folder, idx = file.split('-')
            
            
            url = f'https://school.programmers.co.kr/learn/courses/30/lessons/{idx}'
            rq = requests.get(url)
            
            with open(file, 'r', encoding='UTF8') as file_content:
                code = file_content.read()

            soup = BeautifulSoup(rq.content, 'html.parser')

            title = soup.select_one('#tab > div.challenge-nav-left-menu > div.nav-item.algorithm-nav-link.algorithm-title > span').text.lstrip().rstrip()

            result = []
            content = str(soup.select_one('body > div.main.theme-dark > div > div.challenge-content.lesson-algorithm-main-section > div.main-section.tab-content > div.guide-section'))
            content = content.split('\n')
            
            for con in content:
                if ' class' in con:
                    con = con[:con.index(' class')] + con[con.index('">')+1:]

                if '<h6>' or '<h5>' in con:
                    con = con.replace('<h6>', '\n## ')
                    con = con.replace('<h5>', '\n## ')
                
                if '</h6>' or '</h5>' in con:
                    con = con.replace('</h6>', '')
                    con = con.replace('</h5>', '')
                
                if '<div>' in con:
                    con = con.replace('<div>', '')
                if '</div>' in con:
                    con = con.replace('</div>', '')
                
                if '<hr/>' or '</hr>' in con:
                    con = con.replace('</hr>', '\n---\n\n')
                    con = con.replace('<hr/>', '\n---\n\n')

                if '<ul>' or '</ul>' in con:
                    con = con.replace('<ul>', '')
                    con = con.replace('</ul>', '')
                
                if '<li>' in con:
                    con = con.replace('<li>', '\n* ')
                
                if '</li>' in con:
                    con = con.replace('</li>','\n\n')

                if '<p>' or '</p>' in con:
                    con = con.replace('<p>', '')
                    con = con.replace('</p>', '\n')

                if 'code>' in con:
                    con  =con.replace('<code>', '```')
                    con  =con.replace('</code>', '```')
                
                if '<table>' in con:
                    con = con.replace('<table>', '\n<table>')
                
                if '</table>' in con:
                    con = con.replace('</table>', '\n</table>\n')


                if '문제 설명' in con:
                    con = con.replace('## 문제 설명', '## 💡문제 설명\n')
                if '제한사항' in con:
                    con = con.replace('## 제한사항', '## 🚫제한사항\n')
                if '입출력 예 설명' in con:
                    con = con.replace('## 입출력 예 설명', '## 🔍입출력 예 설명\n')
                if '입출력 예' in con:
                    con = con.replace('## 입출력 예', '## 🔢입출력 예\n\n')
                if '테스트 케이스 구성 안내' in con:
                    con = con.replace('## 테스트 케이스 구성 안내', '## 테스트 케이스 구성 안내\n\n')
                

                result.append(con)

            result.append('---\n\n')
            result.append('## 💻코드')
            result.append('\n')
            result.append(f'''
```python
{code}
```
        ''')
            result.append('\n\n')


            # 맨 처음에 사진 추가하기
            result.insert(0, '![](https://velog.velcdn.com/images/dlsdud9098/post/e1464da6-734f-4172-a5d3-8df73b71a328/image.png)')

            # 해당 문제 링크 추가
            result.append(url.replace('.py', '?language=python3'))

            # print(result)

            # result
            velog_content_all = ''.join(result)
            self.variables[f'page_{id}'] = (title, velog_content_all)
            
            file_name = os.path.basename(file)
            new_file_path = os.path.join(self.upload_files.text(), file_name)
            shutil.move(file, new_file_path)

        # return variables

    # 창 띄우기
    def create_driver(self):
        self.driver = Driver(
            uc=True,           # undetected 모드
            headless=False,    # 브라우저 창 표시 (디버깅용)
            incognito=True,    # 시크릿 모드
            # guest_mode=True, # 게스트 모드 (필요시)
        )

    # 구글로 로그인
    def google_login(self):
        self.driver.open('https://v3.velog.io/api/auth/v3/social/redirect/google?next=&isIntegrate=0')

        # 아이디 입력
        self.driver.wait_for_element("input[type='email']", timeout=10)
        self.driver.type("input[type='email']", "remember33330")
        # 다음 버튼
        self.driver.wait_for_element("/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div/button", timeout=10)
        self.driver.click("/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div/button")
        # 비밀번호 입력
        self.driver.wait_for_element("input[type='password']", timeout=10)
        self.driver.type("input[type='password']", "tmddlf795")
        # 다음 버튼
        self.driver.wait_for_element('//*[@id="passwordNext"]/div/button', timeout=10)
        self.driver.click('//*[@id="passwordNext"]/div/button')

        self.driver.open('https://velog.io/')

    # 깃허브로 로그인
    def github_login(self):
        self.driver.get('https://velog.io/')
        time.sleep(1)
        # 로그인 버튼
        self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/div/header/div/div[2]/button').click()
        time.sleep(.5)

        # 깃허브 선택
        self.driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div[2]/div[2]/div/div[1]/section[2]/div/a[1]').click()
        time.sleep(.5)
        # 아이디 비밀번호 입력, 로그인
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/main/div/div[3]/form/input[3]').send_keys('dlsdud9098@naver.com')
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/main/div/div[3]/form/div/input[1]').send_keys('dud7959098@')
        self.driver.find_element(By.CSS_SELECTOR, '#login > div.auth-form-body.mt-3 > form > div > input.btn.btn-primary.btn-block.js-sign-in-button').click()
        # time.sleep(5)
        # 시리즈 선택
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div[2]/div/header/div/div[2]/a[3]/button'))
        )

    # 글쓰기
    def write_content(self):
        self.crawl_data()
        self.create_driver()

        if self.on_radio_selected() == 'github':
            self.github_login()
        elif self.on_radio_selected() == 'google':
            self.google_login()
        else:
            print('아무것도 선택되지 않음')
            return

        for i in range(len(self.variables)):
            title, velog_content_all = self.variables[f'page_{i}']

            # 새 글 작성
            self.driver.wait_for_element('//*[@id="html"]/body/div/div[2]/div[2]/div/header/div/div[2]/a[3]/button', timeout=10)
            self.driver.click('//*[@id="html"]/body/div/div[2]/div[2]/div/header/div/div[2]/a[3]/button')

            # 제목 작성
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/textarea')
            self.driver.type('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/textarea', '프로그래머스 ' + title)

            #  태그 입력
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[2]/div/input')
            self.driver.type('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[2]/div/input', '프로그래머스, 파이썬,')
            # time.sleep(100)

            # 내용 쓰기
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[3]/div/div[6]/div[1]/div/div/div/div[5]')
            self.driver.click('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[3]/div/div[6]/div[1]/div/div/div/div[5]')
            act = ActionChains(self.driver)

            pyperclip.copy(velog_content_all)
            act.key_down(Keys.CONTROL).send_keys("v").perform()
            # 출간하기 버튼 클릭
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div/div[1]/div/div[2]/div/div/button[2]', timeout=10)
            self.driver.click('//*[@id="root"]/div[2]/div/div[1]/div/div[2]/div/div/button[2]')

            # 시리즈 버튼 클릭
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div[2]/div/div[3]/div[1]/section[3]/div/button', timeout=10)
            self.driver.click('//*[@id="root"]/div[2]/div[2]/div/div[3]/div[1]/section[3]/div/button')

            # 프로그래머스 선택
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div[2]/div/div[3]/section/div/div[1]/ul//li[contains(text(), "프로그래머스")]')
            self.driver.click('//*[@id="root"]/div[2]/div[2]/div/div[3]/section/div/div[1]/ul//li[contains(text(), "프로그래머스")]')

            # 선택하기
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div[2]/div/div[3]/section/div/div[2]/button[2]', timeout=10)
            self.driver.click('//*[@id="root"]/div[2]/div[2]/div/div[3]/section/div/div[2]/button[2]')

            time.sleep(5)

            # 출간하기 버튼 클릭
            self.driver.wait_for_element('//*[@id="root"]/div[2]/div[2]/div/div[3]/div[2]/button[2]', timeout=10)
            self.driver.click('//*[@id="root"]/div[2]/div[2]/div/div[3]/div[2]/button[2]')

            # self.add_logs(f'업로드 완료')

        self.driver.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 부모를 None으로 했으니 실제 쓰는 MainWindow에 맞게 조정하세요
    window = MainMenu()
    window.show()
    sys.exit(app.exec())