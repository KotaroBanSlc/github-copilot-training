# エラーが起きたらcatchへ進むようにし、JSONの入出力をUTF-8（BOMなし）にそろえる。
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

# 判定と理由をJSONで返す。このScript自体は依頼されたコマンドを実行・停止しない。
# 実際に実行するか、実行を見送るかは、判定を受け取ったAIが決める。
function Write-HookDecision {
    param(
        [string]$Decision,
        [string]$Reason
    )

    @{
        hookSpecificOutput = @{
            hookEventName = 'PreToolUse'
            permissionDecision = $Decision
            permissionDecisionReason = $Reason
        }
    } | ConvertTo-Json -Depth 4 -Compress
}

try {
    # 標準入力からJSON全体を読み、先頭にBOMがあれば除いて解析する。
    $inputJson = [Console]::In.ReadToEnd()
    $event = $inputJson.TrimStart([char]0xFEFF) | ConvertFrom-Json
    # 必須のツール名と操作内容がなければ、入力エラーとして扱う。
    if ([string]::IsNullOrWhiteSpace($event.tool_name) -or $null -eq $event.tool_input) {
        throw 'Expected Local hook input: tool_name and tool_input.'
    }

    # 拒否条件に該当しない操作はallow（許可）とし、ログではotherに分類する。
    $decision = 'allow'
    $case = 'other'
    $reason = 'No demonstration block condition matched.'
    $isTerminal = $event.tool_name -match '(^|[./])run_in_terminal$'

    # ターミナル操作だけコマンドの内容を調べる。空のコマンドは入力エラーにする。
    if ($isTerminal) {
        $command = [string]$event.tool_input.command
        if ([string]::IsNullOrWhiteSpace($command)) {
            throw 'The terminal command is missing.'
        }

        # 安全な表示コマンドでも、この目印があれば演習用ルールとしてdeny（拒否）にする。
        if ($command -match '\bHARNESS_DEMO_BLOCK\b') {
            $decision = 'deny'
            $case = 'blocked-demo'
            $reason = 'BLOCK: HARNESS_DEMO_BLOCK represents a prohibited operation. The tool was stopped before execution. Do not retry or bypass this hook.'
        }
        # 最初の動作確認用の目印。判定はallowのまま、ログの分類と理由を変更する。
        elseif ($command -match '\bHARNESS_DEMO_READY\b') {
            $case = 'ready-probe'
            $reason = 'ALLOW: Hook readiness probe.'
        }
        # 拒否後に別の依頼を試すケース。指定されたREADMEの読み取りをallowに分類する。
        elseif ($command.Trim() -eq 'Get-Content ./README.md -Encoding UTF8 -TotalCount 5') {
            $case = 'safe-read'
            $reason = 'ALLOW: Read-only demonstration command.'
        }
    }

    # 時刻・ツール名・ケース・判定・理由をJSONの1行にまとめ、演習フォルダのログへ追記する。
    $record = [ordered]@{
        timestamp = [DateTimeOffset]::Now.ToString('o')
        tool = [string]$event.tool_name
        case = $case
        decision = $decision
        reason = $reason
    } | ConvertTo-Json -Compress
    $logPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'guardrail-events.jsonl'
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::AppendAllText($logPath, $record + [Environment]::NewLine, $encoding)

    Write-HookDecision -Decision $decision -Reason $reason
}
catch {
    # 入力不備やログの書き込み失敗時はdenyを返し、演習を止めて確認するよう伝える。
    Write-HookDecision -Decision 'deny' -Reason ('Guardrail validation failed. Stop the exercise and ask the instructor: ' + $_.Exception.Message)
}

# 終了コード0は許可を意味しない。許可・拒否は返却JSONのpermissionDecisionで確認する。
exit 0