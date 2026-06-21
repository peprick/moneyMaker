# Spring Boot Backend

This service is the Java API layer for the Quant Portfolio Optimizer.

It does not perform quant calculations directly. It forwards portfolio requests
to the Python FastAPI quant engine and returns the results to future frontend
clients.

## Local Ports

```text
Python quant engine: http://localhost:8001
Spring Boot backend: http://localhost:8081
```

## Run Order

Start Python first:

```powershell
cd C:\Users\Sagarnil\new_proj
.\.venv\Scripts\Activate.ps1
python -m uvicorn quant_engine.main:app --reload --port 8001
```

Then start Java:

```powershell
cd C:\Users\Sagarnil\new_proj\backend
mvn spring-boot:run
```

## Backend API

```text
GET  /api/health
POST /api/optimize
POST /api/risk
POST /api/frontier
POST /api/montecarlo
```

The request bodies are validated through Java DTOs and then forwarded to the
Python quant engine. The optimizer strategy is still selected by request fields,
so future Python optimizers can be added without changing the Java route shape.
