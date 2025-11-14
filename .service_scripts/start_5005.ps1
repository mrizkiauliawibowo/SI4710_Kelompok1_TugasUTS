Write-Host "DEBUG: Script started for Payment Service"
Write-Host "Service Path: microservices/payment-service"
Write-Host "Port: 5005"
Write-Host "Description: Payment Management"
Write-Host "-------------------------------"

try {
    # Navigate to service folder
    Set-Location 'D:\Telkom University\Materi Kuliah Semester 5\Integrasi Aplikasi Enterprise\TubesUTS\food_delivery_system\microservices/payment-service'

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
    Write-Host "Starting Payment Service on port 5005..."
    python app.py

} catch {
    Write-Host "ERROR: Payment Service failed to start!" -ForegroundColor Red
    Write-Host "Details: "
}

Write-Host "Service Payment Service exited. Check errors above."
Read-Host "Press Enter to close this service window..."
