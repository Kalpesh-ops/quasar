FROM python:3.10-slim
WORKDIR /app

# Install uv, a lightning-fast python package installer
RUN pip install uv

# Copy project files
COPY . .

# Force Python to recognize the /app directory as a module source
ENV PYTHONPATH="/app"

# Install the project globally in the container using uv
RUN uv pip install --system .

# The entrypoint defined in pyproject.toml
CMD ["server"]