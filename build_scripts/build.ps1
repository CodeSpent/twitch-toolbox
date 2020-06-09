Write-Host "Checking for newer builds."

if ($env:APPVEYOR_PULL_REQUEST_NUMBER -and $env:APPVEYOR_BUILD_NUMBER -ne ((Invoke-RestMethod `
        https://ci.appveyor.com/api/projects/$env:APPVEYOR_ACCOUNT_NAME/$env:APPVEYOR_PROJECT_SLUG/history?recordsNumber=50).builds | `
        Where-Object pullRequestId -eq $env:APPVEYOR_PULL_REQUEST_NUMBER)[0].buildNumber) { `
          throw "There are newer queued builds for this pull request, failing early." }

Write-Host "Starting Build"

if ($env:APPVEYOR_REPO_TAG -eq "true") {
    $newName = "pyinstaller-${env:APPVEYOR_REPO_TAG_NAME}_win"
} else {
    $newName = "pyinstaller-build${env:APPVEYOR_BUILD_VERSION}_win"
}

pyinstaller --onefile clip-manager.spec -n $newName