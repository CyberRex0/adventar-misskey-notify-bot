# adventar-misskey-notify-bot
これは、[Adventar](https://adventar.org/)のカレンダーを取得して、Misskeyに投稿するボットです。

## 必要なもの
- Google Chrome (or Chromium)
- Python 3.8以上
- 3GB RAM (推奨 4GB)

## セットアップ
1. `pip3 install -U virtualenv` でvirtualenvをインストール
2. `virtualenv env`で環境を作成、`. env/bin/activate` で入る
3. `pip3 install -U -r requirements.txt` で依存パッケージをインストール
4. Chromeのメジャーバージョン番号を確認し、`pip3 install -U "chromedriver-binary<メジャーバージョン番号に1足した数字"` を実行 (""は外さないこと！)
5. config.pyをコメントに従って編集する

### config.pyの内容
|Name|Type|Description|
|------|------|------|
|TOKEN|str|MisskeyのAPIトークン|
|DOMAIN|str|Misskeyのサーバーのホスト名(misskey.io等)|
|CALENDAR_ID|int|adventar.orgのカレンダーID (adventar.org/calendars/XXXX → XXXX)
|NOTE_VISIBILITY|str|投稿の公開範囲(public=パブリック, home=ホーム, followers=フォロワーのみ)|
|SHOW_YEAR|bool|カレンダータイトルの後ろに年を表示するかどうか。(True=する, False=しない) ※Adventarで勝手に付けてくれるみたいなので不要かもしれません|

これらの設定は環境変数にて、設定名の頭に`ADVMI_` を付けて設定することもできます。(ADVMI_TOKEN等)

## 実行方法
`run_venv.sh` を実行するだけ

自動で指定時間に投稿する機能はありません。cronなどを利用して自由に設定することができます。

どのような内容が投稿されるかを確かめるには `run_venv.sh --dry-run` を実行します。(実際に投稿はされません)

crontabの例:<br>
`0 8 1-25 12 * bash -c "cd /home/user/adventar-misskey-notify-bot && bash run_venv.sh"` (12月1日〜25日の間、毎日午前8時に実行)

### 引数
|arg|Type|Description|
|------|------|------|
|`--dry-run`|-|投稿内容を確認します。実際に投稿はされません。|
|`--force`|True|日付判定をスキップして強制的に投稿します。デバッグ用です。|
|`--force-day DAY`|int|指定した日にちの投稿を行います。デバッグ用です。|
|`--calendar-id ID`|int|カレンダーIDを直接指定します。|

# Copyright
&copy; 2022-2023 CyberRex<br>
MIT License