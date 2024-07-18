import datetime
import getpass
import os
from time import sleep
from typing import Tuple

import pyperclip
from threading import Thread
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, \
    MoveTargetOutOfBoundsException, InvalidSessionIdException
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service

from .common_config import *


# from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


def get_sap_web_gui_functions():
    """This function is used to initial WebSapCommonFunctions

    """
    return WebSapCommonFunctions()


class WebSapCommonFunctions:
    """This class is used to design web sap common functions across different t-codes

    """

    def __init__(self):
        """This function is used to initial basic parameters

        """
        self.sap_system = 'poe'
        self.save_folder_path = ''
        self.stop_screenshot_thread = True
        self.thr = None

    @staticmethod
    def clear_save_folder(save_folder_path: str):
        """This function is used to clear save folder

        Args:
            save_folder_path (str): This is the folder path to save downloaded files
        """
        if os.path.exists(save_folder_path):
            for file_name in os.listdir(save_folder_path):
                os.remove(save_folder_path + os.sep + file_name)

    @staticmethod
    def check_file_download_status(save_folder_path: str, file_name: str):
        """This function is used to check whether file has been downloaded successfully

        Args:
            file_name(str): This is the file name of file that will be saved in save folder
            save_folder_path(str): This is the folder path of save folder
        """
        save_file_path = save_folder_path + os.sep + file_name
        sleep(4)
        is_loop = True
        while is_loop:
            for current_file_name in os.listdir(save_folder_path):
                current_save_file_path = save_folder_path + os.sep + current_file_name
                if os.path.getsize(current_save_file_path) != 0 and file_name.upper().strip() in current_file_name.upper().strip():
                    try:
                        os.rename(save_folder_path + os.sep + current_file_name, save_file_path)
                    except:
                        pass
                    else:
                        is_loop = False
                        break
            sleep(4)

    def initial_browser(self, has_save_folder: bool = False, save_folder_path: str = '', has_proxy: bool = True, proxy_area: str = 'hk',
                        is_private: bool = False, is_headless=False, firefox_binary_location: str = '', geckodriver_binary_location: str = '',
                        timeout=1800, auto_get_screenshot=False, time_interval=15, browser_screenshot_tag=''):
        """This function is used to initial FireFox browser

        Args:
            auto_get_screenshot(bool): This is the flag whether to auto get browser screenshots
            time_interval(int): This is the time interval to get screenshot
            browser_screenshot_tag(str): Tag in screenshot name
            is_private(bool): Whether to open a private window
            has_save_folder(bool):This is the flag whether to set save folder path
            save_folder_path(str): This is the folder path of save folder
            has_proxy(bool): This is whether to use proxy when open browser
            proxy_area(str): This is the proxy setting for network.proxy.autoconfig_url
            firefox_binary_location(str): This is the path of firefox.exe
            is_headless(bool): This indicates whether to use headless mode to execute automation task
            timeout(int): This is the timeout setting
            geckodriver_binary_location(str): This is the path of geckodriver.exe
        Returns:
            Tuple[Firefox,WebDriverWait]: [self.browser, self.wait]

        """
        # add new tab setting
        opts = Options()

        opts.set_preference("browser.link.open_newwindow.restriction", 0)
        opts.set_preference("browser.link.open_newwindow", 3)
        # opts.headless = is_headless
        if is_headless:
            opts.add_argument("--headless")
        if firefox_binary_location:
            opts.binary_location = firefox_binary_location
        if is_private:
            opts.add_argument('-private')

        if has_proxy or has_save_folder:
            # profile = FirefoxProfile()
            # proxy setting
            if has_proxy:
                opts.set_preference("network.proxy.type", 2)
                opts.set_preference("network.proxy.autoconfig_url", f'http://rbins-ap.bosch.com/{proxy_area}.pac')

            # default download folder setting
            if has_save_folder:
                opts.set_preference("browser.download.folderList", 2)
                opts.set_preference("browser.download.manager.showWhenStarting", False)
                opts.set_preference("browser.download.dir", f'{save_folder_path}')
                opts.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
                self.save_folder_path = save_folder_path
        if geckodriver_binary_location:
            service = Service(executable_path=geckodriver_binary_location, log_path='geckodriver.log')
            self.browser = webdriver.Firefox(options=opts, service=service)
        else:
            self.browser = webdriver.Firefox(options=opts)
        self.wait = WebDriverWait(self.browser, timeout)

        if auto_get_screenshot:
            self.stop_screenshot_thread = False
            self.thr = Thread(self.auto_get_browser_screenshots, args=[save_folder_path, time_interval, browser_screenshot_tag])
            self.thr.start()

        return self.browser, self.wait

    def auto_get_browser_screenshots(self, save_folder_path, time_interval=15, browser_screenshot_tag=''):
        """ This function is used to auto get browser screenshots

        Args:
            save_folder_path(str): This is the folder to save screenshots
            time_interval(int): This is the time interval to get screenshot
            browser_screenshot_tag(str): Tag in screenshot name
        """

        screenshot_folder_path = save_folder_path + os.sep + 'Screenshots'
        if not os.path.exists(screenshot_folder_path):
            os.mkdir(screenshot_folder_path)

        for file_name in os.listdir(screenshot_folder_path):
            os.remove(screenshot_folder_path + os.sep + file_name)

        while not self.stop_screenshot_thread:
            if time_interval < 15:
                sleep(15)
            else:
                sleep(time_interval)

            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if browser_screenshot_tag:
                screenshot_file_path = screenshot_folder_path + os.sep + f'{browser_screenshot_tag}_{current_time}.png'
            else:
                screenshot_file_path = screenshot_folder_path + os.sep + f'{current_time}.png'

            try:
                self.browser.save_screenshot(screenshot_file_path)
            except InvalidSessionIdException:
                break

    def wait_page_loaded(self):
        """This function is used to wait page loaded

        """
        is_loaded = False
        while not is_loaded:
            page_status = self.browser.execute_script("return document.readyState")
            print('page_status: ', page_status)
            if page_status == 'complete':
                is_loaded = True
            else:
                sleep(1)

    def create_and_switch_tab(self, web_link: str, tab_index: int, close_pre_tab: bool = False, pre_tab_index: int = 0):
        """This function is used to create new tab and switch to it

        Args:
            close_pre_tab(bool): This indicates whether to close history tab
            pre_tab_index(int): This is the history tab index
            web_link(str): This is the link where browser will navigate to
            tab_index(int): This is the index of tab whose index starts from 0. if close_pre_tab is True, this is the tab index after close history tab

        """
        self.browser.execute_script('window.open("","_blank");')
        if close_pre_tab:
            if pre_tab_index:
                self.browser.switch_to.window(self.browser.window_handles[pre_tab_index])
            self.browser.close()
        sleep(1)
        self.browser.switch_to.window(self.browser.window_handles[tab_index])
        self.browser.get(web_link)
        sleep(1)

    def wait_element_presence_by_css_selector(self, css_selector: str):
        """This function is used to wait element by css selector

        Args:
            css_selector(str): This is the css selector of target element
        """
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        sleep(1)

    def wait_element_invisible_by_css_selector(self, css_selector: str):
        """This function is used to wait element by css selector

        Args:
            css_selector(str): This is the css selector of target element
        """
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        sleep(1)

    def wait_invisibility_of_loading_window(self, wait_time_before_check: int = 2):
        """This function is used to wait loading window to disappear

        Args:
            wait_time_before_check(int):This is the wait time before check invisibility of loading window

        """
        sleep(wait_time_before_check)
        self.wait.until(EC.invisibility_of_element_located((By.ID, LOADING_WINDOW_ID_NAME)))
        sleep(2)

    def check_login_error(self):
        """This function is used to check whether password is correct

        """
        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, ERROR_ICON_CSS_SELECTOR)
            except NoSuchElementException:
                try:
                    self.switch_iframe([IFRAME_CSS_SELECTOR])
                    sleep(1)
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_PAGE_HEADER_CSS_SELECTOR)))
                    sleep(1)
                except NoSuchElementException:
                    sleep(1)
                else:
                    return True
            else:
                return False

    def login_sap_with_password(self, sap_user: str = '', sap_password: str = ''):
        """This function is used to log in sap with username and password

        Args:
            sap_user(str): This is the username of current sap system
            sap_password(str):This is the password of sap user
        """
        while True:
            sleep(2)
            try:
                self.browser.find_element(By.CSS_SELECTOR, USERNAME_CSS_SELECTOR)
            except NoSuchElementException:
                try:
                    self.switch_iframe([IFRAME_CSS_SELECTOR])
                    sleep(1)
                    self.browser.find_element(By.CSS_SELECTOR, MAIN_PAGE_HEADER_CSS_SELECTOR)
                except NoSuchElementException:
                    sleep(1)
                else:
                    return True
            else:
                self.fill_input_filed_with_single_value(sap_user, USERNAME_CSS_SELECTOR)
                sleep(1)
                self.fill_input_filed_with_single_value(sap_password, PASSWORD_CSS_SELECTOR)
                sleep(1)
                self.click_or_input_by_css_selector(LOGIN_BUTTON_CSS_SELECTOR, 'click')
                sleep(2)
                return self.check_login_error()

    def login_web_sap(self, sap_system_name: str, sap_user: str, sap_password: str):
        """This function is used to wait sap web page loaded before input t-code

        sleep is the buffer time for assuring page loaded

        Args:
            sap_system_name(str): This is the sap system name
            sap_user(str): This is the username of current sap system
            sap_password(str):This is the password of sap user

        """
        self.browser.delete_all_cookies()
        sleep(2)
        self.browser.get(
            f'https://{sap_system_name}.wdisp.bosch.com/sap/bc/gui/sap/its/webgui?sap-client=011&sap-language=EN#')
        is_login = self.login_sap_with_password(sap_user, sap_password)
        if is_login:
            self.browser.refresh()
            self.wait.until(EC.invisibility_of_element_located((By.ID, CENTER_BOX_ID)))
            sleep(2)
            self.wait.until(EC.invisibility_of_element_located((By.ID, INFO_BOX_ID)))
            sleep(2)
            self.wait_invisibility_of_loading_window()
            return True
        else:
            return False

    def switch_iframe(self, iframe_list: list, loop_check: bool = False):
        """This function is used to switch iframe if there are iframes within html

        Args:
            loop_check(bool): Whether to loop check iframe exists
            iframe_list (list): This is the list of iframe css selectors or names
        """
        is_switch = False
        while not is_switch:
            self.browser.switch_to.default_content()
            for iframe in iframe_list:
                try:
                    iframe_element = self.browser.find_element(By.CSS_SELECTOR, iframe)
                    self.browser.switch_to.frame(iframe_element)
                    is_switch = True
                except NoSuchElementException:
                    is_switch = False
            if not loop_check:
                is_switch = True
            sleep(1)

    def input_t_code(self, t_code: str, iframe_list=None):
        """This function is used to input t-code and click enter

        Args:
            iframe_list(list): This is the list of iframe name
            t_code(str): This is the t-code of task

        """
        if iframe_list is None:
            iframe_list = [IFRAME_CSS_SELECTOR]
        sleep(2)
        if iframe_list:
            self.switch_iframe(iframe_list)
            sleep(1)

        t_code_element = self.browser.find_element(By.CSS_SELECTOR, T_CODE_CSS_SELECTOR)
        t_code_element.clear()
        t_code_element.send_keys(t_code)
        t_code_element.send_keys(Keys.ENTER)

    def clear_single_input_field(self, css_selector: str, is_enter: bool = False):
        """This function is used to clear single input field

        Args:
            is_enter(bool): This is the flag whether to press Enter key
            css_selector(str): This is the css selector of target input field
        """
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        sleep(1)
        target_element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
        target_element.clear()
        if is_enter:
            target_element.send_keys(Keys.ENTER)

    def fill_input_filed_with_single_value(self, single_value: str, css_selector: str, is_enter: bool = False, is_tab=False, click_tip: bool = False,
                                           tip_css_selector=''):
        """This function is used to input single value to single input field

        Args:
            tip_css_selector(str): This is the css selector of target tip/suggestion
            is_enter(bool): This is the flag whether to press Enter key
            is_tab(bool): This is the flag whether to press Tab key
            single_value(str): This is the single value
            css_selector(str): This is the css selector of target input field
            click_tip(bool): Whether to wait and click opinion
        """
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        sleep(1)
        target_element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
        target_element.clear()
        sleep(1)
        actions = ActionChains(self.browser)
        actions.click(target_element)
        actions.send_keys(single_value)
        actions.pause(1)
        actions.perform()
        actions.reset_actions()
        sleep(1)
        if click_tip:
            if not tip_css_selector:
                tip_css_selector = f"div[data-itemvalue1='{single_value}']"
            self.wait_element_presence_by_css_selector(tip_css_selector)
            sleep(1)
            self.click_or_input_by_css_selector(tip_css_selector, 'click')
            sleep(1)
        if is_enter:
            self.press_keyboard_shortcut([Keys.ENTER])
            sleep(1)
        if is_tab:
            self.press_keyboard_shortcut([Keys.TAB])
            sleep(1)
        return target_element

    def input_layout(self, layout: str = ''):
        """This function is used to input layout name

        Args:
            layout(str): This is the name of layout
        """
        layout_element = self.browser.find_element(By.CSS_SELECTOR, LAYOUT_CSS_SELECTOR)
        layout_element.clear()
        layout_element.send_keys(layout)

    def click_execute_button(self):
        """This function is used to click execute button to load data page

        """
        self.click_by_selenium_webdriver(EXECUTION_BUTTON_CSS_SELECTOR)

    def press_keyboard_shortcut(self, keyboard_shortcut_list: list, wait_css_selector: str = '', target_css_selector: str = ''):
        """This function is used to press keyboard shortcut

        Args:
            target_css_selector(str): This is the css selector of target element who will receive key shortcut
            wait_css_selector(str): This is the css selector to wait before press shortcut keys
            keyboard_shortcut_list(list): This is the list of keyboard keys
        """
        if wait_css_selector:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_css_selector)))
        sleep(1)
        action_chains = ActionChains(self.browser)
        if target_css_selector:
            target_element = self.browser.find_element(By.CSS_SELECTOR, target_css_selector)
            action_chains.click(target_element)
            sleep(0.5)
        for keyboard in keyboard_shortcut_list:
            action_chains.key_down(keyboard)
        for keyboard in keyboard_shortcut_list:
            action_chains.key_up(keyboard)
        action_chains.perform()
        sleep(1)
        action_chains.reset_actions()

    def activate_context_click(self, css_selector: str):
        """This function is used to execute context click

        Args:
            css_selector(str): This is the css selector which will receive context click
        """
        self.wait_element_presence_by_css_selector(css_selector)
        target_element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
        action_chains = ActionChains(self.browser)
        action_chains.context_click(target_element).perform()
        sleep(1)
        action_chains.reset_actions()

    def activate_download_excel_file_window(self, wait_css_selector: str = DATA_PAGE_WAIT_CSS_SELECTOR):
        """This function is used to pop up download Excel file window

            Args:
                wait_css_selector(str): This is the css selector to wait before press shortcut keys
        """
        self.press_keyboard_shortcut([Keys.LEFT_SHIFT, Keys.F4], wait_css_selector)

    def select_sap_layout(self, layout_name: str, shortcut_list: list):
        """This function is used to select sap layout

        Args:
            layout_name(str): This is the name of layout
            shortcut_list(list): This is the list of shortcut keys that will activate select layout window

        """
        self.press_keyboard_shortcut(shortcut_list)
        self.wait_invisibility_of_loading_window()
        sleep(1)
        self.wait_element_presence_by_css_selector("#SAPMSSY0120_1-cntTD")
        sleep(1)
        self.click_or_input_by_css_selector("div[title='Find (Ctrl+F)']", 'click')
        sleep(1)
        self.wait_element_presence_by_css_selector("input[title='Search string in Find function in lists']")
        self.fill_input_filed_with_single_value(layout_name,
                                                "input[title='Search string in Find function in lists']", is_enter=True)
        self.wait_element_presence_by_css_selector("#SAPMSSY0120_3-cnt")
        self.click_element_by_key_word('#SAPMSSY0120_3-cnt', "#SAPMSSY0120_3-cnt div.urColorTotalIntensifiedOff",
                                       layout_name)
        sleep(2)
        self.wait_invisibility_of_loading_window()
        self.click_or_input_by_css_selector("div[title='Copy (Enter)']", 'click')
        self.wait_element_invisible_by_css_selector("#SAPMSSY0120_1-cntTD")
        sleep(1)

    def remove_existed_file_with_file_name(self, file_name):
        """This function is used to remove files with incorrect file name

        Args:
            file_name(str): This is the file name of file that will be saved in save folder
        """
        for current_file_name in os.listdir(self.save_folder_path):
            if file_name.upper().strip() in current_file_name.upper().strip():
                os.remove(self.save_folder_path + os.sep + current_file_name)
        sleep(2)

    def input_download_excel_file_name(self, file_name: str):
        """This function used to input excel download file name

        Args:
            file_name(str): This is the file name of Excel file
        """
        # save_file_path = self.save_folder_path + os.sep + file_name
        self.remove_existed_file_with_file_name(file_name)

        switch_result = self.check_window_switch_status(EXCEL_FILE_NAME_INPUT_CSS_SELECTOR, ALWAYS_EXCEL_CSS_SELECTOR)
        if not switch_result['switchResult']:
            self.click_or_input_by_css_selector(ALWAYS_EXCEL_CSS_SELECTOR, 'click')
            sleep(1)
            self.wait_element_presence_by_css_selector(EXCEL_CONTINUE_CSS_SELECTOR)
            ok_button = self.browser.find_element(By.CSS_SELECTOR, EXCEL_CONTINUE_CSS_SELECTOR)
            actions = ActionChains(self.browser)
            actions.click(ok_button)
            actions.perform()
            actions.reset_actions()
            sleep(2)
            try:
                self.browser.find_element(By.CSS_SELECTOR, EXCEL_CONTINUE_CSS_SELECTOR)
            except NoSuchElementException:
                pass
            else:
                self.click_or_input_by_css_selector(EXCEL_CONTINUE_CSS_SELECTOR, 'click')
                sleep(2)
            self.wait_invisibility_of_loading_window()

        while True:
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, EXCEL_FILE_NAME_INPUT_CSS_SELECTOR)))
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, EXCEL_FILE_NAME_INPUT_CSS_SELECTOR)))
                sleep(1)
                self.press_keyboard_shortcut([Keys.DELETE])

                file_name_input_element = self.browser.find_element(By.CSS_SELECTOR, EXCEL_FILE_NAME_INPUT_CSS_SELECTOR)
                actions = ActionChains(self.browser)
                actions.click(file_name_input_element)
                actions.perform()
                actions.reset_actions()
                sleep(1)
                actions = ActionChains(self.browser)
                actions.send_keys(file_name)
                actions.pause(2)
                actions.send_keys(Keys.ENTER)
                actions.perform()
                actions.reset_actions()
                sleep(1)
                break
            except StaleElementReferenceException or ElementNotInteractableException:
                sleep(2)
        sleep(2)
        if not switch_result['switchResult']:
            self.wait_element_invisible_by_css_selector(ALWAYS_EXCEL_CSS_SELECTOR)
            sleep(1)
        self.check_file_download_status(self.save_folder_path, file_name)

    def determine_dynamic_selection_button_index(self, section_name: str, multi_selection_button_index: int):
        """This function is used to dynamically determine multiple selection button index according to user input

        Args:
            section_name(str): This the section name
            multi_selection_button_index(int): This is the index of multiple selection button in G/L account selection or other section
        """
        is_find = False
        div_elements = self.browser.find_elements(By.CSS_SELECTOR,
                                                  f"table[aria-label='{section_name}'] div.lsRasterLayout div")
        div_elements_length = len(div_elements)
        while not is_find and multi_selection_button_index <= div_elements_length:
            try:
                self.browser.find_element(By.CSS_SELECTOR,
                                          f"table[aria-label='{section_name}'] div.lsRasterLayout div:nth-child({multi_selection_button_index}) div[title='Multiple selection']").click()
            except NoSuchElementException:
                multi_selection_button_index += 1
            else:
                is_find = True

        return [is_find, multi_selection_button_index]

    def input_multiple_selection(self,
                                 value_list: list,
                                 tab_index: int = 1,
                                 section_name=SECTION_NAME,
                                 multi_selection_button_index: int = MULTIPLE_SECTION_BUTTON_INDEX,
                                 input_css_path: str = MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR,
                                 clear_section_data: bool = False,
                                 get_screenshot: bool = False,
                                 screenshot_folder_path: str = '',
                                 screenshot_file_name_tag: str = 'error_info',
                                 name_format: str = 'time',
                                 paste_method: str = 'clipboard'
                                 ):
        """This function is used to input multiple selection for company code, gl account and so on

        Args:
            paste_method(str): This is the copy and paste method for multiple input. e.g. clipboard or file
            tab_index(int): This is the tab index of multiple selection
            section_name(str): This the section name
            multi_selection_button_index(int): This is the index of multiple selection button in G/L account selection
            input_css_path(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            clear_section_data(bool): This is the indicator whether delete all section data before pasting new values
            get_screenshot(bool): This is the flag that indicates whether to save screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
        """
        # re-locate multiple selection button
        multiple_index_check_result, multi_selection_button_index = self.determine_dynamic_selection_button_index(
            section_name, multi_selection_button_index)
        if multiple_index_check_result:
            # click multiple selection button
            self.browser.find_element(By.CSS_SELECTOR,
                                      f"table[aria-label='{section_name}'] div.lsRasterLayout div:nth-child({multi_selection_button_index}) div[title='Multiple selection']").click()
            sleep(2)
            self.wait_invisibility_of_loading_window()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, input_css_path)))
            if clear_section_data:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR)))
                sleep(1)
                self.click_or_input_by_css_selector(DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR, 'click')
                sleep(2)
            # click select ranges tab
            if tab_index == 2:
                sleep(3)
                self.click_or_input_by_css_selector(SELECT_RANGES_CSS_SELECTOR, 'click')

            self.wait_multiple_selection_switch(tab_index)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, input_css_path)))
            if paste_method == 'clipboard':
                self.copy_paste_values(value_list, input_css_path)
            elif paste_method == 'file':
                # temp re-write for linux
                self.copy_paste_values(value_list, input_css_path)
                # upload_file_path = self.copy_paste_values_by_file(value_list)
                # os.remove(upload_file_path)

            if get_screenshot:
                self.get_screenshot(screenshot_folder_path, screenshot_file_name_tag, name_format)
                sleep(1)
            self.click_or_input_by_css_selector(COPY_BUTTON_CSS_SELECTOR, 'click')
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, input_css_path)))
        else:
            return False

    def input_multiple_selection_with_index(self,
                                            value_list: list,
                                            multiple_selection_index: int = 1,
                                            tab_index: int = 1,
                                            input_css_path: str = MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR,
                                            clear_section_data: bool = False,
                                            get_screenshot: bool = False,
                                            screenshot_folder_path: str = '',
                                            screenshot_file_name_tag: str = 'error_info',
                                            name_format: str = 'time',
                                            paste_method: str = 'clipboard'
                                            ):

        """This function is used to input multiple selection for company code, gl account and so on

        Args:
            paste_method(str): This is the copy and paste method for multiple input. e.g. clipboard or file
            tab_index(int): This is the tab index of multiple selection
            multiple_selection_index(int): This is the order of Multiple selection button which starts from 1
            input_css_path(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            clear_section_data(bool): This is the indicator whether delete all section data before pasting new values
            get_screenshot(bool): This is the flag that indicates whether to save screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
        """
        multiple_selection_buttons = self.browser.find_elements(By.CSS_SELECTOR, "div[title='Multiple selection']")
        for button_index, multiple_selection_button in enumerate(multiple_selection_buttons):
            if button_index + 1 == multiple_selection_index:
                self.click_or_input_by_element(multiple_selection_button, 'click')
                sleep(2)
                self.wait_invisibility_of_loading_window()
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, input_css_path)))
                if clear_section_data:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR)))
                    sleep(1)
                    self.click_or_input_by_css_selector(DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR, 'click')
                    sleep(2)
                # click select ranges tab
                if tab_index == 2:
                    sleep(3)
                    self.click_or_input_by_css_selector(SELECT_RANGES_CSS_SELECTOR, 'click')
                elif tab_index == 3:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_SINGLE_VALUES_CSS_SELECTOR, 'click')
                elif tab_index == 4:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_RANGES_CSS_SELECTOR, 'click')

                self.wait_multiple_selection_switch(tab_index)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, input_css_path)))
                if paste_method == 'clipboard':
                    self.copy_paste_values(value_list, input_css_path)
                # elif paste_method == 'file':
                #     upload_file_path = self.copy_paste_values_by_file(value_list)
                #     os.remove(upload_file_path)

                if get_screenshot:
                    self.get_screenshot(screenshot_folder_path, screenshot_file_name_tag, name_format)
                    sleep(1)
                self.click_or_input_by_css_selector(COPY_BUTTON_CSS_SELECTOR, 'click')
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, input_css_path)))
                return True

        return False

    def copy_paste_values(self, value_list: list, input_css_selector: str, wait_alert: bool = True, is_enter: bool = True):
        """This function is used to copy and paste values

        Args:
            wait_alert(bool): This indicates whether to click copy button and wait paster warning window pop up
            input_css_selector(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            is_enter(bool): Whether to press enter key
        """
        input_element = self.browser.find_element(By.CSS_SELECTOR, input_css_selector)
        value_list = [item for item in value_list if item.strip()]
        paste_values = '\r\n'.join(value_list)
        pyperclip.copy(paste_values)
        sleep(2)
        action_chains = ActionChains(self.browser)
        if wait_alert:
            self.press_keyboard_shortcut([Keys.SHIFT, Keys.F12])
            self.wait_element_presence_by_css_selector("#UpDownDialogDontAllow-cnt")
            sleep(1)
        action_chains.key_down(Keys.CONTROL, input_element).send_keys('v').key_up(Keys.CONTROL).perform()
        action_chains.reset_actions()
        sleep(1)
        try:
            first_row_element = self.browser.find_element(by=By.CSS_SELECTOR, value=MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR)
            while not first_row_element.get_attribute('value'):
                sleep(1)
                first_row_element = self.browser.find_element(by=By.CSS_SELECTOR, value=MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR)
        except NoSuchElementException or StaleElementReferenceException:
            sleep(2)
        if is_enter:
            self.press_keyboard_shortcut([Keys.ENTER])
            # action_chains = ActionChains(self.browser)
            # action_chains.key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
            # action_chains.reset_actions()
        sleep(2)

    # def copy_paste_values_by_file(self, value_list: list):
    #     """This function is used to copy and paste values by uploading file
    #
    #     Args:
    #         value_list(list): This is the values need to be input
    #     """
    #     nt_account = getpass.getuser()
    #     current_time = str(datetime.datetime.now()).replace('-', '').replace(' ', '').replace(':', '').replace('.', '')
    #     temp_file_path = fr'C:\Users\{nt_account}\Documents\{current_time}.txt'
    #     value_list = [item for item in value_list if item.strip()]
    #     paste_values = '\r\n'.join(value_list)
    #     with open(temp_file_path, 'w', encoding='utf-8') as upload_file:
    #         upload_file.write(paste_values)
    #     sleep(2)
    #     self.press_keyboard_shortcut([Keys.SHIFT, Keys.F11])
    #     self.wait_element_presence_by_css_selector("#UpDownDialogChoose")
    #     sleep(1)
    #     self.click_or_input_by_css_selector("#UpDownDialogChoose", 'click')
    #     sleep(1)
    #     self.wait_com_window_pop_up('#32770', 'File Upload')
    #     self.process_file_upload_com_window('#32770', 'File Upload', temp_file_path)
    #     sleep(3)
    #     self.wait_invisibility_of_loading_window()
    #     sleep(1)
    #     return temp_file_path

    def wait_multiple_selection_switch(self, tab_index: int):
        """This function is used to wait multiple selection tab switch complete

        Args:
            tab_index(int): This is the tab index of multiple selection
        """
        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, f'td.lsTbsPanel2 div:first-child div:nth-child({tab_index}) div[aria-selected="true"]')
            except NoSuchElementException:
                try:
                    self.browser.find_element(By.CSS_SELECTOR, f'td.lsTbsPanel2 div:first-child div[selected="true"]:nth-child({tab_index})')
                except NoSuchElementException:
                    sleep(2)
                else:
                    break
            else:
                break

    def click_or_input_by_css_selector(self, css_selector: str, action_type: str, content: str = ''):
        """Click or input element by using css selector to find it

        Args:
            css_selector(str): This is css selector
            action_type(str): click or input
            content(str): This is the content to be input
        """
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        sleep(1)
        element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
        if action_type == 'click':
            self.browser.execute_script("arguments[0].click();", element)
        elif action_type == 'input':
            self.browser.execute_script(f"arguments[0].value=arguments[1];", element, content)

    def move_to_and_click_element(self, css_selector: str, target_element=None):
        """This function is used to move mouse to element and click

        Args:
            css_selector: This is css selector of element
        """
        actions = None
        try:
            if target_element is None:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
                target_element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
            actions = ActionChains(self.browser)
            try:
                actions.move_to_element(target_element)
                actions.click()
                actions.perform()
            except MoveTargetOutOfBoundsException:
                self.browser.execute_script('arguments[0].scrollIntoView(true);', target_element)
                sleep(2)
                actions.move_to_element(target_element)
                actions.click()
                actions.perform()
            sleep(1)
            # actions.reset_actions()
        except StaleElementReferenceException:
            pass
        finally:
            if actions is not None:
                actions.reset_actions()

    def click_or_input_by_element(self, css_element: WebElement, action_type: str, content: str = ''):
        """Click or input element by using css selector to find it

        Args:
            css_element(WebElement): This is css element
            action_type(str): click or input
            content(str): This is the content to be input
        """
        if action_type == 'click':
            self.browser.execute_script("arguments[0].click();", css_element)
        elif action_type == 'input':
            self.browser.execute_script(f"arguments[0].value=arguments[1];", css_element, content)

    def click_element_by_key_word(self, wait_css_selector: str, target_elements_css_selector: str, key_word: str, click_type: str = 'single',
                                  search_method: str = 'accurate', click_method: str = 'css_selector'):
        """This function is used to click element by key word when there is no effective css selector

        Args:
            wait_css_selector(str): This is the css selector to wait before click target element
            target_elements_css_selector(str): This is the css selector for all siblings elements of target element(contains target element)
            key_word(str): This is the key word to identify target element
            click_type(str): single or double
            search_method(str): accurate or blur
            click_method(str):css_selector or element
        """
        is_find = False
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_css_selector)))
        sleep(1)
        target_elements = self.browser.find_elements(By.CSS_SELECTOR, target_elements_css_selector)
        correct_target_element = None
        element_index = 1
        for target_element in target_elements:
            if search_method == 'accurate' and target_element.text.strip() == key_word or search_method == 'blur' and key_word in target_element.text.strip():
                is_find = True
                if click_method == 'css_selector':
                    self.click_or_input_by_element(target_element, 'click')
                else:
                    self.move_to_and_click_element('', target_element)
                if click_type == 'double':
                    if click_method == 'css_selector':
                        self.click_or_input_by_element(target_element, 'click')
                    else:
                        self.move_to_and_click_element('', target_element)
                correct_target_element = target_element
                break
            element_index += 1
        sleep(1)
        return is_find, correct_target_element, element_index

    def click_by_selenium_webdriver(self, element_css_selector: str):
        """This function is used to click element by selenium original click

        Args:
            element_css_selector(str): This the is css selector of target element
        """
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, element_css_selector)))
        target_element = self.browser.find_element(By.CSS_SELECTOR, element_css_selector)
        target_element.click()

    def get_screenshot(self, screenshot_folder_path: str, screenshot_file_name_tag: str = 'error_info', name_format: str = 'time'):
        """This function is used to get screenshot of current webpage

        Args:
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
        """
        if name_format == 'time':
            date_info = str(datetime.datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')
        else:
            date_info = str(datetime.datetime.now().date())
        screenshot_file_name = f'{screenshot_file_name_tag}_{date_info}.png'
        screen_file_path = screenshot_folder_path + os.sep + screenshot_file_name
        self.browser.save_screenshot(screen_file_path)
        return [screenshot_file_name, screen_file_path]

    def check_target_text_appearance(self, target_text: str, text_css_selector: str, after_text_css_selector: str,
                                     check_method: str = 'equal',
                                     text_tag: str = 'No Data',
                                     case_sensitive: bool = False,
                                     has_screenshot: bool = False,
                                     screenshot_folder_path: str = '',
                                     screenshot_file_name_tag: str = 'No Data',
                                     name_format: str = 'time'):
        """

        Args:
            case_sensitive(bool): This indicates whether to consider the upper and lower case of text
            check_method(str): This is the method to check target text.  e.g. equal, contain, startswith, endswith
            text_tag(str): This is the status which is used to describe situation or result when target text occurs
            target_text(str): This is the target text to detect
            text_css_selector(str): This is the css selector of text element
            after_text_css_selector(str): This is the css selector of element if there is no target text
            has_screenshot(bool): Whether to save screenshot when target text occurs
            screenshot_folder_path(str): This is the folder path of screenshot when target text occurs
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
        """
        check_result = self.check_window_switch_status(after_text_css_selector, text_css_selector, has_screenshot,
                                                       screenshot_folder_path, screenshot_file_name_tag, name_format)
        check_result['text_tag'] = text_tag
        if not check_result['switchResult']:
            text_element_content = self.browser.find_element(By.CSS_SELECTOR, text_css_selector).text.strip()
            if not case_sensitive:
                target_text = target_text.upper()
                text_element_content = text_element_content.upper()

            if check_method == 'equal' and text_element_content == target_text:
                check_result['is_text'] = True
            elif check_method == 'contain' and target_text in text_element_content:
                check_result['is_text'] = True
            elif check_method == 'startswith' and text_element_content.startswith(target_text):
                check_result['is_text'] = True
            elif check_method == 'endswith' and text_element_content.endswith(target_text):
                check_result['is_text'] = True

        return check_result

    def check_window_switch_status(self, target_css_selector: str,
                                   before_target_css_selector: str = ERROR_ICON_CSS_SELECTOR,
                                   has_screenshot: bool = False,
                                   screenshot_folder_path: str = '',
                                   screenshot_file_name_tag: str = 'error_info',
                                   name_format: str = 'time'
                                   ):
        """This function is used to check whether there are temp elements before loading target element

        Args:
            has_screenshot(bool): Whether to save screenshot when there is an error window popping up
            screenshot_folder_path(str): This is the folder path of screenshot when there is an error occurred
            target_css_selector(str): This is the selector whose occurrence indicates data is loaded successfully
            before_target_css_selector(str): This is the selector whose occurrence indicates that there is temp element
            before loading target element
            name_format(str): This indicates whether user date or datetime to name screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
        """
        check_result = self.check_data_load_status(target_css_selector, before_target_css_selector, has_screenshot,
                                                   screenshot_folder_path, screenshot_file_name_tag, name_format)
        check_result['switchResult'] = not check_result['isError']
        return check_result

    def check_data_load_status(self, success_css_selector: str,
                               error_css_selector: str = ERROR_ICON_CSS_SELECTOR,
                               has_screenshot: bool = False,
                               screenshot_folder_path: str = '',
                               screenshot_file_name_tag: str = 'error_info',
                               name_format: str = 'time'
                               ):
        """This function is used to check whether there are errors when loading data by clicking execution button

        Args:
            has_screenshot(bool): Whether to save screenshot when there is an error window popping up
            screenshot_folder_path(str): This is the folder path of screenshot when there is an error occurred
            success_css_selector(str): This is the selector whose occurrence indicates data loaded successfully
            error_css_selector(str): This is the selector whose occurrence indicates that there is an error or no data
            name_format(str): This indicates whether user date or datetime to name screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
        """
        check_result = {'isError': False, 'Screenshot Path': '', 'Screenshot Name': ''}
        is_loop = True
        sleep(3)
        self.wait_invisibility_of_loading_window()
        while is_loop:
            try:
                self.browser.find_element(By.CSS_SELECTOR, success_css_selector)
            except NoSuchElementException:
                try:
                    self.browser.find_element(By.CSS_SELECTOR, error_css_selector)
                except NoSuchElementException:
                    sleep(2)
                else:
                    check_result['isError'] = True
                    is_loop = False
            else:
                is_loop = False

        if has_screenshot:
            screenshot_file_name, screen_file_path = self.get_screenshot(screenshot_folder_path,
                                                                         screenshot_file_name_tag,
                                                                         name_format)
            check_result['Screenshot Path'] = screen_file_path
            check_result['Screenshot Name'] = screenshot_file_name

        return check_result

    def wait_file_upload_confirmation_dialog(self):
        """This function is used to wait file upload confirmation dialog window and click ok button

        """
        sleep(1)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, UPLOAD_CONFIRM_BUTTON_CSS_SELECTOR)))
        sleep(1)
        self.click_or_input_by_css_selector(UPLOAD_CONFIRM_BUTTON_CSS_SELECTOR, 'click')
        sleep(1)

    # @staticmethod
    # def wait_com_window_pop_up(window_class: str, window_name: str):
    #     """This function is used to wait COM upload or save window pop up
    #
    #     Args:
    #         window_class(str): This is the class of window
    #         window_name(str): This is the window title
    #     """
    #     is_loop = True
    #     while is_loop:
    #         sleep(1)
    #         hwnd = win32gui.FindWindow(window_class, window_name)
    #         if hwnd != 0:
    #             is_loop = False

    # @staticmethod
    # def process_file_upload_com_window(window_class: str, window_name: str, file_path: str):
    #     """This function is used to input file path to COM popup file upload window
    #
    #     Args:
    #         window_class(str): This is the class of window
    #         window_name(str): This is the window title
    #         file_path(str): This is the file path that need to be uploaded
    #
    #     """
    #     hwnd = win32gui.FindWindow(window_class, window_name)
    #     win32gui.ShowWindow(hwnd, win32con.HIDE_WINDOW)
    #     a1 = win32gui.FindWindowEx(hwnd, None, "ComboBoxEx32", None)
    #     a2 = win32gui.FindWindowEx(a1, None, "ComboBox", None)
    #     hwnd_filename = win32gui.FindWindowEx(a2, None, "Edit", None)
    #     win32gui.SendMessage(hwnd_filename, win32con.WM_SETTEXT, None, file_path)
    #     sleep(1)
    #     hwnd_save = win32gui.FindWindowEx(hwnd, None, "Button", None)
    #     win32gui.PostMessage(hwnd_save, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    #     win32gui.PostMessage(hwnd_save, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    #     sleep(1)

    def quit_browser(self):
        """This function is used to quit browser

        """
        if not self.stop_screenshot_thread:
            self.stop_screenshot_thread = True
            if self.thr is not None:
                self.thr.join()

        self.browser.quit()
