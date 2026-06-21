async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    ...options
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload?.message || payload?.detail || payload?.error || "Request failed";
    throw new Error(message);
  }
  return payload;
}

export function health() {
  return request("/api/health");
}

export function optimizePortfolio(body) {
  return request("/api/optimize", {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export function analyzeRisk(body) {
  return request("/api/risk", {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export function fetchFrontier(body) {
  return request("/api/frontier", {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export function runMonteCarlo(body) {
  return request("/api/montecarlo", {
    method: "POST",
    body: JSON.stringify(body)
  });
}

