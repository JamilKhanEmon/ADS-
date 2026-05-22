<p align="center">
  <h1 align="center">Agriculture Database API</h1>
  <p align="center">
    A high-performance RESTful API for agricultural data analytics and reporting
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License">
</p>

---

## Overview

Agriculture Database API is a robust backend service built with **FastAPI** that provides comprehensive agricultural analytics through two main report categories:

- **Farm Performance Report** — Track farm productivity, profitability, and loss analysis
- **Crop & Market Intelligence Report** — Analyze yield efficiency, seasonal trends, and market dynamics

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async web framework |
| **SQLAlchemy** | Database ORM and connection management |
| **pandas** | Data processing and aggregation |
| **PyMySQL** | MySQL database connector |
| **Uvicorn** | ASGI server |
| **Docker** | Containerization |

---

## Quick Start

### Prerequisites

- Python 3.11+
- MySQL database
- Docker (optional)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/JamilKhanEmon/ADS-.git
cd ADS-
```

**2. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the root directory:
```env
HOST=your_database_host
PORT=3306
DB=agriculture_db
USER=your_username
PASSWORD=your_password
```

**5. Run the server**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## Docker Deployment

### Using Docker

```bash
# Build the image
docker build -t agriculture-api .

# Run the container
docker run -d -p 8000:8000 --env-file .env agriculture-api
```

### Using Docker Compose

```bash
docker compose up -d
```

---

## CI/CD Pipeline

This project includes a GitHub Actions workflow for automated builds.

### Required Secrets

Configure these in your GitHub repository settings:

| Secret | Description |
|--------|-------------|
| `ENV_FILE` | Complete `.env` file content |
| `DOCKER_HUB_USERNAME` | Docker Hub username |
| `DOCKER_HUB_ACCESS_TOKEN` | Docker Hub access token |

### Workflow Triggers

- **Push to `main` branch** — Builds and pushes Docker image to Docker Hub

---

## API Documentation

### Interactive Docs

| Type | URL |
|------|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

### Endpoints

#### Farm Performance Report

| Method | Endpoint | Description |
|:------:|----------|-------------|
| `GET` | `/farms/summary` | Aggregated farm statistics with optional filters |
| `GET` | `/farms/{farm_id}/performance` | Detailed performance metrics for a specific farm |
| `GET` | `/farms/top` | Top N farms ranked by specified metric |
| `GET` | `/farms/loss-analysis` | Post-harvest loss breakdown analysis |

#### Crop & Market Intelligence Report

| Method | Endpoint | Description |
|:------:|----------|-------------|
| `GET` | `/crops/yield-efficiency` | Yield comparison against benchmarks |
| `GET` | `/crops/seasonal-trend` | Revenue trends across seasons |
| `GET` | `/markets/price-comparison` | Price analysis across different markets |
| `GET` | `/crops/quality-breakdown` | Distribution of quality grades |

---

## Query Parameters

All endpoints support case-insensitive filtering. Below are the accepted values:

<details>
<summary><b>Geographic & Farm Filters</b></summary>

| Parameter | Values |
|-----------|--------|
| `region` | Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, Rangpur, Barisal, Mymensingh |
| `farm_type` | Small, Medium, Large, Commercial |

</details>

<details>
<summary><b>Crop Filters</b></summary>

| Parameter | Values |
|-----------|--------|
| `crop_category` | Cereal, Vegetable, Fruit, Pulse, Oilseed, Cash Crop, Spice |
| `growing_season` | Rabi, Kharif, Zaid, Year-Round |
| `water_requirement` | Low, Medium, High |

</details>

<details>
<summary><b>Market Filters</b></summary>

| Parameter | Values |
|-----------|--------|
| `market_type` | Local, Wholesale, Export, Retail, Government Procurement |
| `price_tier` | Low, Medium, High, Premium |

</details>

<details>
<summary><b>Quality Filters</b></summary>

| Parameter | Values |
|-----------|--------|
| `quality_grade` | A, B, C, D |
| `pesticide_residue` | None, Trace, Low, High |

</details>

<details>
<summary><b>Time & Metric Filters</b></summary>

| Parameter | Values |
|-----------|--------|
| `year` | 2022, 2023, 2024 |
| `quarter` | 1, 2, 3, 4 |
| `season` | Spring, Summer, Autumn, Winter |
| `metric` | profit, revenue, yield |
| `limit` | Any positive integer (default: 10) |

</details>

---

## Project Structure

```
agriculture_api/
├── main.py              # Application entry point
├── database.py          # Database connection configuration
├── validators.py        # Input validation utilities
├── routers/
│   ├── farms.py         # Farm performance endpoints
│   └── crops_markets.py # Crop & market intelligence endpoints
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── .github/
    └── workflows/
        └── deploy.yml   # CI/CD pipeline
```

---

## License

This project is licensed under the MIT License.

---

<p align="center">
  <sub>Built with FastAPI</sub>
</p>
