# Django Project with PostgreSQL

Project to control the notifications sent to clients. 

## Project Structure

The project is divided into three main applications:

1. **rates**: It contains service to check if rates for a certain type and user are ok.
2. **notifications**: Manages the creation, edition and sending of notifications.
3. **clients**: Handles client management.

## Environment Variables Setup

Before starting the application, make sure to configure the environment variables listed in the `.env.example` file at the root of the project, into a new `.env` file

## Running the app with Docker Compose
1. **Build the Docker images**
 `docker compose build`
2. **Start the containers**
 `docker compose up -d`
3. **Apply migrations inside container**
 `docker compose exec backend python3 manage.py migrate`
4. **Access app: in your browser, browse to `http://localhost:8000`**
5. **Run tests inside container**
 `docker compose exec backend python3 manage.py test`
