# 🚦 STATS19 Road Casualty Severity Prediction

End-to-end machine learning application for predicting whether a road casualty is likely to be **Severe** or **Non-severe** using 2023 Great Britain STATS19 road safety data.

The project combines an XGBoost classification pipeline with a production-style architecture using **FastAPI, PostgreSQL, Streamlit, Docker Compose, automated testing and GitHub Actions CI**.

---

## Model Performance

| Metric | Score |
|---|---:|
| Macro F1 | 0.619 |
| Severe Recall | 0.649 |
| Severe Precision | 0.361 |
| ROC-AUC | 0.739 |
| Average Precision | 0.430 |

The final model is a cost-sensitive XGBoost classifier designed to improve detection of the minority Severe class.

---

## Architecture

```mermaid
flowchart LR
    A[User] --> B[Streamlit]
    B --> C[FastAPI]
    C --> D[XGBoost]
    C --> E[(PostgreSQL)]

Application flow
Streamlit — frontend for single and batch prediction
FastAPI — prediction API and request validation
XGBoost — trained classification pipeline
PostgreSQL — prediction logs, batch tracking and model versioning
Docker Compose — runs the full application stack
Features
Single-record prediction through POST /predict
Batch inference through POST /predict/batch
Vectorised batch scoring
Prediction logging in PostgreSQL
Batch traceability using batch_id
Model version tracking
SHAP feature-importance analysis
Oversampling sensitivity analysis
Automated API tests with Pytest
GitHub Actions continuous integration
Dockerised Streamlit, FastAPI and PostgreSQL services
Running the Application

Create .env from .env.example, then run:

docker compose up -d --build

Open:

Streamlit: http://localhost:8501
FastAPI docs: http://localhost:8000/docs

Run tests with:

python -m pytest -v

Current test suite:

4 passed
Repository Structure
├── app/          # FastAPI backend
├── frontend/     # Streamlit frontend
├── model/        # trained model and metadata
├── data/         # demo input data
├── outputs/      # SHAP and evaluation outputs
├── sql/          # PostgreSQL schema and queries
├── tests/        # automated API tests
├── scripts/
├── Dockerfile
├── compose.yaml
└── requirements.txt
Tech Stack

Python · Pandas · Scikit-learn · XGBoost · SHAP · FastAPI · PostgreSQL · Streamlit · Docker · Pytest · GitHub Actions

Limitations
Trained on 2023 STATS19 data only
Severe casualties remain a minority class
Severe-class precision is relatively low
Input data must follow the same preprocessing schema used during training
Portfolio/academic demonstration only; not intended for operational road-safety decisions

Author

Umrah 
MSc Data Science