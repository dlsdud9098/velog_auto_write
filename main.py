from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton, 
    QLineEdit,
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QApplication,
    QRadioButton,
    QFileDialog,
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
from selenium.webdriver.common.by import By

# from auto_upload import Ui_Form

class WorkerThread(QThread):
    """백그라운드 작업을 위한 워커 스레드"""
    log_signal = Signal(str, str)  # 메시지, 로그타입
    finished_signal = Signal()
    error_signal = Signal(str)
    
    # def __init__(self, main_window, user_id, password, not_upload_path, upload_path, login_method):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # self.user_id = user_id
        # self.password = password
        # self.not_upoad_path = not_upload_path
        # self.upload_path = upload_path
        # self.login_method = login_method
        self.variables = {}
        self.driver = None
        
    def run(self):
        """백그라운드에서 실행될 메인 작업"""
        try:
            self.log_signal.emit("작업을 시작합니다...", "INFO")
            
            # 1. 데이터 크롤링
            self.crawl_data()
            
            # 2. 브라우저 드라이버 생성
            self.create_driver()
            
            # 3. 로그인
            self.perform_login()
            
            # 4. 콘텐츠 업로드
            self.upload_content()
            
            self.log_signal.emit("모든 작업이 완료되었습니다!", "SUCCESS")
            self.finished_signal.emit()
            
        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}", "ERROR")
            self.error_signal.emit(str(e))
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    def crawl_data(self):
        """데이터 크롤링"""
        self.log_signal.emit("데이터 크롤링을 시작합니다...", "INFO")
        self.move_file_list = {}
        
        file_paths = glob(os.path.join(self.main_window.not_upload_files.text(), '*'))
        self.log_signal.emit(f"{len(file_paths)}개의 파일을 발견했습니다.", "INFO")
        
        for id, file in enumerate(file_paths):
            try:
                file_name = os.path.basename(file)[:-3]
                if '-' in file:
                    _, idx = file.split('-')
                else:
                    idx = file
                
                self.log_signal.emit(f"파일 처리 중: {os.path.basename(file)} ({id+1}/{len(file_paths)})", "INFO")
                
                url = f'https://school.programmers.co.kr/learn/courses/30/lessons/{idx}'
                rq = requests.get(url)
                
                with open(file, 'r', encoding='UTF8') as file_content:
                    code = file_content.read()

                soup = BeautifulSoup(rq.content, 'html.parser')
                title = soup.select_one('#tab > div.challenge-nav-left-menu > div.nav-item.algorithm-nav-link.algorithm-title > span').text.lstrip().rstrip()
                
                self.log_signal.emit(f"문제 제목: {title}", "INFO")

                result = []
                content = str(soup.select_one('body > div.main.theme-dark > div > div.challenge-content.lesson-algorithm-main-section > div.main-section.tab-content > div.guide-section'))
                content = content.split('\n')
                
                # HTML 파싱 로직 (기존과 동일)
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

                velog_content_all = ''.join(result)
                self.variables[f'page_{id}'] = (title, velog_content_all)
                
                # 파일 이동
                file_name = os.path.basename(file)
                new_file_path = os.path.join(self.main_window.upload_files.text(), file_name)

                self.move_file_list[file] = new_file_path
                
                # shutil.move(file, new_file_path)
                
                self.log_signal.emit(f"파일 처리 완료: {file_name}", "SUCCESS")
                
            except Exception as e:
                self.log_signal.emit(f"파일 처리 중 오류: {str(e)}", "ERROR")
                continue

    def create_driver(self):
        """드라이버 생성"""
        self.log_signal.emit("브라우저를 시작합니다...", "INFO")
        self.driver = Driver(
            uc=True,           # undetected 모드
            headless=False,    # 브라우저 창 표시 (디버깅용)
            incognito=True,    # 시크릿 모드
        )

    def perform_login(self):
        """로그인 수행"""
        selected_radio = self.main_window.get_selected_radio()
        
        if selected_radio == 'github':
            self.log_signal.emit('깃허브 로그인을 시작합니다...', "INFO")
            self.github_login()
        elif selected_radio == 'google':
            self.log_signal.emit('구글 로그인을 시작합니다...', "INFO")
            self.google_login()
        else:
            raise Exception('로그인 방법이 선택되지 않았습니다.')

    def google_login(self):
        # print('구글 로그인 시작')
        """구글 로그인"""
        try:
            self.driver.open('https://velog.io/')

            # 로그인 버튼
            self.driver.wait_for_element('//*[@id="html"]/body/div/div[2]/div[2]/div/header/div/div[2]/button', timeout=10)
            self.driver.click('//*[@id="html"]/body/div/div[2]/div[2]/div/header/div/div[2]/button')

            time.sleep(1)
            # 구글 선택
            self.driver.wait_for_element('//*[@id="html"]/body/div/div[3]/div/div[2]/div[2]/div/div[1]/section[2]/div/a[2]', timeout=10)
            self.driver.click('//*[@id="html"]/body/div/div[3]/div/div[2]/div[2]/div/div[1]/section[2]/div/a[2]')

            # 아이디 입력
            self.driver.wait_for_element("input[type='email']", timeout=10)
            self.driver.type("input[type='email']", self.main_window.id.text())
            
            # 다음 버튼
            self.driver.wait_for_element("/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div/button", timeout=10)
            self.driver.click("/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div/button")
            
            # 비밀번호 입력
            self.driver.wait_for_element("input[type='password']", timeout=10)
            self.driver.type("input[type='password']", self.main_window.password.text())
            
            # 다음 버튼
            self.driver.wait_for_element('//*[@id="passwordNext"]/div/button', timeout=10)
            self.driver.click('//*[@id="passwordNext"]/div/button')

            self.log_signal.emit("구글 로그인 완료", "SUCCESS")
            
        except Exception as e:
            self.log_signal.emit(f"구글 로그인 실패: {str(e)}", "ERROR")
            raise

    def github_login(self):
        """깃허브 로그인"""
        try:
            self.driver.get('https://velog.io/')
            time.sleep(1)
            
            # 로그인 버튼
            self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/div/header/div/div[2]/button').click()
            time.sleep(.5)

            # 깃허브 선택
            self.driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div[2]/div[2]/div/div[1]/section[2]/div/a[1]').click()
            time.sleep(.5)
            
            # 아이디 비밀번호 입력, 로그인
            self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/main/div/div[3]/form/input[3]').send_keys(self.main_window.id.text())
            self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/main/div/div[3]/form/div/input[1]').send_keys(self.main_window.password.text())
            self.driver.find_element(By.CSS_SELECTOR, '#login > div.auth-form-body.mt-3 > form > div > input.btn.btn-primary.btn-block.js-sign-in-button').click()

            self.log_signal.emit("깃허브 로그인 완료", "SUCCESS")
            
        except Exception as e:
            self.log_signal.emit(f"깃허브 로그인 실패: {str(e)}", "ERROR")
            raise

    def upload_content(self):
        """콘텐츠 업로드"""
        self.log_signal.emit(f"총 {len(self.variables)}개의 게시물을 업로드합니다...", "INFO")
        
        time.sleep(1) 
        
        for i in range(len(self.variables)):
            try:
                title, velog_content_all = self.variables[f'page_{i}']
                self.log_signal.emit(f"업로드 중: {title} ({i+1}/{len(self.variables)})", "INFO")

                # 새 글 작성
                self.driver.wait_for_element('//*[@id="html"]/body/div/div[2]/div[2]/div/header/div/div[2]/a[3]/button', timeout=10)
                self.driver.click('//*[@id="html"]/body/div/div[2]/div[2]/div/header/div/div[2]/a[3]/button')

                # 제목 작성
                self.driver.wait_for_element('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/textarea')
                self.driver.type('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/textarea', '프로그래머스 ' + title)

                #  태그 입력
                self.driver.wait_for_element('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[2]/div/input')
                self.driver.type('//*[@id="root"]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[2]/div/input', '프로그래머스, 파이썬,')

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

                self.log_signal.emit(f'업로드 완료: {title}', "SUCCESS")
                
            except Exception as e:
                self.log_signal.emit(f'업로드 실패: {title} - {str(e)}', "ERROR")
                continue

        for origin, new in self.move_file_list.items():
            shutil.move(origin, new)

def resource_path(relative_path):
    """PyInstaller 실행 환경에서 파일 경로를 반환"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainMenu(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


        # .ui 파일 로드
        # loader = QUiLoader()
        # ui_file = QFile("ui/auto_upload.ui")
        # ui_file.open(QFile.ReadOnly)
        # self.ui = loader.load(ui_file, self)
        # ui_file.close()

        ui_path = resource_path("ui/auto_upload.ui")
        loader = QUiLoader()
        self.ui = loader.load(ui_path, self)
        self.setCentralWidget(self.ui)

        # 방법 1: 고정 크기 설정
        self.resize(550, 600)  # 너비 800px, 높이 600px
        self.connect_widget()
        self.setup_log_scroll_area()
        self.set_default_radio()
        
        # 워커 스레드 초기화
        self.worker_thread = None

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

        # 라디오 버튼 이벤트 연결
        self.github_radio_btn.clicked.connect(self.on_radio_changed)
        self.google_radio_btn.clicked.connect(self.on_radio_changed)

        # 폴더 선택 버튼 이벤트 연결
        self.upload_btn.clicked.connect(self.select_upload_folder)
        self.not_upload_btn.clicked.connect(self.select_not_upload_folder)

        self.write_btn = self.ui.findChild(QPushButton, 'write_btn')
        self.write_btn.clicked.connect(self.write_content)

    def setup_log_scroll_area(self):
        """로그용 스크롤 영역 설정"""
        if self.logs is None:
            print("ERROR: logs 위젯을 찾을 수 없습니다!")
            return
        
        # logs 위젯에 수직 레이아웃 설정
        self.log_layout = QVBoxLayout(self.logs)
        self.log_layout.setAlignment(Qt.AlignTop)  # 위쪽 정렬
        self.log_layout.setSpacing(2)  # 로그 간격
        self.log_layout.setContentsMargins(5, 5, 5, 5)  # 여백
        
        # 초기 로그
        self.add_logs("프로그램이 시작되었습니다.")

    def add_logs(self, message, log_type='INFO'):
        """로그 메시지 추가"""
        if not hasattr(self, 'log_layout'):
            print("로그 레이아웃이 설정되지 않았습니다!")
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {log_type}: {message}"
        
        # 새 라벨 생성
        log_label = QLabel(log_message)
        log_label.setWordWrap(True)  # 텍스트 줄바꿈 허용
        log_label.setMargin(3)  # 여백 설정
        
        # 로그 타입에 따른 스타일 설정
        if log_type == "ERROR":
            log_label.setStyleSheet("""
                color: red; 
                background-color: #ffe6e6; 
                padding: 4px; 
                border-radius: 3px;
                border-left: 3px solid red;
                margin: 1px;
            """)
        elif log_type == "WARNING":
            log_label.setStyleSheet("""
                color: #ff8c00; 
                background-color: #fff3cd; 
                padding: 4px; 
                border-radius: 3px;
                border-left: 3px solid #ff8c00;
                margin: 1px;
            """)
        elif log_type == "SUCCESS":
            log_label.setStyleSheet("""
                color: green; 
                background-color: #e6ffe6; 
                padding: 4px; 
                border-radius: 3px;
                border-left: 3px solid green;
                margin: 1px;
            """)
        else:  # INFO
            log_label.setStyleSheet("""
                color: black; 
                background-color: #f8f9fa; 
                padding: 4px; 
                border-radius: 3px;
                border-left: 3px solid #6c757d;
                margin: 1px;
            """)
        
        # 레이아웃에 라벨 추가
        self.log_layout.addWidget(log_label)
        
        # 스크롤을 맨 아래로 이동
        QTimer.singleShot(10, self.scroll_to_bottom)
        
        print(log_message)  # 콘솔에도 출력

    def scroll_to_bottom(self):
        """스크롤을 맨 아래로 이동"""
        # logs 위젯의 부모인 ScrollArea 찾기
        scroll_area = self.logs.parent()
        while scroll_area and not isinstance(scroll_area, QScrollArea):
            scroll_area = scroll_area.parent()
        
        if scroll_area:
            scrollbar = scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    # 라디오 버튼 기본 설정
    def set_default_radio(self):
        self.github_radio_btn.setChecked(True)
        self.google_radio_btn.setChecked(False)
        self.add_logs("기본 설정: GitHub 선택됨")

    def on_radio_changed(self):
        """라디오 버튼 변경시"""
        selected = self.get_selected_radio()
        self.add_logs(f"로그인 방법 변경: {selected}")

    # 라디오 클릭하기
    def get_selected_radio(self):
        if self.github_radio_btn.isChecked():
            return 'github'
        if self.google_radio_btn.isChecked():
            return 'google'
        return None
    
    # 업로드할 코드들이 있는 폴더
    def select_not_upload_folder(self):
        self.add_logs("업로드할 폴더 선택 중...")
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "업로드할 코드들이 있는 폴더 선택", 
            "",  # 시작 디렉토리 (빈 문자열이면 현재 디렉토리)
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:  # 폴더가 선택되었으면
            self.not_upload_files.setText(folder_path)
            self.add_logs(f"업로드할 폴더 선택됨: {folder_path}", "SUCCESS")
        else:
            self.add_logs("폴더 선택이 취소되었습니다.", "WARNING")

    # 업로드한 코드들이 있는 폴더
    def select_upload_folder(self):
        self.add_logs("완료된 코드 폴더 선택 중...")
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "업로드한 코드들이 있는 폴더 선택", 
            "",  # 시작 디렉토리 (빈 문자열이면 현재 디렉토리)
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:  # 폴더가 선택되었으면
            self.upload_files.setText(folder_path)
            self.add_logs(f"완료된 코드 폴더 선택됨: {folder_path}", "SUCCESS")
        else:
            self.add_logs("폴더 선택이 취소되었습니다.", "WARNING")

    def write_content(self):
        """메인 작업 시작 (백그라운드에서 실행)"""
        # 입력값 검증
        if not self.not_upload_files.text():
            self.add_logs("업로드할 폴더를 선택해주세요!", "ERROR")
            return
        
        if not self.upload_files.text():
            self.add_logs("완료된 코드 폴더를 선택해주세요!", "ERROR")
            return
        
        if not self.get_selected_radio():
            self.add_logs("로그인 방법을 선택해주세요!", "ERROR")
            return
        
        # 기존 스레드가 실행 중이면 중단
        if self.worker_thread and self.worker_thread.isRunning():
            self.add_logs("이미 작업이 진행 중입니다.", "WARNING")
            return
        
        # 버튼 비활성화
        self.write_btn.setEnabled(False)
        self.write_btn.setText("작업 중...")
        
        # 워커 스레드 시작
        self.worker_thread = WorkerThread(self)
        self.worker_thread.log_signal.connect(self.add_logs)
        self.worker_thread.finished_signal.connect(self.on_work_finished)
        self.worker_thread.error_signal.connect(self.on_work_error)
        self.worker_thread.start()
    
    def on_work_finished(self):
        """작업 완료시"""
        self.write_btn.setEnabled(True)
        self.write_btn.setText("글쓰기 시작")
        self.add_logs("작업이 완료되었습니다!", "SUCCESS")
    
    def on_work_error(self, error_message):
        """작업 오류시"""
        self.write_btn.setEnabled(True)
        self.write_btn.setText("글쓰기 시작")
        self.add_logs(f"작업 중 오류가 발생했습니다: {error_message}", "ERROR")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())