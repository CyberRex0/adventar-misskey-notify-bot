# adventar-misskey-notify-bot
これは、[Adventar](https://adventar.org/)のカレンダーを取得して、Misskeyに投稿するボットです。

## 必要なもの
- Chrome
- Python 3.8以上
- 2GB RAM

## セットアップ
1. `pip3 install -U virtualenv` でvirtualenvをインストール
2. `virtualenv env`で環境を作成、`. env/bin/activate` で入る
3. `pip3 install -U -r requirements.txt` で依存パッケージをインストール
4. Chromeのメジャーバージョン番号を確認し、`pip3 install -U "chromedriver-binary<メジャーバージョン番号に1足した数字"` を実行 (""は外さないこと！)
5. config.pyをコメントに従って編集する

## 実行方法
`run_venv.sh` を実行するだけ

自動で指定時間に投稿する機能はありません。cronなどを利用して自由に設定することができます。

crontabの例: `0 8 1-25 12 * bash -c "cd /home/user/adventar-misskey-notify-bot && bash run_venv.sh"` (12月1日〜25日の間、毎日午前8時に実行)

# Copyright
&copy; 2022 CyberRex<br>
MIT License