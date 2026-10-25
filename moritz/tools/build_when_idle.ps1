# Launch: cmd /c "start /low /wait /b powershell -NoProfile -ExecutionPolicy Bypass -File G:\Code\Moritz\build_when_idle.ps1 [-Config Debug]"
# Wait until CPU and GPU are free (3 checks in a row, a minute apart), then run the gentle build.
param([string]$Config = 'Release')
$calm = 0
while ($calm -lt 3) {
    Start-Sleep -Seconds 60
    $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    $gpu = 0
    try { $gpu = [int](& nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>$null | Select-Object -First 1) } catch {}
    if ($cpu -lt 30 -and $gpu -lt 20) { $calm++ } else { $calm = 0 }
    "$(Get-Date -Format HH:mm) cpu $cpu gpu $gpu calm $calm" | Out-File -Append G:\Code\Moritz\build_wait.log
}
"$(Get-Date -Format HH:mm) starting $Config build" | Out-File -Append G:\Code\Moritz\build_wait.log
# This script runs at low priority (see the launcher), so the build inherits it.
& cmd.exe /c G:\Code\Moritz\build_gentle.cmd $Config
