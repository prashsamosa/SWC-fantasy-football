# Comprehensive Guide: FastAPI with UV and Docker

This guide covers setting up a FastAPI application using UV package manager and deploying it with Docker.

## Table of Contents
- [Local Development Setup](#local-development-setup)
  - [Installing UV](#installing-uv)
  - [Setting Up the Virtual Environment](#setting-up-the-virtual-environment)
  - [Installing Dependencies](#installing-dependencies)
  - [Running the FastAPI Application](#running-the-fastapi-application)
  - [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Docker Deployment](#docker-deployment)
  - [Using Pip Dockerfile](#using-pip-dockerfile)
  - [Using UV Dockerfile](#using-uv-dockerfile)
  - [Docker Commands Reference](#docker-commands-reference)
- [Project Structure](#project-structure)
- [Configuration Files](#configuration-files)
  - [Dockerfile with Pip](#dockerfile-with-pip)
  - [Dockerfile with UV](#dockerfile-with-uv)
  - [.dockerignore](#dockerignore)

---

## Local Development Setup

### Installing UV

UV is a fast Python package installer and resolver written in Rust. To install UV:

```bash
pip install uv
```

### Setting Up the Virtual Environment

Create a new virtual environment using UV:

```bash
uv venv
```

Activate the virtual environment:

**On Unix/macOS**:
```bash
source .venv/bin/activate
```

**On Windows**:
```bash
.venv\Scripts\activate
```

### Installing Dependencies

Install dependencies from your requirements.txt file:

```bash
uv pip install -r requirements.txt
```

For a typical FastAPI application, your requirements.txt should include:

```
fastapi>=0.115.0
uvicorn>=0.23.0
sqlalchemy>=2.0.0
pydantic>=2.4.0
python-multipart>=0.0.9
pytest>=8.1.0 # Optional, for testing
httpx>=0.27.0 # Optional, for testing
```

### Running the FastAPI Application

To run your FastAPI application:

```bash
uvicorn main:app --reload
```

Where:
- `main` is the name of your Python file (main.py)
- `app` is the FastAPI instance in your code
- `--reload` enables auto-reload during development

Your API will be available at:
- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

### Troubleshooting Common Issues

1. **Port already in use**
   ```bash
   uvicorn main:app --reload --port 8001
   ```

2. **Debug mode for verbose output**
   ```bash
   uvicorn main:app --reload --debug
   ```

3. **Missing dependencies**
   ```bash
   uv pip install fastapi "uvicorn[standard]" sqlalchemy pydantic
   ```

4. **Database connectivity issues**
   Ensure your database file is in the correct location and accessible.

5. **Schema/model issues**
   Verify that all models referenced in main.py are properly defined.

---

## Docker Deployment

### Using Pip Dockerfile

1. **Create Dockerfile.pip**

```dockerfile
# Dockerfile for FastAPI application (using pip)
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code and database
COPY *.py /code/
COPY *.db /code/

# Expose port
EXPOSE 80

# Start the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

2. **Build and run the Docker image**

```bash
# Build
docker build -t fastapi-pip -f Dockerfile.pip .

# Run
docker run -p 8000:80 --name fastapi-container-pip fastapi-pip
```

### Using UV Dockerfile

1. **Create Dockerfile.uv**

```dockerfile
# Dockerfile for FastAPI application (using uv)
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --no-cache-dir --system -r requirements.txt

# Copy application code and database
COPY *.py /code/
COPY *.db /code/

# Expose port
EXPOSE 80

# Start the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

2. **Build and run the Docker image**

```bash
# Build
docker build -t fastapi-uv -f Dockerfile.uv .

# Run
docker run -p 8000:80 --name fastapi-container-uv fastapi-uv
```

### Docker Commands Reference

**Building Images**
```bash
# Build with a tag
docker build -t [image-name] -f [dockerfile-name] .

# Build with no cache
docker build --no-cache -t [image-name] .
```

**Running Containers**
```bash
# Run with port mapping
docker run -p [host-port]:[container-port] --name [container-name] [image-name]

# Run in detached mode
docker run -d -p [host-port]:[container-port] --name [container-name] [image-name]

# Run with environment variables
docker run -p [host-port]:[container-port] -e ENV_VAR_NAME=value --name [container-name] [image-name]

# Run with volume mounting
docker run -p [host-port]:[container-port] -v [host-path]:[container-path] --name [container-name] [image-name]
```

**Container Management**
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop [container-name]

# Start a stopped container
docker start [container-name]

# Remove a container
docker rm [container-name]

# View logs
docker logs [container-name]

# Execute command in a running container
docker exec -it [container-name] [command]
```

**Image Management**
```bash
# List images
docker images

# Remove an image
docker rmi [image-name]

# Clean up unused images
docker image prune
```

---

## Project Structure

A typical FastAPI project structure:

```
project_directory/
├── .dockerignore
├── .env                  # Environment variables (do not commit to version control)
├── .gitignore
├── Dockerfile.pip        # Dockerfile using pip
├── Dockerfile.uv         # Dockerfile using uv
├── main.py               # FastAPI application entry point
├── models.py             # SQLAlchemy models
├── schemas.py            # Pydantic schemas
├── database.py           # Database connection setup
├── crud.py               # CRUD operations
├── requirements.txt      # Dependencies
├── README.md             # Project documentation
├── test_main.py         # Unit tests for main application
└── test_crud.py         # Unit tests for CRUD operations
              
``` 

---

## Configuration Files

### Dockerfile with Pip

```dockerfile
# Dockerfile for FastAPI application (using pip)
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code and database
COPY *.py /code/
COPY *.db /code/

# Expose port
EXPOSE 80

# Start the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

### Dockerfile with UV

```dockerfile
# Dockerfile for FastAPI application (using uv)
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --no-cache-dir --system -r requirements.txt

# Copy application code and database
COPY *.py /code/
COPY *.db /code/

# Expose port
EXPOSE 80

# Start the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

### .dockerignore

```
# .dockerignore file
.git
.gitignore
.env
.venv
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.pytest_cache/
htmlcov/
.coverage
.DS_Store
README.md
```

---

This guide was created on May 01, 2025, for FastAPI version 0.115.0, SQLAlchemy 2.0.0, Pydantic 2.4.0, and Uvicorn 0.23.0.