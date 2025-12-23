#!/bin/bash
cd /home/samoradc/SamoraDC/AgenticRealEstateSystem
source .venv/bin/activate
echo "Starting API Server on http://localhost:8000"
python3 api_server.py
