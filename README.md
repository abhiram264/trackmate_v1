# TrackMate Backend

## About
TrackMate is a comprehensive application designed to manage and track various entities. This README focuses on the backend services that power the application, handling data storage, processing, and API endpoints.

## Tech Stack (Backend)
- **Python**: The core programming language used for backend development.
- **FastAPI**: A modern, fast web framework for building APIs with Python based on standard Python type hints.
- **Uvicorn**: A lightning-fast ASGI server implementation, used for running FastAPI applications.
- **SQLAlchemy**: An SQL toolkit and Object-Relational Mapper (ORM) that provides a full suite of well-known persistence patterns for Python.
- **MySQL**: A popular open-source relational database management system used for data storage.
- **PyMySQL**: A pure Python MySQL client library for connecting to MySQL databases.
- **Pytest**: A testing framework for Python, used for writing and running backend API tests.
- **Marshmallow**: An ORM/ODM/framework-agnostic library for converting complex objects to and from native Python datatypes.

## Setup

### Prerequisites
- Python 3.x
- pip (Python package installer)
- MySQL Server (version 5.7 or higher)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/trackmate.git
    cd trackmate_v1
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up MySQL database:**
    - Install MySQL Server if you haven't already
    - Create a new database named `trackmate`
    - Create a MySQL user with appropriate permissions or use the root user

5.  **Set up environment variables:**
    Create a `.env` file in the root directory of the project (if it doesn't exist) and add the following:
    ```
    DATABASE_URL=mysql+pymysql://username:password@localhost:3306/trackmate
    SECRET_KEY='your_super_secret_key_here'
    ```
    *Replace `username`, `password` with your MySQL credentials and `your_super_secret_key_here` with a strong, random key.*

6.  **Initialize the database:**
    The database tables will be created automatically when you start the application for the first time.

## Running the Application

To start the FastAPI backend server:

1.  **Ensure your virtual environment is active.**

2.  **Run the FastAPI application with uvicorn:**
    ```bash
    uvicorn app.main:app --reload
    ```

    The application will typically run on `http://127.0.0.1:8000`.

    **Optional flags:**
    - `--reload`: Automatically reloads the server when code changes (development only)
    - `--host 0.0.0.0`: Makes the server accessible from other devices on the network
    - `--port 8000`: Specifies the port (default is 8000)

3.  **Access the API documentation:**
    - Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
    - Alternative API docs (ReDoc): `http://127.0.0.1:8000/redoc`

## API Testing

The backend APIs can be tested using `pytest`. To run the tests, ensure your virtual environment is active and run:

```bash
pytest
```

This will discover and run all tests in the `tests/` directory.

### Example API Endpoints (Conceptual)

While specific endpoints will depend on your application's design, here are examples of common API interactions:

-   **GET /api/items**: Retrieve a list of items.
-   **GET /api/items/{id}**: Retrieve a single item by ID.
-   **POST /api/items**: Create a new item (with a JSON body).
-   **PUT /api/items/{id}**: Update an existing item (with a JSON body).
-   **DELETE /api/items/{id}**: Delete an item by ID.

You can use tools like `curl`, Postman, Insomnia, or write Python scripts to interact with these APIs.

### Using `curl` (Example)

```bash
# Example: Get all items
curl -X GET http://127.0.0.1:8000/api/items

# Example: Create a new item
curl -X POST -H "Content-Type: application/json" -d '{"name": "New Item", "description": "This is a new item."}' http://127.0.0.1:8000/api/items
```

*(Note: The actual port and endpoint paths might vary based on your FastAPI application's configuration.)*

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: Visit `http://127.0.0.1:8000/docs` to explore and test your APIs interactively
- **ReDoc**: Visit `http://127.0.0.1:8000/redoc` for an alternative documentation view