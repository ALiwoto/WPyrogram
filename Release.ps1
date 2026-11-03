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

    if ((Invoke-Git branch --show-current) -ne 'master') {
        throw 'Run releases from the master branch.'
    }

    Invoke-Git fetch origin --tags
    if ((Invoke-Git rev-parse HEAD) -ne (Invoke-Git rev-parse origin/master)) {
        throw 'Push master and bring it up to date with origin/master before releasing.'
    }

    $versionPattern = '^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
    $lastTag = Invoke-Git tag --list 'v*' --sort=-version:refname |
        Where-Object { $_ -match $versionPattern } |
        Select-Object -First 1
    if (!$lastTag) {
        throw 'No vMAJOR.MINOR.PATCH release tag found.'
    }

    $majorVersion, $minorVersion, $patchVersion = ($lastTag -replace '^v') -split '\.' |
        ForEach-Object { [int]$_ }

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
    $newTag = "v$newVersion"
    Invoke-Git tag -a $newTag -m "WPyrogram $newVersion" HEAD
    Invoke-Git push origin "refs/tags/$newTag"
} finally {
    Pop-Location
}
