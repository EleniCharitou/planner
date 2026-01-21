# TravelPlanner API

[![Python: 3.12](https://img.shields.io/badge/Python-3.12-3670A0?style=flat&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Framework: Django 5.1](https://img.shields.io/badge/Framework-Django_5.1-092e20?style=flat&logo=django)](https://www.djangoproject.com/)
[![API: DRF 3.16](https://img.shields.io/badge/API-DRF_3.16-ff1709?style=flat)](https://www.django-rest-framework.org/)
[![Database: PostgreSQL 15+](https://img.shields.io/badge/DB-PostgreSQL_15+-316192?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Auth: SimpleJWT 5.5](https://img.shields.io/badge/Auth-SimpleJWT_5.5-black?style=flat&logo=jsonwebtokens)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![Code Quality: SonarQube](https://img.shields.io/badge/Code_Quality-SonarQube-blue?style=flat&logo=sonarqube)](https://sonarqube.org)

The core RESTful API for the TravelPlanner application. This service handles user authentication, complex trip logistics, and relational data management for a seamless travel planning experience.

---

## 🚀 Tech Stack
* **Framework:** [Django 5.1](https://docs.djangoproject.com/en/5.1/) / [Django REST Framework](https://www.django-rest-framework.org/)
* **Language:** [Python 3.12](https://docs.python.org/3.12/)
* **Database:** [PostgreSQL](https://www.postgresql.org/)
* **Authentication:** [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
* **API Documentation:** [Swagger (drf-yasg)](https://drf-yasg.readthedocs.io/)

---

## 🛠️ Getting Started

### 1. Prerequisites
* Python 3.12+
* PostgreSQL installed and running
* Virtual Environment (recommended)

### 2. Installation
Clone the repository and navigate to the backend directory:
```bash
# Create a virtual environment
python -m venv venv
```
```
# Activate virtual environment (Windows)
.\venv\Scripts\activate
```
```
# Install dependencies
pip install -r requirements.txt
```
### Managing Dependencies
If you install new packages during development, ensure the `requirements.txt` is updated:
```bash
pip freeze > requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```
# Copy the provided template to create your local .env file

cp .env.template .env
```
```env
# Or configure your local insatnce with the following keys
 
SECRET_KEY=your_secret_key_here
DEBUG=True

DB_NAME=travel-planner-db
DB_USER=your_postgres_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5174
```
### 4. Database Setup
**Create the Database:** Before running migrations, manually create a PostgreSQL database named `travel-planner-db` (or the name you chose in your `.env`), via psql or pgAdmin:
   ```sql
   CREATE DATABASE "travel-planner-db";
   ```
```bash
# Apply database migrations to create tables
python manage.py migrate
```
```
# Create an administrator account for the Django Admin UI
python manage.py createsuperuser
```

--- 

### 5. Running the Application 
```bash
# The standard command to launch the development server.
python manage.py runserver
```
---

## 📍 API Documentation

This project uses **Swagger** and **ReDoc** to provide real-time, interactive API documentation. This allows for testing endpoints directly through the browser.

* **Swagger UI:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
* **ReDoc:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

### Primary API Reference

| Service | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/token/` | Obtain Access & Refresh JWTs |
| **Auth** | `POST` | `/api/token/refresh/` | Renew an expired Access Token |
| **Users** | `POST` | `/api/users/` | User registration and management |
| **App** | `ALL` | `/api/` | Core itinerary and destination logic |

---

## ⚙️ Development Standards

### Database Management
Professional schema evolution is handled through Django's migration system:
* **Check migration status:** `python manage.py showmigrations`
* **Generate new schema changes:** `python manage.py makemigrations`
* **Sync database:** `python manage.py migrate`

### Quality Assurance
* **Static Analysis:** Integrated with **SonarQube** via GitHub Actions to monitor code smells and technical debt.
* **Testing:** Automated unit and integration testing suite using `pytest` (In Development).
* **Security:** Environment variables are managed via `python-decouple` and strictly excluded from version control.
