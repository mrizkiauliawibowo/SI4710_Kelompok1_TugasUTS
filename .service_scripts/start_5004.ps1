Write-Host "DEBUG: Script started for Delivery Service"
Write-Host "Service Path: microservices/delivery-service"
Write-Host "Port: 5004"
Write-Host "Description: Delivery Management"
Write-Host "-------------------------------"

try {
    # Navigate to service folder
    Set-Location 'D:\Telkom University\Materi Kuliah Semester 5\Integrasi Aplikasi Enterprise\TubesUTS\food_delivery_system\microservices/delivery-service'

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
    Write-Host "Starting Delivery Service on port 5004..."
    python app.py

} catch {
    Write-Host "ERROR: Delivery Service failed to start!" -ForegroundColor Red
    Write-Host "Details: "
}

Write-Host "Service Delivery Service exited. Check errors above."
Read-Host "Press Enter to close this service window..."
