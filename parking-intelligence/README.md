# Parking-Induced Congestion Intelligence System

A real-world parking intelligence system that detects illegal on-street parking hotspots near commercial areas and metro stations, and quantifies their impact on traffic congestion.

## Stage 1 Rebuild

This project was rebuilt to ensure strict deployment reliability and avoid native C/C++/Cython compilation issues in Docker environments.

### Key Architectural Decisions
- **No `hdbscan`**: The `hdbscan` library was completely removed due to Cython/gcc type-mismatch bugs inside Docker. We exclusively use `scikit-learn`'s `DBSCAN` with the haversine metric.
- **Embedded Database**: We use DuckDB with the `spatial` extension instead of PostgreSQL+PostGIS for Stage 1. Since there are no concurrent writes yet, an embedded file-based database removes infrastructure overhead. The data access layer (`src/data/dao.py`) is abstracted to allow a seamless swap to Postgres later.
- **Prebuilt Wheels Only**: All Python dependencies in `requirements.txt` (like `pyogrio`, `shapely`, `geopandas`) are explicitly pinned to versions known to have stable, prebuilt binary wheels for `python:3.11-slim` on Linux. This avoids the need for system libraries like `gdal-bin`.

## Stage 2 Scaffold (Computer Vision)
This stage builds the computer vision pipeline (`src/cv/`) using YOLOv8 and ByteTrack. 
**Crucial Note:** This pipeline is currently scaffolded and unit-tested against *synthetic fixtures only*. It is not yet validated against real camera feeds.

### Deployment Note: GPU vs CPU Inference
For scaffolding and local testing, the `backend.Dockerfile` explicitly installs CPU-only versions of `torch` and `torchvision` (via `https://download.pytorch.org/whl/cpu`). This keeps the Docker image lean and fast to build.
**When transitioning to the centralized GPU server deployment target**, you MUST swap the Dockerfile installation commands to pull the CUDA-enabled wheels (e.g., standard PyPI torch) and ensure the NVIDIA container toolkit (`--gpus all`) is passed to Docker.

## How to Run Stage 1

1. **Place the historical data:** Ensure the historical e-challan CSV is located at `data/raw/jan_to_may_police_violation.csv`.
2. **Setup virtual environment (Optional but recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Load historical data:**
   ```bash
   python scripts/load_historical_data.py
   ```
   This reads the CSV, cleans the data, runs the clustering and scoring algorithms, and persists the results into a DuckDB database (`data/processed/parking_intelligence.duckdb`).
4. **Start the application:**
   ```bash
   docker-compose up --build
   ```
   This will start the FastAPI backend and the React frontend.
5. **Access the dashboard:** Open `http://localhost:5173` (or the port specified by the frontend) in your browser.

## Configuration

- **`config/dbscan_params.yaml`**: Configures the DBSCAN clustering radius and density parameters.
- **`config/scoring_weights.yaml`**: Configures the weights for the proxy congestion scoring heuristic.
