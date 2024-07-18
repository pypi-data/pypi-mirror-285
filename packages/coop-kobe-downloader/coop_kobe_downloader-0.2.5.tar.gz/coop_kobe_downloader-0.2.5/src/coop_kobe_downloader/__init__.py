import glob
import os
import time
from coop_kobe_downloader.lib import DriverHelper, Weekday, get_weekday_str, init_logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def main():
    login_id = os.environ.get("LOGIN_ID")
    password = os.environ.get("PASSWORD")
    download_dir = ".output"

    downloader = CoopKobeDownloader(login_id, password, download_dir)
    phase = downloader.get_phase(Weekday.WED)
    downloader.download(phase)


class CoopKobeDownloader:
    def __init__(self, login_id: str, password: str, download_dir: str = None):
        """
        CoopKobeDownloader クラスの初期化。
        """
        self.logger = init_logger()

        # 認証情報を定義
        self.login_id = login_id
        self.password = password

        # ダウンロードディレクトリを定義
        self.download_dir = download_dir

        # ChromeDriverを取得
        try:
            self.driver = self._get_chrome_driver()
        except Exception as e:
            self.logger.error(f"ChromeDriverの取得に失敗しました: {e}")
            self.driver = None

        # 宅配ページの共通URLを定義
        self.base_url = "https://wwwckapp.coop-kobe.net"

    def download(self, phase: str):
        """
        ダウンロード処理

        Parameters:
        * phase: 企画回 (例: `2024062`)
        """
        if self.driver is None:
            self.logger.error(
                "WebDriverが存在しないため、ダウンロード処理をスキップします。"
            )

        self.logger.info("ダウンロード処理を開始します。")
        self.logger.info(f"企画回: {phase}")

        # 宅配ページにログインする
        self._login()

        # 注文書をダウンロードする
        self._download_csv(phase)

        # ChromeDriverを閉じる
        self.driver.quit()

        self.logger.info("ダウンロード処理が完了しました。")

    def get_phase(self, weekday: Weekday, offset: int = 0) -> str:
        """
        企画回を取得

        Parameters:
        * offset: 企画回のオフセット (デフォルト: 0)
          * デフォルト: `0`
          * 過去の回: `n`
          * 未来の回: `-n`
        """
        return get_weekday_str(weekday, offset)

    def _get_chrome_driver(self) -> webdriver.Chrome:
        """
        ChromeのWebDriverを取得
        WebDriverはChromeDriverManagerを通じてインストールされる。

        Returns:
            webdriver.Chrome: ChromeのWebDriverインスタンス
        """
        try:
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=self._get_chrome_options(),
            )
            return driver
        except Exception as e:
            self.logger.error(f"WebDriverのインスタンス作成に失敗しました: {e}")
            return None

    def _login(self):
        """
        宅配ページにログインする
        """
        self.logger.info("ログイン処理を開始します。")
        helper = DriverHelper(self.driver)

        # ログイン画面に遷移
        login_url = f"{self.base_url}/login.html"
        helper.navigate_to_url(login_url)

        # ログインIDを入力
        input_login_id = helper.find_element(By.NAME, "LOGIN_ID")
        helper.input_form(input_login_id, self.login_id)

        # パスワードを入力
        input_password = helper.find_element(By.NAME, "LOGIN_PASS")
        helper.input_form(input_password, self.password)

        # ログインボタンをクリック
        login_button = helper.find_element(By.CLASS_NAME, "p-mypage-part-btn--action")
        helper.click_button(login_button)

        self.logger.info("ログイン処理が完了しました。")

    def _download_csv(self, phase: str):
        """
        注文書のCSVファイルをダウンロードする
        """
        self.logger.info("CSVファイルのダウンロードを開始します。")

        helper = DriverHelper(self.driver)

        # 注文履歴詳細画面に遷移
        history_detail_url = (
            f"{self.base_url}/order/member/historydetail.html?kikaku_ymkai={phase}"
        )
        helper.navigate_to_url(history_detail_url)

        self.logger.info("注文履歴詳細画面にアクセスしました。")

        # ダウンロードボタンをクリック
        download_button = helper.find_element(
            By.CLASS_NAME, "p-order-history-detail-control__dl-btn"
        )
        helper.click_button(download_button)

        # ファイルダウンロード完了まで待機する
        self._wait_for_download()

        self.logger.info("CSVファイルのダウンロードが完了しました。")

    def _get_chrome_options(self) -> ChromeOptions:
        """
        Chromeのオプションを設定

        Returns:
        * 設定済みのChromeOptions
        """

        # ダウンロードディレクトリが指定されていない場合は、オプションを指定しない
        if self.download_dir is None:
            return None

        os.makedirs(self.download_dir, exist_ok=True)

        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_experimental_option(
            "prefs",
            {
                "profile.default_content_settings.popups": 0,
                "download.default_directory": os.path.realpath(self.download_dir),
            },
        )

        return options

    def _wait_for_download(self):
        """
        ファイルダウンロード完了まで待機する
        """
        timeout_second = 10
        for i in range(timeout_second):
            downloaded_files = glob.glob(f"{os.path.realpath(self.download_dir)}\\*.*")

            if all(
                ".crdownload" not in os.path.splitext(file)[1]
                for file in downloaded_files
            ):
                return  # ダウンロードが成功した場合は正常終了

            time.sleep(1)

        raise TimeoutError("ダウンロードが指定時間内に完了しませんでした。")


__all__ = [CoopKobeDownloader, Weekday]
