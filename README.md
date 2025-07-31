# Kindle Scraper

Amazon Kindle の蔵書データを自動で取得し、CSV形式で保存するための Python スクリプトです。

## 機能
- Amazon Kindle の蔵書一覧を取得
- 書名を `kindle_books.csv` に出力
- ログイン後のクッキー情報を `.env` に保存・再利用

## 使用技術
- Python 3.10+
- Selenium
- Chrome WebDriver（自動管理）
- dotenv（環境変数管理）

## インストール

```bash
pip install -r requirements.txt
```

## セットアップ

`.env` ファイルを以下の形式で作成してください：

```env
AMAZON_EMAIL=your_email@example.com
AMAZON_PASSWORD=your_password
AMAZON_COOKIES=
```

- 初回ログイン後、クッキーは自動的に `.env` に保存され、次回以降に再利用されます。
- `.env` や `kindle_books.csv` は `.gitignore` により Git 管理外としてください。

## 実行方法

```bash
python kindle_scraper.py
```

## 出力ファイル
- `kindle_books.csv`：蔵書のタイトル一覧（サンプル除外・購入日降順）

## セキュリティ
- `.env` に保存される情報には パスワードやセッショントークンが含まれるため絶対に公開しないでください。
- GitHub 等で公開する場合は `.env` を `.gitignore` に追加し、管理外にすること。

## 注意事項
- Amazonのログインに2段階認証（OTP）がある場合は、手動での入力を促します。
- 本スクリプトは https://read.amazon.co.jp にアクセスして動作します。
