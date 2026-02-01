#!/bin/bash
echo "Starting Ollama..."
ollama serve &
sleep 10
echo "Downloading models..."
ollama pull llama3.1:8b || echo "Failed to download llama3.1:8b"
ollama pull llama3.2:latest || echo "Failed to download llama3.2"
ollama pull llama3.2-vision:latest || echo "Failed to download llama3.2-vision"
echo "Models downloaded!"
pkill ollama
sleep 5
echo "Starting Ollama for production..."
ollama serve &
sleep 5
echo "Starting FastAPI server..."
/opt/venv/bin/python fastapi_server.py &
sleep 3
echo "Starting Streamlit app..."
/opt/venv/bin/streamlit run ollama_vrm_integrated_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false --server.enableCORS=false --server.enableXsrfProtection=false --logger.level=error --client.showErrorDetails=false
wait
