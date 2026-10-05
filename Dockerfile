# Agentic GraphRAG - Reproducible Container Environment
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered UTF-8 logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    WORKSPACE_ROOT=/app

WORKDIR /app

# Install system dependencies (sqlite3 with FTS5 support, curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application pipeline code and runners
COPY agentic_pipeline/ /app/agentic_pipeline/
COPY rag_only_pipeline/ /app/rag_only_pipeline/
COPY graphrag_pipeline/ /app/graphrag_pipeline/
COPY tests/ /app/tests/
COPY run_agent.py run_benchmark_15q.py run_full_100q_benchmark.py run_optimized_agent_100q.py run_hidden_50q_benchmark.py generate_dashboard.py /app/

# Ensure runtime directories exist for mounting data, dataset, and results
RUN mkdir -p /app/data /app/dataset /app/results

# Default entrypoint: bash shell for interactive execution or CLI commands
CMD ["/bin/bash"]
