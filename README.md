#  Deliveroo Project

Deliveroo is a full-stack parcel delivery platform designed to streamline the process of sending, tracking, and managing parcels for both customers and administrators. The project combines a robust backend API, a user-friendly frontend interface, and seamless integrations with third-party services like Google Maps. Deliveroo is built for scalability, security, and ease of use, making it suitable for real-world deployment by logistics companies or as a learning project for modern web development.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Database Migrations & Seeding](#database-migrations--seeding)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Google Maps Integration](#google-maps-integration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
Deliveroo is a comprehensive parcel delivery management system. It allows users to register, log in, create and track parcels, and view delivery histories. Admins can manage all parcels, update statuses, and oversee the logistics process. The system integrates with Google Maps for address geocoding and route calculations, providing accurate delivery estimates and costs. Deliveroo is designed for both end-users (customers) and administrators, offering a seamless experience across web and mobile platforms.

---

## Features
- **User Registration & Authentication** (JWT-based)
- **Admin Role Management**
- **Parcel Creation, Tracking, and Status Updates**
- **Parcel History Logging**
- **Google Maps Integration** for geocoding and route calculations
- **RESTful API** for backend/frontend communication
- **Modern Frontend UI** (React or similar, if present)
- **Database Migrations & Seeding**
- **Comprehensive Testing Suite**
- **Dockerized for Easy Deployment**

---

## System Architecture

Deliveroo is structured as a modular, scalable web application:

```
+-------------------+        +-------------------+        +-------------------+
|    Frontend UI    | <----> |     Backend API   | <----> |     Database      |
| (React, Vue, etc) |        |   (Flask, REST)   |        | (Postgres/SQLite) |
+-------------------+        +-------------------+        +-------------------+
         |                          |
         |                          v
         |                +-------------------+
         |                | Google Maps API   |
         |                +-------------------+
```

- **Frontend:** Provides a user-friendly interface for customers and admins to interact with the system (e.g., parcel creation, tracking, admin dashboard).
- **Backend:** Handles business logic, authentication, parcel management, and exposes a RESTful API.
- **Database:** Stores users, parcels, histories, and other persistent data.
- **Integrations:** Google Maps API for geocoding, distance, and cost calculations.

---

## Tech Stack
- **Frontend:** React (or Vue/Angular, if implemented)
- **Backend:** Python, Flask, Flask-RESTful, Flask-JWT-Extended, Flask-Migrate, Flask-SQLAlchemy, Flask-Bcrypt, Flask-Cors
- **Database:** PostgreSQL (production), SQLite (development)
- **Integrations:** Google Maps API
- **DevOps:** Docker, Docker Compose

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Deliveroo
   ```

2. **Backend:**
   - Create a virtual environment and install dependencies:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -r server/requirements.txt
     ```
   - Set up environment variables (see below).

3. **Frontend:**
   - If a frontend directory exists (e.g., `client/`), follow its README for setup (usually `npm install` and `npm start`).

4. **Docker (Full Stack):**
   - To run everything with Docker:
     ```bash
     docker compose up --build
     ```

---

## Environment Variables

| Variable                  | Description                        |
|---------------------------|------------------------------------|
| SECRET_KEY                | Flask secret key                   |
| JWT_SECRET_KEY            | JWT signing key                    |
| SQLALCHEMY_DATABASE_URI   | Database connection string         |
| GOOGLE_MAPS_API_KEY       | Google Maps API key                |

---

## Database Migrations & Seeding

1. **Initialize migrations:**
   ```bash
   flask db init
   ```
2. **Create migration scripts:**
   ```bash
   flask db migrate
   ```
3. **Apply migrations:**
   ```bash
   flask db upgrade
   ```
4. **Seed the database:**
   ```bash
   python -m server.seed
   ```

---

## Running the Project

- **Backend (Development):**
  ```bash
  python -m server.app
  ```
- **Frontend (Development):**
  ```bash
  cd client
  npm start
  ```
- **Production (Docker):**
  ```bash
  docker compose up --build
  ```

---

## API Endpoints

See the [API Endpoints section above](#api-endpoints) for detailed routes, request/response formats, and authentication requirements. The backend exposes endpoints for user registration, login, profile, parcel management, and admin operations. All endpoints are documented for easy use with Postman or frontend integration.

---

## Google Maps Integration
- Used for geocoding addresses, calculating route distances, and estimating delivery costs.
- Requires a valid `GOOGLE_MAPS_API_KEY` in your environment variables.
- All location-based features in the UI and backend leverage this integration for accuracy.

---

## Testing
- **Backend:**
  ```bash
  pytest server/tests
  ```
- **Frontend:**
  - If present, run `npm test` in the frontend directory.
- Tests cover authentication, parcel logic, admin endpoints, and more.

---

## Deployment
- **Docker:**
  - Build and run with Docker Compose:
    ```bash
    docker compose up --build
    ```
- **Cloud (Render, Heroku, etc):**
  - Set environment variables in your cloud dashboard.
  - Use PostgreSQL for production.
  - Ensure Google Maps API key is set.
- **Frontend:**
  - Deploy to Netlify, Vercel, or similar (if applicable).

---

## Troubleshooting
- **Database errors:** Ensure migrations are up to date and the correct database URI is set.
- **Admin access:** Promote users to admin via the database if needed.
- **Google Maps errors:** Check your API key and billing status.
- **JWT errors:** Ensure your JWT secret is set and tokens are valid.
- **Frontend/Backend connection:** Ensure CORS is configured and both services are running.

---

## Contributing
1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## License
MIT License. See [LICENSE](LICENSE) for details.
