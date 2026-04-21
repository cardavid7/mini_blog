# Mini Blog API

This is a simple blog API built with [FastAPI](https://fastapi.tiangolo.com/). It uses SQLAlchemy for database operations and supports PostgreSQL.

## Features

- RESTful API for blog posts, authors, and tags.
- Environment variables configured via `.env`.
- Database integration using SQLAlchemy.

## Prerequisites

- Python 3.8+
- PostgreSQL (or SQLite as fallback)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mini_blog
   ```

2. **Create and activate a virtual environment:**
   Using `venv`:
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup:**
   Ensure you have a `.env` file in the root directory. You can configure your database URL here. Example for PostgreSQL:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:123456@localhost:5432/fastapi_blog
   ```

## Running the Application

Start the development server using `uvicorn`:

```bash
uvicorn app.main:app --reload
```

Or using the FastAPI CLI (if available):

```bash
fastapi dev app/main.py
```

## API Documentation

Once the server is running, you can access the automatic interactive API documentation:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
