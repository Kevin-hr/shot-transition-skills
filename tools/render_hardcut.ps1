# Hard-cut renderer: concat N shots with no xfade, frame/sample-exact trims,
# and an 8ms fade on each side of every join.
#
# Kept ASCII-only on purpose: PowerShell 5.1 reads a BOM-less .ps1 as ANSI, so a
# literal CJK path in the source would be mangled. Pass paths in as parameters.
#
# usage:
#   .\render_hardcut.ps1 -Source <src> -Out <out.mp4> `
#                        -Starts 3.0,67.0,102.5,125.5,148.5,175.0,216.5 `
#                        -Durations 7,4,3,3,3,6,7
#
# -Durations drives everything: the total length, the trim frame/sample counts
# and the fade offsets. -Starts are the per-shot in-points on the source.
# Override -Fps / -SampleRate / -Codec only if your delivery spec differs.
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Out,
    [Parameter(Mandatory = $true)][double[]]$Starts,
    [Parameter(Mandatory = $true)][double[]]$Durations,
    [string]$Ffmpeg = $env:FFMPEG,
    [int]$Fps = 120,
    [int]$SampleRate = 48000,
    [string]$VideoCodec = "libx265",
    [string]$Preset = "medium",
    [string]$Crf = "18",
    [string]$PixFmt = "yuv420p10le",
    [string]$Tag = "hvc1",
    [string]$AudioCodec = "aac",
    [string]$AudioBitrate = "320k",
    [int]$Channels = 2,
    # Colour tags. Defaults assume an HLG/BT.2020 HDR source.
    # Pass empty strings (-ColorPrimaries "") for an SDR delivery.
    [string]$ColorPrimaries = "bt2020",
    [string]$ColorTrc = "arib-std-b67",
    [string]$ColorSpace = "bt2020nc",
    [string]$ColorRange = "tv"
)

$ErrorActionPreference = "Stop"
$inv = [System.Globalization.CultureInfo]::InvariantCulture

if (-not $Ffmpeg) { $Ffmpeg = "ffmpeg" }
$n = $Durations.Count
if ($Starts.Count -ne $n) { throw "Starts ($($Starts.Count)) and Durations ($n) length mismatch" }

$total = 0.0
foreach ($d in $Durations) { $total += $d }

$args = @("-hide_banner", "-loglevel", "warning", "-stats")
for ($i = 0; $i -lt $n; $i++) {
    $s = [string]::Format($inv, "{0:F3}", $Starts[$i])
    $d = [string]::Format($inv, "{0:F3}", $Durations[$i])
    # -t is an upper bound only: it keeps the boundary frame, so trim cuts it back
    $args += @("-ss", $s, "-t", $d, "-i", $Source)
}

$chains = @()
for ($i = 0; $i -lt $n; $i++) {
    # end_frame / end_sample are exact: time-based trim let the boundary frame slip
    # through, which made the video stream longer than the audio stream.
    $nf = [int]($Durations[$i] * $Fps)
    $ns = [int]($Durations[$i] * $SampleRate)
    # 8ms fade each side of every join: butting unrelated waveforms together
    # leaves a step that is audible as a click.
    $fo = [string]::Format($inv, "{0:F3}", $Durations[$i] - 0.008)
    $chains += "[$i`:v]trim=end_frame=$nf,setpts=PTS-STARTPTS[v$i]"
    $chains += "[$i`:a:0]atrim=end_sample=$ns,asetpts=PTS-STARTPTS," +
               "afade=t=in:st=0:d=0.008,afade=t=out:st=$fo`:d=0.008[a$i]"
}
$vlabels = (0..($n - 1) | ForEach-Object { "[v$_]" }) -join ""
$alabels = (0..($n - 1) | ForEach-Object { "[a$_]" }) -join ""
$chains += "$vlabels`concat=n=$n`:v=1:a=0[vout]"
$chains += "$alabels`concat=n=$n`:v=0:a=1[aout]"
$fc = $chains -join ";"

$args += @(
    "-filter_complex", $fc,
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", $VideoCodec, "-preset", $Preset, "-crf", $Crf,
    "-pix_fmt", $PixFmt, "-tag:v", $Tag
)
if ($ColorPrimaries) { $args += @("-color_primaries", $ColorPrimaries) }
if ($ColorTrc)       { $args += @("-color_trc", $ColorTrc) }
if ($ColorSpace)     { $args += @("-colorspace", $ColorSpace) }
if ($ColorRange)     { $args += @("-color_range", $ColorRange) }
$args += @(
    "-x265-params", "log-level=warning",
    "-c:a", $AudioCodec, "-b:a", $AudioBitrate, "-ar", $SampleRate, "-ac", $Channels,
    "-r", "$Fps", "-t", ([string]::Format($inv, "{0:F3}", $total)),
    "-movflags", "+faststart",
    "-y", $Out
)

Write-Output "FILTER: $fc"
Write-Output "TOTAL: $total s over $n shots"
Write-Output "RENDER START $(Get-Date -Format 'HH:mm:ss')"
& $Ffmpeg @args
Write-Output "RENDER EXIT=$LASTEXITCODE $(Get-Date -Format 'HH:mm:ss')"
if (Test-Path $Out) {
    Write-Output ("SIZE MB = {0:N1}" -f ((Get-Item $Out).Length / 1MB))
}