<# Read-only native Excel verification. Captures only its own window.
   No desktop capture, clipboard use, printer changes or workbook saving. #>
param(
    [string]$Report = "demo/qa_report.xlsx",
    [string]$Output = "outputs/excel-visual-qa",
    [switch]$Visible
)
$ErrorActionPreference = "Stop"
$reportPath = (Resolve-Path -LiteralPath $Report).Path
$sourceHash = (Get-FileHash -LiteralPath $reportPath -Algorithm SHA256).Hash
$outputPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Output))
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class ExcelWindowCapture {
    [StructLayout(LayoutKind.Sequential)]
    public struct Rect { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out Rect r);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
}
'@
$excel = $null
$book = $null
$records = @()
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AutomationSecurity = 3
    $window = [IntPtr]$excel.Hwnd
    [uint32]$excelProcessId = 0
    [ExcelWindowCapture]::GetWindowThreadProcessId($window, [ref]$excelProcessId) | Out-Null
    @{ process_id=$excelProcessId; version=$excel.Version; build=$excel.Build } |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputPath "instance.json") -Encoding UTF8
    $book = $excel.Workbooks.Open($reportPath, 0, $true)
    if (-not $book.ReadOnly) { throw "The workbook must be read-only." }
    if ($Visible) {
        $excel.Visible = $true
        $excel.WindowState = -4143
        $excel.Width = 1100
        $excel.Height = 700
    }
    foreach ($sheet in $book.Worksheets) {
        $sheet.Activate()
        $excel.ActiveWindow.Zoom = 100
        $sheet.Range("A1").Select() | Out-Null
        $excel.ActiveWindow.ScrollRow = 1
        $excel.ActiveWindow.ScrollColumn = 1
        $rect = New-Object ExcelWindowCapture+Rect
        [ExcelWindowCapture]::GetWindowRect($window, [ref]$rect) | Out-Null
        $width = $rect.Right - $rect.Left
        $height = $rect.Bottom - $rect.Top
        $captured = $false
        if ($width -gt 0 -and $height -gt 0) {
            $bitmap = New-Object System.Drawing.Bitmap($width, $height)
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $dc = $graphics.GetHdc()
            try { $captured = [ExcelWindowCapture]::PrintWindow($window, $dc, 2) }
            finally { $graphics.ReleaseHdc($dc); $graphics.Dispose() }
            try {
                # PrintWindow can return true for a completely blank hidden window.
                $colors = New-Object 'System.Collections.Generic.HashSet[int]'
                for ($x = 0; $x -lt $width; $x += 17) {
                    for ($y = 0; $y -lt $height; $y += 17) {
                        $colors.Add($bitmap.GetPixel($x, $y).ToArgb()) | Out-Null
                    }
                }
                $captured = $captured -and $colors.Count -gt 8
                if ($captured) {
                    $bitmap.Save((Join-Path $outputPath ($sheet.Name + ".png")), [System.Drawing.Imaging.ImageFormat]::Png)
                }
            } finally { $bitmap.Dispose() }
        }
        $records += @{
            sheet=$sheet.Name; rows=$sheet.UsedRange.Rows.Count; columns=$sheet.UsedRange.Columns.Count
            filter=$sheet.AutoFilterMode; freeze_panes=$excel.ActiveWindow.FreezePanes
            header_bold=$sheet.Range("A1").Font.Bold; capture_contains_content=$captured
            width=$width; height=$height
            has_formula=$sheet.UsedRange.HasFormula
        }
        if ($sheet.UsedRange.HasFormula -ne $false) { throw "Unexpected formula cells in $($sheet.Name)" }
    }
    $records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $outputPath "result.json") -Encoding UTF8
    Write-Output "Native Excel read-only checks completed. Captures require visual review: $outputPath"
} finally {
    try { if ($null -ne $book) { $book.Close($false) } }
    finally {
        if ($null -ne $excel) { $excel.Quit(); [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel) | Out-Null }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
if ((Get-FileHash -LiteralPath $reportPath -Algorithm SHA256).Hash -ne $sourceHash) {
    throw "The source workbook changed."
}
