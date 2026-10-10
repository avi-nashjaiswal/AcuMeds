param(
    [bool]$OpenBrowser = $true,
    [int]$OpenDelaySeconds = 1,
    [string]$EnvFile = '.env.local'
)

$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'

function Import-EnvFile {
    param([string]$FilePath)

    Get-Content $FilePath | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) {
            return
        }

        $parts = $line -split '=', 2
        if ($parts.Count -ne 2) {
            return
        }

        $name = $parts[0].Trim()
        $value= $parts[1].Trim()
        if (-not $name) {
            return
        }

        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        Set-Item -Path "Env:$name" -Value $value
    }
}

function Wait-ForPort {
    param(
        [int]$Port,
        [int]$TimeoutSeconds = 15
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($listener) {
            return $true
        }

        Start-Sleep -Milliseconds 250
    }

    return $false
}

if (-not (Test-Path $python)) {
    Write-Host "Python venv not found at: $python" -ForegroundColor Red
    Write-Host "Create the venv first, then rerun this script." -ForegroundColor Yellow
    exit 1
}

$envPath = if ([System.IO.Path]::IsPathRooted($EnvFile)) { $EnvFile } else { Join-Path $root $EnvFile }
if (Test-Path $envPath) {
    Import-EnvFile -FilePath $envPath
    Write-Host "Loaded environment from $envPath" -ForegroundColor Green
} else {
    Write-Host "Env file not found: $envPath" -ForegroundColor Yellow
    Write-Host "Tip: copy .env.sms.example to .env.local and set Twilio values for live OTP SMS." -ForegroundColor DarkYellow
}

$smsProviderRaw = $env:SMS_PROVIDER -as [string]
$smsProvider = ''
if ($smsProviderRaw) {
    $smsProvider = $smsProviderRaw.ToLower()
}
if ($smsProvider -eq 'twilio') {
    if (-not $env:TWILIO_ACCOUNT_SID -or -not $env:TWILIO_AUTH_TOKEN -or -not $env:TWILIO_FROM_NUMBER) {
        Write-Host "SMS_PROVIDER=twilio but Twilio credentials are incomplete. OTP SMS may fail." -ForegroundColor Yellow
    }
}

$apps = @(
    @{ Name = 'Customer'; Path = Join-Path $root 'pharmacy_system\run.py'; Port = 5000 },
    @{ Name = 'Shopkeeper'; Path = Join-Path $root 'shopkeeper_system\run.py'; Port = 5001 },
    @{ Name = 'Admin'; Path = Join-Path $root 'admin_system\run.py'; Port = 5002 },
    @{ Name = 'Delivery'; Path = Join-Path $root 'delivery_system\run.py'; Port = 5003 },
    @{ Name = 'Doctor'; Path = Join-Path $root 'doctor_system\run.py'; Port = 5004 }
)

$tabsToOpen = @()

foreach ($app in $apps) {
    if (-not (Test-Path $app.Path)) {
        Write-Host "Missing $($app.Name) app: $($app.Path)" -ForegroundColor Yellow
        continue
    }

    $url = "http://127.0.0.1:$($app.Port)"
    if ($OpenBrowser) {
        $tabsToOpen += [pscustomobject]@{
            Name = $app.Name
            Url = $url
            Port = $app.Port
        }
    }

    $portInUse = Get-NetTCPConnection -LocalPort $app.Port -State Listen -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "$($app.Name) already listening on port $($app.Port). Skipping." -ForegroundColor Yellow
        continue
    }

    $appDir = Split-Path $app.Path
    Write-Host "Starting $($app.Name) on $url" -ForegroundColor Cyan
    Start-Process -FilePath $python -ArgumentList @("`"$($app.Path)`"") -WorkingDirectory $appDir
}

if ($OpenBrowser -and $tabsToOpen.Count -gt 0) {
    if ($OpenDelaySeconds -gt 0) {
        Start-Sleep -Seconds $OpenDelaySeconds
    }

    foreach ($tab in $tabsToOpen) {
        $ready = Wait-ForPort -Port $tab.Port
        if (-not $ready) {
            Write-Host "Timed out waiting for $($tab.Name) on port $($tab.Port). Opening anyway." -ForegroundColor Yellow
        }

        Start-Process $tab.Url
    }
}

Write-Host 'All apps launched.' -ForegroundColor Green
