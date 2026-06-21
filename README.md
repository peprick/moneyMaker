# Quant Portfolio Optimizer

A local, no-Docker full-stack quantitative portfolio optimizer. The application combines a Python quant engine, a Spring Boot API gateway, and a React analytics UI to optimize stock allocations and explain portfolio risk.

## What It Does

- Downloads historical adjusted-close market data from Yahoo Finance.
- Computes daily returns, annualized expected returns, and covariance.
- Optimizes long-only portfolio weights using a swappable optimizer interface.
- Reports expected return, volatility, Sharpe ratio, VaR, drawdown, and beta.
- Generates efficient-frontier-style points for risk/return visualization.
- Runs Monte Carlo simulations for future portfolio value bands.
- Exposes the quant engine through FastAPI and routes browser requests through Spring Boot.
- Provides a React dashboard for tickers, constraints, allocation, risk, frontier, and simulation charts.

## Architecture

```text
React Frontend
  http://127.0.0.1:5173 or next free Vite port
        |
        | /api/*
        v
Spring Boot Backend
  http://127.0.0.1:8081
        |
        | HTTP
        v
Python FastAPI Quant Engine
  http://127.0.0.1:8001
        |
        | yfinance
        v
Yahoo Finance market data
```

The Java backend intentionally does not implement quant math. It validates and routes requests to the Python service, which owns the numerical work.

## Project Layout

```text
new_proj/
  backend/              # Spring Boot API gateway
  frontend/             # Vite React dashboard
  quant_engine/         # Python FastAPI quant service
  requirements.txt      # Python dependencies
  README.md
```

Important Python modules:

```text
quant_engine/main.py          FastAPI routes
quant_engine/market_data.py   Yahoo Finance adjusted-close loading
quant_engine/optimizer.py     optimizer facade and current random-search strategy
quant_engine/risk.py          VaR, drawdown, volatility, beta
quant_engine/frontier.py      efficient-frontier-like points
quant_engine/monte_carlo.py   simulation percentile bands
```

Important Java modules:

```text
backend/src/main/java/com/quantoptimizer/backend/controller/QuantController.java
backend/src/main/java/com/quantoptimizer/backend/service/QuantEngineClient.java
backend/src/main/java/com/quantoptimizer/backend/dto/
```

Important frontend modules:

```text
frontend/src/App.jsx
frontend/src/api/quantApi.js
frontend/src/styles.css
```

## Prerequisites

Installed on this machine during setup:

- Python 3.13
- Java 17
- Node.js 24
- npm 11

You also need Maven to run the backend. If Maven is installed globally, use `mvn`. During development here, Maven was downloaded temporarily under the Codex workspace:

```text
C:\Users\Sagarnil\Documents\Codex\2026-06-21\files-mentioned-by-the-user-quant\work\tools\apache-maven-3.9.16\bin\mvn.cmd
```

For long-term use, install Maven globally or add that Maven `bin` directory to your PATH.

## Setup

From the project root:

```powershell
cd C:\Users\Sagarnil\new_proj
```

Activate Python:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install frontend dependencies:

```powershell
cd C:\Users\Sagarnil\new_proj\frontend
npm.cmd install
```

If npm is pointed at an unreachable private registry, use:

```powershell
npm.cmd install --registry=https://registry.npmjs.org/
```

## Run Locally

Open three PowerShell windows.

Terminal 1, Python quant engine:

```powershell
cd C:\Users\Sagarnil\new_proj
.\.venv\Scripts\Activate.ps1
python -m uvicorn quant_engine.main:app --reload --port 8001
```

Terminal 2, Spring Boot backend:

```powershell
cd C:\Users\Sagarnil\new_proj\backend
mvn spring-boot:run
```

If Maven is not installed globally:

```powershell
C:\Users\Sagarnil\Documents\Codex\2026-06-21\files-mentioned-by-the-user-quant\work\tools\apache-maven-3.9.16\bin\mvn.cmd spring-boot:run
```

Terminal 3, React frontend:

```powershell
cd C:\Users\Sagarnil\new_proj\frontend
npm.cmd run dev
```

Open the URL printed by Vite. Usually:

```text
http://127.0.0.1:5173
```

If that port is busy, Vite will print the next available port, such as:

```text
http://127.0.0.1:5174
```

## API Surface

Python quant engine:

```text
GET  /health
POST /optimize
POST /risk
POST /frontier
POST /montecarlo
```

Spring Boot backend:

```text
GET  /api/health
POST /api/optimize
POST /api/risk
POST /api/frontier
POST /api/montecarlo
```

The frontend calls the Spring Boot `/api/*` routes. Vite proxies those calls to `http://127.0.0.1:8081`.

## Example Optimize Request

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "start": "2023-01-01",
  "end": "2026-01-01",
  "riskFreeRate": 0.04,
  "maxWeight": 0.6,
  "trials": 12000,
  "seed": 42
}
```

Example response:

```json
{
  "weights": {
    "AAPL": 0.21,
    "AMZN": 0.11,
    "GOOGL": 0.55,
    "MSFT": 0.13
  },
  "expected_return": 0.39,
  "volatility": 0.24,
  "sharpe_ratio": 1.49,
  "price_rows": 752,
  "start": "2023-01-03",
  "end": "2025-12-31"
}
```

## Optimizer Design

The Python optimizer is intentionally behind a stable facade:

```python
optimize_portfolio(prices, config=OptimizationConfig(...))
```

The current strategy is `random_search`, which is simple and transparent. Later strategies can be added without changing the Java or React contracts:

```text
random_search
scipy
pypfopt
black_litterman
sentiment_adjusted
```

## Notes And Limitations

- This is not investment advice.
- The optimizer uses historical returns and covariance, which are estimates, not guarantees.
- yfinance is convenient for local development but is not an institutional-grade data source.
- The current optimizer is educational and swappable; a deterministic SciPy or PyPortfolioOpt optimizer should be added later.
- No Docker is required.
- No database is required yet; all analysis is request-driven.

## Verification Completed

The current stack has been verified locally:

```text
Python FastAPI health: passed
Spring Boot health: passed
React production build: passed
Frontend proxy to Java: passed
Java to Python optimize/risk/frontier/montecarlo: passed
Java DTO validation: passed
```

## Next Steps

Good next improvements:

- Add a deterministic SciPy optimizer strategy.
- Add request/response tests for Java controller and client behavior.
- Add frontend tests for form validation and loading/error states.
- Add persistence with PostgreSQL once the workflow stabilizes.
- Add AI sentiment and allocation explanation as a separate optional layer.

