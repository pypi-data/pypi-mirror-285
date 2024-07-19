import base64
import datetime
import os
import re
import io
import random
import shutil
import smtplib
import traceback
import zipfile
from time import sleep
from pprint import pprint
from email.header import Header
from email.mime.application import MIMEApplication  # 发送附件
from email.mime.multipart import MIMEMultipart  # 发送多个部分
from email.mime.text import MIMEText  # 专门发送正文
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
# import xlwings as xw
from BoschRpaMagicBox.common_functions import WebSapCommonFunctions
urllib3.disable_warnings(InsecureRequestWarning)

# from requests_kerberos import HTTPKerberosAuth, OPTIONAL
# from xlwings import Sheet


def create_error_log(error_log_folder_path: str, error_info: str):
    """This function is used to create error log when there is an error occurred during RPA operation

    Args:
        error_log_folder_path(str): This is the path of folder to save error logs
        error_info(str): This is the error message that need to be added to error log
    """

    if not os.path.exists(error_log_folder_path):
        os.mkdir(error_log_folder_path)

    time_in_path = str(datetime.datetime.now().date())
    with open(error_log_folder_path + os.sep + f'error_log_{time_in_path}.txt', 'a', encoding='utf-8') as file:
        file.write('{time}\n'.format(time=datetime.datetime.now()))
        file.write(error_info)
        file.write('\n')


# def auto_close_messagebox():
#     """This function is used to close message box if user do not click ok to close window
#
#     """
#     handle = win32gui.FindWindow(None, r'Important Message')
#     win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)


# def pop_up_messagebox(message: str, auto_close: bool = True, duration: int = 20):
#     """This function is used for popping up message for users
#
#     :param message: This is the information that RPA will show to users
#     :param duration: This is the duration the message box will show
#
#     Args:
#         message(str): This is the information that RPA will show to users
#         auto_close(bool): This is the flag whether to auto close window if user doesn't close window
#         duration(int): This is the duration for window to show
#     """
#     if auto_close:
#         t = Timer(duration, auto_close_messagebox)
#         t.start()
#     win32api.MessageBox(0, message, "Important Message", win32con.MB_TOPMOST)


# def pop_up_confirm_messagebox(message: str):
#     """This function is used for popping up message for users
#
#     :param message: This is the information that RPA will show to users
#
#     Args:
#         message(str): This is the information that RPA will show to users
#
#     """
#     is_confirm = win32api.MessageBox(0, message, 'Message', win32con.MB_YESNO)
#     return is_confirm


# def create_excel_sample_result(normal_sample_result_list: list, first_number: int, last_number: int, spot_check_for: str,
#                                sample_file_path: str, responsible_person: str, sample_excel_template_file_path, sample_type: str = 'MP-Stichprobe'):
#     """This function is used to create sample result in html format
#
#     Args:
#         normal_sample_result_list(list): This is the sample list out of highest_sample_result_list
#         first_number(int): This is the first number of sample population
#         last_number(int): This is the last number of sample population
#         spot_check_for(str): This is the check point information
#         sample_file_path(str): This is the file path of sample result
#         responsible_person(str): This is the name of all related responsible persons
#         sample_type(str): This is the name of sample type
#         sample_excel_template_file_path(str): This is the file path of sample excel template file
#     """
#     current_time = str(datetime.datetime.now()).split('.')[0]
#     shutil.copy(sample_excel_template_file_path, sample_file_path)
#     sample_app = xw.App(visible=True, add_book=False)
#     sample_book = sample_app.books.open(sample_file_path)
#     sample_sheet: Sheet = sample_book.sheets('Sample')
#     sample_sheet.select()
#     sample_sheet.range('B1').value = spot_check_for
#     sample_sheet.range('B2').value = responsible_person
#     sample_sheet.range('B3').value = current_time
#     sample_sheet.range('B4').value = first_number
#     sample_sheet.range('B5').value = last_number
#     sample_sheet.range('B6').value = sample_type
#
#     sample_size = len(normal_sample_result_list)
#     sample_cut = sample_size // 4 if sample_size % 4 == 0 else sample_size // 4 + 1
#     # start_number=0
#     column_lindex_dict = {0: 'A', 1: 'D', 2: 'G', 3: 'J'}
#     for start_number in range(4):
#         if start_number <= 2:
#             current_sample_list = normal_sample_result_list[start_number * sample_cut:(start_number + 1) * sample_cut]
#         else:
#             current_sample_list = normal_sample_result_list[start_number * sample_cut:]
#
#         current_column = column_lindex_dict[start_number]
#         sample_sheet.range(f'{current_column}10').options(transpose=True).value = current_sample_list
#     sample_sheet.range('A9:K9').expand('down').api.Borders.Weight = 2
#     sample_sheet.autofit('c')
#     sample_book.save()
#     sample_book.close()
#     sample_app.quit()


# def save_sample_history_records(sample_history_file_path: str, sample_history_sheet_name: str, spot_check_for: str, mp_auditor: str, sample_time: str,
#                                 sample_method: str, sample_size: int, sample_file_path: str, sample_file_name: str):
#     """This function is used to save sample operation into history records
#
#     Args:
#         spot_check_for(str): This is the check point information
#         sample_file_path(str): This is the file path of sample result
#         mp_auditor(str): This is the name of all related responsible persons
#         sample_time(str): This is the time for sampling
#         sample_method(str): This is the name of sample method
#         sample_size(int): This is the number of samples
#         sample_history_file_path(str):This is the file path of sample history file
#         sample_history_sheet_name(str): This is the sheet name in sample history file
#         sample_file_name(str): This is the file name of sample file
#     """
#     sample_history_app = xw.App(visible=True, add_book=False)
#     sample_history_book = sample_history_app.books.open(sample_history_file_path)
#     sample_history_sheet: Sheet = sample_history_book.sheets(sample_history_sheet_name)
#     sample_history_sheet.select()
#     target_row_number = sample_history_sheet.used_range.last_cell.row + 1
#     sample_history_sheet.range(f'A{target_row_number}').value = target_row_number - 1
#     sample_history_sheet.range(f'B{target_row_number}').value = spot_check_for
#     sample_history_sheet.range(f'C{target_row_number}').value = mp_auditor
#     sample_history_sheet.range(f'D{target_row_number}').value = sample_time
#     sample_history_sheet.range(f'E{target_row_number}').value = sample_method
#     sample_history_sheet.range(f'F{target_row_number}').value = sample_size
#     sample_history_sheet.range(f'G{target_row_number}').add_hyperlink(address=sample_file_path, text_to_display=sample_file_name)
#     sample_history_sheet.autofit('c')
#     sample_history_book.save()
#     sample_history_book.close()
#     sample_history_app.quit()


# def create_html_sample_result(normal_sample_result_list: list, first_number: int, last_number: int, spot_check_for: str,
#                               sample_file_path: str, responsible_person: str, sample_type: str = 'MP-Stichprobe', save_excel_sample: bool = False,
#                               excel_file_path: str = '', excel_file_name: str = '', sample_history_file_path: str = '',
#                               sample_history_sheet_name: str = 'Sheet1'):
#     """This function is used to create sample result in html format
#
#     Args:
#         normal_sample_result_list(list): This is the sample list out of highest_sample_result_list
#         first_number(int): This is the first number of sample population
#         last_number(int): This is the last number of sample population
#         spot_check_for(str): This is the check point information
#         sample_file_path(str): This is the file path of sample result
#         responsible_person(str): This is the name of all related responsible persons
#         sample_type(str): This is the name of sample type
#         save_excel_sample(bool): Whether to save sample in format of sample tool
#         excel_file_path(str): This is the file path of Excel sample file
#         excel_file_name(str): This is the file name of Excel sample file
#         sample_history_file_path(str):This is the file path of sample history file
#         sample_history_sheet_name(str): This is the sheet name in sample history file
#     """
#     normal_sample_result_list.sort()
#     current_time = str(datetime.datetime.now()).split('.')[0]
#     table_data_list = []
#     with open(sample_file_path, 'w') as sample_file:
#         for sample_type, sample_result_list in {sample_type: normal_sample_result_list}.items():
#             tr_data = ''
#             sample_size = len(sample_result_list)
#             sample_first_number = first_number if sample_type in ['MP-Stichprobe', 'MAX 5'] else 4
#             sample_last_number = last_number if sample_type in ['MP-Stichprobe', 'MAX 5'] else min(last_number, 3)
#             if sample_size > 0:
#                 for index, sample_number in enumerate(sample_result_list):
#                     if index == 0:
#                         tr_data += f'<tr><td>{spot_check_for}</td><td>{responsible_person}</td><td>{current_time}</td><td>{sample_first_number}</td><td>{sample_last_number}</td><td>{sample_type}</td><td>{sample_size}</td><td>{sample_number}</td></tr>'
#                     else:
#                         tr_data += f'<tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>{sample_number}</td></tr>'
#                 table_data = '<table border="1"cellspacing="0"cellpadding="4">' \
#                              '<thead><tr><th>Spot Check For</th><th>DC/MP-Checker</th><th>Date/Time</th><th>First Number</th><th>Last Number</th><th>Sampling</th><th>Sample Size</th><th>Sample Results</th></tr></thead>' \
#                              '<tbody>' \
#                              f'{tr_data}' \
#                              '</tbody></table>'
#                 table_data_list.append(table_data)
#         combine_table_data = '<br/>'.join(table_data_list)
#         main_content = f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{responsible_person} Sample Result</title></head>' \
#                        f'<body><div>{combine_table_data}</div></body></html>'
#         sample_file.write(main_content)
#         if save_excel_sample:
#             save_sample_history_records(sample_history_file_path, sample_history_sheet_name, spot_check_for, responsible_person, current_time,
#                                         sample_type, sample_size, excel_file_path, excel_file_name)


# def generate_random_sample_mp_stichprobe(first_number: int, last_number: int, spot_check_for: str, sample_file_path: str,
#                                          responsible_person: str, save_excel_sample: bool = False, excel_file_path: str = '',
#                                          excel_file_name: str = '', sample_history_file_path: str = '', sample_excel_template_file_path: str = '',
#                                          sample_history_sheet_name: str = 'Sheet1'):
#     """This function is used to generate random sample
#
#     Args:
#         save_excel_sample(bool): Whether to save sample in format of sample tool
#         excel_file_path(str): This is the file path of Excel sample file
#         excel_file_name(str): This is the file name of Excel sample file
#         first_number(int): This is the first number of sample population
#         last_number(int): This is the last number of sample population
#         spot_check_for(str): This is the check point information
#         sample_file_path(str): This is the file path of sample result
#         responsible_person(str): This is the name of all related responsible persons
#         sample_history_file_path(str):This is the file path of sample history file
#         sample_history_sheet_name(str): This is the sheet name in sample history file
#         sample_excel_template_file_path(str): This is the file path of sample excel template file
#     """
#     base_population = last_number - first_number + 1
#     base_population_list = list(range(first_number, last_number + 1))
#     if base_population in range(1, 11):
#         sample_size = 3
#     elif base_population in range(11, 26):
#         sample_size = 5
#     elif base_population in range(26, 51):
#         sample_size = 10
#     elif base_population in range(51, 101):
#         sample_size = 20
#     elif base_population in range(101, 251):
#         sample_size = 24
#     elif base_population in range(251, 501):
#         sample_size = 30
#     elif base_population in range(501, 1001):
#         sample_size = 40
#     elif base_population in range(1001, 2001):
#         sample_size = 50
#     else:
#         sample_size = 60
#
#     sample_size = min(sample_size, last_number)
#
#     normal_sample_result_list = random.sample(population=base_population_list, k=sample_size)
#
#     normal_sample_result_list.sort()
#     if save_excel_sample and os.path.exists(sample_excel_template_file_path):
#         create_excel_sample_result(normal_sample_result_list, first_number, last_number, spot_check_for, excel_file_path, responsible_person,
#                                    sample_excel_template_file_path, 'MP Stichprobe')
#
#     create_html_sample_result(normal_sample_result_list, first_number, last_number, spot_check_for,
#                               sample_file_path, responsible_person, 'MP Stichprobe', save_excel_sample, excel_file_path, excel_file_name,
#                               sample_history_file_path,
#                               sample_history_sheet_name)
#
#     return normal_sample_result_list
#
#
# def generate_random_sample_mp_max_five(first_number: int, last_number: int, spot_check_for: str, sample_file_path: str,
#                                        responsible_person: str, save_excel_sample: bool, excel_file_path: str = '', excel_file_name: str = '',
#                                        sample_history_file_path: str = '', sample_excel_template_file_path: str = '',
#                                        sample_history_sheet_name: str = 'Sheet1'):
#     """This function is used to generate random sample
#
#     Args:
#         first_number(int): This is the first number of sample population
#         last_number(int): This is the last number of sample population
#         spot_check_for(str): This is the check point information
#         sample_file_path(str): This is the file path of sample result
#         responsible_person(str): This is the name of all related responsible persons
#         sample_history_file_path(str):This is the file path of sample history file
#         sample_history_sheet_name(str): This is the sheet name in sample history file
#         save_excel_sample(bool): Whether to save sample in format of sample tool
#         excel_file_path(str): This is the file path of Excel sample file
#         excel_file_name(str): This is the file name of Excel sample file
#         sample_excel_template_file_path(str): This is the file path of sample excel template file
#     """
#     base_population = last_number - first_number + 1
#     base_population_list = list(range(first_number, last_number + 1))
#     sample_size = base_population if base_population <= 5 else 5
#
#     normal_sample_result_list = random.sample(population=base_population_list, k=sample_size)
#
#     normal_sample_result_list.sort()
#     if save_excel_sample and os.path.exists(sample_excel_template_file_path):
#         create_excel_sample_result(normal_sample_result_list, first_number, last_number, spot_check_for, excel_file_path, responsible_person,
#                                    sample_excel_template_file_path, 'MAX 5')
#
#     create_html_sample_result(normal_sample_result_list, first_number, last_number, spot_check_for,
#                               sample_file_path, responsible_person, 'MAX 5', save_excel_sample, excel_file_path, excel_file_name,
#                               sample_history_file_path, sample_history_sheet_name)
#
#     return normal_sample_result_list


# def download_workon_attachment(base_link: str, download_id: str, file_name: str, file_path: str):
#     """This function is used to download workon attachment
#
#     Args:
#         base_link(str): This is the base link of  download link
#         download_id(str): This is the unique id for download attachment
#         file_name(str): This is the file name of attachment
#         file_path(str): This is the file pat for saving attachment
#     """
#     kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
#     download_link = f'{base_link}/{download_id}/{file_name}'
#     res = requests.get(download_link, auth=kerberos_auth)
#     with open(file_path, 'wb') as file:
#         file.write(res.content)


def print_webpage_as_pdf(web_rpa: WebSapCommonFunctions, save_file_path: str):
    """This function is used to

    Args:
        web_rpa(WebSapCommonFunctions): This is the instance of WebSapCommonFunctions
        save_file_path(str): This is the file path to save
    """
    webpage_content = web_rpa.browser.print_page()

    with open(save_file_path, 'wb') as file:
        file.write(base64.b64decode(webpage_content))


def send_email_by_server(nt_account: str, email_password: str, email_address: str, email_body: str, email_header: str, email_subject: str,
                         email_to: list, email_cc: list, attachment_dict: dict,
                         error_log_folder_path: str):
    """This function is used to send emails

    Args:
        nt_account(str): This is the nt account of user
        email_password(str): This is the email password for nt account
        email_address(str): This is the email address of nt account
        email_body(str): This is the email content
        email_header(str): This is the customized sender name instead of actual user nt
        email_subject(str): This is the email subject
        email_to(list): This is the list of to emails
        email_cc(list): This is the list of cc emails
        attachment_dict(dict): This is the dict of attachment info. r.g. {file name： file path}
        error_log_folder_path(str): This is the folder path for saving error log
    """
    mail_host = 'rb-smtp-auth.rbesz01.com'
    # outlook用户名
    mail_user = f'APAC\\{nt_account}'
    # 密码(部分邮箱为授权码)
    mail_pass = f'{email_password}'
    # 邮件发送方邮箱地址
    sender = email_address

    try:
        smtpObj = smtplib.SMTP(mail_host, 25)
        # 连接到服务器
        # smtpObj.connect(mail_host, 25)
        smtpObj.starttls()
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
        receivers = ','.join(email_to)
        ccs = ','.join(email_cc)

        # 设置email信息
        # 邮件内容设置
        message = MIMEMultipart()
        # 邮件主题

        # 发送方信息
        message['From'] = Header(email_header, 'utf-8')
        # 接受方信息
        message['To'] = receivers
        message['Cc'] = ccs

        message['Subject'] = email_subject
        content = MIMEText(email_body, 'html', 'utf-8')
        message.attach(content)
        # 添加附件
        for file_name, file_path in attachment_dict.items():
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    content = file.read()
                att = MIMEApplication(content)
                att.add_header('Content-Disposition', 'attachment', filename=file_name)  # 为附件命名
                message.attach(att)

        # 发送
        smtpObj.sendmail(from_addr=sender, to_addrs=email_to + email_cc, msg=message.as_string())

        # 退出
        smtpObj.quit()
        print(f'-----email is sent successfully!-----')
    except:
        print('Mail sent failed.')
        create_error_log(error_log_folder_path, traceback.format_exc())


# def send_email_by_outlook_terminal(email_to: list, email_cc: list, email_bcc: list, email_subject: str, email_body: str,
#                                    attachment_list: list = None):
#     """This function is used to send emails by using outlook customer terminal
#
#     Args:
#         email_to(list): This is the list of to emails
#         email_cc(list): This is the list of cc emails
#         email_bcc(list): This is the list of bcc email
#         email_body(str): This is the email content
#         email_subject(str): This is the email subject
#         attachment_list(list): This is the list of attachment file path
#
#     """
#
#     if attachment_list is None:
#         attachment_list = []
#     outlook = win32com.client.Dispatch('Outlook.Application')
#     mail_item = outlook.CreateItem(0)
#     mail_item.To = ';'.join(email_to)
#     if email_cc:
#         mail_item.CC = ';'.join(email_cc)
#     if email_bcc:
#         mail_item.BCC = ';'.join(email_bcc)
#     mail_item.Subject = email_subject
#     mail_item.Body = email_body
#     for file_path in attachment_list:
#         mail_item.Attachments.Add(file_path)
#     mail_item.Send()


def transform_amount_into_float_format(str_amount: str, precision=2):
    """This function is used to transform str amount into float format

    Args:
        precision(int): This is the precision requirement
        str_amount(str): This is the amount in string format
    """
    str_amount = str_amount.replace(',', '').replace('，', '').replace('(', '-').replace('（', '-').replace(')', '').replace('）', '')
    if str_amount:
        if str_amount != '-':
            float_amount = round(float(str_amount), precision)
        else:
            float_amount = 0
    else:
        float_amount = 0
    return float_amount


def get_chrome_browser_version(chrome_error_message):
    """This function is used to extract Chrome version info

    Args:
        chrome_error_message(str): This is the error message from exception to SessionNotCreatedException
    """
    chrome_version = ''
    current_version_list = re.findall('.*?Current browser version is (.*?) with binary pfath.*', chrome_error_message)
    if current_version_list:
        chrome_version = current_version_list[0]
    else:
        current_version_list = re.findall('(\d+\.\d+\.\d+\.\d+)', chrome_error_message)
        if current_version_list:
            chrome_version = current_version_list[0]
    return chrome_version


def unzip_chrome_driver(target_file_path, target_folder_path, win_type):
    """This function is used to unzip Chrome driver zip file

    Args:
        target_file_path(str): This the file path of chromedriver.exe
        target_folder_path(str): This is the folder to save chromedriver.exe
        win_type(str): win64 or win32
    """
    existed_file_path = target_folder_path + os.sep + 'chromedriver.exe'
    existed_folder_path = target_folder_path + os.sep + f'chromedriver-{win_type}'
    if os.path.exists(existed_file_path):
        os.remove(existed_file_path)

    if os.path.exists(existed_folder_path):
        shutil.rmtree(existed_folder_path)

    zip_file = zipfile.ZipFile(target_file_path)
    zip_file.extractall(path=target_folder_path)
    zip_file.close()
    sleep(1)
    shutil.move(existed_folder_path + os.sep + 'chromedriver.exe', existed_file_path)


def download_chrome_driver(target_driver_version_list):
    """This function is used to download Chrome driver

    Args:
        target_driver_version_list(list[dict]): This is the list of chrome driver

    """
    is_successful = False
    download_url_dict = {}
    win_type = ''
    current_date = datetime.datetime.now().date()
    for chrome_driver_info in target_driver_version_list:
        if chrome_driver_info['platform'] == 'win64':
            download_url_dict['win64'] = chrome_driver_info['url']
            win_type = 'win64'
        if chrome_driver_info['platform'] == 'win32':
            download_url_dict['win32'] = chrome_driver_info['url']
            win_type = 'win32'
    if download_url_dict.get('win64'):
        download_url = download_url_dict.get('win64')
    elif download_url_dict.get('win32'):
        download_url = download_url_dict.get('win32')
    else:
        download_url = ''

    if download_url:
        print(f'download_url: {download_url}')
        res = requests.get(download_url, timeout=None)
        with open(f'chrome_driver_{current_date}.zip', 'wb') as file:
            file.write(res.content)

        target_file_path = os.getcwd() + os.sep + f'chrome_driver_{current_date}.zip'
        target_folder_path = os.getcwd()
        unzip_chrome_driver(target_file_path, target_folder_path, win_type)
        is_successful = True
    return is_successful


def auto_update_chrome_driver(chrome_driver_version):
    """This function is used to auto download chrome  driver

    Args:
        chrome_driver_version(str): This is the version of  chrome driver

    """
    is_successful = False
    if chrome_driver_version:
        res = requests.get('https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json')
        res_json = res.json()
        chrome_versions = res_json['versions']

        target_version_list = []
        target_driver_version_list = []

        cv1, cv2, cv3, cv4 = [int(v) for v in chrome_driver_version.split('.')]
        for chrome_version_dict in chrome_versions:
            chrome_version = chrome_version_dict['version']
            chrome_driver_list = chrome_version_dict.get('downloads', {'chromedriver': []}).get('chromedriver', [])
            v1, v2, v3, v4 = [int(v) for v in chrome_version.split('.')]
            if chrome_driver_list and v1 == cv1 and v2 == cv2 and v3 <= cv3 and v4 <= cv4:
                if target_version_list:
                    if (v1 >= target_version_list[0]
                            and v2 >= target_version_list[1]
                            and v3 >= target_version_list[2]
                            and v4 >= target_version_list[3]):
                        target_version_list = [v1, v2, v3, v4]
                        target_driver_version_list = chrome_driver_list
                else:
                    target_version_list = [v1, v2, v3, v4]
                    target_driver_version_list = chrome_driver_list
        pprint(target_driver_version_list)
        if target_driver_version_list:
            is_successful = download_chrome_driver(target_driver_version_list)

    return is_successful


def smb_copy_file_local_to_remote(username, password, server_ip, server_name, share_name, local_file_path, remote_file_path, port):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_ip(str): This is the ip address of the public folder, which can be same as server name
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        local_file_path(str): This is the local file path
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    # 建立连接
    conn = SMBConnection(username, password, username, server_name, use_ntlm_v2=True)
    assert conn.connect(server_ip, port)

    with open(local_file_path, 'rb') as file:
        file_obj = io.BytesIO(file.read())
        # 将内容写入新文件
        conn.storeFile(share_name, remote_file_path, file_obj)
        file_obj.close()

    # 断开连接
    conn.close()


def smb_copy_file_remote_to_local(username, password, server_ip, server_name, share_name, local_file_path, remote_file_path, port):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_ip(str): This is the ip address of the public folder, which can be same as server name
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        local_file_path(str): This is the local file path
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    # 建立连接
    conn = SMBConnection(username, password, username,
                         server_name, use_ntlm_v2=True)
    assert conn.connect(server_ip, port)

    with open(local_file_path, 'wb') as file_obj:
        conn.retrieveFile(share_name, remote_file_path, file_obj)
        file_obj.close()

    # 断开连接
    conn.close()


def smb_load_file_obj(username: str, password: str, server_ip: str, server_name: str, share_name: str, remote_file_path: str, port: int = 139):
    """ This function is used to get file object from public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_ip(str): This is the ip address of the public folder, which can be same as server name
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    # 建立连接
    conn = SMBConnection(username, password, username,
                         server_name, use_ntlm_v2=True)
    assert conn.connect(server_ip, port)

    file_obj = io.BytesIO()
    conn.retrieveFile(share_name, remote_file_path, file_obj)
    file_obj.seek(0)

    # 断开连接
    conn.close()

    return file_obj


def smb_delete_file(username, password, server_ip, server_name, share_name, remote_file_path, port=139):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_ip(str): This is the ip address of the public folder, which can be same as server name
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    # 建立连接
    conn = SMBConnection(username, password, username, server_name, use_ntlm_v2=True)
    assert conn.connect(server_ip, port)

    conn.deleteFiles(share_name, remote_file_path)

    # 断开连接
    conn.close()


def smb_create_folder(username, password, server_ip, server_name, share_name, remote_folder_path, port=139):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_ip(str): This is the ip address of the public folder, which can be same as server name
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_folder_path(str): This is the public folder path that folder will be created under share name folder
        port(int): This is the port number of the server name
    """
    # 建立连接
    conn = SMBConnection(username, password, username, server_name, use_ntlm_v2=True)
    assert conn.connect(server_ip, port)
    try:
        conn.createDirectory(share_name, remote_folder_path)
    except OperationFailure:
        pass

    # 断开连接
    conn.close()


def get_bot_variants(bot_url):
    """ This function is used to get bot variants

    Args:
        bot_url(str): This is the url of bot
    """
    container_name = os.environ.get('CONTAINER_NAME', '')
    api_file_path = f'/bot_tasks/{container_name}/Code_Folder/VARIANT_API_SECRET.txt'

    if os.path.exists(api_file_path):
        with open(api_file_path, 'r', encoding='utf-8') as api_file:
            api_secret = api_file.read().strip()

        if api_secret:
            request_data = {
                "queryType": "get_bot_variants",
                "apiCredential": api_secret,
            }
            res = requests.post(url=bot_url, data=request_data, verify=False)
            try:
                bot_variant_dict = res.json()['data']
                return bot_variant_dict
            except:
                return {}
        else:
            return {}

    else:
        return {}
