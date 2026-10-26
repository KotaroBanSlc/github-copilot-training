# ハンズオン⑥ 検証Harnessの作成

H1でruffを実行するScriptを仕様から作り、H2でinstructionsに検証手順を書いてAIの編集作業へ組み込み、H3で独自の検証Scriptを追加する演習です。受講者はAIへの依頼文と確認ケースを自分で考え、結果を見ながらScriptやinstructionsを改善します。対象Pythonファイルの手編集は行いません。

検証の入口は`scripts/check_all.py`のままにします。H1・H2はruffだけ、H3はruffと独自Script（`print()`の直接呼び出しの禁止）の2つを実行します。

詳しい操作は、[受講者向けハンズオン](../../../portable/session5.html#ho6)の「ハンズオン⑥」を参照してください。第5回の最後の演習として80～110分を目安に実施し、進捗に応じて＋αと解説の時間を調整します。

## 利用環境

- Windows、Windows PowerShell 5.1、Python 3（3.13.14で動作確認）、ruff 0.17.0を使用します。
- この`generate_harness`フォルダをVS Codeで単独で開き、GitHub CopilotのLocalセッションでAgentモードを選びます。
- ターミナルの作業ディレクトリもこのフォルダに合わせます。
- Hook対応や`chat.useHooks`の有効化は不要です。Hook設定は配布・作成しません。既存の安全対策は無効にしません。

## 事前準備（演習時間に含めない）

演習前に[受講前 環境構築手順書のSTEP 4](../../../portable/setup.html#s4-venv)の手順で教材フォルダー直下の共通`.venv`にruff 0.17.0が導入されていることを確認します。確認できるまで演習へ進みません。

依存関係は教材ルートの`requirements.txt`にまとめています。この演習フォルダには`requirements.txt`や`.venv`を作成しません。検証コマンドは共通のPython実行ファイルを直接指定するため、仮想環境の有効化も不要です。

開始時の`.github/copilot-instructions.md`は、作成・改善を許可するファイルや保持するものを定める作業範囲だけです。編集後の検証手順はH2で受講者が追記します。`templates/copilot-instructions.md`は追記後の参考例であり、開始状態とは異なります。

## 配布ファイル

```text
generate_harness/
  README.md
  .github/
    copilot-instructions.md
  order_summary.py
  pyproject.toml
  templates/
    check_all.py
    check_no_print.py
    copilot-instructions.md
```

| ファイル | 役割 |
| -------- | ---- |
| `order_summary.py` | 注文数・数量・金額の集計と表示用文字列を返す演習対象。AIに変更させる。配布時はruffの違反と`print()`なし |
| `pyproject.toml` | ruffの設定。有効にするルール（E・W・F・I）の正本 |
| `.github/copilot-instructions.md` | 作業範囲を記した開始用ファイル。H2で検証の実行手順を追記する |
| `templates/check_all.py` | H3完了後の参考実装。ruffと独自Scriptを実行する |
| `templates/check_no_print.py` | 独自Scriptの参考実装。`print(...)`の直接呼び出しを検出する |
| `templates/copilot-instructions.md` | H2で整備する検証手順の参考例。構築後の比較に使う |

`templates`は演習後の比較用です。H1～H3の構築中は参照・コピーせず、仕様から作成します。初期配布に`scripts/`は含めません。開始用instructionsを完成例で置き換えて配布しないでください。

## Harnessの構成

| 構成要素 | 配置先 | 役割 |
| -------- | ------ | ---- |
| instructions | `.github/copilot-instructions.md` | H2で変更後の検証・修正・再検証・報告の手順を追記する。規約の内容は重複して書かない |
| 検証の入口 | `scripts/check_all.py` | H1でruffを実行し、H3で独自Scriptも呼び出すよう拡張する |
| 既存のLinter | ruff（設定は`pyproject.toml`） | 未使用のimport、importの並び順、空白などの一般的な規約を検出する |
| 独自の検証Script | `scripts/check_no_print.py` | H3で作成し、対象コードの`print(...)`という直接呼び出しを検出する |

判定できるルールは、Scriptと`pyproject.toml`だけに持たせます。同じルールをinstructionsにも書くと、片方だけが更新されて内容がずれるためです。また、AIがルールを事前に知らなくても、変更後の検証で違反が見つかり修正される流れを観察できます。

ruffにも`print`を検出するルール（T201）がありますが、この演習では独自の検証Scriptを作る練習のため有効にしていません。同じルールを2つの仕組みで重複して判定しないためです。実務では、既存のLinterのルールで足りる場合はそちらを優先します。

## 演習の流れ

1. 対象コード・ruffの設定・課題の仕様を読み、依頼内容と確認ケースを整理します（3分）。
2. **H1 検証Scriptの作成**：ruffだけを実行する`scripts/check_all.py`を作成し、正常時の`0`と違反時の`1`を確かめます。この段階は検証を都度依頼し、修正しない指定なら検出結果だけを確認します。確認後は対象コードを修正して成功へ戻します（7分）。
3. **H2 開発作業への組み込み**：instructionsへ実行タイミング・コマンド・違反時の修正と再検証・エラー時の停止・報告内容を追記します。新しいAgentチャットで対象コードの変更だけを依頼し、検証から修正まで実行されるか確かめます（8分）。
4. **H3 独自検証の追加**：`print(...)`の直接呼び出しを検出するScriptを作り、同じ入口からruffと一緒に実行するよう拡張します。両検証の成功を確かめ、デバッグ出力の追加依頼から検出・修正・再検証までを確認します（7分）。
5. **＋α**：コメントや文字列を誤検知しないか試します。判定に問題があればScriptを改善し、正常・違反の両ケースを再確認します。
6. 最後の5分で、依頼文・実行結果・改善した点と理由・未確認事項を記録し、解答例と比較します。少なくとも1回は条件を変えて再試行します。

課題ページには完成プロンプトを載せていません。作成後に[解答例・解説](../../../portable/session5.html#ho6-answer)で、仕様からの依頼例、実装の要点、確認手順を比べます。テンプレートとの一致ではなく、完成条件を満たすかで判断します。

## 検証コマンド

`scripts/check_all.py`を作成した後、このフォルダを作業ディレクトリとして実行します。`..\..\..\.venv`は、3階層上の教材フォルダー直下にある共通の仮想環境です。引数は不要です。終了コードまで同じ実行の出力に残すため、外側の `& { ... }` を含むブロック全体を1回で実行します。

```powershell
& {
  $ErrorActionPreference = 'Stop'
  ..\..\..\.venv\Scripts\python.exe -B ./scripts/check_all.py
  $validationExitCode = $LASTEXITCODE
  Write-Output "ExitCode=$validationExitCode"
}
```

参考実装では各検証の結果を`=== OK ruff ===`のような見出しで表示します。H1・H2は`Passed 成功数/1`、H3は`Passed 成功数/2`となります。どの検証が失敗したか、出力と終了コードから分かるようにします。

| 状態 | 出力の例 | 終了コード |
| ---- | -------- | ---------- |
| H1・H2で正常 | ruffが成功し、`Passed 1/1` | `0` |
| H3で正常 | ruffと独自Scriptが成功し、`Passed 2/2` | `0` |
| `print`の違反 | `=== FAIL check_no_print ===`、`order_summary.py:行番号: printの使用は禁止です。出力が必要な場合はloggingを使用してください` | `1` |
| ruffの違反 | `=== FAIL ruff ===`、``order_summary.py:1:8: F401 [*] `os` imported but unused`` | `1` |
| 検証エラー | `=== ERROR ruff ===`（ruff未導入）、`=== ERROR check_no_print ===`（読み取り・構文エラー） | `2` |

- 検証対象は`order_summary.py`の1ファイルだけです。対象Pythonファイルを実行・変更せず、他のPythonファイルも検査しません。
- ruffは`--no-cache`で実行し、このフォルダにキャッシュを作りません。`--ignore-noqa`で実行するため、`# noqa`コメントでは違反を回避できません。
- `check_no_print.py`は、AST上の`print(...)`という直接呼び出しを検出する学習用Scriptです。コメントや文字列中の`print`は違反にしません。属性経由や別名経由などのすべての出力方法を禁止する仕組みではありません。検証Script自身の結果表示に使う`print()`は検証対象外です。
- テンプレートのPythonファイルは、日本語を`\u`エスケープで記述してASCII文字だけで構成しています。作成したScriptが保存時の文字コードの違いで構文エラーにならないようにするためです。

## 作業範囲と確認上の注意

- 受講者は`order_summary.py`を手で編集しません。変更はAIへの依頼だけで行います。
- 構築・改善の対象は`scripts/check_all.py`、`scripts/check_no_print.py`、`.github/copilot-instructions.md`です。対象コードの動作を保ち、設定・テンプレート・他の演習は変更しません。
- 誤検知などの判定の問題はScript、実行・報告の手順の問題はinstructionsを改善します。正常系と異常系を再確認し、規則を削除・弱体化して成功扱いにしません。
- 通常の編集作業で検出された規約違反は、対象コード側を修正します。検証できない場合は未検証として停止します。
- instructionsはScriptの起動や違反時の停止を強制しません。ツールの実行履歴、メッセージ、直後に取得した終了コードを確認します。
- ファイル保存だけでは検証されません。Hookによる自動発火・強制停止を確認したとは記録しません。
- この演習ではHookを作成しません。

## 講師向けの事前確認

配布前に、演習フォルダの複製でH1～H3の作成と確認を試してください。H1ではruffだけで`Passed 1/1`になり、H2で追記したinstructionsに従って検証・修正・再検証されることを確認します。H3を拡張した後は、次のケースで確認します。テンプレートを使ったScript単体の確認だけでは、受講者の作成手順やAIの行動まで確認したことにはなりません。

| 対象ファイルの状態 | 期待する結果 |
| ------------------ | ------------ |
| 配布時のまま | `Passed 2/2`、終了コード`0` |
| `format_summary`に`print(...)`を追加 | `FAIL check_no_print`、終了コード`1` |
| `print(...)`を`logging`へ置き換え | `Passed 2/2`、終了コード`0` |
| 先頭に`import os`を追加 | `FAIL ruff`（F401）、終了コード`1` |
| 先頭に`import os  # noqa: F401`を追加 | `FAIL ruff`（F401）、終了コード`1` |
| コメント`# print('x')`と文字列`'print(1)'`だけを追加 | `Passed 2/2`、終了コード`0` |
| 構文エラーを追加 | `ERROR check_no_print`、終了コード`2` |
| ruffを導入していないPythonで実行 | `ERROR ruff`、終了コード`2` |

配布用には開始状態のinstructionsを残し、作成済みの`scripts/`やH2の検証手順を含めません。AIの応答は確率的に変わるため、最初から`print`を使わない、検証を実行しない場合もあります。追加の依頼や改善が必要だった点を、そのまま記録してください。