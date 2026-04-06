FROM python:3.10-slim
WORKDIR /app

# Install uv, a lightning-fast python package installer
RUN pip install uv

# Copy project files
COPY . .

# Install the project globally in the container using uv
RUN uv pip install --system .

# The entrypoint defined in pyproject.toml
CMD ["server"]