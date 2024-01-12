from PyQt5 import QtWidgets, QtGui, QtCore
from gui import Ui_MainWindow
from qt_material import apply_stylesheet
import requests
import human_readable as hr
import re
import time
import json
import dots
import SAG
import save_gui
from PyQt5.QtCore import QThread


EMAIL_REG = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
def get_current_ip():
    print('Getting current IP')
    return requests.get('https://api.ipify.org', timeout=5).text


def increment_ip_counter(ip):
    try:
        with open('counter.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {'ip': {}}

    if ip not in data['ip']:
        data['ip'][ip] = {'count': 0, 'last_update': time.time()}

    data['ip'][ip]['count'] += 1
    data['ip'][ip]['last_update'] = time.time()

    with open('counter.json', 'w') as f:
        json.dump(data, f)

    return data['ip'][ip]['count']

def get_ip_counter(ip):
    try:
        with open('counter.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return 0

    return data['ip'].get(ip, {'count': 0})['count']

def get_last_update(ip):
    try:
        with open('counter.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return 0

    return data['ip'].get(ip, {'last_update': 0})['last_update']


class UpdateTitleThread(QThread):
    def __init__(self, brand, window):
        super().__init__()
        self.window = window
        self.brand = brand
        self.ip = None

    def run(self):
        while True:
            self.window.setWindowTitle(f'{self.brand} | Fetching IP...')
            try:
                self.ip = get_current_ip()
                count = get_ip_counter(self.ip)
                last_update = get_last_update(self.ip)
                if last_update == 0:
                    last_update = 'Never'
                else:
                    last_update = hr.date_time(int(time.time()-last_update))
                self.window.setWindowTitle(f'{self.brand} | IP: {self.ip} | {count} Accounts Made | Last: {last_update}')
            except:
                self.window.setWindowTitle(f'{self.brand} | No Internet Connection')
            finally:
                time.sleep(5)

from PyQt5.QtCore import QThread, pyqtSignal

class AccountGeneratorThread(QThread):
    account_generated = pyqtSignal(str, str, str)  # signal with three string parameters
    account_failed = pyqtSignal(str, str, str)  # signal with three string parameters

    def __init__(self, username, password, email, webhook):
        super().__init__()
        self.username = username
        self.password = password
        self.email = email
        self.webhook = webhook

    def run(self):
        # generate account using self.username, self.password, self.email
        try:
            SAG.create_steam_account(email=self.email, password=self.password, username=self.username, webhook=self.webhook)
        except:
            self.account_failed.emit(self.username, self.password, self.email)
            return

        # emit signal when account is generated
        self.account_generated.emit(self.username, self.password, self.email)

class GuiLogic(Ui_MainWindow):
    def __init__(self, app):
        super().__init__()
        self.setupUi(app)

        app.setWindowIcon(QtGui.QIcon('design\logo.ico'))


        save_gui.init(self.webhookBrand)       

        app.setWindowTitle(f'{self.webhookBrand.text()} | Fetching IP...')
        self.title_thread = UpdateTitleThread(window=app, brand=self.webhookBrand.text())
        self.title_thread.start()


        self.originalEmailAddress.textChanged.connect(self.estimateDotCombination)
        save_gui.init(self.originalEmailAddress)
        
        self.emailCombinationNumber.valueChanged.connect(lambda v: self.uniqueEmailAddress.setText(str(dots.email_combination(self.originalEmailAddress.text(), v))))
        save_gui.init(self.emailCombinationNumber)


        save_gui.init(self.webhookGroupBox)
        save_gui.init(self.webhookUrl)
        self.testWebhookButton.clicked.connect(self.testWebhook)

        
        


        self.chromeExecutablePathLocate.clicked.connect(self.locateChromeExeFile)
        save_gui.init(self.chromePathTextEdit)

        self.passwordLengthSlider.valueChanged.connect(lambda v: self.passwordLengthLabel.setText(str(v)))
        self.passwordLengthSlider.valueChanged.emit(self.passwordLengthSlider.value())
        save_gui.init(self.passwordLengthSlider)

        self.usernameLengthSlider.valueChanged.connect(lambda v: self.usernameLengthLabel.setText(str(v)))
        self.usernameLengthSlider.valueChanged.emit(self.usernameLengthSlider.value())
        save_gui.init(self.usernameLengthSlider)

        self.generateAccountsButton.clicked.connect(self.generateAccount)
        self.KILL_LABEL, self.START_LABEL = 'Terminate', 'Generate'
        self.generateLabels = {True: self.KILL_LABEL, False: self.START_LABEL}


        self.account_generator_thread = None
        print("set account generator thread to none", type(self.account_generator_thread), f'{self.account_generator_thread is not None}')

    def generateAccount(self):


        if self.account_generator_thread is None:
            self.generateAccountsButton.setText(self.KILL_LABEL)
        else:
            self.generateAccountsButton.setText(self.START_LABEL)
            print("Terminating thread")
            self.account_generator_thread.terminate()
            self.account_generator_thread = None
            return
        print(f'Generating account, {self.generateAccountsButton.text() == self.KILL_LABEL} {self.account_generator_thread is not None}')

        print(self.title_thread.ip)
        if get_ip_counter(self.title_thread.ip) >= 1:
            last_update = get_last_update(self.title_thread.ip)
            last_update = hr.time_delta(int(time.time() - last_update))
            self.show_message('Warning', 
            'You have already created an account with this IP address.\nLast account created: ' + last_update + '\nPlease be aware that Steam will put you through captcha hell if you create too many accounts in a short period of time on the same IP.')


        if not self.originalEmailAddress.text() or not self.originalEmailAddress.text().strip():
            self.show_message('Error', 'Invalid Email Address entered')
            return
        
        if not self.uniqueEmailAddress.text() or not self.uniqueEmailAddress.text().strip():
            self.show_message('Error', 'Invalid unique Email Address entered.\nTry increasing the email combination number and try again.')
            return

        webhook = None
        if self.webhookGroupBox.isChecked():
            webhook = SAG.Webhook(self.webhookUrl.text(), self.webhookBrand.text())

        self.account_generator_thread = AccountGeneratorThread(username=random_string(self.usernameLengthSlider.value()), password=random_string(self.passwordLengthSlider.value()), email=self.uniqueEmailAddress.text(), webhook=webhook)
        self.account_generator_thread.account_generated.connect(self.on_account_generated)
        self.account_generator_thread.account_failed.connect(lambda username, password, email: self.show_message('Error', f'Error creating account\n{username} | {password} | {email}'))
        self.account_generator_thread.start()


                                     
    def on_account_generated(self):
        # Increment IP Counter
        increment_ip_counter(self.title_thread.ip)

        self.account_generator_thread = None
        self.generateAccountsButton.setText(self.START_LABEL)

        # Increment Email Counter
        dots.increment_email_counter(self.uniqueEmailAddress.text())

        # Increase combo number
        self.emailCombinationNumber.setValue(self.emailCombinationNumber.value() + 1)
        self.show_message('Success', 'Account created successfully!')


    def testWebhook(self):
        print("Testing webhook...")
        try:
            webhook = SAG.Webhook(self.webhookUrl.text(), self.webhookBrand)
            webhook.test_webhook()
            print("Webhook test successful!")
            self.show_message('Success', 'Webhook test successful!')
        except Exception as err:
            self.show_message('Error', f'Invalid Webhook URL\n{err}')
            print("Webhook test failed!")
            print(err)

    def popEmailList(self):
        # Pop the first email from the list

        if not self.emailAddressListTextEdit.text() or not self.emailAddressListTextEdit.text().strip():
            self.show_message('Error', 'Invalid Email Address List File')
            return

        with open(self.emailAddressListTextEdit.text(), 'r') as f:
            emails = f.readlines()
            email = emails.pop(0)
        
        with open(self.emailAddressListTextEdit.text(), 'w') as f:
            f.writelines(emails)
        
        self.remainingEmailLabel.setText(f'{len(emails)} emails remaining')

        print(f'Popped {email} from the email list, {len(emails)} emails remaining')

        self.emailAddress.setText(email.strip())

    def locateEmailAddressList(self):
        dlg = QtWidgets.QFileDialog(directory='emails')
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilter("Text files (*.txt)")
        
        filenames = []

        if dlg.exec_():
            filenames = dlg.selectedFiles()
        
        if len(filenames) == 0:
            return
        self.emailAddressListTextEdit.setText(filenames[0])

    def locateChromeExeFile(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilter("Executable files (*.exe)")
        
        filenames = []

        if dlg.exec_():
            filenames = dlg.selectedFiles()
        
        if len(filenames) == 0:
            return
        self.chromePathTextEdit.setText(filenames[0])

    def estimateDotCombination(self, email):
        print("Estimating Dot Combination")
        if re.match(EMAIL_REG, email):
            self.dotCombinationsLabel.setText(f'Combinations: {dots.estimateDotCombination(email)}')
        else:
            self.dotCombinationsLabel.setText(f'Combinations: Invalid Email')
    
    def generateDotCombination(self):
        print("Generating Dot Combination")
        # Regex match

        if not re.match(EMAIL_REG, self.dotCombinationEmailAddress.text()):
            self.show_message('Error', 'Invalid Email')
            return
        
        # Get email address list file name
        filename = self.input_dialog('List Filename', 'The name of the file for the list of email combinations you are about to generate.\ne.g \'email_list\' or \'emails\'.')
        if not filename or not filename.strip() or filename.strip() == '':
            self.show_message('Error', 'Invalid Filename')
            return
        
        filename = filename.strip()

        s = time.time()
        email = self.dotCombinationEmailAddress.text()
        email_dots = dots.email_combinations(email)
        print(f'Generated {len(email_dots)} email combinations in {time.time() - s} seconds')


        with open(f'emails\\{filename}.txt', 'w') as f:
            for email in email_dots:
                f.write(email + '\n')
        
        self.show_message('Success', f'Generated {len(email_dots)} email combinations and saved them to {filename}.txt\nS')
            
    def show_message(self, title, message):
        msg = QtWidgets.QMessageBox(self.centralwidget)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def input_dialog(self, title, message):
        text, ok = QtWidgets.QInputDialog.getText(self.centralwidget, title, message)
        if ok:
            return text
        else:
            return None
        
def random_string(length):
    pool = string.ascii_letters + string.digits
    return "".join(random.choice(pool) for i in range(length))






if __name__ == "__main__":
    import sys, ctypes, random, string
    myappid = f'company.cooker.{"".join([random.choice([random.choice(string.ascii_lowercase), random.choice(string.digits)]) for c in range(16)])}' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QtWidgets.QApplication(sys.argv)
    extra = {
    'font_family': 'Roboto',
    'font_size': '10px',
    'line_height': '13px',
    # Density Scale
    'density_scale': '-1',
}
    apply_stylesheet(app, theme='design\\teal.xml', extra=extra, )

    MainWindow = QtWidgets.QMainWindow()
    ui = GuiLogic(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
