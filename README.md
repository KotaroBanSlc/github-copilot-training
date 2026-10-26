# GitHub Copilot ハンズオントレーニング教材

> AI コーディングエージェント初心者向けの 5 回構成（合計 10 時間）のハンズオン教材

---

## 1. この教材について

GitHub Copilot を実務で使いこなせるようになることを目的とした、講師主導型のハンズオントレーニングです。講義と手元での実機操作を組み合わせて、全 5 回（1 回 120 分）で進めます。

この教材一式に含まれるもの：

| フォルダ / ファイル | 内容 |
|---|---|
| `portable/setup.html` | **受講前の環境構築手順書（Windows）**。まずこれを開いてセットアップしてください |
| `portable/session1.html` 〜 `session5.html` | 各回の受講者ハンドアウト（ブラウザで開いて使います） |
| `samples/` | ハンズオンで使う演習用サンプルコード |
| `requirements.txt` | Python 依存パッケージ（セットアップ §4.3 で使用） |

---

## 2. 対象者・前提知識

### 受講者の前提
- いずれかのプログラミング言語での 1 年以上の業務経験（Python のコードが読める程度が望ましい）
- Git の基本操作（`git init` / `commit` / `diff` 程度。GitHub アカウントも用意）
- VS Code を使った開発経験

### 必要なアカウント・ライセンス
- GitHub アカウント
- GitHub Copilot ライセンス：**Business / Enterprise の組織契約者** または個人プラン契約者を主対象
  - 個人プラン（Pro / Pro+ / Student）の新規申込は 2026 年 4 月 20 日に一時停止された後、2026 年 6 月 17 日から段階的に再開されています（最新は[公式](https://docs.github.com/ja/copilot/about-github-copilot/plans-for-github-copilot)を参照）
  - ライセンス未付与でもペア観察形式での受講は可能（事前に受講事務局へ連絡）
- VS Code 最新版（v1.106 以降）
- GitHub Copilot 拡張機能 + GitHub Copilot Chat 拡張機能
- **OS：Windows 10 / 11**（本研修は Windows のみ動作保証）

---

## 3. カリキュラム概要

| 回 | テーマ | 主な題材 | ハンドアウト |
|---|---|---|---|
| 第 1 回 | 生成 AI と GitHub Copilot の基礎 | コード補完、コード説明、処理フロー図の生成 | [session1.html](portable/session1.html) |
| 第 2 回 | 実装支援機能をマスターする | リファクタ、バグ修正、テスト生成、Vibe Coding でテトリス | [session2.html](portable/session2.html) |
| 第 3 回 | Plan モードと協働開発実践 | Plan モード、ペアプロで TODO アプリ改善 | [session3.html](portable/session3.html) |
| 第 4 回 | Skill の設計・作成と改善 | Skill の修正、TODO アプリのファイル案内 Skill の作成 | [session4.html](portable/session4.html) |
| 第 5 回 | Harness による制御・検証と instructions の活用 | ガードレールの判定確認、検証 Harness の作成、instructions による変数名の規則 | [session5.html](portable/session5.html) |

---

## 4. 環境セットアップ

> **本研修は Windows 環境を前提**としています。Mac / Linux / WSL は動作保証範囲外です。やむを得ない場合は事前に受講事務局へご相談ください。
> 受講前に必ず完了させてください。詰まった場合は受講事務局までご連絡ください。
> **スクリーンショット付きの詳細版**は [`portable/setup.html`](portable/setup.html) にあります。以下は要点のみの一覧です。

### 4.1 必須ツール

| ツール | バージョン | 確認コマンド |
|---|---|---|
| Python | **3.13.14**（64-bit）／[ダウンロード](https://www.python.org/downloads/release/python-31314/)<br>※3.11 / 3.12 / 3.13 系が既に入っていれば入れ直し不要 | `python --version` |
| pip | 最新 | `pip --version` |
| Git | 2.40 以上 | `git --version` |
| VS Code | **1.106 以降必須**（Plan モード演習で必要） | `code --version` |

### 4.2 VS Code 拡張機能

インストールが必要なのは **Python 拡張の 1 つだけ**です。

```
- Python（Microsoft 公式 / ms-python.python）
  → Pylance・Python Debugger・Python Environments も自動で一緒に入ります
```

> **GitHub Copilot（`GitHub.copilot-chat`）は VS Code 1.106 以降では本体に同梱**されており、補完（ゴーストテキスト）とチャットの両方を提供します。拡張機能タブで「Copilot」を検索して「インストール済み」になっていれば作業不要です。実際に使えるようにするサインイン手順は、詳細版 [`portable/setup.html`](portable/setup.html) の STEP 3 を参照してください。
> 旧バージョンの補完専用拡張（`GitHub.copilot`）が別に入っている場合も、そのままで構いません。

### 4.3 教材の展開と依存関係インストール（PowerShell）

教材は ZIP ファイルで配布します。受け取った ZIP を任意のフォルダに展開すると `github-copilot-training` フォルダができます。

```powershell
# ZIP を展開したフォルダに移動
cd github-copilot-training

# Git を初めて使う場合のみ（未設定だと下の git commit が失敗します）
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# 変更履歴を追えるよう、ローカルで Git 管理を始めておく
git init
git add -A
git commit -m "初期状態"

# Python 仮想環境の作成と依存関係のインストール
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> ハンズオンでは Copilot が加えた変更を `git diff` で見比べます。上記の `git init` を済ませておくと、この差分確認がそのまま使えます。
> `Activate.ps1` でエラーが出る場合は `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` を実行してから再度試してください。

### 4.4 動作確認（PowerShell）

§4.3 の `.venv` を有効化した同じターミナルで実行します。

```powershell
pytest --version   # 第 2 回で使用
flask --version    # 第 3 回・第 4 回で使用（Python / Flask / Werkzeug のバージョンが出れば OK）
ruff --version     # 第 5 回で使用
python -m tkinter  # 第 3 回で使用（テストウィンドウが開けば OK。閉じるとプロンプトに戻ります）
```

続けて、教材フォルダーを開いた VS Code で `Ctrl+Alt+I` を押してチャットを開き、Ask モードで質問して**日本語の返答があれば Copilot は正常**です。

> `pytest` / `flask` / `ruff` が見つからないと出る場合は、`.venv` を有効化したターミナルかどうかを確認してください。
