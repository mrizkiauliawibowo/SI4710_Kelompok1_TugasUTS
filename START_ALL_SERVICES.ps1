#!/usr/bin/env powershell
<#
.SYNOPSIS
Food Delivery System - Final Robust Service Starter

.DESCRIPTION
- Membuka 6 jendela PowerShell untuk API Gateway + 5 Microservices
- Menampilkan log realtime, termasuk error
- Menggunakan virtual environment jika ada
- Mengatasi path panjang dan spasi
#>

$ErrorActionPreference = "Stop"
$project_root = Get-Location

# Services definition
$services = @(
    @{ name="API Gateway";        port=5000; path="microservices/api-gateway";        description="API Gateway (Main Entry Point)" },
    @{ name="User Service";       port=5001; path="microservices/user-service";        description="User Management" },
    @{ name="Restaurant Service"; port=5002; path="microservices/restaurant-service"; description="Restaurant Management" },
    @{ name="Order Service";      port=5003; path="microservices/order-service";      description="Order Management" },
    @{ name="Delivery Service";   port=5004; path="microservices/delivery-service";   description="Delivery Management" },
    @{ name="Payment Service";    port=5005; path="microservices/payment-service";    description="Payment Management" }
)

# Create .service_scripts folder
$temp_scripts_dir = "$project_root/.service_scripts"
if (-not (Test-Path $temp_scripts_dir)) { New-Item -ItemType Directory -Path $temp_scripts_dir -Force | Out-Null }

Write-Host "Creating service startup scripts..." -ForegroundColor Cyan

function Create-ServiceScript {
    param(
        [string]$ServiceName,
        [int]$Port,
        [string]$ServicePath,
        [string]$Description
    )

    $script_content = @"
Write-Host "DEBUG: Script started for $ServiceName"
Write-Host "Service Path: $ServicePath"
Write-Host "Port: $Port"
Write-Host "Description: $Description"
Write-Host "-------------------------------"

try {
    # Navigate to service folder
    Set-Location '$project_root\$ServicePath'

    # Activate virtual environment if exists
    if (Test-Path '.\venv\Scripts\Activate.ps1') {
        Write-Host "Activating virtual environment..."
        . .\venv\Scripts\Activate.ps1
    }

    # Install dependencies if requirements.txt exists
    if (Test-Path 'requirements.txt') {
        Write-Host "Installing dependencies..."
        python -m pip install -r requirements.txt
    }

    # Start service and display logs realtime
    Write-Host "Starting $ServiceName on port $Port..."
    python app.py

} catch {
    Write-Host "ERROR: $ServiceName failed to start!" -ForegroundColor Red
    Write-Host "Details: $_"
}

Write-Host "Service $ServiceName exited. Check errors above."
Read-Host "Press Enter to close this service window..."
"@
    return $script_content
}

# Create and launch scripts
$count = 0
foreach ($service in $services) {
    $count++
    $script_file = "$temp_scripts_dir\start_$($service.port).ps1"
    $script_content = Create-ServiceScript -ServiceName $service.name -Port $service.port -ServicePath $service.path -Description $service.description
    Set-Content -Path $script_file -Value $script_content -Encoding UTF8

    Write-Host "[$count/6] Script created for $($service.name)"

    # Launch in new PS window (handle spaces in path)
    Start-Process powershell -ArgumentList "-NoExit -File `"$script_file`"" -WindowStyle Normal
    Start-Sleep -Milliseconds 500
}

Write-Host "All services launched. Check each window for logs." -ForegroundColor Green
Read-Host "Press Enter to close this launcher window..."
