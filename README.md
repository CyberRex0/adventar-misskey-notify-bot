# adventar-misskey-notify-bot
これは、[Adventar](https://adventar.org/)のカレンダーを取得して、Misskeyに投稿するボットです。

## 必要なもの
- Python 3.12以上
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## セットアップ
1. uvをインストールし、プロジェクトのディレクトリに移動する
2. `uv sync --locked` を実行する
3. `config.sample.py` を `config.py` にコピーし、コメントに従って編集する

依存関係は `pyproject.toml` と `uv.lock` で管理します。<br>
`uv add` は両ファイルを更新し、`.venv` に依存パッケージをインストールします。<br>
変更した両ファイルは一緒にコミットしてください。<br>

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
プロジェクトのディレクトリで `uv run --locked python adventar.py` を実行します。仮想環境の有効化は不要です。既存の `run_venv.sh` からも同じコマンドで起動できます。

自動で指定時間に投稿する機能はありません。cronなどを利用して自由に設定することができます。

どのような内容が投稿されるかを確かめるには `run_venv.sh --dry-run` を実行します。(実際に投稿はされません)

crontabの例:<br>
`0 8 1-25 12 * bash -c "cd /home/user/adventar-misskey-notify-bot && bash run_venv.sh"` (12月1日〜25日の間、毎日午前8時に実行)

### 引数
|arg|Type|Description|
|------|------|------|
|`--dry-run`|-|投稿内容を確認します。実際に投稿はされません。|
|`--force`|-|日付判定をスキップして強制的に投稿します。デバッグ用です。|
|`--force-day DAY`|int|指定した日にちの投稿を行います。デバッグ用です。|
|`--calendar-id ID`|int|カレンダーIDを直接指定します。|

## 取得・解析処理のテスト
`uv run --locked python -m unittest discover -s tests -v` で実行します。Misskey投稿処理は読み込まず、通信はモックに置き換えます。

# Copyright
&copy; 2022-2026 CyberRex<br>
MIT License
