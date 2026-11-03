[CmdletBinding(DefaultParameterSetName = 'Patch')]
param(
    [Parameter(ParameterSetName = 'Major')]
    [switch]$Major,

    [Parameter(ParameterSetName = 'Minor')]
    [switch]$Minor,

    [Parameter(ParameterSetName = 'Patch')]
    [switch]$Patch
)

$ErrorActionPreference = 'Stop'

function Invoke-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($args -join ' ')"
    }
}

Push-Location -LiteralPath $PSScriptRoot
try {
    if (Invoke-Git status --porcelain) {
        throw 'Commit or stash pending changes before releasing.'
    }

    Invoke-Git checkout woto-version

    $versionPath = Join-Path $PSScriptRoot 'pyrogram/__init__.py'
    $source = Get-Content -LiteralPath $versionPath -Raw
    $versionPattern = '(?m)^__version__ = "(\d+)\.(\d+)\.(\d+)"'
    if ($source -notmatch $versionPattern) {
        throw 'Expected __version__ in pyrogram/__init__.py to use major.minor.patch.'
    }

    $majorVersion = [int]$Matches[1]
    $minorVersion = [int]$Matches[2]
    $patchVersion = [int]$Matches[3]

    if ($Major) {
        $majorVersion++
        $minorVersion = 0
        $patchVersion = 0
    } elseif ($Minor) {
        $minorVersion++
        $patchVersion = 0
    } else {
        $patchVersion++
    }

    $newVersion = "$majorVersion.$minorVersion.$patchVersion"
    $source = $source -replace $versionPattern, "__version__ = `"$newVersion`""
    Set-Content -LiteralPath $versionPath -Value $source -Encoding utf8 -NoNewline

    Invoke-Git commit --only -m "Bump version to $newVersion" -- pyrogram/__init__.py
    Invoke-Git checkout Production
    Invoke-Git merge woto-version
    Invoke-Git push origin Production
    Invoke-Git checkout woto-version
} finally {
    Pop-Location
}
