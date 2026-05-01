# Mini Blog API

A comprehensive and scalable RESTful API for a blog platform, built with **FastAPI**. It includes features like user authentication, role-based access control, and robust database operations.

## 🚀 Features

- **Modern & Fast**: Built with [FastAPI](https://fastapi.tiangolo.com/) using Python type hints for maximum performance and auto-completion.
- **Authentication & Security**:
  - Secure login with **JWT (JSON Web Tokens)** via OAuth2 with Password Flow.
  - Password hashing utilizing **Argon2** (`pwdlib`).
- **Role-Based Access Control (RBAC)**:
  - Differentiated roles: `admin`, `editor`, and `user` to restrict access to specific endpoints.
- **Robust Database Integration**:
  - ORM powered by **SQLAlchemy** (version 2.0+ styling).
  - PostgreSQL support using the high-performance `psycopg` driver.
- **Data Validation**: End-to-end data validation and serialization with **Pydantic**.
- **Pagination & Filtering**: Built-in support for listing, sorting, and searching resources (like Posts and Tags).
- **Interactive Documentation**: Automatic interactive API docs via Swagger UI and ReDoc.

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database ORM**: SQLAlchemy
- **Database Driver**: Psycopg (PostgreSQL)
- **Validation**: Pydantic
- **Security/Auth**: PyJWT, OAuth2PasswordBearer, pwdlib[argon2]
- **Environment**: python-dotenv

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL (or SQLite as a fallback for local testing)

## ⚙️ Installation & Setup

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
   Create a `.env` file in the root directory and configure your variables (such as the database URL and JWT secret):
   ```env
   # Example for PostgreSQL
   DATABASE_URL=postgresql+psycopg://postgres:123456@localhost:5432/fastapi_blog
   
   # Authentication settings
   SECRET_KEY=your_super_secret_jwt_key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## 🏃 Running the Application

You can start the development server using the FastAPI CLI (which uses Uvicorn under the hood):

```bash
fastapi dev app/main.py
```

Alternatively, run Uvicorn directly:

```bash
uvicorn app.main:app --reload
```

## 🌱 Database Seeding

You can populate the database with initial data using the provided seed scripts:

```bash
# Seed all data
python -m app.seeds all

# Or run specific seeds individually
python -m app.seeds users
python -m app.seeds categories
python -m app.seeds tags
```

## 📚 API Documentation

Once the server is running, you can access the automatic interactive API documentation:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 🔐 API Endpoints

### 👤 Authentication & Users
- `POST /api/v1/auth/register` - Register a new user account
- `POST /api/v1/auth/login` - Login to get the JWT Bearer token and user info
- `GET /api/v1/auth/me` - Get current logged-in user profile
- `PUT /api/v1/auth/role/{id}` - Change user role (Admin only)
- `POST /api/v1/auth/token` - Login to get the JWT Bearer token (OAuth2)

### 🏷️ Tags
- `GET /tags` - List tags with pagination and search
- `POST /tags` - Create a new tag (Editor/Admin only)
- `PUT /tags/{id}` - Update a tag (Editor/Admin only)
- `DELETE /tags/{id}` - Delete a tag (Admin only)
- `GET /tags/popular/top` - Get the most popular tags (User only)

### 📝 Posts
- `GET /posts` - List posts with pagination, sorting, and filtering
- `POST /posts` - Create a new post with optional image upload (Editor/Admin only)
- `GET /posts/by-tags` - List posts by tags
- `GET /posts/{id}` - Retrieve a specific post by its ID
- `PUT /posts/{id}` - Update an existing post (Editor/Admin only)
- `DELETE /posts/{id}` - Delete a post (Admin only)
- `GET /posts/post/{slug}` - Retrieve a specific post by its slug

### 📁 Categories
- `GET /categories` - List categories with pagination
- `POST /categories` - Create a new category
- `GET /categories/{id}` - Retrieve a specific category by its ID
- `PUT /categories/{id}` - Update a category
- `DELETE /categories/{id}` - Delete a category

### 📤 Uploads
- `POST /upload/bytes` - Upload an image as bytes
- `POST /upload/file` - Upload file to get metadata
- `POST /upload/save` - Save uploaded image to the media directory
