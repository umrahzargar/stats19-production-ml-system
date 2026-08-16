FROM python:3.13-slim

WORKDIR /app

COPY frontend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY frontend ./frontend
COPY model/model_metrics.json ./model/model_metrics.json
COPY data/X_test_demo_sample.csv ./data/X_test_demo_sample.csv
COPY outputs ./outputs

EXPOSE 8501

CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]