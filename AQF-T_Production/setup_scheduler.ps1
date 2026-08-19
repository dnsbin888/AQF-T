# AQF-T Windows Task Scheduler 安装脚本
# 以管理员权限运行此脚本
# 用法: powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1

$taskName = "AQF-T Daily Run"
$scriptPath = "D:\AQF-T\AQF-T_Production\run_daily.bat"
$workingDir = "D:\AQF-T\AQF-T_Production"

# 删除旧任务（如果存在）
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task: $taskName"
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 创建新任务
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At 15:30

# 任务配置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

# 以当前用户运行（不要求密码）
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "AQF-T 每日自动运行 — 15:30 触发，读取 AKSHARE EOD 数据生成每日报告"

Write-Host ""
Write-Host "Task '$taskName' registered successfully."
Write-Host "  Schedule: Daily at 15:30"
Write-Host "  Script:   $scriptPath"
Write-Host ""
Write-Host "验证:"
Write-Host "  schtasks /run /tn 'AQF-T Daily Run'   # 手动触发一次"
Write-Host "  schtasks /query /tn 'AQF-T Daily Run'  # 查看状态"
Write-Host "  type D:\AQF-T\AQF-T_Production\logs\scheduler.log  # 查看日志"
