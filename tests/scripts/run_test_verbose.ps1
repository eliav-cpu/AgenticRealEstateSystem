# PowerShell script to run test with verbose output
& .venv\Scripts\activate.ps1
python test_simple_import.py
Write-Host "Test completed"