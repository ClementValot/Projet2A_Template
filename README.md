## Project 2A - Ub'EJR Eats

This project implements a meal delivery application, named Ub'EJR Eats, using a layered architecture (DAO, Service, API) and a PostgreSQL database. The application provides a RESTful API (based on FastAPI) for administrators and a Command Line Interface (CLI) for customers and drivers.

## 1\. General Architecture

The application follows a Model-Service-DAO (Data Access Object) architecture:

  * **API/WebService:** Entry point using FastAPI to handle HTTP requests.
  * **Service:** Contains the business logic, including authentication, order management, menu management, and integration with external services (Google Maps API for deliveries).
  * **DAO:** Data access layer that interacts with the PostgreSQL database.
  * **Client (CLI):** A command line interface allows users (customers and drivers) to interact with the application to place orders or manage deliveries.

## 2\. Prerequisites and Configuration

The project uses **PDM** (Python Development Master) for dependency and Python environment management.

### 2.1. PDM Installation

PDM must be installed globally on your system:

```bash
> pip install --user pdm
> pdm --version
```

(Optional) For faster dependency installation:

```bash
> pip install --user uv
> pdm config use_uv true
```

### 2.2. Environment Configuration (`.env`)

Create a `.env` file at the root of the project based on `.env.sample` and fill in the necessary variables.

| Variable | Description |
| :--- | :--- |
| `POSTGRES_HOST` | Database host. |
| `POSTGRES_PORT` | Database port. |
| `POSTGRES_DATABASE` | Database name. |
| `POSTGRES_USER` | Username. |
| `POSTGRES_PASSWORD` | Password. |
| `POSTGRES_SCHEMA=fd` | Default schema |
| `POSTGRES_SCHEMA_TEST=tests` | Integration tests schema |
| `JWT_SECRET` | Secret key for signing JSON Web Tokens. |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key required for address validation and itinerary calculations. |

## 3\. Installation and Initialization

### 3.1. Dependency Installation

Install all project dependencies defined in `pyproject.toml`:

```bash
> pdm install
```

### 3.2. Database Initialization

Three commands are available to initialize (or reset) the database:

| Script | Description | PDM Command |
| :--- | :--- | :--- |
| **Production** | Creates the production schema (`fd`) and inserts base data. | `pdm reset` |
| **Test** | Creates the test schema (`tests`) and inserts data for unit tests. | `pdm reset_test` |
| **Big Data** | Creates/resets the database and adds 10,000 dummy users. | `pdm bigdata` |

## 4\. How to Run the Application

### 4.1. Starting the API Server

To launch the FastAPI server (using Uvicorn):

```bash
> pdm start
```

The server will be accessible on port 5000 (default) at the address `http://0.0.0.0:5000` or via the link onyxia provides you if you are using it. The API documentation is available on the `/docs` endpoint.

### 4.2. Accessing the CLI (Console Interface)

To launch the interactive console mode:

```bash
> pdm CLI
```

## 5\. Development and Quality Tools

The project uses **Ruff** for formatting and linting, and **Pytest** for unit tests and coverage.

| Task | Tool | PDM Command |
| :--- | :--- | :--- |
| **Linter** | Ruff | `pdm run lint` |
| **Formatting** | Ruff | `pdm run format` |
| **Tests** | Pytest + Coverage | `pdm run test` |
| **Type Checking**| PyreFly | `pdm run typecheck` |

### 5.1. API Testing (Bruno)

You can test the API using the provided Bruno collection.

1.  Click the badge to fetch the collection:
    [\<img src="https://fetch.usebruno.com/button.svg" alt="Fetch in Bruno" style="width: 130px; height: 30px;" width="128" height="32"\>](https://fetch.usebruno.com?url=https%3A%2F%2Fgithub.com%2FJFLapitre%2FProjet2A_Groupe8.git "target=_blank rel=noopener noreferrer")
2.  Create an environment in Bruno and add a variable named `BASE_URL` containing your API link (e.g., `http://localhost:5000` or the link provided by your deployment environment).

## 6\. Note for Onyxia/k8s Users

The `init_project.sh` script can handle the installation. Ensure that you configure the necessary ports (e.g., port `5000` used by the application) in the network access configuration.