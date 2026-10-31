# Install every Rabet skill into ~/.claude/skills (side by side, so they can find the shared rabet-reels engine).
# usage: powershell -ExecutionPolicy Bypass -File install.ps1     (run from this folder; re-run to update)
$dest = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $HOME ".claude\skills" }
New-Item -ItemType Directory -Force $dest | Out-Null
Get-ChildItem (Join-Path $PSScriptRoot "skills") -Directory | ForEach-Object {
  $t = Join-Path $dest $_.Name
  if (Test-Path $t) { Remove-Item -Recurse -Force $t }
  Copy-Item -Recurse $_.FullName $t
  Write-Host "installed $($_.Name)"
}
$cfg = Join-Path $HOME ".rabet-reels.json"
if (-not (Test-Path $cfg)) { Copy-Item (Join-Path $PSScriptRoot "skills\rabet-reels\config.example.json") $cfg; Write-Host "created ~/.rabet-reels.json: fill in your paths" }
