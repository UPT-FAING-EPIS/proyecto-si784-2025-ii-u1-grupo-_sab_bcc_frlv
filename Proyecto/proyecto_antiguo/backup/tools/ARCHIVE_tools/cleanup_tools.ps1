$items = @(
    'antivirus_control.cpp',
    'antivirus_control.exe',
    'antivirus_control.ps1',
    'antivirus_daemon.cpp',
    'README_antivirus_control.md',
    'README_antivirus_daemon.md'
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$archive = Join-Path $root 'ARCHIVE_tools'
if (-not (Test-Path $archive)) { New-Item -ItemType Directory -Path $archive | Out-Null }

foreach ($f in $items) {
    $src = Join-Path $root $f
    if (Test-Path $src) {
        $dst = Join-Path $archive $f
        try {
            Move-Item -Path $src -Destination $dst -Force
            Write-Host "Moved: $f -> ARCHIVE_tools/" -ForegroundColor Green
        } catch {
            Write-Host "Failed to move $f : $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Not found: $f" -ForegroundColor DarkGray
    }
}
