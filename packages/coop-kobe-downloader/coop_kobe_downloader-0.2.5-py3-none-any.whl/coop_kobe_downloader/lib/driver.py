from .logger import init_logger
from selenium.webdriver import Chrome as webdriver_Chrome
import time


class DriverHelper:
    def __init__(self, driver: webdriver_Chrome):
        """
        DriverHelper クラスの初期化。

        Parameters:
        * driver: webdriverのインスタンス
        * download_dir (str): ダウンロードディレクトリのパス
        """
        self.logger = init_logger()
        self.driver = driver

    def navigate_to_url(self, url: str):
        """
        指定したURLに遷移

        Parameters:
        * url (str): 遷移先のURL
        """
        try:
            self.driver.get(url)
            time.sleep(5)
        except Exception as e:
            self.logger.error(f"ページ遷移時にエラーが発生しました: {e}")

    def find_element(self, type, selector: str):
        """
        指定した要素を探します。

        Parameters:
        * type: 要素の種類
        * selector (str): 要素のセレクター

        Returns:
        * elements[0]: 要素
        """
        elements = self.driver.find_elements(type, selector)
        if elements:
            return elements[0]
        else:
            raise Exception(f"Element not found: {selector}")

    def input_form(self, element, value: str):
        """
        指定した要素に値を入力します。

        Parameters:
        * element: 入力する要素
        * value (str): 入力する値
        """
        element.send_keys(value)
        time.sleep(1)

    def click_button(self, button):
        """
        指定したボタンをクリックします。

        Parameters:
        * button: クリックするボタン
        """
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(2)
