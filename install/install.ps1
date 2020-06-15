Write-Output "Creating postman-toolkit installation package"

Remove-Item -Recurse -Force -path "staging" -ErrorAction SilentlyContinue
Remove-Item -Force -Path "postman-toolkit.zip" -ErrorAction SilentlyContinue

New-Item -Type Directory -Path "staging" | Out-Null

Write-Output "Building frontend"
Set-Location ..\front
npm run build
Set-Location ..\install

Write-Output "Copying files"
Copy-Item -Recurse -Path ..\toolkit -Destination staging | Out-Null
New-Item -Type Directory -Path staging\front | Out-Null
Copy-Item -Recurse -Path ..\front\dist\* -Destination staging\toolkit\front | Out-Null
Copy-Item -path ..\__main__.py -Destination staging\ | Out-Null
New-Item -type File -Path staging\toolkit\front\__init__.py | Out-Null
New-Item -type File -Path staging\toolkit\front\js\__init__.py | Out-Null
New-Item -type File -Path staging\toolkit\front\css\__init__.py | Out-Null
New-Item -type File -Path staging\toolkit\front\fonts\__init__.py | Out-Null
New-Item -type File -Path staging\toolkit\front\img\__init__.py | Out-Null

Write-Output "Creating archive"
Compress-Archive -path staging/* -DestinationPath postman-toolkit.zip
