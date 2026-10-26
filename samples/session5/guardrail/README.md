# ハンズオン④ ガードレール判定Scriptの直接実行

このフォルダには、講師が配布する動作確認用Harnessが用意されています。今回はHookを使用せず、instructionsに従ってCopilotが判定Scriptを直接実行し、模擬操作の`allow`・`deny`を確認します。**配布済みの参考用Hook設定、判定Script、instructionsは変更しません。**

判定はScriptが行いますが、Scriptの起動や判定への従属はAIの行動に依存します。Hookによる自動呼び出しや、ツール呼び出しの強制停止を確認する演習ではありません。

詳しい操作は、[受講者向けハンズオン](../../../portable/session5.html#ho4)の「ハンズオン④」を参照してください。所要時間は15分です。

## 利用環境

- WindowsとWindows PowerShell 5.1を使用します。追加パッケージは不要です。
- VS CodeのGitHub Copilotで、LocalセッションのAgentモードを使用します。Hook対応は前提にしません。
- この`guardrail`を「フォルダーを開く」で単独で開きます。Copilotが使うターミナルの作業ディレクトリも`guardrail`にします。

配布元と内容を確認したうえでワークスペースを信頼します。`chat.useHooks`の有効化や`/hooks`での発火確認は行いません。PowerShellの実行ポリシーや組織の制限でScriptを実行できない場合は、設定を回避せず講師へ相談します。既存の安全対策も無効化しません。

## 配布済みファイル

| ファイル | 役割 |
| -------- | ---- |
| `templates/guardrail.json` | 本来の`PreToolUse`からの呼び出し方を確認する参考資料。自動検出されない配置で配布する |
| `.github/copilot-instructions.md` | 操作前に判定Scriptを直接実行し、判定結果に従うようAIへ指示するinstructions |
| `scripts/check-operation.ps1` | 標準入力のJSONを読み、模擬操作の`allow`・`deny`を返すScript |
| `README.md` | 配布物、利用環境、確認方法の説明 |
| `.gitignore` | 動作確認で生成されるログをGitの管理対象から除外する設定 |

参考用Hook設定は、自動検出される`.github/hooks/`ではなく`templates/`に置いています。演習中は移動・コピーせず、既存のHookや安全設定も変更しません。他のHookが動作して演習を進められない場合は、講師へ相談します。

判定Scriptは`guardrail-events.jsonl`をこのフォルダに自動生成し、判定ごとに追記します。受講者がログを作成する必要はありません。ログには時刻、入力した模擬ツール名、確認ケース、判定、理由を記録し、操作対象のファイルは書き換えません。

## 配布済みのinstructions

`.github/copilot-instructions.md`は配布済みです。受講者は作成・変更しません。このフォルダを開いた状態でAgentチャットを使うと、instructionsとして読み込まれます。

instructionsには、判定Scriptの呼び出しコードと、次の手順を記載しています。

- 依頼された模擬コマンドをJSONの入力データとして判定Scriptへ渡す。
- 出力の`permissionDecision`と理由、直後の終了コード、今回のログの時刻・`case`・`decision`を確認する。
- `allow`で出力とログが一致した場合だけ、依頼された安全なコマンドを別のツール呼び出しで1回実行する。
- `deny`の場合は対象コマンドを実行せず、判定理由を報告する。再試行や置き換えは行わない。
- Scriptを実行できない場合や、出力・ログが確認できない場合は、未確認として停止する。

## 判定に使う入力データ

以下は、プロンプトで実行を依頼し、**判定ScriptへJSONで渡す文字列**です。判定前にコマンド自体は実行しません。

| 順番 | 入力するコマンド文字列 | ログの`case` | 期待する`decision` |
| ---- | -------- | ----------- | ---------------- |
| 1. 直接実行の確認 | `Write-Output 'HARNESS_DEMO_READY'` | `ready-probe` | `allow` |
| 2. 拒否判定の確認 | `Write-Output 'HARNESS_DEMO_BLOCK'` | `blocked-demo` | `deny` |
| 3. 安全な操作の確認 | `Get-Content ./README.md -Encoding UTF8 -TotalCount 5` | `safe-read` | `allow` |

`HARNESS_DEMO_BLOCK`は、強制pushなどの禁止操作を表す演習用の目印です。文字列自体は無害ですが、`deny`の判定後はこの表示コマンドも実行しません。実際のGitコマンドには置き換えないでください。

## Scriptの直接実行方法

次は配布済みinstructionsに記載した呼び出しコードと同じ構成の例です。`guardrail`を作業ディレクトリとし、`$candidate`だけを上の表の文字列に置き換えて使用します。判定結果と終了コードを同じ実行の出力に残すため、外側の `& { ... }` を含むブロック全体を1回で実行します。

```powershell
& {
	$candidate = "Write-Output 'HARNESS_DEMO_READY'"
	$payload = @{
		tool_name = 'run_in_terminal'
		tool_input = @{ command = $candidate }
	} | ConvertTo-Json -Depth 4 -Compress
	$decisionJson = $payload | powershell -NoProfile -File ./scripts/check-operation.ps1
	$scriptExitCode = $LASTEXITCODE
	if ($scriptExitCode -ne 0) {
		throw "Decision script failed: ExitCode=$scriptExitCode"
	}
	$result = $decisionJson | ConvertFrom-Json
	if ($result.hookSpecificOutput.permissionDecision -notin @('allow', 'deny')) {
		throw 'Decision JSON is missing allow or deny.'
	}
	$result.hookSpecificOutput | Format-List
	Write-Output "ScriptExitCode=$scriptExitCode"
}
```

このコードは別プロセスの`powershell`へJSONを標準入力で渡し、判定だけを行います。`$candidate`の文字列自体は実行しません。`Invoke-Expression`などで文字列を実行しないでください。

## 確認の順番

1. 配布済みScriptを読み、JSONの入力形式と拒否条件を確認します。Hook設定は呼び出し方の参考として読むだけにし、配布済みファイルは変更しません。
2. 配布済みのinstructionsを読み、内容を確認します。instructionsは変更せず、新しいAgentチャットを開きます。
3. プロンプトで`HARNESS_DEMO_READY`の表示コマンドの実行だけを依頼します。instructionsに従って判定Scriptが先に1回直接実行され、出力と今回の`ready-probe`・`allow`のログを確認できた場合だけ、別の呼び出しで表示コマンドが実行されることを確認します。
4. 同じチャットで`HARNESS_DEMO_BLOCK`の表示コマンドの実行を依頼します。判定Scriptの`blocked-demo`・`deny`と理由を確認し、表示コマンド自体が実行されないことを確認します。
5. 同じチャットで、別の操作としてREADMEの読み取りコマンドの実行を依頼します。判定Scriptの出力と今回の`safe-read`・`allow`のログを確認できた場合だけ、別の呼び出しでREADMEの先頭5行が表示されることを確認します。一度`deny`が返ってもチャット全体が実行禁止になるわけではなく、依頼した操作ごとに判定されることを確認します。
6. ツール実行履歴、判定JSON、今回のログを突き合わせます。実行や結果を確認できない場合は、先へ進まず停止します。

## 判定結果の読み方

- `permissionDecision: deny`は、入力した模擬操作を禁止と判定したことを表します。直接実行では、このJSONだけで別のツール呼び出しが強制停止されるわけではありません。
- Scriptの終了コードは`deny`でも`0`です。入力不備でも`deny`のJSONと終了コード`0`が返るため、終了コードだけで成功や許可と判断せず、期待した`case`の今回のログまで確認します。
- 理由の`BLOCK:`から禁止理由を確認します。AIは判定理由と対象コマンドを実行していないことを報告し、再試行や別コマンドへの置き換えは行いません。手順5の読み取りは、拒否された操作の代わりではなく、独立した新しい依頼として判定します。
- 配布済みScriptには`The tool was stopped before execution`、`Do not retry or bypass this hook`、`Hook readiness probe`という本来のHook向けの文言が残ります。この出力をHookの発火や強制停止の証拠にはしません。
- ログの`tool`はJSONに入力した模擬ツール名です。最新の該当ケースと時刻を確認し、古いログやScriptを読んだだけの説明では検証済みと判断しません。

Scriptの実行に問題がある場合は、チャットのツール実行履歴、ターミナルの出力、入力JSON、作業ディレクトリを講師と確認してください。Hookの発火確認へは進みません。

## 安全性と制限

- このHarnessは模擬操作の確認専用です。入力JSONの`run_in_terminal`のコマンドに演習用の目印が含まれる場合を`deny`とし、それ以外は原則`allow`とします。実際の危険なGit操作を網羅して防ぐ仕組みではありません。
- 強制push、ブランチ変更、ファイル削除などは依頼・実行しません。判定を回避するための入力の書き換えや別ツールでの実行も行いません。
- 配布済みHook・Script・instructions・教材は変更しません。演習で許容する変更は、Scriptによるログの生成・追記だけです。
- instructionsはAIへの指示であり、Scriptの起動や操作の停止を機械的に保証しません。AIが`deny`に従わず対象コマンドを実行した場合は、成功とせず停止して講師へ報告します。

## 講師向けの事前確認

配布前に、上の実行例と3種類の入力データで、判定JSON、終了コード、ログが対応することを確認してください。入力不備で`deny`が返っても、期待したケースのログがない場合は正常な演習結果とみなしません。

続いて、受講環境のLocalセッションでinstructionsを読み込ませ、Copilotが判定Scriptを直接実行すること、`deny`では対象コマンドを実行しないこと、`allow`では確認後に指定コマンドを実行することを確認してください。Script単体のテストだけで、AIがinstructionsに従ったことまで確認したとは記録しません。今回はHookの発火を完了条件にしません。

入出力形式の参考：[Local Hookの入出力仕様](https://code.visualstudio.com/docs/agents/reference/hooks-reference)。今回はこの形式のJSONを直接渡すだけで、Hookは使用しません。