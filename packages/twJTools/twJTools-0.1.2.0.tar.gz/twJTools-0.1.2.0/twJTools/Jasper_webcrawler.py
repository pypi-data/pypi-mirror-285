import requests

# pip install beautifulsoup4
from bs4 import BeautifulSoup


class WebCrawler:
    def __init__(self, headers=None):
        """
        初始化方法，設置HTTP標頭。

        :param headers: 可選的HTTP標頭
        """
        self.headers = headers if headers else {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

    def get_html(self, url):
        """
        使用GET請求從指定的URL獲取HTML內容。

        :param url: 要訪問的URL
        :return: URL的HTML內容
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"請求發生錯誤: {e}")
            return None

    def post_html(self, url, data):
        """
        使用POST請求從指定的URL獲取HTML內容。

        :param url: 要訪問的URL
        :param data: 要發送的數據
        :return: URL的HTML內容
        """
        try:
            response = requests.post(url, data=data, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"請求發生錯誤: {e}")
            return None

    def get_element_by_css_selector(self, html, selector):
        """
        根據CSS選擇器獲取HTML中的特定元素。

        :param html: 要解析的HTML內容
        :param selector: 要查找的CSS選擇器
        :return: 匹配的元素內容
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.select(selector)
            return elements if elements else None
        except Exception as e:
            print(f"解析HTML時發生錯誤: {e}")
            return None

    def get_element_by_id(self, html, element_id):
        """
        根據ID獲取HTML中的特定元素。

        :param html: 要解析的HTML內容
        :param element_id: 要查找的元素ID
        :return: 匹配的元素內容
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            element = soup.find(id=element_id)
            return element if element else None
        except Exception as e:
            print(f"解析HTML時發生錯誤: {e}")
            return None