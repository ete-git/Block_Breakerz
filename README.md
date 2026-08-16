# Block Breakerz

チーム制作プロジェクトで作成した7ステージのブロック崩しゲームです。

## 遊び方

### EXE版（すぐに遊べます）【推奨】

**[リリースページから最新版をダウンロード](https://github.com/ete-git/Block_Breakerz/releases)**

1. 最新のリリースから `block_breakerz.exe` をダウンロード
2. ダブルクリックで起動

### Python版（開発・実行）

```bash
# 1. このリポジトリをクローン
git clone https://github.com/ete-git/Block_Breakerz.git
cd Block_Breakerz

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. Main.pyを実行
python Main.py
```

## 操作方法

| キー | 機能 |
|------|------|
| スペースキー | ゲーム開始 |
| 左右矢印キー | パドル操作 |
| Pキー | 一時停止 |
| Rキー | リトライ |
| Cキー | クレジット表示 |
| Qキー | ゲーム終了 |

## ゲームルール

- ボールをパドルで跳ね返してブロックを壊します
- 各ステージの目標スコアを達成するとクリアになります
- 次のステージへ進みます
- 全7ステージをクリアするとゲーム完了です

## ファイル構成

```
Block_Breakerz/
├── Main.py                 # メインプログラム
├── README.md               # このファイル
├── requirements.txt        # 必要なPythonパッケージ
├── .gitignore              # Git管理対象外ファイル
├── modules/
│   ├── functions.py        # 共通関数（クレジット表示など）
│   └── NotoSansJP-Regular.ttf  # 日本語フォント
├── stages/
│   ├── Stage1.py ~ Stage7.py  # 各ステージのプログラム
├── images/
│   ├── stage1/ ~ stage7/   # 各ステージの画像ファイル
└── sounds/
    ├── stage1/ ~ stage7/   # 各ステージの音声ファイル
```

## 必要な環境

- Python 3.10以上
- pygame 2.6.1
- Pillow 10.0.0以上

## ビルド方法（EXE作成）

```bash
# PyInstallerをインストール
pip install pyinstaller

# EXEをビルド
pyinstaller --onefile --windowed --name "block_breakerz" \
  --add-data "images;images" \
  --add-data "sounds;sounds" \
  --add-data "modules;modules" \
  --add-data "stages;stages" \
  Main.py
```

生成されたEXEは `dist/block_breakerz.exe` にあります。

## 開発情報

- 使用言語：Python 3.13.14
- ゲームライブラリ：Pygame 2.6.1
- 画像処理：Pillow (PIL)

## ライセンス

このプロジェクトのコードはMITライセンスの下で公開されています。
アセット（画像・音声）は各提供元の利用規約に従ってください。
詳細はクレジット表示を参照してください。

## クレジット

各ステージのアセットの著作権情報はゲーム内のクレジット表示で確認できます。
ゲーム起動後、スタート画面で「C」キーを押してください。
