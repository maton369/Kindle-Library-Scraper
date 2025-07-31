# kindle_scraper.py

import csv
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# .env から環境変数を読み込む
load_dotenv()
AMAZON_EMAIL = os.getenv("AMAZON_EMAIL")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")
AMAZON_COOKIES = os.getenv("AMAZON_COOKIES")

# ブラウザ起動設定（必要に応じてヘッドレス化）
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=/Users/maton/ChromeProfileForSelenium")
options.add_argument(
    "--profile-directory=Default"
)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

try:
    driver.get("https://read.amazon.co.jp")

    # 事前に保存されたクッキーを追加する（あれば）
    if AMAZON_COOKIES:
        try:
            cookies = json.loads(AMAZON_COOKIES)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()
        except Exception as e:
            print("クッキーの読み込みに失敗しました:", e)

    # ログインページへ遷移（既にログイン済みの場合はスキップ）
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "top-sign-in-btn"))).click()

        # ログインフォーム入力
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(AMAZON_EMAIL)
        driver.find_element(By.ID, "continue").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(AMAZON_PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()

        # OTP確認が出る場合に備える
        try:
            otp_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "auth-mfa-otpcode")))
            print("OTP（ワンタイムパスワード）入力画面です。手動で入力してください。")
            WebDriverWait(driver, 120).until(lambda d: d.find_element(By.ID, "auth-mfa-otpcode").get_attribute("value") != "")
            driver.find_element(By.ID, "auth-signin-button").click()
        except:
            pass  # OTPが表示されなければ無視
    except:
        print("ログインボタンが見つかりません。既にログイン済みとみなします。")

    # 蔵書情報をAPIから繰り返し取得
    WebDriverWait(driver, 10).until(EC.url_contains("read.amazon.co.jp"))
    books = []
    pagination_token = "0"
    while pagination_token:
        url = f"https://read.amazon.co.jp/kindle-library/search?&sortType=acquisition_asc&paginationToken={pagination_token}"
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        pre = driver.find_element(By.TAG_NAME, "pre").text
        data = json.loads(pre)
        books.extend(data.get("itemsList", []))
        pagination_token = data.get("paginationToken")

    # SAMPLEでない書籍のみを抽出し、acquiredDateで降順にソート
    filtered_books = [
        book for book in books
        if book.get("contentType") != "SAMPLE" and book.get("acquiredDate")
    ]
    sorted_books = sorted(filtered_books, key=lambda x: x.get("acquiredDate", ""), reverse=True)

    # 書籍情報出力
    book_data = []
    for book in sorted_books:
        title = book.get("title", "No title")
        print(title)
        book_data.append([title])

    print(f"蔵書数は{len(sorted_books)}冊です。")

    # 書籍情報をCSVに保存（SAMPLEを除き、acquiredDate降順）
    csv_path = os.path.join(os.path.dirname(__file__), "kindle_books.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title"])
        writer.writerows(book_data)
    print(f"CSVファイルに{len(book_data)}件のデータを書き込みました: {csv_path}")

finally:
    # ログイン直後のクッキーを取得し、.env ファイルに保存
    try:
        cookies = driver.get_cookies()
        cookies_str = json.dumps(cookies)

        # .env ファイルのパスを明示的に指定
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "r") as f:
            lines = f.readlines()

        with open(env_path, "w") as f:
            for line in lines:
                if not line.startswith("AMAZON_COOKIES="):
                    f.write(line)
            f.write(f'AMAZON_COOKIES="{cookies_str}"\n')

        print(".env ファイルにクッキー情報を保存しました。")
    except Exception as e:
        print("クッキーの保存に失敗しました:", e)
    driver.quit()
