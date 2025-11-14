Write-Host "DEBUG: Script started for API Gateway"
Write-Host "Service Path: microservices/api-gateway"
Write-Host "Port: 5000"
Write-Host "Description: API Gateway (Main Entry Point)"
Write-Host "-------------------------------"

try {
    # Navigate to service folder
    Set-Location 'D:\Telkom University\Materi Kuliah Semester 5\Integrasi Aplikasi Enterprise\TubesUTS\food_delivery_system\microservices/api-gateway'

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
    Write-Host "Starting API Gateway on port 5000..."
    python app.py

} catch {
    Write-Host "ERROR: API Gateway failed to start!" -ForegroundColor Red
    Write-Host "Details: "
}

Write-Host "Service API Gateway exited. Check errors above."
Read-Host "Press Enter to close this service window..."
