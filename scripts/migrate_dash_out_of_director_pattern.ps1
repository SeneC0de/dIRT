<#
.SYNOPSIS
  Migrates dashboard product files out of the company `director-pattern` repo
  into the new standalone `dASH` repo.

.DESCRIPTION
  Authored by Jones (dIRT) on 2026-05-23 as part of the dIRT / dASH split.

  The original `C:\Users\randa\source\repos\director-pattern` repo historically
  held both the Director platform (CLI, doctrine, workflow) AND the dashboard
  product (web/, functions/, dashboard ADRs). This script moves the dashboard
  product files into `C:\Users\randa\source\repos\dASH` so that:

    - director-pattern == platform only (the company general Director runtime)
    - dASH            == dashboard product (Firebase Hosting + Cloud Functions)
    - dIRT            == Randall's personal Director runtime (already split)

  Defaults to DRY-RUN. Pass -Execute to perform the moves. Always git-commits
  the deletions on the director-pattern side in a separate commit so the move
  is reviewable.

.PARAMETER Execute
  Actually perform the moves. Without this flag, prints what WOULD happen.

.PARAMETER OverwriteDash
  If a target file already exists in dASH (likely because dIRT seeded it from
  its own stale copy), overwrite with the live director-pattern version.
  Without this flag, the script SKIPS files that already exist in dASH and
  prints a warning.

.PARAMETER SrcDirectorPattern
  Override the source path. Default: C:\Users\randa\source\repos\director-pattern

.PARAMETER DstDash
  Override the dASH destination path. Default: C:\Users\randa\source\repos\dASH

.EXAMPLE
  # See what would happen
  .\migrate_dash_out_of_director_pattern.ps1

.EXAMPLE
  # Do it for real, preferring live director-pattern content over dIRT-seeded copies
  .\migrate_dash_out_of_director_pattern.ps1 -Execute -OverwriteDash
#>
[CmdletBinding()]
param(
    [switch]$Execute,
    [switch]$OverwriteDash,
    [string]$SrcDirectorPattern = 'C:\Users\randa\source\repos\director-pattern',
    [string]$DstDash            = 'C:\Users\randa\source\repos\dASH'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Write-Section($msg) {
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor DarkGray
    Write-Host $msg -ForegroundColor Cyan
    Write-Host ('=' * 70) -ForegroundColor DarkGray
}

function Move-Tree {
    param(
        [string]$From,
        [string]$To,
        [string]$Label
    )
    if (-not (Test-Path $From)) {
        Write-Host "  SKIP   $Label  (source does not exist: $From)" -ForegroundColor DarkGray
        return
    }
    $exists = Test-Path $To
    if ($exists -and -not $OverwriteDash) {
        Write-Host "  SKIP   $Label  (target exists, pass -OverwriteDash to replace): $To" -ForegroundColor Yellow
        return
    }
    if ($exists -and $OverwriteDash) {
        Write-Host "  REPL   $Label  (overwriting): $To" -ForegroundColor Magenta
        if ($Execute) { Remove-Item $To -Recurse -Force }
    } else {
        Write-Host "  MOVE   $Label  ->  $To" -ForegroundColor Green
    }
    if ($Execute) {
        $parent = Split-Path $To -Parent
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        # Use Move-Item so the source is removed atomically (with -Force across drive ok via Copy + Remove)
        try {
            Move-Item -Path $From -Destination $To -Force
        } catch {
            # Fall back to copy+remove if Move-Item refuses across volumes
            Copy-Item -Path $From -Destination $To -Recurse -Force
            Remove-Item -Path $From -Recurse -Force
        }
    }
}

function Move-File {
    param(
        [string]$From,
        [string]$To,
        [string]$Label
    )
    if (-not (Test-Path $From)) {
        Write-Host "  SKIP   $Label  (source does not exist)" -ForegroundColor DarkGray
        return
    }
    $exists = Test-Path $To
    if ($exists -and -not $OverwriteDash) {
        Write-Host "  SKIP   $Label  (target exists, pass -OverwriteDash to replace)" -ForegroundColor Yellow
        return
    }
    if ($exists -and $OverwriteDash) {
        Write-Host "  REPL   $Label  (overwriting)" -ForegroundColor Magenta
    } else {
        Write-Host "  MOVE   $Label" -ForegroundColor Green
    }
    if ($Execute) {
        $parent = Split-Path $To -Parent
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        Move-Item -Path $From -Destination $To -Force
    }
}

Write-Section 'dASH migration plan'
if (-not $Execute) {
    Write-Host 'MODE: DRY-RUN (no files will be touched). Pass -Execute to apply.' -ForegroundColor Yellow
} else {
    Write-Host 'MODE: EXECUTE — moves WILL happen.' -ForegroundColor Red
}
Write-Host "Source (director-pattern): $SrcDirectorPattern"
Write-Host "Destination (dASH):        $DstDash"
Write-Host "Overwrite dASH on conflict: $OverwriteDash"

if (-not (Test-Path $SrcDirectorPattern)) {
    Write-Error "Source not found: $SrcDirectorPattern"
}
if (-not (Test-Path $DstDash)) {
    Write-Error "Destination not found: $DstDash. Create the dASH skeleton first."
}

# Confirm we're in a git checkout
$gitDir = Join-Path $SrcDirectorPattern '.git'
if (-not (Test-Path $gitDir)) {
    Write-Error "Source is not a git repo (no .git): $SrcDirectorPattern"
}

# Check working tree is clean BEFORE we touch anything
if ($Execute) {
    Push-Location $SrcDirectorPattern
    $dirty = git status --porcelain
    Pop-Location
    if ($dirty) {
        Write-Host ''
        Write-Host 'director-pattern working tree is not clean. Resolve before running with -Execute:' -ForegroundColor Red
        Write-Host $dirty
        exit 1
    }
}

Write-Section '1. web/ (Firebase Hosting site)'
Move-Tree -From (Join-Path $SrcDirectorPattern 'web') `
          -To   (Join-Path $DstDash 'web') `
          -Label 'web/'

Write-Section '2. functions/ (Cloud Functions)'
Move-Tree -From (Join-Path $SrcDirectorPattern 'functions') `
          -To   (Join-Path $DstDash 'functions') `
          -Label 'functions/'

Write-Section '3. Dashboard ADRs'
$dashAdrs = @(
    '0001-dash-design.md',
    '0003-dash-avatar-image-source.md',
    '0004-comments-mentions.md'
)
foreach ($adr in $dashAdrs) {
    Move-File -From (Join-Path $SrcDirectorPattern "docs\decisions\$adr") `
              -To   (Join-Path $DstDash "docs\decisions\$adr") `
              -Label "docs/decisions/$adr"
}

Write-Section '4. Other dashboard-adjacent files (if present)'
# Common items that might exist depending on history. Each is a no-op if absent.
$maybe = @(
    @{ From='firebase.json'; To='firebase.json'; Label='firebase.json (root)' },
    @{ From='firestore.rules'; To='firestore.rules'; Label='firestore.rules (root)' },
    @{ From='firestore.indexes.json'; To='firestore.indexes.json'; Label='firestore.indexes.json (root)' },
    @{ From='.firebaserc'; To='.firebaserc'; Label='.firebaserc (root)' }
)
foreach ($m in $maybe) {
    Move-File -From (Join-Path $SrcDirectorPattern $m.From) `
              -To   (Join-Path $DstDash $m.To) `
              -Label $m.Label
}

Write-Section '5. Git commits'
if ($Execute) {
    # Commit the deletion side in director-pattern
    Push-Location $SrcDirectorPattern
    Write-Host 'Committing removal in director-pattern...' -ForegroundColor Cyan
    git add -A
    $msg = "Split: move dASH product files out to standalone dASH repo`n`nMoved web/, functions/, dashboard ADRs (0001/0003/0004), and Firebase config files into C:\Users\randa\source\repos\dASH (separate repo, dapp-controls/dASH).`n`ndirector-pattern now contains only the Director platform (CLI, doctrine, workflow).`n`nAuthored by Jones (dIRT) as part of the 2026-05-23 dIRT / dASH split."
    git commit -m $msg
    Pop-Location

    # Stage in dASH (don't commit — Randall reviews before push)
    Push-Location $DstDash
    Write-Host 'Staging moves in dASH (NOT committing — review then commit yourself)...' -ForegroundColor Cyan
    git add -A 2>$null
    Pop-Location

    Write-Host ''
    Write-Host 'DONE. Next steps:' -ForegroundColor Green
    Write-Host '  1. cd ' + $DstDash
    Write-Host '  2. git status      # review what was moved in'
    Write-Host '  3. git commit -m "Initial dASH repo — split from director-pattern"'
    Write-Host '  4. Push to dapp-controls/dASH (see git_remote_setup.md)'
} else {
    Write-Host '(would commit removal in director-pattern and stage adds in dASH)' -ForegroundColor DarkGray
}

Write-Host ''
Write-Host 'Done.' -ForegroundColor Green
