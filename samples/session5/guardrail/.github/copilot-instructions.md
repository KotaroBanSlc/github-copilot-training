# ガードレール判定Scriptの直接実行

- 作業対象は現在開いているguardrail内に限定する。
- 操作前にscripts/check-operation.ps1を直接実行し、実行予定コマンドの判定を確認する。Hookの発火は前提にしない。
- 判定対象は、依頼されたHARNESS_DEMO_READYの表示、HARNESS_DEMO_BLOCKの表示、README先頭5行の読み取りだけとする。実際の危険操作は行わない。
- 下のコードの$candidateを依頼された模擬コマンドに置き換え、guardrailを作業ディレクトリとして、外側の & { ... } を含むブロック全体を1回のターミナル呼び出しで実行する。コマンド文字列はJSONの入力データであり、このコードでは実行しない。
- Scriptの出力と、guardrail-events.jsonlの今回の時刻・case・decisionを確認する。ログのtoolは入力した模擬ツール名であり、Hook発火の証拠とはしない。
- permissionDecisionがallowで、出力とログが一致した場合だけ、依頼された安全なコマンドを別のツール呼び出しで1回実行する。
- denyなら対象コマンドを実行せず、判定理由と対象コマンドを実行していないことを報告する。再試行や別コマンドへの置き換えは行わない。
- Scriptの異常終了、JSONの不備、今回のログがない場合は未確認として停止する。終了コード0だけでallowと判断しない。
- 配布済みファイルやinstructionsは変更せず、Scriptによるログ追記だけを許容する。Invoke-Expressionなどで入力文字列を実行しない。

## 判定Scriptの呼び出し

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
