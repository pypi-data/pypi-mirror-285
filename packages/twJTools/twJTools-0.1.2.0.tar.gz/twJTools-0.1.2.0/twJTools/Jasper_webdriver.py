#
# pip install selenium
# pip install webdriver-manager
# 
from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class WebCrawler:
    def __init__(self, browser='chrome', hidden=False):
        """
        初始化方法。根據提供的選項配置瀏覽器。

        :param browser: 要使用的瀏覽器（'chrome' 或 'firefox'），默認為'chrome'
        :param hidden: 是否隱藏瀏覽器窗口，默認為False
        :param options: 瀏覽器選項對象，用於配置瀏覽器選項，默認為None
        """
        if browser not in ['chrome', 'firefox', 'edge']:
            raise ValueError("Invalid browser option. Choose 'chrome', 'firefox', or 'edge'.")

        if browser == 'chrome':
            options = ChromeOptions()
            options.add_argument("no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=800,600")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument('ignore-certificate-errors')

            if hidden:
                options.add_argument('--headless')

            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )

        elif browser == 'firefox':
            options = FirefoxOptions()
            options.add_argument("--disable-gpu")
            options.add_argument("--width=800")
            options.add_argument("--height=600")
            if hidden:
                options.add_argument('--headless')

            self.driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )

        elif browser == 'edge':
            options = EdgeOptions()
            options.use_chromium = True  # 使用 Chromium 版本的 Edge
            options.add_argument("no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=800,600")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument('ignore-certificate-errors')

            if hidden:
                options.add_argument('--headless')

            self.driver = webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=options
            )

    def wait_for_all_element(self, xpath, timeout=10):
        """
        等待指定的元素加載完成，並返回該元素。

        :param xpath: 要等待的元素的XPath
        :param timeout: 等待超時的時間，默認為10秒
        :return: 成功找到的WebElement對象，如果發生錯誤返回None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            # print(f"找到元素: {xpath}")
            return element
        except Exception as e:
            print(f"等待元素時發生錯誤: {e}")
            return []

    def wait_for_element(self, xpath, timeout=10):
        """
        等待指定的元素加載完成，並返回該元素。

        :param xpath: 要等待的元素的XPath
        :param timeout: 等待超時的時間，默認為10秒
        :return: 成功找到的WebElement對象，如果發生錯誤返回None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            # print(f"找到元素: {xpath}")
            return element
        except Exception as e:
            print(f"等待元素時發生錯誤: {e}")
            return None

    def open_url(self, url, timeout=10):
        """
        打開指定的網址並等待網頁完全加載。

        :param url: 要打開的網址
        :param timeout: 等待超時的時間，默認為10秒
        """
        self.driver.get(url)
        self.wait_for_element(xpath='//body')

    def read_html_element(self, xpath):
        """
        讀取指定HTML元素的內容。

        :param xpath: 要讀取的HTML元素的XPath
        :return: HTML元素的內容，如果發生錯誤則返回None
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            return element.text
        except Exception as e:
            print(f"讀取HTML元素時發生錯誤: {e}")
            return None

    def write_html_element(self, xpath, value):
        """
        寫入內容到指定HTML元素。

        :param xpath: 要寫入的HTML元素的XPath
        :param value: 要寫入的內容
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            self.driver.execute_script("arguments[0].innerText = arguments[1];", element, value)
            print(f"HTML元素的內容已設置為: {value}")
        except Exception as e:
            print(f"寫入HTML元素時發生錯誤: {e}")

    def read_text_input(self, xpath):
        """
        讀取指定文本輸入框(input=text)的值。

        :param xpath: 要讀取的文本輸入框的XPath
        :return: 文本輸入框的值，如果發生錯誤則返回None
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            return element.get_attribute('value')
        except Exception as e:
            print(f"讀取文本輸入框時發生錯誤: {e}")
            return None

    def write_text_input(self, xpath, value):
        """
        寫入值到指定文本輸入框(input=text)。

        :param xpath: 要寫入的文本輸入框的XPath
        :param value: 要寫入的值
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            element.clear()  # 清空輸入框的現有內容
            element.send_keys(value)  # 輸入新的值
            print(f"值 '{value}' 已寫入到文本輸入框: {xpath}")
        except Exception as e:
            print(f"寫入文本輸入框時發生錯誤: {e}")

    def read_checkbox(self, xpath):
        """
        讀取指定勾選框(input=checkbox)的狀態。

        :param xpath: 要讀取的勾選框的XPath
        :return: 勾選框的狀態（True或False），如果發生錯誤則返回None
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            return element.is_selected()
        except Exception as e:
            print(f"讀取勾選框時發生錯誤: {e}")
            return None

    def write_checkbox(self, xpath, checked=True):
        """
        設置指定勾選框(input=checkbox)的狀態。

        :param xpath: 要設置的勾選框的XPath
        :param checked: 要設置的狀態，True表示勾選，False表示不勾選，默認為True
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            current_state = element.is_selected()
            if current_state != checked:
                element.click()
                print(f"勾選框的狀態已設置為: {xpath} {checked}")
            else:
                print(f"勾選框已經是所需狀態: {xpath} {checked}")
        except Exception as e:
            print(f"設置勾選框時發生錯誤: {e}")

    def read_radio_button(self, xpath):
        """
        讀取指定單選框(input=radio)的狀態。

        :param xpath: 要讀取的單選框的XPath
        :return: 單選框的狀態（True或False），如果發生錯誤則返回None
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            return element.is_selected()
        except Exception as e:
            print(f"讀取單選框時發生錯誤: {e}")
            return None

    def write_radio_button(self, xpath):
        """
        設置指定單選框(input=radio)的狀態，選中指定的選項。

        :param xpath: 要設置的單選框的XPath
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            element.click()
            print(f"單選框已選中: {xpath}")
        except Exception as e:
            print(f"設置單選框時發生錯誤: {e}")

    def click_button(self, xpath):
        """
        點擊指定按鈕元素。

        :param xpath: 要點擊的按鈕元素的XPath
        """
        try:
            element = self.wait_for_element(xpath=xpath)
            element.click()
            print(f"點擊按鈕成功: {xpath}")
        except Exception as e:
            print(f"點擊按鈕時發生錯誤: {e}")

    def close(self):
        """
        關閉瀏覽器。
        """
        self.driver.quit()
