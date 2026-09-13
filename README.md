# Large Number Calculator

## はじめに
このプロジェクトは、AlteryxのPlatformSDKのチュートリアル用として作成しています。

## Large Number Calculatorとは
Alteryx Designer用のカスタムツールです。INT64で扱える範囲を超える数値を文字列として受け取り、任意精度の10進数で加算、減算、乗算、除算を行います。

## ツールの説明
このツールでは、Python標準ライブラリの `decimal.Decimal` を使って計算しています。

実装は `large_number_calculator.py` の `_calculate` です。

### 仕様

- 入力値を文字列化して `Decimal` に変換
- `+`、`-`、`*`、`/` に対応
- 結果は `pyarrow.string()` の文字列列として出力
- Pythonの通常の `float` やAlteryxのINT64に変換しないため、非常に大きな整数を扱える
- `Decimal` は固定小数点・任意精度の10進数型
- 入力が `None` の場合、結果も `None`
- 小数末尾の不要なゼロは削除
- `123.4500` → `123.45`
- `100.0` → `100`
- `1E+100` のような指数表記も、出力時には通常の数字表記に展開

ただし、完全に無制限の精度ではありません。現在のコードでは、入力文字列の長さを基準に次の精度を設定しています。

```
precision = max(len(first_text), len(second_text)) * 2 + 50
```

つまり、最大入力長の2倍に50桁を加えた精度で計算します。通常の加算・減算・乗算では十分な余裕がありますが、除算結果が循環小数になる場合は、この精度で丸められます。

例えば、 `1/3` は無限小数なので、設定された精度まで計算されます。

また、入力元が最初から `float` の場合、Pythonに渡る前に丸められている可能性があります。たとえば非常に長い数値をAlteryx側で数値型として保持すると、その時点で精度を失うため、巨大数は文字列型として入力するのが重要です。

## 前提条件

- Windows11
- Alteryx Designer 2026.1以降
- Python 3.13
- Node.js 18以上（UIのビルドに使用）
- npm

Pythonの仮想環境やnpmの依存パッケージはリポジトリに含めません。以下の手順でローカルに作成します。

以下のセットアップ方法などは、ブログにて公開しているので、そちらを参照願います。

## セットアップ

PowerShellでプロジェクトのルートディレクトリに移動し、仮想環境を作成します。

```powershell
py -3.13 -m venv alteryx_venv
.\alteryx_venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install ayx_plugin_cli==1.4.0
python -m pip install -r backend\requirements-thirdparty.txt
python -m pip install -r backend\requirements-local.txt
```

PowerShellの実行ポリシーによって有効化できない場合は、CLIを仮想環境の実行ファイルから直接呼び出してください。

```powershell
.\alteryx_venv\Scripts\python.exe -m ayx_plugin_cli --help
```

## UIのビルド

```powershell
Set-Location ui\LargeNumberCalculator
npm install
npm run build
Set-Location ..\..
```

開発用UIを起動する場合は、次のコマンドを実行します。

```powershell
Set-Location ui\LargeNumberCalculator
npm start
```

## テスト

プロジェクトルートで実行します。

```powershell
python -m ayx_plugin_cli test
```

または、テストを直接実行します。

```powershell
python -m pytest backend\tests
```

## Designerへのインストール

UIをビルドした後、プロジェクトルートで次を実行します。

```powershell
python -m ayx_plugin_cli designer-install
```

インストール後、Alteryx Designerを再起動すると、Preparationカテゴリの「Large Number Calculator」から利用できます。

## YXIパッケージの作成

配布用のYXIファイルを作成する場合は、UIをビルドした後に次を実行します。

```powershell
python -m ayx_plugin_cli create-yxi
```

生成されたYXIは `build\yxi\` に出力されます。

## ディレクトリ構成

```text
backend/                     Pythonバックエンドとテスト
configuration/               Alteryxツール設定、アイコン、生成設定
DcmSchemas/                  DCMスキーマ
ui/LargeNumberCalculator/    UIソースとwebpack設定
ayx_workspace.json           Alteryx SDKワークスペース設定
```

`alteryx_venv/`、`build/`、`node_modules/`、`dist/`、`.ayx_cli.cache/` などのローカル環境・生成物は `.gitignore` で除外しています。

## ライセンス

Alteryx SDK/API由来のコードには、各ソースファイルに記載されたAlteryx SDK and API License Agreementが適用されます。UI依存パッケージのライセンスについては、各パッケージの配布条件を確認してください。
